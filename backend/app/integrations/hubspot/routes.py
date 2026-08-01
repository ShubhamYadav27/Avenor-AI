"""
HubSpot integration.
OAuth2 connection flow + webhook receiver for deal stage changes.
Outcome capture is automatic — zero behavior change for users.
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
    Company, HubSpotConnection, Outcome,
    OutcomeType, OutcomeSource, Signal,
)

logger = get_logger(__name__)
router = APIRouter(prefix="/integrations/hubspot", tags=["hubspot"])

HUBSPOT_TOKEN_URL = "https://api.hubapi.com/oauth/v1/token"
HUBSPOT_AUTH_URL = "https://app.hubspot.com/oauth/authorize"
HUBSPOT_API_BASE = "https://api.hubapi.com"

# Scopes we need
HUBSPOT_SCOPES = "crm.objects.deals.read crm.objects.companies.read oauth"

# Deal stages that trigger outcome logging
CLOSED_WON_STAGES = {"closedwon"}
CLOSED_LOST_STAGES = {"closedlost"}


# ── Encryption helpers (simple Fernet-style for MVP) ──────────

def _encrypt(value: str) -> str:
    """
    Encrypt a string for storage. MVP uses base64 + XOR with secret key.
    Replace with proper Fernet/KMS in production.
    """
    import base64
    key = settings.APP_SECRET_KEY[:32].encode().ljust(32)[:32]
    encoded = value.encode()
    encrypted = bytes(b ^ key[i % len(key)] for i, b in enumerate(encoded))
    return base64.b64encode(encrypted).decode()


def _decrypt(value: str) -> str:
    """Decrypt a previously encrypted string."""
    import base64
    key = settings.APP_SECRET_KEY[:32].encode().ljust(32)[:32]
    encrypted = base64.b64decode(value.encode())
    decrypted = bytes(b ^ key[i % len(key)] for i, b in enumerate(encrypted))
    return decrypted.decode()


# ── OAuth flow ─────────────────────────────────────────────────

@router.get("/connect")
def get_oauth_url(current_user: CurrentUser):
    """Return the HubSpot OAuth authorization URL."""
    if not settings.HUBSPOT_APP_CLIENT_ID:
        raise HTTPException(status_code=503, detail="HubSpot integration not configured")

    redirect_uri = f"{settings.ALLOWED_ORIGINS.split(',')[0]}/api/v1/integrations/hubspot/callback"

    auth_url = (
        f"{HUBSPOT_AUTH_URL}"
        f"?client_id={settings.HUBSPOT_APP_CLIENT_ID}"
        f"&redirect_uri={redirect_uri}"
        f"&scope={HUBSPOT_SCOPES.replace(' ', '%20')}"
        f"&state={str(current_user.workspace_id)}"
    )
    return {"auth_url": auth_url}


@router.get("/callback")
def oauth_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db),
):
    """
    HubSpot OAuth callback. Exchanges code for tokens and stores connection.
    The 'state' param carries the workspace_id.
    """
    if not settings.HUBSPOT_APP_CLIENT_ID:
        raise HTTPException(status_code=503, detail="HubSpot integration not configured")

    redirect_uri = f"{settings.ALLOWED_ORIGINS.split(',')[0]}/api/v1/integrations/hubspot/callback"

    # Exchange code for tokens
    try:
        resp = httpx.post(
            HUBSPOT_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "client_id": settings.HUBSPOT_APP_CLIENT_ID,
                "client_secret": settings.HUBSPOT_APP_CLIENT_SECRET,
                "redirect_uri": redirect_uri,
                "code": code,
            },
            timeout=15,
        )
        resp.raise_for_status()
        token_data = resp.json()
    except httpx.HTTPStatusError as e:
        logger.error("hubspot_token_exchange_failed", error=str(e))
        raise HTTPException(status_code=400, detail="Failed to exchange OAuth code")

    access_token = token_data["access_token"]
    refresh_token = token_data["refresh_token"]
    expires_in = token_data.get("expires_in", 1800)

    # Get portal info
    hub_id, hub_domain = _get_hub_info(access_token)

    # Store connection
    workspace_id = state
    conn = db.query(HubSpotConnection).filter_by(workspace_id=workspace_id).first()
    if conn is None:
        conn = HubSpotConnection(workspace_id=workspace_id)
        db.add(conn)

    conn.hub_id = hub_id
    conn.hub_domain = hub_domain
    conn.access_token_encrypted = _encrypt(access_token)
    conn.refresh_token_encrypted = _encrypt(refresh_token)
    conn.token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    conn.is_active = True

    db.commit()

    # Register webhook
    _register_webhook(access_token, hub_id, workspace_id)

    # Trigger historical sync in background
    from app.workers.tasks import celery_app
    celery_app.send_task(
        "app.integrations.hubspot.tasks.sync_historical_deals",
        args=[workspace_id],
    )

    logger.info("hubspot_connected", workspace_id=workspace_id, hub_id=hub_id)
    return {"status": "connected", "hub_id": hub_id, "hub_domain": hub_domain}


@router.get("/status")
def connection_status(current_user: CurrentUser, db: Session = Depends(get_db)):
    """Get HubSpot connection status for this workspace."""
    conn = db.query(HubSpotConnection).filter_by(workspace_id=current_user.workspace_id).first()
    if not conn:
        return {"connected": False}

    return {
        "connected": conn.is_active,
        "hub_id": conn.hub_id,
        "hub_domain": conn.hub_domain,
        "last_sync_at": conn.last_sync_at.isoformat() if conn.last_sync_at else None,
        "deals_synced": conn.deals_synced,
        "sync_error": conn.sync_error,
        "token_expires_at": conn.token_expires_at.isoformat(),
    }


@router.delete("/disconnect")
def disconnect(current_user: CurrentUser, db: Session = Depends(get_db)):
    """Disconnect HubSpot from this workspace."""
    current_user.require_admin()
    conn = db.query(HubSpotConnection).filter_by(workspace_id=current_user.workspace_id).first()
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
):
    """
    Receive HubSpot webhook events.
    Processes deal stage changes and logs outcomes automatically.
    """
    body = await request.body()

    # Verify HMAC signature
    if settings.HUBSPOT_WEBHOOK_SECRET and x_hubspot_signature:
        expected = hmac.new(
            settings.HUBSPOT_WEBHOOK_SECRET.encode(),
            body,
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(expected, x_hubspot_signature):
            raise HTTPException(status_code=401, detail="Invalid webhook signature")

    try:
        events = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    if not isinstance(events, list):
        events = [events]

    processed = 0
    for event in events:
        try:
            if _process_webhook_event(event, db):
                processed += 1
        except Exception as e:
            logger.error("webhook_event_processing_error", event=event, error=str(e))

    db.commit()
    logger.info("hubspot_webhook_processed", events_received=len(events), processed=processed)
    return {"processed": processed}


def _process_webhook_event(event: dict, db: Session) -> bool:
    """
    Process a single HubSpot webhook event.
    Returns True if an outcome was logged.
    """
    event_type = event.get("subscriptionType", "")

    # We care about deal property changes (specifically dealstage)
    if "deal.propertyChange" not in event_type:
        return False

    property_name = event.get("propertyName", "")
    if property_name != "dealstage":
        return False

    new_stage = (event.get("propertyValue") or "").lower()
    deal_id = str(event.get("objectId", ""))
    portal_id = str(event.get("portalId", ""))

    # Determine outcome type
    if new_stage in CLOSED_WON_STAGES:
        outcome_type = OutcomeType.CLOSED_WON
    elif new_stage in CLOSED_LOST_STAGES:
        outcome_type = OutcomeType.CLOSED_LOST
    else:
        return False  # Only process terminal stages

    # Find which workspace this portal belongs to
    conn = db.query(HubSpotConnection).filter_by(hub_id=portal_id).first()
    if not conn or not conn.is_active:
        logger.warning("hubspot_webhook_unknown_portal", portal_id=portal_id)
        return False

    workspace_id = conn.workspace_id

    # Fetch deal details from HubSpot to get associated company
    try:
        access_token = _get_valid_token(conn, db)
        deal_details = _fetch_deal(deal_id, access_token)
    except Exception as e:
        logger.error("hubspot_deal_fetch_failed", deal_id=deal_id, error=str(e))
        return False

    deal_value = _extract_deal_value(deal_details)
    associated_domain = _extract_company_domain(deal_details, access_token)

    if not associated_domain:
        logger.warning("hubspot_deal_no_domain", deal_id=deal_id)
        return False

    # Match to Avenor company
    company = (
        db.query(Company)
        .filter_by(workspace_id=workspace_id, domain=associated_domain)
        .first()
    )

    if not company:
        # Try fuzzy match
        company = _fuzzy_match_company(db, workspace_id, associated_domain, deal_details)

    if not company:
        logger.info(
            "hubspot_deal_company_not_in_avenor",
            domain=associated_domain,
            deal_id=deal_id,
        )
        return False

    # Check for duplicate
    existing = (
        db.query(Outcome)
        .filter_by(workspace_id=workspace_id, hubspot_deal_id=deal_id)
        .first()
    )
    if existing:
        return False

    # Snapshot current signals
    signals = db.query(Signal).filter_by(company_id=company.id).all()
    signals_snapshot = [
        {"type": s.signal_type, "strength": s.decayed_strength}
        for s in signals
    ]

    # Days from first signal
    days_from_first = None
    if signals:
        earliest = min(s.detected_at for s in signals)
        earliest_aware = earliest.replace(tzinfo=timezone.utc) if earliest.tzinfo is None else earliest
        days_from_first = (datetime.now(timezone.utc) - earliest_aware).days

    outcome = Outcome(
        workspace_id=workspace_id,
        company_id=company.id,
        outcome_type=outcome_type,
        outcome_source=OutcomeSource.HUBSPOT,
        predicted_composite_score=company.composite_score,
        predicted_buying_window=company.buying_window,
        active_signals_snapshot=signals_snapshot,
        days_from_first_signal=days_from_first,
        hubspot_deal_id=deal_id,
        deal_value_usd=deal_value,
        occurred_at=datetime.now(timezone.utc),
    )
    db.add(outcome)

    # Update stats
    conn.deals_synced += 1
    conn.last_sync_at = datetime.now(timezone.utc)

    logger.info(
        "hubspot_outcome_logged",
        company=company.name,
        outcome=outcome_type.value,
        deal_id=deal_id,
        workspace_id=str(workspace_id),
    )
    return True


# ── HubSpot API helpers ────────────────────────────────────────

def _get_hub_info(access_token: str) -> tuple[str, str]:
    resp = httpx.get(
        f"{HUBSPOT_API_BASE}/oauth/v1/access-tokens/{access_token}",
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    return str(data.get("hub_id", "")), data.get("hub_domain", "")


def _fetch_deal(deal_id: str, access_token: str) -> dict:
    resp = httpx.get(
        f"{HUBSPOT_API_BASE}/crm/v3/objects/deals/{deal_id}",
        params={
            "properties": "dealname,amount,dealstage,closedate",
            "associations": "companies",
        },
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def _extract_deal_value(deal: dict) -> float | None:
    try:
        return float(deal.get("properties", {}).get("amount", 0) or 0)
    except (ValueError, TypeError):
        return None


def _extract_company_domain(deal: dict, access_token: str) -> str | None:
    """Get associated company domain from deal."""
    try:
        associations = deal.get("associations", {}).get("companies", {}).get("results", [])
        if not associations:
            return None

        company_id = associations[0]["id"]
        resp = httpx.get(
            f"{HUBSPOT_API_BASE}/crm/v3/objects/companies/{company_id}",
            params={"properties": "domain,website"},
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=15,
        )
        resp.raise_for_status()
        props = resp.json().get("properties", {})
        return props.get("domain") or props.get("website")
    except Exception:
        return None


def _fuzzy_match_company(
    db: Session, workspace_id, domain: str, deal_details: dict
) -> Company | None:
    """Try to match by company name similarity if domain fails."""
    from rapidfuzz import fuzz
    company_name = deal_details.get("properties", {}).get("dealname", "")
    if not company_name:
        return None

    candidates = db.query(Company).filter_by(workspace_id=workspace_id).all()
    for c in candidates:
        if fuzz.ratio(c.name.lower(), company_name.lower()) > 85:
            return c
    return None


def _get_valid_token(conn: HubSpotConnection, db: Session) -> str:
    """Return valid access token, refreshing if needed."""
    now = datetime.now(timezone.utc)
    expires = conn.token_expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)

    if expires - now < timedelta(minutes=5):
        # Refresh
        try:
            resp = httpx.post(
                HUBSPOT_TOKEN_URL,
                data={
                    "grant_type": "refresh_token",
                    "client_id": settings.HUBSPOT_APP_CLIENT_ID,
                    "client_secret": settings.HUBSPOT_APP_CLIENT_SECRET,
                    "refresh_token": _decrypt(conn.refresh_token_encrypted),
                },
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            conn.access_token_encrypted = _encrypt(data["access_token"])
            conn.refresh_token_encrypted = _encrypt(data["refresh_token"])
            conn.token_expires_at = now + timedelta(seconds=data.get("expires_in", 1800))
            db.commit()
            return data["access_token"]
        except Exception as e:
            logger.error("hubspot_token_refresh_failed", error=str(e))
            raise

    return _decrypt(conn.access_token_encrypted)


def _register_webhook(access_token: str, hub_id: str, workspace_id: str) -> None:
    """Register HubSpot webhook subscription for deal stage changes."""
    if not settings.HUBSPOT_APP_CLIENT_ID:
        return

    webhook_url = f"{settings.ALLOWED_ORIGINS.split(',')[0]}/api/v1/integrations/hubspot/webhook"

    try:
        resp = httpx.post(
            f"{HUBSPOT_API_BASE}/webhooks/v3/{settings.HUBSPOT_APP_CLIENT_ID}/subscriptions",
            json={
                "eventType": "deal.propertyChange",
                "propertyName": "dealstage",
                "active": True,
            },
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=15,
        )
        if resp.status_code in (200, 201):
            logger.info("hubspot_webhook_registered", hub_id=hub_id)
        else:
            logger.warning(
                "hubspot_webhook_registration_failed",
                status=resp.status_code,
                body=resp.text[:200],
            )
    except Exception as e:
        logger.warning("hubspot_webhook_registration_error", error=str(e))
