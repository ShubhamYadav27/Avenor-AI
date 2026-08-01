"""
app/integrations/hubspot/sync.py

CRM sync engine for HubSpot.
Handles both historical import (on first connect) and incremental sync.

Architecture:
  - Each sync type is an independent function (composable, testable)
  - All writes are idempotent (upsert on HubSpot ID)
  - CrmSyncState table tracks cursors/checkpoints for incremental sync
  - Company matching: exact domain → HS company ID → fuzzy name → create stub
  - Soft-delete handling for archived objects across all sync types
  - Structured metric tracking (duration, created, updated, skipped, failed, retries, api_requests)

Called by:
  - Celery tasks (scheduled incremental sync every 30 min)
  - OAuth callback (triggers historical import on first connect)
  - Manual API trigger (admin refresh)
"""
from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone
from typing import Any

try:
    from rapidfuzz import fuzz
except ImportError:
    from difflib import SequenceMatcher

    class _FuzzFallback:
        @staticmethod
        def ratio(s1: str, s2: str) -> float:
            if not s1 or not s2:
                return 0.0
            s1_l, s2_l = s1.lower().strip(), s2.lower().strip()
            if s1_l == s2_l:
                return 100.0
            return round(SequenceMatcher(None, s1_l, s2_l).ratio() * 100.0, 1)

        @staticmethod
        def token_set_ratio(s1: str, s2: str) -> float:
            return _FuzzFallback.ratio(s1, s2)

    fuzz = _FuzzFallback()



from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.integrations.hubspot.client import HubSpotClient
from app.models import (
    Company, CompanyStatus, Contact, CrmSyncState, CrmSyncStatus,
    HubSpotConnection, HubSpotDeal, HubSpotObjectType, HubSpotOwner,
    Outcome, OutcomeSource, OutcomeType, Signal, Workspace,
)

logger = get_logger(__name__)


# ── Sync state helpers ─────────────────────────────────────────

def _get_or_create_sync_state(
    db: Session, workspace_id: str, object_type: str
) -> CrmSyncState:
    state = (
        db.query(CrmSyncState)
        .filter_by(workspace_id=workspace_id, object_type=object_type)
        .first()
    )
    if state is None:
        state = CrmSyncState(
            workspace_id=workspace_id,
            object_type=object_type,
        )
        db.add(state)
        db.flush()
    return state


def _mark_sync_running(state: CrmSyncState, db: Session) -> None:
    state.last_run_status = CrmSyncStatus.RUNNING
    state.last_run_at = datetime.now(timezone.utc)
    state.last_run_error = None
    db.flush()


def _mark_sync_complete(
    state: CrmSyncState, db: Session, created: int, updated: int, sync_timestamp: datetime | None = None
) -> None:
    state.last_run_status = CrmSyncStatus.COMPLETED
    # Maintain checkpoint timestamp on successful sync
    state.last_synced_at = sync_timestamp or datetime.now(timezone.utc)
    state.last_run_created = created
    state.last_run_updated = updated
    state.total_synced += created + updated
    db.flush()


def _mark_sync_failed(state: CrmSyncState, db: Session, error: str) -> None:
    state.last_run_status = CrmSyncStatus.FAILED
    state.last_run_error = error[:1000]
    db.flush()


# ── Company matching ───────────────────────────────────────────

def _match_or_create_company(
    db: Session,
    workspace_id: str,
    domain: str | None,
    company_name: str | None,
    hs_company_id: str,
) -> Company | None:
    """
    Find an existing Avenor company or create a stub for CRM-only companies.
    Match order: exact domain → HS company ID in raw data → fuzzy name.
    Persists crm_match_metadata for auditing.
    """
    matched_at = datetime.now(timezone.utc).isoformat()
    threshold = getattr(settings, "HUBSPOT_FUZZY_MATCH_THRESHOLD", 85)

    # 1. Exact domain match
    if domain:
        company = (
            db.query(Company)
            .filter_by(workspace_id=workspace_id, domain=domain)
            .first()
        )
        if company:
            raw = dict(company.raw_apollo_data or {})
            raw["hubspot_id"] = str(hs_company_id)
            raw["crm_match_metadata"] = {
                "match_type": "exact_domain",
                "confidence_score": 1.0,
                "matched_at": matched_at,
            }
            company.raw_apollo_data = raw
            return company

    # 2. Search by HubSpot company ID in raw data
    companies = db.query(Company).filter_by(workspace_id=workspace_id).all()
    for c in companies:
        raw = c.raw_apollo_data or {}
        if str(raw.get("hubspot_id", "")) == str(hs_company_id):
            raw_dict = dict(raw)
            raw_dict["crm_match_metadata"] = {
                "match_type": "hubspot_id",
                "confidence_score": 1.0,
                "matched_at": matched_at,
            }
            c.raw_apollo_data = raw_dict
            return c

    # 3. Configurable fuzzy name match (> threshold)
    if company_name:
        for c in companies:
            ratio = fuzz.ratio(c.name.lower(), company_name.lower())
            if ratio > threshold:
                raw = dict(c.raw_apollo_data or {})
                raw["hubspot_id"] = str(hs_company_id)
                raw["crm_match_metadata"] = {
                    "match_type": "fuzzy_name",
                    "confidence_score": round(ratio / 100.0, 3),
                    "fuzzy_ratio": ratio,
                    "threshold_used": threshold,
                    "matched_at": matched_at,
                }
                c.raw_apollo_data = raw
                logger.info(
                    "fuzzy_company_match_found",
                    workspace_id=workspace_id,
                    matched_name=c.name,
                    hs_name=company_name,
                    ratio=ratio,
                    threshold=threshold,
                )
                return c

    # 4. Create a minimal stub company for CRM-only companies
    if company_name or domain:
        stub = Company(
            workspace_id=workspace_id,
            name=company_name or domain or "Unknown",
            domain=domain,
            status=CompanyStatus.MONITORING,
            composite_score=0.0,
            raw_apollo_data={
                "hubspot_id": str(hs_company_id),
                "crm_match_metadata": {
                    "match_type": "stub_created",
                    "confidence_score": 1.0,
                    "matched_at": matched_at,
                },
            },
        )
        db.add(stub)
        db.flush()
        logger.info(
            "crm_stub_company_created",
            name=company_name,
            domain=domain,
            workspace_id=workspace_id,
            hs_company_id=hs_company_id,
        )
        return stub

    return None


# ── Owner sync ─────────────────────────────────────────────────

def sync_owners(
    db: Session, client: HubSpotClient, workspace_id: str
) -> dict:
    """Sync HubSpot owners (deal owners / salespeople). Handles soft-delete for archived owners."""
    start_time = time.time()
    state = _get_or_create_sync_state(db, workspace_id, HubSpotObjectType.OWNER)
    _mark_sync_running(state, db)

    created = updated = skipped = failed = 0
    checkpoint_time = datetime.now(timezone.utc)

    try:
        owners = client.get_owners()
        for raw in owners:
            hs_owner_id = str(raw.get("id", ""))
            if not hs_owner_id:
                skipped += 1
                continue

            is_archived = bool(raw.get("archived", False))

            existing = (
                db.query(HubSpotOwner)
                .filter_by(workspace_id=workspace_id, hubspot_owner_id=hs_owner_id)
                .first()
            )
            if existing:
                existing.email = raw.get("email")
                existing.first_name = raw.get("firstName")
                existing.last_name = raw.get("lastName")
                # Soft-delete: update is_active status based on archived state
                existing.is_active = not is_archived
                existing.synced_at = checkpoint_time
                updated += 1
            else:
                db.add(HubSpotOwner(
                    workspace_id=workspace_id,
                    hubspot_owner_id=hs_owner_id,
                    email=raw.get("email"),
                    first_name=raw.get("firstName"),
                    last_name=raw.get("lastName"),
                    is_active=not is_archived,
                ))
                created += 1

        db.flush()
        _mark_sync_complete(state, db, created, updated, sync_timestamp=checkpoint_time)
        db.commit()

        duration = round(time.time() - start_time, 3)
        metrics = {
            "created": created,
            "updated": updated,
            "skipped": skipped,
            "failed": failed,
            "duration_seconds": duration,
            "api_requests": getattr(client, "request_count", 0),
            "retries": getattr(client, "retry_count", 0),
        }
        logger.info("owners_synced", workspace_id=workspace_id, **metrics)
        return metrics

    except Exception as e:
        _mark_sync_failed(state, db, str(e))
        db.commit()
        raise


# ── Company sync ───────────────────────────────────────────────

def sync_companies(
    db: Session, client: HubSpotClient, workspace_id: str
) -> dict:
    """
    Directly sync HubSpot companies into Avenor companies table.
    Handles incremental checkpointing and soft-deletes (archived companies).
    """
    start_time = time.time()
    state = _get_or_create_sync_state(db, workspace_id, HubSpotObjectType.COMPANY)
    modified_after = state.last_synced_at
    _mark_sync_running(state, db)

    created = updated = skipped = failed = 0
    checkpoint_time = datetime.now(timezone.utc)

    try:
        for raw in client.get_companies(modified_after=modified_after):
            hs_company_id = str(raw.get("id", ""))
            if not hs_company_id:
                skipped += 1
                continue

            props = raw.get("properties", {})
            domain = props.get("domain") or props.get("website")
            company_name = props.get("name")
            is_archived = bool(raw.get("archived", False))

            try:
                company = _match_or_create_company(
                    db=db,
                    workspace_id=workspace_id,
                    domain=domain,
                    company_name=company_name,
                    hs_company_id=hs_company_id,
                )

                if company:
                    # Update company properties
                    if company_name:
                        company.name = company_name
                    if domain and not company.domain:
                        company.domain = domain
                    if props.get("website") and not company.website:
                        company.website = props.get("website")
                    if props.get("industry") and not company.industry:
                        company.industry = props.get("industry")
                    if props.get("numberofemployees"):
                        try:
                            company.employee_count = int(props.get("numberofemployees"))
                        except (ValueError, TypeError):
                            pass
                    if props.get("city"):
                        company.location_city = props.get("city")
                    if props.get("state"):
                        company.location_state = props.get("state")
                    if props.get("country"):
                        company.location_country = props.get("country")
                    if props.get("description"):
                        company.description = props.get("description")

                    # Handle soft-delete / status if archived in HubSpot
                    if is_archived:
                        company.status = CompanyStatus.DISQUALIFIED.value

                    raw_data = dict(company.raw_apollo_data or {})
                    raw_data["hubspot_id"] = hs_company_id
                    raw_data["hubspot_properties"] = props
                    company.raw_apollo_data = raw_data
                    updated += 1
                else:
                    skipped += 1

            except Exception as item_err:
                failed += 1
                logger.warning(
                    "company_sync_item_error",
                    workspace_id=workspace_id,
                    hs_company_id=hs_company_id,
                    error=str(item_err),
                )

        db.flush()
        _mark_sync_complete(state, db, created, updated, sync_timestamp=checkpoint_time)
        db.commit()

        duration = round(time.time() - start_time, 3)
        metrics = {
            "created": created,
            "updated": updated,
            "skipped": skipped,
            "failed": failed,
            "duration_seconds": duration,
            "api_requests": getattr(client, "request_count", 0),
            "retries": getattr(client, "retry_count", 0),
        }
        logger.info("companies_synced", workspace_id=workspace_id, **metrics)
        return metrics

    except Exception as e:
        _mark_sync_failed(state, db, str(e))
        db.commit()
        raise


# ── Contact sync ───────────────────────────────────────────────

def sync_contacts(
    db: Session, client: HubSpotClient, workspace_id: str
) -> dict:
    """
    Incrementally sync HubSpot contacts into Avenor contacts table.
    Ensures contacts are attached to companies and supports soft-deletes.
    """
    start_time = time.time()
    state = _get_or_create_sync_state(db, workspace_id, HubSpotObjectType.CONTACT)
    modified_after = state.last_synced_at
    _mark_sync_running(state, db)

    created = updated = skipped = failed = 0
    checkpoint_time = datetime.now(timezone.utc)

    try:
        for raw in client.get_contacts(modified_after=modified_after):
            hs_contact_id = str(raw.get("id", ""))
            if not hs_contact_id:
                skipped += 1
                continue

            props = raw.get("properties", {})
            is_archived = bool(raw.get("archived", False))

            # Resolve associated company
            hs_company_id = props.get("associatedcompanyid")
            company = None
            if hs_company_id:
                company_domain = client.get_company_domain(hs_company_id)
                company = _match_or_create_company(
                    db=db,
                    workspace_id=workspace_id,
                    domain=company_domain,
                    company_name=props.get("company"),
                    hs_company_id=hs_company_id,
                )

            if not company:
                # If no specific company, attempt match by contact company name or domain from email
                email = props.get("email")
                domain = email.split("@")[-1] if email and "@" in email else None
                company = _match_or_create_company(
                    db=db,
                    workspace_id=workspace_id,
                    domain=domain,
                    company_name=props.get("company"),
                    hs_company_id=hs_company_id or f"ct_{hs_contact_id}",
                )

            if not company:
                skipped += 1
                continue

            # Idempotent match by apollo_id or email
            existing = (
                db.query(Contact)
                .filter_by(company_id=company.id, apollo_id=f"hs_{hs_contact_id}")
                .first()
            )
            if not existing and props.get("email"):
                existing = (
                    db.query(Contact)
                    .filter_by(company_id=company.id, email=props.get("email"))
                    .first()
                )

            full_name = f"{props.get('firstname', '')} {props.get('lastname', '')}".strip() or props.get("email") or "Unknown"

            if existing:
                existing.first_name = props.get("firstname") or existing.first_name
                existing.last_name = props.get("lastname") or existing.last_name
                existing.full_name = full_name
                existing.title = props.get("jobtitle") or existing.title
                existing.email = props.get("email") or existing.email
                existing.phone = props.get("phone") or existing.phone
                existing.linkedin_url = props.get("linkedinbio") or existing.linkedin_url
                # Handle soft-delete / status flag in raw_data
                existing.raw_data = {
                    "hubspot_id": hs_contact_id,
                    "hubspot_company_id": hs_company_id,
                    "is_archived": is_archived,
                }
                updated += 1
            else:
                db.add(Contact(
                    company_id=company.id,
                    apollo_id=f"hs_{hs_contact_id}",
                    first_name=props.get("firstname"),
                    last_name=props.get("lastname"),
                    full_name=full_name,
                    title=props.get("jobtitle"),
                    email=props.get("email"),
                    phone=props.get("phone"),
                    linkedin_url=props.get("linkedinbio"),
                    email_status="hubspot",
                    is_primary=False,
                    raw_data={
                        "hubspot_id": hs_contact_id,
                        "hubspot_company_id": hs_company_id,
                        "is_archived": is_archived,
                    },
                ))
                created += 1

        db.flush()
        _mark_sync_complete(state, db, created, updated, sync_timestamp=checkpoint_time)
        db.commit()

        duration = round(time.time() - start_time, 3)
        metrics = {
            "created": created,
            "updated": updated,
            "skipped": skipped,
            "failed": failed,
            "duration_seconds": duration,
            "api_requests": getattr(client, "request_count", 0),
            "retries": getattr(client, "retry_count", 0),
        }
        logger.info("contacts_synced", workspace_id=workspace_id, **metrics)
        return metrics

    except Exception as e:
        _mark_sync_failed(state, db, str(e))
        db.commit()
        raise


# ── Deal sync (incremental) ────────────────────────────────────

def sync_deals_incremental(
    db: Session, client: HubSpotClient, workspace_id: str
) -> dict:
    """
    Incrementally sync deals modified since last run.
    Updates existing HubSpotDeal records and creates Outcome records for
    stage changes to closed_won / closed_lost.
    """
    start_time = time.time()
    state = _get_or_create_sync_state(db, workspace_id, HubSpotObjectType.DEAL)
    modified_after = state.last_synced_at
    _mark_sync_running(state, db)

    created = updated = skipped = failed = outcomes_logged = 0
    checkpoint_time = datetime.now(timezone.utc)

    try:
        for raw in client.get_deals(modified_after=modified_after):
            result = _upsert_deal(db, client, workspace_id, raw, is_historical=False)
            if result == "created":
                created += 1
            elif result == "updated":
                updated += 1
            else:
                skipped += 1

            if result in ("created", "updated"):
                # Check if this deal should create an outcome
                deal = (
                    db.query(HubSpotDeal)
                    .filter_by(
                        workspace_id=workspace_id,
                        hubspot_deal_id=str(raw.get("id", "")),
                    )
                    .first()
                )
                if deal and (deal.is_closed_won or deal.is_closed_lost):
                    if _maybe_log_outcome(db, workspace_id, deal):
                        outcomes_logged += 1

        db.flush()
        _mark_sync_complete(state, db, created, updated, sync_timestamp=checkpoint_time)
        db.commit()

        conn = db.query(HubSpotConnection).filter_by(workspace_id=workspace_id).first()
        if conn:
            conn.deals_synced += created + updated
            conn.last_sync_at = checkpoint_time
            db.commit()

        duration = round(time.time() - start_time, 3)
        metrics = {
            "created": created,
            "updated": updated,
            "skipped": skipped,
            "failed": failed,
            "outcomes_logged": outcomes_logged,
            "duration_seconds": duration,
            "api_requests": getattr(client, "request_count", 0),
            "retries": getattr(client, "retry_count", 0),
        }
        logger.info(
            "deals_incremental_sync_complete",
            workspace_id=workspace_id,
            **metrics,
        )
        return metrics

    except Exception as e:
        _mark_sync_failed(state, db, str(e))
        db.commit()
        raise


def _upsert_deal(
    db: Session,
    client: HubSpotClient,
    workspace_id: str,
    raw: dict,
    is_historical: bool,
) -> str:
    """Insert or update a HubSpotDeal. Returns 'created' | 'updated' | 'skipped'."""
    hs_deal_id = str(raw.get("id", ""))
    if not hs_deal_id:
        return "skipped"

    props = raw.get("properties", {})
    deal_stage = (props.get("dealstage") or "").lower()
    is_archived = bool(raw.get("archived", False))

    # Get associated HubSpot company ID
    associations = raw.get("associations", {})
    hs_company_ids = [
        str(r["id"])
        for r in associations.get("companies", {}).get("results", [])
    ]
    hs_company_id = hs_company_ids[0] if hs_company_ids else None

    # Resolve to Avenor company
    company = None
    domain = None
    if hs_company_id:
        domain = client.get_company_domain(hs_company_id)
        company_name = props.get("dealname")
        company = _match_or_create_company(
            db, workspace_id, domain, company_name, hs_company_id
        )

    # Parse dates
    close_date = _parse_hs_date(props.get("closedate"))
    create_date = _parse_hs_date(props.get("createdate"))

    # Determine if closed or soft-deleted/archived
    is_closed_won = deal_stage in {"closedwon", "closed_won"} and not is_archived
    is_closed_lost = (deal_stage in {"closedlost", "closed_lost"}) or is_archived
    closed_at = close_date if (is_closed_won or is_closed_lost) else None

    # Days to close
    days_to_close = None
    if create_date and closed_at:
        days_to_close = (closed_at - create_date).days

    # Avenor attribution data
    avenor_score = company.composite_score if company else None
    avenor_window = company.buying_window if company else None

    # Days Avenor was ahead of CRM deal creation
    days_ahead = None
    if company and create_date:
        first_signal = (
            db.query(Signal)
            .filter_by(company_id=company.id)
            .order_by(Signal.detected_at.asc())
            .first()
        )
        if first_signal:
            sig_dt = first_signal.detected_at
            if sig_dt.tzinfo is None:
                sig_dt = sig_dt.replace(tzinfo=timezone.utc)
            create_dt = create_date
            if create_dt.tzinfo is None:
                create_dt = create_dt.replace(tzinfo=timezone.utc)
            diff = (create_dt - sig_dt).days
            if diff > 0:
                days_ahead = diff

    existing = (
        db.query(HubSpotDeal)
        .filter_by(workspace_id=workspace_id, hubspot_deal_id=hs_deal_id)
        .first()
    )

    if existing:
        existing.company_id = company.id if company else existing.company_id
        existing.deal_stage = deal_stage
        existing.amount_usd = _parse_float(props.get("amount"))
        existing.close_date = close_date
        existing.is_closed_won = is_closed_won
        existing.is_closed_lost = is_closed_lost
        existing.closed_at = closed_at
        existing.days_to_close = days_to_close
        # Store soft-delete / archived state in raw_properties
        updated_props = dict(props)
        updated_props["is_archived"] = is_archived
        existing.raw_properties = updated_props
        return "updated"
    else:
        updated_props = dict(props)
        updated_props["is_archived"] = is_archived
        db.add(HubSpotDeal(
            workspace_id=workspace_id,
            company_id=company.id if company else None,
            hubspot_deal_id=hs_deal_id,
            hubspot_company_id=hs_company_id,
            hubspot_contact_ids=[
                str(r["id"])
                for r in associations.get("contacts", {}).get("results", [])
            ],
            hubspot_owner_id=props.get("hubspot_owner_id"),
            deal_name=props.get("dealname"),
            deal_stage=deal_stage,
            pipeline_id=props.get("pipeline"),
            amount_usd=_parse_float(props.get("amount")),
            close_date=close_date,
            created_date=create_date,
            is_closed_won=is_closed_won,
            is_closed_lost=is_closed_lost,
            closed_at=closed_at,
            days_to_close=days_to_close,
            avenor_predicted_score=avenor_score,
            avenor_predicted_window=avenor_window,
            avenor_first_detected_at=(
                db.query(Signal)
                .filter_by(company_id=company.id)
                .order_by(Signal.detected_at.asc())
                .first()
            ).detected_at if company else None,
            days_ahead_of_crm=days_ahead,
            is_historical=is_historical,
            raw_properties=updated_props,
        ))
        db.flush()
        return "created"


def _maybe_log_outcome(
    db: Session, workspace_id: str, deal: HubSpotDeal
) -> bool:
    """
    Log an Outcome record if this closed deal doesn't already have one.
    Returns True if a new outcome was created.
    """
    if not deal.company_id:
        return False

    # Deduplicate by HubSpot deal ID
    existing = (
        db.query(Outcome)
        .filter_by(workspace_id=workspace_id, hubspot_deal_id=deal.hubspot_deal_id)
        .first()
    )
    if existing:
        return False

    outcome_type = (
        OutcomeType.CLOSED_WON.value
        if deal.is_closed_won
        else OutcomeType.CLOSED_LOST.value
    )

    company = db.get(Company, deal.company_id)
    signals = db.query(Signal).filter_by(company_id=deal.company_id).all()
    signals_snapshot = [
        {"type": s.signal_type, "strength": round(s.decayed_strength, 3)}
        for s in signals
    ]

    days_from_first = None
    if signals:
        earliest = min(
            (s.detected_at.replace(tzinfo=timezone.utc) if s.detected_at.tzinfo is None else s.detected_at)
            for s in signals
        )
        days_from_first = (datetime.now(timezone.utc) - earliest).days

    db.add(Outcome(
        workspace_id=workspace_id,
        company_id=deal.company_id,
        outcome_type=outcome_type,
        outcome_source=OutcomeSource.HUBSPOT.value,
        predicted_composite_score=company.composite_score if company else deal.avenor_predicted_score,
        predicted_buying_window=company.buying_window if company else deal.avenor_predicted_window,
        active_signals_snapshot=signals_snapshot,
        days_from_first_signal=days_from_first,
        hubspot_deal_id=deal.hubspot_deal_id,
        deal_value_usd=deal.amount_usd,
        occurred_at=deal.closed_at or datetime.now(timezone.utc),
    ))
    db.flush()
    logger.info(
        "outcome_logged_from_deal",
        workspace_id=workspace_id,
        deal_id=deal.hubspot_deal_id,
        outcome_type=outcome_type,
    )
    return True


# ── Historical import ──────────────────────────────────────────

def run_historical_import(
    db: Session, client: HubSpotClient, workspace_id: str
) -> dict:
    """
    Import past CRM data when a customer first connects HubSpot.
    Imports deals from the past HUBSPOT_HISTORICAL_DAYS days.
    This bootstraps the model before enough new outcome data exists.
    """
    start_time = time.time()
    state = _get_or_create_sync_state(db, workspace_id, HubSpotObjectType.DEAL)
    if state.historical_import_completed:
        logger.info("historical_import_already_done", workspace_id=workspace_id)
        return {"skipped": True, "reason": "already_completed"}

    _mark_sync_running(state, db)
    cutoff = datetime.now(timezone.utc) - timedelta(days=settings.HUBSPOT_HISTORICAL_DAYS)

    stats = {
        "deals_processed": 0,
        "deals_created": 0,
        "outcomes_created": 0,
        "companies_matched": 0,
        "companies_created_as_stub": 0,
        "errors": 0,
    }

    logger.info(
        "historical_import_start",
        workspace_id=workspace_id,
        days_back=settings.HUBSPOT_HISTORICAL_DAYS,
    )

    try:
        # Sync owners first — needed for deal attribution
        sync_owners(db, client, workspace_id)

        # Import all deals modified in the historical window
        for raw in client.get_deals(modified_after=cutoff):
            stats["deals_processed"] += 1
            try:
                result = _upsert_deal(db, client, workspace_id, raw, is_historical=True)
                if result == "created":
                    stats["deals_created"] += 1

                    deal = (
                        db.query(HubSpotDeal)
                        .filter_by(
                            workspace_id=workspace_id,
                            hubspot_deal_id=str(raw.get("id", "")),
                        )
                        .first()
                    )
                    if deal and (deal.is_closed_won or deal.is_closed_lost):
                        if _maybe_log_outcome(db, workspace_id, deal):
                            stats["outcomes_created"] += 1

                if stats["deals_processed"] % settings.HUBSPOT_HISTORICAL_BATCH_SIZE == 0:
                    db.commit()
                    logger.info(
                        "historical_import_progress",
                        workspace_id=workspace_id,
                        processed=stats["deals_processed"],
                    )

            except Exception as e:
                stats["errors"] += 1
                logger.error(
                    "historical_deal_import_error",
                    deal_id=raw.get("id"),
                    error=str(e),
                )

        state.historical_import_completed = True
        state.historical_import_completed_at = datetime.now(timezone.utc)
        state.historical_deals_imported = stats["deals_created"]
        _mark_sync_complete(state, db, stats["deals_created"], 0)
        db.commit()

        stats["duration_seconds"] = round(time.time() - start_time, 3)
        stats["api_requests"] = getattr(client, "request_count", 0)
        stats["retries"] = getattr(client, "retry_count", 0)
        logger.info("historical_import_complete", workspace_id=workspace_id, **stats)
        return stats

    except Exception as e:
        _mark_sync_failed(state, db, str(e))
        db.commit()
        logger.error("historical_import_failed", workspace_id=workspace_id, error=str(e))
        raise


# ── Full incremental sync ──────────────────────────────────────

def run_incremental_sync(
    db: Session, workspace_id: str
) -> dict:
    """
    Run full incremental sync for one workspace.
    Called by Celery every HUBSPOT_SYNC_INTERVAL_MINUTES.
    Sync order: owners → companies → contacts → deals.
    """
    start_time = time.time()
    conn = db.query(HubSpotConnection).filter_by(workspace_id=workspace_id, is_active=True).first()
    if not conn:
        return {"skipped": True, "reason": "no_active_connection"}

    workspace = db.get(Workspace, workspace_id)
    if not workspace or not workspace.is_active:
        return {"skipped": True, "reason": "inactive_workspace"}

    client = HubSpotClient(conn, db)

    all_stats: dict[str, Any] = {}

    try:
        all_stats["owners"] = sync_owners(db, client, workspace_id)
    except Exception as e:
        all_stats["owners"] = {"error": str(e)}
        logger.error("incremental_owner_sync_failed", workspace_id=workspace_id, error=str(e))

    try:
        all_stats["companies"] = sync_companies(db, client, workspace_id)
    except Exception as e:
        all_stats["companies"] = {"error": str(e)}
        logger.error("incremental_company_sync_failed", workspace_id=workspace_id, error=str(e))

    try:
        all_stats["contacts"] = sync_contacts(db, client, workspace_id)
    except Exception as e:
        all_stats["contacts"] = {"error": str(e)}
        logger.error("incremental_contact_sync_failed", workspace_id=workspace_id, error=str(e))

    try:
        all_stats["deals"] = sync_deals_incremental(db, client, workspace_id)
    except Exception as e:
        all_stats["deals"] = {"error": str(e)}
        logger.error("incremental_deal_sync_failed", workspace_id=workspace_id, error=str(e))

    total_duration = round(time.time() - start_time, 3)
    all_stats["total_duration_seconds"] = total_duration
    all_stats["total_api_requests"] = getattr(client, "request_count", 0)
    all_stats["total_retries"] = getattr(client, "retry_count", 0)

    logger.info("incremental_sync_complete", workspace_id=workspace_id, stats=all_stats)
    return all_stats


# ── Utility functions ──────────────────────────────────────────

def _parse_hs_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        from dateutil.parser import parse
        dt = parse(str(value))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        try:
            ts_ms = int(value)
            return datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
        except Exception:
            return None


def _parse_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None
