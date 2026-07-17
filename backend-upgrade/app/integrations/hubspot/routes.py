"""
app/integrations/hubspot/routes.py  (Phase 4.2 upgrade)

Production HubSpot integration routes.
Changes from Phase 4.1:
  - Fernet encryption replaces XOR for token storage
  - Expanded webhook: all deal stage changes (not just terminal)
  - New /sync/trigger endpoint for manual CRM refresh
  - New /sync/status endpoint showing per-object sync state
  - Webhook signature uses v3 scheme (hash of request body + timestamp)
  - Historical import triggered via proper Celery task
"""
import hashlib
import hmac
import json
from datetime import datetime, timezone, timedelta
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.auth import CurrentUser
from app.core.config import settings
from app.core.logging import get_logger
from app.db.session import get_db
from app.models import (
    Company, CrmSyncState, HubSpotConnection, HubSpotDeal,
    Outcome, OutcomeSource, OutcomeType, Signal,
)
from app.utils.encryption import encrypt_token, decrypt_token, is_fernet_token

logger = get_logger(__name__)
router = APIRouter(prefix="/integrations/hubspot", tags=["hubspot"])

HUBSPOT_TOKEN_URL = "https://api.hubapi.com/oauth/v1/token"
HUBSPOT_AUTH_URL = "https://app.hubspot.com/oauth/authorize"
HUBSPOT_API_BASE = "https://api.hubapi.com"

HUBSPOT_SCOPES = (
    "crm.objects.deals.read "
    "crm.objects.companies.read "
    "crm.objects.contacts.read "
    "crm.objects.owners.read "
    "oauth"
)

CLOSED_WON_STAGES = {"closedwon", "closed_won"}
CLOSED_LOST_STAGES = {"closedlost", "closed_lost"}


# ── OAuth flow ─────────────────────────────────────────────────

@router.get("/connect")
def get_oauth_url(current_user: CurrentUser):
    """Return the HubSpot OAuth authorization URL."""
    if not settings.has_hubspot:
        raise HTTPException(status_code=503, detail="HubSpot integration not configured")

    redirect_uri = _redirect_uri()
    auth_url = (
        f"{HUBSPOT_AUTH_URL}"
        f"?client_id={settings.HUBSPOT_APP_CLIENT_ID}"
        f"&redirect_uri={redirect_uri}"
        f"&scope={HUBSPOT_SCOPES.replace(' ', '%20')}"
        f"&state={current_user.workspace_id}"
    )
    return {"auth_url": auth_url, "redirect_uri": redirect_uri}


@router.get("/callback")
def oauth_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db),
):
    """
    HubSpot OAuth callback.
    Exchanges code for tokens (stored with Fernet encryption),
    registers webhooks, and triggers historical import.
    """
    if not settings.has_hubspot:
        raise HTTPException(status_code=503, detail="HubSpot integration not configured")

    try:
        resp = httpx.post(
            HUBSPOT_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "client_id": settings.HUBSPOT_APP_CLIENT_ID,
                "client_secret": settings.HUBSPOT_APP_CLIENT_SECRET,
                "redirect_uri": _redirect_uri(),
                "code": code,
            },
            timeout=15,
        )
        resp.raise_for_status()
        token_data = resp.json()
    except httpx.HTTPStatusError as e:
        logger.error("hubspot_token_exchange_failed", status=e.response.status_code)
        raise HTTPException(status_code=400, detail="Failed to exchange OAuth code")

    access_token = token_data["access_token"]
    refresh_token = token_data["refresh_token"]
    expires_in = token_data.get("expires_in", 1800)

    hub_id, hub_domain = _get_hub_info(access_token)

    workspace_id = state
    conn = db.query(HubSpotConnection).filter_by(workspace_id=workspace_id).first()
    if conn is None:
        conn = HubSpotConnection(workspace_id=workspace_id)
        db.add(conn)

    # Store tokens with production Fernet encryption
    conn.hub_id = hub_id
    conn.hub_domain = hub_domain
    conn.access_token_encrypted = encrypt_token(access_token)
    conn.refresh_token_encrypted = encrypt_token(refresh_token)
    conn.token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    conn.is_active = True
    conn.sync_error = None
    db.commit()

    # Register webhook subscriptions
    webhook_id = _register_webhooks(access_token, hub_id)
    if webhook_id:
        conn.webhook_id = webhook_id
        db.commit()

    # Trigger historical import as a background task
    try:
        from app.workers.tasks import hubspot_historical_import
        hubspot_historical_import.delay(workspace_id)
        logger.info("historical_import_queued", workspace_id=workspace_id)
    except Exception as e:
        logger.warning("historical_import_queue_failed", error=str(e))

    logger.info("hubspot_connected", workspace_id=workspace_id, hub_id=hub_id)
    return {
        "status": "connected",
        "hub_id": hub_id,
        "hub_domain": hub_domain,
        "message": "HubSpot connected. Historical import is running in background.",
    }


@router.get("/status")
def connection_status(current_user: CurrentUser, db: Session = Depends(get_db)):
    """Connection status + per-object sync state."""
    conn = db.query(HubSpotConnection).filter_by(
        workspace_id=current_user.workspace_id
    ).first()
    if not conn:
        return {"connected": False}

    # Per-object sync states
    sync_states = (
        db.query(CrmSyncState)
        .filter_by(workspace_id=current_user.workspace_id)
        .all()
    )

    return {
        "connected": conn.is_active,
        "hub_id": conn.hub_id,
        "hub_domain": conn.hub_domain,
        "deals_synced": conn.deals_synced,
        "last_sync_at": conn.last_sync_at.isoformat() if conn.last_sync_at else None,
        "sync_error": conn.sync_error,
        "token_expires_at": conn.token_expires_at.isoformat(),
        "token_encrypted_with": "fernet" if is_fernet_token(conn.access_token_encrypted) else "legacy_xor",
        "sync_states": [
            {
                "object_type": s.object_type,
                "status": s.last_run_status,
                "last_synced_at": s.last_synced_at.isoformat() if s.last_synced_at else None,
                "last_run_created": s.last_run_created,
                "last_run_updated": s.last_run_updated,
                "last_run_error": s.last_run_error,
                "historical_import_completed": s.historical_import_completed,
                "historical_deals_imported": s.historical_deals_imported,
                "total_synced": s.total_synced,
            }
            for s in sync_states
        ],
    }


@router.post("/sync/trigger")
def trigger_sync(current_user: CurrentUser, db: Session = Depends(get_db)):
    """Manually trigger incremental CRM sync for this workspace."""
    current_user.require_admin()
    conn = db.query(HubSpotConnection).filter_by(
        workspace_id=current_user.workspace_id, is_active=True
    ).first()
    if not conn:
        raise HTTPException(status_code=404, detail="No active HubSpot connection")

    from app.workers.tasks import hubspot_incremental_sync
    hubspot_incremental_sync.delay(str(current_user.workspace_id))
    return {"status": "sync_queued", "workspace_id": str(current_user.workspace_id)}


@router.post("/sync/historical")
def trigger_historical_import(current_user: CurrentUser, db: Session = Depends(get_db)):
    """Re-trigger historical import (e.g. to pull more history)."""
    current_user.require_admin()
    conn = db.query(HubSpotConnection).filter_by(
        workspace_id=current_user.workspace_id, is_active=True
    ).first()
    if not conn:
        raise HTTPException(status_code=404, detail="No active HubSpot connection")

    # Reset historical import flag so it runs again
    from app.models import CrmSyncState, HubSpotObjectType
    state = db.query(CrmSyncState).filter_by(
        workspace_id=current_user.workspace_id,
        object_type=HubSpotObjectType.DEAL,
    ).first()
    if state:
        state.historical_import_completed = False
        db.commit()

    from app.workers.tasks import hubspot_historical_import
    hubspot_historical_import.delay(str(current_user.workspace_id))
    return {"status": "historical_import_queued"}


@router.delete("/disconnect")
def disconnect(current_user: CurrentUser, db: Session = Depends(get_db)):
    """Disconnect HubSpot — marks connection inactive, preserves sync data."""
    current_user.require_admin()
    conn = db.query(HubSpotConnection).filter_by(
        workspace_id=current_user.workspace_id
    ).first()
    if conn:
        conn.is_active = False
        db.commit()
    return {"status": "disconnected"}


# ── Webhook receiver ───────────────────────────────────────────

@router.post("/webhook")
async def receive_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_hubspot_signature: Optional[str] = Header(None),
    x_hubspot_signature_v3: Optional[str] = Header(None),
    x_hubspot_request_timestamp: Optional[str] = Header(None),
):
    """
    HubSpot webhook event receiver.
    Verifies signature (v3 preferred, v1 fallback).
    Processes: deal stage changes (all stages), deal creation.
    """
    body_bytes = await request.body()

    # Signature verification
    if settings.HUBSPOT_WEBHOOK_SECRET:
        valid = False
        if x_hubspot_signature_v3 and x_hubspot_request_timestamp:
            valid = _verify_signature_v3(
                body_bytes, x_hubspot_signature_v3,
                x_hubspot_request_timestamp, str(request.url),
            )
        elif x_hubspot_signature:
            valid = _verify_signature_v1(body_bytes, x_hubspot_signature)

        if not valid:
            logger.warning("hubspot_webhook_invalid_signature")
            raise HTTPException(status_code=401, detail="Invalid webhook signature")

    try:
        events = json.loads(body_bytes)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    if not isinstance(events, list):
        events = [events]

    processed = skipped = errors = 0
    for event in events:
        try:
            result = _process_event(event, db)
            if result:
                processed += 1
            else:
                skipped += 1
        except Exception as e:
            errors += 1
            logger.error(
                "webhook_event_error",
                event_type=event.get("subscriptionType"),
                error=str(e),
            )

    db.commit()
    logger.info(
        "webhook_batch_complete",
        total=len(events), processed=processed, skipped=skipped, errors=errors,
    )
    return {"received": len(events), "processed": processed, "errors": errors}


def _process_event(event: dict, db: Session) -> bool:
    """
    Route a single webhook event.
    Returns True if an action was taken.
    """
    event_type = event.get("subscriptionType", "")

    if "deal.propertyChange" in event_type:
        prop = event.get("propertyName", "")
        if prop == "dealstage":
            return _handle_deal_stage_change(event, db)

    elif "deal.creation" in event_type:
        return _handle_deal_creation(event, db)

    return False


def _handle_deal_stage_change(event: dict, db: Session) -> bool:
    """
    Handle deal stage changes.
    For terminal stages (won/lost): log Outcome + upsert HubSpotDeal.
    For all stages: update existing HubSpotDeal record if it exists.
    """
    new_stage = (event.get("propertyValue") or "").lower()
    deal_id = str(event.get("objectId", ""))
    portal_id = str(event.get("portalId", ""))

    conn = db.query(HubSpotConnection).filter_by(hub_id=portal_id, is_active=True).first()
    if not conn:
        logger.debug("webhook_unknown_portal", portal_id=portal_id)
        return False

    workspace_id = str(conn.workspace_id)

    # Update existing HubSpotDeal if we have it
    existing_deal = (
        db.query(HubSpotDeal)
        .filter_by(workspace_id=workspace_id, hubspot_deal_id=deal_id)
        .first()
    )
    if existing_deal:
        existing_deal.deal_stage = new_stage
        existing_deal.is_closed_won = new_stage in CLOSED_WON_STAGES
        existing_deal.is_closed_lost = new_stage in CLOSED_LOST_STAGES
        if existing_deal.is_closed_won or existing_deal.is_closed_lost:
            existing_deal.closed_at = datetime.now(timezone.utc)

    # For terminal stages, log an Outcome
    if new_stage in CLOSED_WON_STAGES:
        outcome_type = OutcomeType.CLOSED_WON
    elif new_stage in CLOSED_LOST_STAGES:
        outcome_type = OutcomeType.CLOSED_LOST
    else:
        return existing_deal is not None  # updated deal but no outcome needed

    # Check for duplicate outcome
    dup = db.query(Outcome).filter_by(
        workspace_id=workspace_id, hubspot_deal_id=deal_id
    ).first()
    if dup:
        return False

    # Find company and log outcome
    try:
        from app.integrations.hubspot.client import HubSpotClient
        client = HubSpotClient(conn, db)
        company_ids = client.get_deal_associated_company_ids(deal_id)
        domain = client.get_company_domain(company_ids[0]) if company_ids else None
    except Exception as e:
        logger.warning("webhook_deal_lookup_failed", deal_id=deal_id, error=str(e))
        domain = None

    company = None
    if domain:
        company = (
            db.query(Company)
            .filter_by(workspace_id=workspace_id, domain=domain)
            .first()
        )

    if not company:
        logger.info("webhook_company_not_in_avenor", deal_id=deal_id, domain=domain)
        return False

    signals = db.query(Signal).filter_by(company_id=company.id).all()
    signals_snapshot = [
        {"type": s.signal_type, "strength": round(s.decayed_strength, 3)}
        for s in signals
    ]

    days_from_first = None
    if signals:
        earliest = min(
            s.detected_at.replace(tzinfo=timezone.utc)
            if s.detected_at.tzinfo is None else s.detected_at
            for s in signals
        )
        days_from_first = (datetime.now(timezone.utc) - earliest).days

    db.add(Outcome(
        workspace_id=workspace_id,
        company_id=company.id,
        outcome_type=outcome_type.value,
        outcome_source=OutcomeSource.HUBSPOT.value,
        predicted_composite_score=company.composite_score,
        predicted_buying_window=company.buying_window,
        active_signals_snapshot=signals_snapshot,
        days_from_first_signal=days_from_first,
        hubspot_deal_id=deal_id,
        occurred_at=datetime.now(timezone.utc),
    ))

    conn.deals_synced += 1
    conn.last_sync_at = datetime.now(timezone.utc)

    logger.info(
        "outcome_logged_via_webhook",
        company=company.name,
        stage=new_stage,
        outcome=outcome_type.value,
        workspace_id=workspace_id,
    )
    return True


def _handle_deal_creation(event: dict, db: Session) -> bool:
    """Record newly created deals for attribution tracking."""
    deal_id = str(event.get("objectId", ""))
    portal_id = str(event.get("portalId", ""))

    conn = db.query(HubSpotConnection).filter_by(hub_id=portal_id, is_active=True).first()
    if not conn:
        return False

    # Fetch deal details and upsert
    try:
        from app.integrations.hubspot.client import HubSpotClient
        from app.integrations.hubspot.sync import _upsert_deal
        client = HubSpotClient(conn, db)
        raw_deal = client.get_deal_by_id(deal_id)
        _upsert_deal(db, client, str(conn.workspace_id), raw_deal, is_historical=False)
        return True
    except Exception as e:
        logger.warning("deal_creation_upsert_failed", deal_id=deal_id, error=str(e))
        return False


# ── Signature verification ─────────────────────────────────────

def _verify_signature_v3(
    body: bytes, signature: str, timestamp: str, url: str
) -> bool:
    """HubSpot v3 signature: HMAC-SHA256 of (client_secret + url + body + timestamp)."""
    try:
        source = settings.HUBSPOT_APP_CLIENT_SECRET + url + body.decode() + timestamp
        expected = hashlib.sha256(source.encode()).hexdigest()
        return hmac.compare_digest(expected, signature)
    except Exception:
        return False


def _verify_signature_v1(body: bytes, signature: str) -> bool:
    """HubSpot v1 signature: HMAC-SHA256 of (client_secret + body)."""
    try:
        source = (settings.HUBSPOT_APP_CLIENT_SECRET + body.decode()).encode()
        expected = hashlib.sha256(source).hexdigest()
        return hmac.compare_digest(expected, signature)
    except Exception:
        return False


# ── HubSpot API helpers ────────────────────────────────────────

def _redirect_uri() -> str:
    return settings.HUBSPOT_REDIRECT_URI
    


def _get_hub_info(access_token: str) -> tuple[str, str]:
    resp = httpx.get(
        f"{HUBSPOT_API_BASE}/oauth/v1/access-tokens/{access_token}",
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    return str(data.get("hub_id", "")), data.get("hub_domain", "")


def _register_webhooks(access_token: str, hub_id: str) -> str | None:
    """Register all webhook subscriptions. Returns comma-joined subscription IDs."""
    if not settings.HUBSPOT_APP_CLIENT_ID:
        return None

    subscriptions = [
        {"eventType": "deal.propertyChange", "propertyName": "dealstage", "active": True},
        {"eventType": "deal.creation", "active": True},
    ]
    ids = []
    for sub in subscriptions:
        try:
            resp = httpx.post(
                f"{HUBSPOT_API_BASE}/webhooks/v3/{settings.HUBSPOT_APP_CLIENT_ID}/subscriptions",
                json=sub,
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=15,
            )
            if resp.status_code in (200, 201):
                sub_id = resp.json().get("id")
                if sub_id:
                    ids.append(str(sub_id))
            else:
                logger.warning(
                    "webhook_sub_failed",
                    event_type=sub["eventType"],
                    status=resp.status_code,
                )
        except Exception as e:
            logger.warning("webhook_sub_error", event_type=sub["eventType"], error=str(e))

    return ",".join(ids) if ids else None
