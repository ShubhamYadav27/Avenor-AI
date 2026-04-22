"""
Apollo.io lead fetcher.
Pulls companies + decision-maker contacts matching your ICP,
stores them in Postgres, and attaches detected signals.
"""
import logging
from datetime import datetime
from typing import Optional
import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Company, Contact, Signal, SignalType, LeadStatus

logger = logging.getLogger(__name__)

APOLLO_BASE = "https://api.apollo.io/v1"


class ApolloFetcher:
    def __init__(self):
        self.api_key = settings.APOLLO_API_KEY
        self.headers = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "X-Api-Key": self.api_key,
        }

    def search_companies(
        self,
        industries: Optional[list[str]] = None,
        min_employees: int = 50,
        max_employees: int = 500,
        locations: Optional[list[str]] = None,
        page: int = 1,
        per_page: int = 25,
    ) -> dict:
        """
        Search Apollo for companies matching ICP filters.
        Returns raw Apollo response.
        """
        payload = {
            "page": page,
            "per_page": per_page,
            "organization_num_employees_ranges": [
                f"{min_employees},{max_employees}"
            ],
        }

        if industries:
            payload["organization_industry_tag_ids"] = []
            # Apollo uses industry names in people_search, not tag IDs
            payload["q_organization_industry_tag_id"] = industries

        if locations:
            payload["organization_locations"] = locations

        try:
            resp = httpx.post(
                f"{APOLLO_BASE}/mixed_companies/search",
                json=payload,
                headers=self.headers,
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Apollo company search failed: {e.response.status_code} — {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Apollo request error: {e}")
            raise

    def get_people_for_company(
        self,
        domain: str,
        titles: Optional[list[str]] = None,
        seniority: Optional[list[str]] = None,
    ) -> dict:
        """
        Get decision-maker contacts for a given company domain.
        Defaults to VP / Head / Director / C-Suite level.
        """
        payload = {
            "q_organization_domains": domain,
            "page": 1,
            "per_page": 5,
            "person_seniorities": seniority or ["vp", "director", "c_suite", "head"],
        }

        if titles:
            payload["person_titles"] = titles

        try:
            resp = httpx.post(
                f"{APOLLO_BASE}/mixed_people/search",
                json=payload,
                headers=self.headers,
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Apollo people search failed: {e.response.status_code}")
            raise

    def enrich_company(self, domain: str) -> dict:
        """Get full company profile by domain."""
        try:
            resp = httpx.get(
                f"{APOLLO_BASE}/organizations/enrich",
                params={"domain": domain},
                headers=self.headers,
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Apollo enrich failed for {domain}: {e.response.status_code}")
            return {}


def fetch_and_store_leads(
    db: Session,
    industries: Optional[list[str]] = None,
    min_employees: int = None,
    max_employees: int = None,
    locations: Optional[list[str]] = None,
    page: int = 1,
    limit: int = 25,
) -> dict:
    """
    Main entry point: fetch leads from Apollo, store companies + contacts.
    Returns summary of what was ingested.
    """
    fetcher = ApolloFetcher()

    # Use ICP defaults from config if not passed
    industries = industries or settings.icp_industries_list
    min_employees = min_employees or settings.ICP_MIN_EMPLOYEES
    max_employees = max_employees or settings.ICP_MAX_EMPLOYEES
    locations = locations or settings.icp_locations_list

    logger.info(f"Fetching leads from Apollo — industry: {industries}, employees: {min_employees}–{max_employees}")

    raw = fetcher.search_companies(
        industries=industries,
        min_employees=min_employees,
        max_employees=max_employees,
        locations=locations,
        page=page,
        per_page=limit,
    )

    companies_created = 0
    contacts_created = 0
    signals_created = 0

    for org in raw.get("organizations", []):
        # Skip if already stored
        existing = db.query(Company).filter_by(apollo_id=org.get("id")).first()
        if existing:
            logger.debug(f"Company already exists: {org.get('name')}")
            continue

        # Build company record
        company = Company(
            apollo_id=org.get("id"),
            name=org.get("name", ""),
            domain=org.get("primary_domain"),
            industry=org.get("industry"),
            employee_count=org.get("estimated_num_employees"),
            location=_extract_location(org),
            founded_year=org.get("founded_year"),
            description=org.get("short_description"),
            technologies=org.get("current_technologies", []),
            funding_total=org.get("total_funding"),
            last_funding_round=org.get("latest_funding_stage"),
            linkedin_url=org.get("linkedin_url"),
            website=org.get("website_url"),
            raw_data=org,
            status=LeadStatus.NEW,
        )
        db.add(company)
        db.flush()  # get the ID
        companies_created += 1

        # Detect and attach signals from company data
        new_signals = _detect_signals_from_company(org, company.id)
        for sig in new_signals:
            db.add(sig)
            signals_created += 1

        # Fetch contacts for this company
        if company.domain:
            try:
                people_data = fetcher.get_people_for_company(domain=company.domain)
                primary_set = False

                for person in people_data.get("people", []):
                    contact = Contact(
                        apollo_id=person.get("id"),
                        company_id=company.id,
                        first_name=person.get("first_name"),
                        last_name=person.get("last_name"),
                        full_name=person.get("name"),
                        title=person.get("title"),
                        seniority=person.get("seniority"),
                        email=_extract_email(person),
                        email_verified=_has_verified_email(person),
                        linkedin_url=person.get("linkedin_url"),
                        location=person.get("city"),
                        is_primary=not primary_set,  # first contact = primary
                        raw_data=person,
                    )
                    db.add(contact)
                    contacts_created += 1
                    primary_set = True

            except Exception as e:
                logger.warning(f"Could not fetch contacts for {company.domain}: {e}")

        company.status = LeadStatus.ENRICHED

    db.commit()

    logger.info(
        f"Ingestion complete — companies: {companies_created}, "
        f"contacts: {contacts_created}, signals: {signals_created}"
    )

    return {
        "companies_created": companies_created,
        "contacts_created": contacts_created,
        "signals_created": signals_created,
        "total_in_response": len(raw.get("organizations", [])),
    }


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _extract_location(org: dict) -> str:
    parts = [org.get("city"), org.get("state"), org.get("country")]
    return ", ".join(p for p in parts if p)


def _extract_email(person: dict) -> Optional[str]:
    email = person.get("email")
    if email and "@" in email:
        return email
    # Apollo sometimes stores in organization_email
    return person.get("organization", {}).get("contact_email")


def _has_verified_email(person: dict) -> bool:
    return person.get("email_status") in ("verified", "likely to engage")


def _detect_signals_from_company(org: dict, company_id) -> list[Signal]:
    """
    Extract signals from raw Apollo company data.
    Real signals come from dedicated monitors; this is a simple baseline.
    """
    signals = []
    now = datetime.utcnow()

    # Funding signal
    if org.get("latest_funding_stage") and org.get("latest_funding_stage") not in ("", None):
        signals.append(Signal(
            company_id=company_id,
            signal_type=SignalType.FUNDING,
            signal_source="apollo",
            raw_value=org.get("latest_funding_stage"),
            strength=0.35,
            decayed_score=0.35,  # will be recalculated by scorer
            detected_at=now,
            metadata_={
                "stage": org.get("latest_funding_stage"),
                "total_funding": org.get("total_funding"),
            },
        ))

    # Tech stack signal (presence of key technologies)
    tech_triggers = {"Snowflake", "Databricks", "Airflow", "dbt", "Segment", "Rudderstack"}
    techs = {t.get("name", "") for t in org.get("current_technologies", [])}
    matching_techs = list(techs & tech_triggers)
    if matching_techs:
        signals.append(Signal(
            company_id=company_id,
            signal_type=SignalType.TECH_CHANGE,
            signal_source="apollo",
            raw_value=", ".join(matching_techs),
            strength=0.20,
            decayed_score=0.20,
            detected_at=now,
            metadata_={"technologies": matching_techs},
        ))

    return signals
