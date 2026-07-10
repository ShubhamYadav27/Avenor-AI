"""
Apollo.io signal collector.
Fetches companies matching the workspace ICP and enriches with contacts.
Detects hiring signals from job posting data in company profiles.
"""
import math
from datetime import datetime, timezone
from typing import Any

import httpx
from sqlalchemy.orm import Session
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.config import settings
from app.core.exceptions import ExternalServiceError, RateLimitError
from app.core.logging import get_logger
from app.models import (
    Company, Contact, Signal, ICPConfig,
    SignalType, SignalSource, CompanyStatus,
)

logger = get_logger(__name__)

APOLLO_BASE = "https://api.apollo.io/v1"
TIMEOUT = 30.0


class ApolloCollector:
    """
    Collects company and contact data from Apollo.io.
    Handles rate limiting with exponential backoff.
    """

    def __init__(self):
        if not settings.has_apollo:
            raise ExternalServiceError("Apollo", "API key not configured")
        self.headers = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "X-Api-Key": settings.APOLLO_API_KEY,
        }

    @retry(
        retry=retry_if_exception_type(httpx.HTTPStatusError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=4, max=30),
    )
    def _post(self, endpoint: str, payload: dict) -> dict:
        try:
            resp = httpx.post(
                f"{APOLLO_BASE}/{endpoint}",
                json=payload,
                headers=self.headers,
                timeout=TIMEOUT,
            )
            if resp.status_code == 429:
                raise RateLimitError("Apollo", retry_after_seconds=60)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise RateLimitError("Apollo", retry_after_seconds=60)
            raise ExternalServiceError("Apollo", f"HTTP {e.response.status_code}: {e.response.text[:200]}")

    @retry(
        retry=retry_if_exception_type(httpx.HTTPStatusError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=4, max=30),
    )
    def _get(self, endpoint: str, params: dict) -> dict:
        try:
            resp = httpx.get(
                f"{APOLLO_BASE}/{endpoint}",
                params=params,
                headers=self.headers,
                timeout=TIMEOUT,
            )
            if resp.status_code == 429:
                raise RateLimitError("Apollo", retry_after_seconds=60)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            raise ExternalServiceError("Apollo", f"HTTP {e.response.status_code}")

    def search_companies(self, icp: ICPConfig, page: int = 1, per_page: int = 25) -> dict:
        """Search Apollo for companies matching the ICP."""
        payload: dict[str, Any] = {
            "page": page,
            "per_page": per_page,
        }

        if icp.industries:
            payload["organization_industry_tag_ids"] = icp.industries  # Apollo uses names too

        if icp.min_employees or icp.max_employees:
            payload["organization_num_employees_ranges"] = [
                f"{icp.min_employees},{icp.max_employees}"
            ]

        if icp.locations:
            payload["organization_locations"] = icp.locations

        if icp.funding_stages:
            payload["organization_latest_funding_stage_cd"] = icp.funding_stages

        return self._post("mixed_companies/search", payload)

    def get_contacts_for_company(self, domain: str, persona_titles: list[str]) -> dict:
        """Get decision-maker contacts for a company domain."""
        payload = {
            "q_organization_domains": domain,
            "page": 1,
            "per_page": 5,
            "person_seniorities": ["vp", "director", "c_suite", "head"],
        }
        if persona_titles:
            payload["person_titles"] = persona_titles[:10]  # API limit

        return self._post("mixed_people/search", payload)

    def enrich_company(self, domain: str) -> dict:
        """Full company enrichment by domain."""
        return self._get("organizations/enrich", {"domain": domain})


# ── Data normalization ─────────────────────────────────────────

def normalize_company(raw: dict, workspace_id: str, icp: ICPConfig) -> dict:
    """Convert raw Apollo org dict → Company field dict."""
    location_parts = [
        raw.get("city"),
        raw.get("state"),
        raw.get("country"),
    ]
    return {
        "workspace_id": workspace_id,
        "apollo_id": raw.get("id"),
        "name": raw.get("name", ""),
        "domain": raw.get("primary_domain"),
        "linkedin_url": raw.get("linkedin_url"),
        "website": raw.get("website_url"),
        "industry": raw.get("industry"),
        "employee_count": raw.get("estimated_num_employees"),
        "employee_range": _employee_range(raw.get("estimated_num_employees")),
        "location_city": raw.get("city"),
        "location_state": raw.get("state"),
        "location_country": raw.get("country"),
        "founded_year": raw.get("founded_year"),
        "description": raw.get("short_description"),
        "technologies": _extract_technologies(raw),
        "funding_total_usd": raw.get("total_funding"),
        "last_funding_stage": raw.get("latest_funding_stage"),
        "last_funding_date": _parse_funding_date(raw),
        "last_funding_amount_usd": raw.get("latest_funding_amount"),
        "status": CompanyStatus.MONITORING,
        "raw_apollo_data": raw,
    }


def normalize_contact(raw: dict, company_id: str, is_primary: bool = False) -> dict:
    """Convert raw Apollo person dict → Contact field dict."""
    email = raw.get("email") or ""
    email_status = raw.get("email_status", "unknown")
    return {
        "company_id": company_id,
        "apollo_id": raw.get("id"),
        "first_name": raw.get("first_name"),
        "last_name": raw.get("last_name"),
        "full_name": raw.get("name"),
        "title": raw.get("title"),
        "seniority": raw.get("seniority"),
        "department": raw.get("department"),
        "email": email if "@" in email else None,
        "email_status": email_status,
        "linkedin_url": raw.get("linkedin_url"),
        "phone": _extract_phone(raw),
        "is_primary": is_primary,
        "raw_data": raw,
    }


def detect_signals_from_apollo(
    raw_org: dict,
    company_id: str,
    workspace_id: str,
) -> list[dict]:
    """
    Extract signals directly available in Apollo company data.
    More granular signals (e.g. specific job posts) come from dedicated collectors.
    """
    signals = []
    now = datetime.now(timezone.utc)

    # Funding signal
    funding_stage = raw_org.get("latest_funding_stage")
    funding_amount = raw_org.get("latest_funding_amount")
    if funding_stage and funding_stage not in ("", "Unknown"):
        amount_str = f"${funding_amount/1_000_000:.1f}M" if funding_amount else ""
        signals.append({
            "workspace_id": workspace_id,
            "company_id": company_id,
            "signal_type": SignalType.FUNDING,
            "signal_source": SignalSource.APOLLO,
            "title": f"{funding_stage} funding {amount_str}".strip(),
            "description": f"{raw_org.get('name')} raised a {funding_stage} round.",
            "base_strength": 0.35,
            "decayed_strength": 0.35,
            "detected_at": now,
            "signal_metadata": {
                "stage": funding_stage,
                "amount_usd": funding_amount,
                "total_funding_usd": raw_org.get("total_funding"),
            },
        })

    # Hiring signal — inferred from employee growth and open roles count
    num_jobs = raw_org.get("jobs_count") or 0
    if num_jobs >= 3:
        strength = min(0.10 + (num_jobs * 0.02), 0.28)
        signals.append({
            "workspace_id": workspace_id,
            "company_id": company_id,
            "signal_type": SignalType.HIRING,
            "signal_source": SignalSource.APOLLO,
            "title": f"Actively hiring — {num_jobs} open roles",
            "description": f"{raw_org.get('name')} has {num_jobs} open positions, indicating active growth.",
            "base_strength": strength,
            "decayed_strength": strength,
            "detected_at": now,
            "signal_metadata": {"open_roles_count": num_jobs},
        })

    # Technology signals — key tools that indicate stack maturity
    tech_triggers = {
        "Snowflake", "Databricks", "dbt", "Airflow", "Segment",
        "Rudderstack", "Fivetran", "Looker", "Amplitude", "Mixpanel",
    }
    techs = {t.get("name", "") for t in raw_org.get("current_technologies", [])}
    matching = list(techs & tech_triggers)
    if matching:
        signals.append({
            "workspace_id": workspace_id,
            "company_id": company_id,
            "signal_type": SignalType.TECH_CHANGE,
            "signal_source": SignalSource.APOLLO,
            "title": f"Uses {', '.join(matching[:3])}",
            "description": f"Tech stack includes: {', '.join(matching)}",
            "base_strength": 0.15,
            "decayed_strength": 0.15,
            "detected_at": now,
            "signal_metadata": {"technologies": matching},
        })

    return signals


# ── Main ingest function ───────────────────────────────────────

def run_apollo_collection(db: Session, workspace_id: str) -> dict:
    """
    Full Apollo collection run for one workspace.
    Fetches companies → stores → fetches contacts → detects signals.
    Returns stats dict.
    """
    from app.models import Workspace
    workspace = db.get(Workspace, workspace_id)
    if not workspace or not workspace.icp_config:
        logger.warning("apollo_collection_skipped", workspace_id=workspace_id, reason="no_icp")
        return {"skipped": True, "reason": "no_icp_config"}

    icp = workspace.icp_config
    collector = ApolloCollector()

    stats = {
        "companies_created": 0,
        "companies_skipped": 0,
        "contacts_created": 0,
        "signals_created": 0,
        "errors": 0,
    }

    logger.info("apollo_collection_start", workspace_id=workspace_id)

    try:
        raw = collector.search_companies(icp, page=1, per_page=25)
    except ExternalServiceError as e:
        logger.error("apollo_search_failed", error=str(e), workspace_id=workspace_id)
        return {"error": str(e)}

    for raw_org in raw.get("organizations", []):
        try:
            domain = raw_org.get("primary_domain")
            if not domain:
                continue

            # Idempotency: skip if already stored for this workspace
            existing = (
                db.query(Company)
                .filter_by(workspace_id=workspace_id, domain=domain)
                .first()
            )
            if existing:
                stats["companies_skipped"] += 1
                continue

            # Create company
            company_data = normalize_company(raw_org, workspace_id, icp)
            company = Company(**company_data)
            db.add(company)
            db.flush()  # get ID
            stats["companies_created"] += 1

            # Detect and store signals
            signal_dicts = detect_signals_from_apollo(raw_org, company.id, workspace_id)
            for sd in signal_dicts:
                db.add(Signal(**sd))
                stats["signals_created"] += 1

            # Fetch contacts
            if domain:
                try:
                    people_raw = collector.get_contacts_for_company(
                        domain=domain,
                        persona_titles=icp.customer_personas or [],
                    )
                    primary_set = False
                    for i, person in enumerate(people_raw.get("people", [])[:5]):
                        contact_data = normalize_contact(
                            person, company.id, is_primary=not primary_set
                        )
                        # Skip contacts with no usable email
                        if not contact_data["email"] and contact_data["email_status"] == "invalid":
                            continue
                        db.add(Contact(**contact_data))
                        stats["contacts_created"] += 1
                        primary_set = True
                except ExternalServiceError as e:
                    logger.warning(
                        "contact_fetch_failed", domain=domain, error=str(e)
                    )

        except Exception as e:
            logger.error(
                "apollo_company_processing_error",
                company_name=raw_org.get("name"),
                error=str(e),
            )
            stats["errors"] += 1
            db.rollback()
            continue

    db.commit()
    logger.info("apollo_collection_complete", workspace_id=workspace_id, **stats)
    return stats


# ── Helpers ────────────────────────────────────────────────────

def _employee_range(count: int | None) -> str | None:
    if count is None:
        return None
    if count < 10: return "1-10"
    if count < 50: return "10-50"
    if count < 200: return "50-200"
    if count < 500: return "200-500"
    if count < 1000: return "500-1000"
    return "1000+"


def _extract_technologies(raw: dict) -> list[str]:
    return [t.get("name", "") for t in raw.get("current_technologies", []) if t.get("name")]


def _extract_phone(person: dict) -> str | None:
    phones = person.get("phone_numbers", [])
    if phones:
        return phones[0].get("sanitized_number")
    return person.get("phone_number")


def _parse_funding_date(raw: dict) -> datetime | None:
    date_str = raw.get("latest_funding_round_date")
    if not date_str:
        return None
    try:
        from dateutil.parser import parse
        return parse(date_str).replace(tzinfo=timezone.utc)
    except Exception:
        return None
