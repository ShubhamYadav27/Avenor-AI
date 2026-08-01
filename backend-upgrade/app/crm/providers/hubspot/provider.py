"""app/crm/providers/hubspot/provider.py
HubSpotProvider — the main ICRMProvider implementation for HubSpot.
Wraps the existing HubSpot API client logic and maps all objects to canonical models.
"""
from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Generator

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.exceptions import ExternalServiceError, RateLimitError
from app.core.logging import get_logger
from app.crm.base.interfaces import ICRMProvider
from app.crm.base.models import (
    CRMAccount, CRMContact, CRMEvent, CRMLead, CRMOpportunity, CRMUser,
    CRMConnectionState, OAuthURLResult, OAuthCallbackResult,
    ProviderCapabilities, SyncResult, SyncStats, SyncStatus,
)
from app.crm.providers.hubspot.oauth import HubSpotOAuth
from app.crm.providers.hubspot.webhook import HubSpotWebhookHandler
from app.utils.encryption import decrypt_token, encrypt_token, is_fernet_token, migrate_legacy_token

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

logger = get_logger(__name__)

HUBSPOT_API_BASE = "https://api.hubapi.com"
HUBSPOT_TOKEN_URL = "https://api.hubapi.com/oauth/v1/token"
_PAGE_SIZE = 100
_DEFAULT_TIMEOUT = 20.0
CLOSED_WON_STAGES = {"closedwon", "closed_won"}
CLOSED_LOST_STAGES = {"closedlost", "closed_lost"}


class _HubSpotAPIClient:
    """Internal HTTP client for HubSpot API. Works with CRMConnectionDB."""

    def __init__(self, connection, db: "Session"):
        self.conn = connection
        self.db = db
        self.request_count = 0

    def _get_token(self) -> str:
        if not is_fernet_token(self.conn.access_token_encrypted):
            self.conn.access_token_encrypted = migrate_legacy_token(
                self.conn.access_token_encrypted, settings.APP_SECRET_KEY
            )
            self.conn.refresh_token_encrypted = migrate_legacy_token(
                self.conn.refresh_token_encrypted, settings.APP_SECRET_KEY
            )
            self.db.commit()

        expires = self.conn.token_expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if expires - datetime.now(timezone.utc) < timedelta(minutes=5):
            self._refresh()

        return decrypt_token(self.conn.access_token_encrypted)

    def _refresh(self) -> None:
        logger.info("hubspot_crm_provider_refreshing_token",
                    workspace_id=str(self.conn.workspace_id))
        try:
            resp = httpx.post(
                HUBSPOT_TOKEN_URL,
                data={
                    "grant_type": "refresh_token",
                    "client_id": settings.HUBSPOT_APP_CLIENT_ID,
                    "client_secret": settings.HUBSPOT_APP_CLIENT_SECRET,
                    "refresh_token": decrypt_token(self.conn.refresh_token_encrypted),
                },
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            self.conn.access_token_encrypted = encrypt_token(data["access_token"])
            self.conn.refresh_token_encrypted = encrypt_token(data["refresh_token"])
            self.conn.token_expires_at = datetime.now(timezone.utc) + timedelta(
                seconds=data.get("expires_in", 1800)
            )
            self.db.commit()
        except Exception as exc:
            if hasattr(exc, "response") and exc.response.status_code in (401, 403):
                self.conn.is_active = False
                self.conn.sync_error = str(exc)
                self.db.commit()
            raise ExternalServiceError("HubSpot", f"Token refresh failed: {exc}") from exc

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._get_token()}",
            "Content-Type": "application/json",
        }

    @retry(
        retry=retry_if_exception_type((httpx.HTTPStatusError, RateLimitError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=30),
    )
    def get(self, path: str, params: dict | None = None) -> dict:
        self.request_count += 1
        resp = httpx.get(
            f"{HUBSPOT_API_BASE}{path}",
            params=params or {},
            headers=self._headers(),
            timeout=_DEFAULT_TIMEOUT,
        )
        if resp.status_code == 429:
            retry_after = int(resp.headers.get("Retry-After", 10))
            raise RateLimitError("HubSpot", retry_after_seconds=retry_after)
        resp.raise_for_status()
        return resp.json()

    @retry(
        retry=retry_if_exception_type((httpx.HTTPStatusError, RateLimitError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=30),
    )
    def post(self, path: str, json_body: dict) -> dict:
        self.request_count += 1
        resp = httpx.post(
            f"{HUBSPOT_API_BASE}{path}",
            json=json_body,
            headers=self._headers(),
            timeout=_DEFAULT_TIMEOUT,
        )
        if resp.status_code == 429:
            retry_after = int(resp.headers.get("Retry-After", 10))
            raise RateLimitError("HubSpot", retry_after_seconds=retry_after)
        resp.raise_for_status()
        return resp.json()

    def paginate(self, path: str, params: dict | None = None) -> Generator[dict, None, None]:
        base = {**(params or {}), "limit": _PAGE_SIZE}
        after = None
        while True:
            if after:
                base["after"] = after
            data = self.get(path, base)
            for rec in data.get("results", []):
                yield rec
            after = data.get("paging", {}).get("next", {}).get("after")
            if not after:
                break

    def search(self, object_type: str, body: dict) -> Generator[dict, None, None]:
        after = None
        while True:
            if after:
                body["after"] = after
            data = self.post(f"/crm/v3/objects/{object_type}/search", body)
            for rec in data.get("results", []):
                yield rec
            after = data.get("paging", {}).get("next", {}).get("after")
            if not after:
                break


def _parse_dt(val: str | None) -> datetime | None:
    if not val:
        return None
    try:
        # HubSpot returns ms timestamps as strings
        return datetime.fromtimestamp(int(val) / 1000, tz=timezone.utc)
    except (ValueError, TypeError):
        pass
    try:
        return datetime.fromisoformat(val.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


class HubSpotProvider(ICRMProvider):
    """ICRMProvider implementation for HubSpot CRM."""

    def __init__(self, connection=None, db: "Session | None" = None):
        self.connection = connection
        self.db = db
        self._client: _HubSpotAPIClient | None = None
        self._oauth = HubSpotOAuth()
        self._webhook = HubSpotWebhookHandler()

    @property
    def provider_name(self) -> str:
        return "hubspot"

    @property
    def display_name(self) -> str:
        return "HubSpot"

    def _get_client(self) -> _HubSpotAPIClient:
        if self._client is None:
            if self.connection is None or self.db is None:
                raise ExternalServiceError("HubSpot", "No active connection")
            self._client = _HubSpotAPIClient(self.connection, self.db)
        return self._client

    # ── Capabilities ──────────────────────────────────────────────────────────

    def get_capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_accounts=True,
            supports_contacts=True,
            supports_leads=False,       # HubSpot has no native Lead object
            supports_opportunities=True,
            supports_users=True,
            supports_incremental_sync=True,
            supports_historical_sync=True,
            supports_webhooks=True,
            supports_webhook_signature_verification=True,
            webhook_event_types=["deal.creation", "deal.propertyChange", "contact.creation"],
            supports_token_refresh=True,
            supports_token_revocation=False,
        )

    # ── OAuth ─────────────────────────────────────────────────────────────────

    def get_oauth_url(self, workspace_id: str) -> OAuthURLResult:
        if not settings.has_hubspot:
            raise ExternalServiceError("HubSpot", "HubSpot credentials not configured")
        return self._oauth.build_auth_url(workspace_id)

    def handle_oauth_callback(
        self, code: str, state: str, workspace_id: str, db: "Session"
    ) -> OAuthCallbackResult:
        from app.models import CRMConnectionDB, Workspace
        import uuid

        result = self._oauth.exchange_to_callback_result(code)

        ws_uuid = uuid.UUID(workspace_id)
        workspace = db.get(Workspace, ws_uuid)
        if not workspace:
            raise ExternalServiceError("HubSpot", f"Workspace {workspace_id} not found")

        conn = (
            db.query(CRMConnectionDB)
            .filter_by(workspace_id=ws_uuid, provider="hubspot")
            .first()
        )
        if conn is None:
            conn = CRMConnectionDB(workspace_id=ws_uuid, provider="hubspot")
            db.add(conn)

        conn.external_account_id = result.external_account_id
        conn.external_account_name = result.external_account_name
        conn.access_token_encrypted = encrypt_token(result.access_token)
        conn.refresh_token_encrypted = encrypt_token(result.refresh_token)
        conn.token_expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=result.token_expires_in
        )
        conn.scopes = result.scopes
        conn.provider_metadata = result.provider_metadata
        conn.is_active = True
        conn.sync_error = None
        workspace.crm_provider = "hubspot"
        db.commit()

        logger.info(
            "hubspot_oauth_callback_complete",
            workspace_id=workspace_id,
            hub_id=result.external_account_id,
        )
        return result

    # ── Token ─────────────────────────────────────────────────────────────────

    def refresh_token(self) -> None:
        self._get_client()._refresh()

    # ── Disconnect ────────────────────────────────────────────────────────────

    def disconnect(self, workspace_id: str, db: "Session") -> bool:
        from app.models import CRMConnectionDB, Workspace
        import uuid
        ws_uuid = uuid.UUID(workspace_id)
        conn = db.query(CRMConnectionDB).filter_by(
            workspace_id=ws_uuid, provider="hubspot"
        ).first()
        if conn:
            conn.is_active = False
            conn.sync_error = "Disconnected by user"
        workspace = db.get(Workspace, ws_uuid)
        if workspace and workspace.crm_provider == "hubspot":
            workspace.crm_provider = None
        db.commit()
        return True

    # ── Status ────────────────────────────────────────────────────────────────

    def get_status(self) -> CRMConnectionState:
        if not self.connection:
            return CRMConnectionState(provider="hubspot", is_active=False)
        return CRMConnectionState(
            provider="hubspot",
            is_active=self.connection.is_active,
            external_account_id=self.connection.external_account_id,
            external_account_name=self.connection.external_account_name,
            last_sync_at=self.connection.last_sync_at,
            sync_error=self.connection.sync_error,
            token_expires_at=self.connection.token_expires_at,
        )

    # ── Object sync ───────────────────────────────────────────────────────────

    def sync_accounts(self, modified_after: datetime | None = None) -> Generator[CRMAccount, None, None]:
        client = self._get_client()
        props = ["name", "domain", "website", "industry", "numberofemployees",
                 "city", "state", "country", "annualrevenue", "phone",
                 "hs_lastmodifieddate", "createdate"]
        if modified_after:
            ts_ms = int(modified_after.timestamp() * 1000)
            body = {
                "filterGroups": [{"filters": [{
                    "propertyName": "hs_lastmodifieddate",
                    "operator": "GTE",
                    "value": str(ts_ms),
                }]}],
                "properties": props,
                "limit": _PAGE_SIZE,
            }
            records = client.search("companies", body)
        else:
            records = client.paginate(
                "/crm/v3/objects/companies",
                {"properties": ",".join(props)},
            )
        for rec in records:
            yield self._map_account(rec)

    def _map_account(self, rec: dict) -> CRMAccount:
        p = rec.get("properties", {})
        return CRMAccount(
            external_id=str(rec["id"]),
            provider="hubspot",
            name=p.get("name") or "",
            domain=p.get("domain"),
            website=p.get("website"),
            industry=p.get("industry"),
            employee_count=int(p["numberofemployees"]) if p.get("numberofemployees") else None,
            location_city=p.get("city"),
            location_state=p.get("state"),
            location_country=p.get("country"),
            annual_revenue=float(p["annualrevenue"]) if p.get("annualrevenue") else None,
            phone=p.get("phone"),
            modified_at=_parse_dt(p.get("hs_lastmodifieddate")),
            created_at=_parse_dt(p.get("createdate")),
            raw_data=rec,
        )

    def sync_contacts(self, modified_after: datetime | None = None) -> Generator[CRMContact, None, None]:
        client = self._get_client()
        props = ["firstname", "lastname", "email", "jobtitle", "phone",
                 "associatedcompanyid", "hs_lastmodifieddate", "createdate",
                 "linkedinbio", "hubspot_owner_id"]
        if modified_after:
            ts_ms = int(modified_after.timestamp() * 1000)
            body = {
                "filterGroups": [{"filters": [{
                    "propertyName": "lastmodifieddate",
                    "operator": "GTE",
                    "value": str(ts_ms),
                }]}],
                "properties": props,
                "limit": _PAGE_SIZE,
            }
            records = client.search("contacts", body)
        else:
            records = client.paginate(
                "/crm/v3/objects/contacts",
                {"properties": ",".join(props)},
            )
        for rec in records:
            yield self._map_contact(rec)

    def _map_contact(self, rec: dict) -> CRMContact:
        p = rec.get("properties", {})
        fn = p.get("firstname") or ""
        ln = p.get("lastname") or ""
        return CRMContact(
            external_id=str(rec["id"]),
            provider="hubspot",
            first_name=fn or None,
            last_name=ln or None,
            full_name=f"{fn} {ln}".strip() or None,
            email=p.get("email"),
            phone=p.get("phone"),
            title=p.get("jobtitle"),
            account_external_id=p.get("associatedcompanyid"),
            owner_external_id=p.get("hubspot_owner_id"),
            modified_at=_parse_dt(p.get("hs_lastmodifieddate")),
            created_at=_parse_dt(p.get("createdate")),
            raw_data=rec,
        )

    def sync_leads(self, modified_after: datetime | None = None) -> Generator[CRMLead, None, None]:
        """HubSpot has no native Lead object — always returns empty."""
        return
        yield  # make it a generator

    def sync_opportunities(self, modified_after: datetime | None = None) -> Generator[CRMOpportunity, None, None]:
        client = self._get_client()
        props = ["dealname", "amount", "dealstage", "pipeline",
                 "closedate", "createdate", "hs_lastmodifieddate",
                 "hubspot_owner_id", "hs_deal_stage_probability"]
        if modified_after:
            ts_ms = int(modified_after.timestamp() * 1000)
            body = {
                "filterGroups": [{"filters": [{
                    "propertyName": "hs_lastmodifieddate",
                    "operator": "GTE",
                    "value": str(ts_ms),
                }]}],
                "properties": props,
                "associations": ["companies", "contacts"],
                "limit": _PAGE_SIZE,
            }
            records = client.search("deals", body)
        else:
            records = client.paginate(
                "/crm/v3/objects/deals",
                {"properties": ",".join(props), "associations": "companies,contacts"},
            )
        for rec in records:
            yield self._map_opportunity(rec)

    def _map_opportunity(self, rec: dict) -> CRMOpportunity:
        p = rec.get("properties", {})
        stage = p.get("dealstage", "")
        is_won = stage.lower() in CLOSED_WON_STAGES
        is_lost = stage.lower() in CLOSED_LOST_STAGES

        assoc = rec.get("associations", {})
        companies = assoc.get("companies", {}).get("results", [])
        contacts = assoc.get("contacts", {}).get("results", [])

        prob_str = p.get("hs_deal_stage_probability")
        probability = float(prob_str) if prob_str else None

        return CRMOpportunity(
            external_id=str(rec["id"]),
            provider="hubspot",
            name=p.get("dealname"),
            stage=stage,
            pipeline=p.get("pipeline"),
            amount_usd=float(p["amount"]) if p.get("amount") else None,
            probability=probability,
            close_date=_parse_dt(p.get("closedate")),
            is_closed_won=is_won,
            is_closed_lost=is_lost,
            account_external_id=str(companies[0]["id"]) if companies else None,
            contact_external_ids=[str(c["id"]) for c in contacts],
            owner_external_id=p.get("hubspot_owner_id"),
            created_at=_parse_dt(p.get("createdate")),
            modified_at=_parse_dt(p.get("hs_lastmodifieddate")),
            raw_data=rec,
        )

    def sync_users(self) -> Generator[CRMUser, None, None]:
        client = self._get_client()
        data = client.get("/crm/v3/owners", {"limit": 100})
        for owner in data.get("results", []):
            yield CRMUser(
                external_id=str(owner["id"]),
                provider="hubspot",
                email=owner.get("email"),
                first_name=owner.get("firstName"),
                last_name=owner.get("lastName"),
                full_name=f"{owner.get('firstName', '')} {owner.get('lastName', '')}".strip() or None,
                is_active=not owner.get("archived", False),
                raw_data=owner,
            )

    # ── Webhooks ──────────────────────────────────────────────────────────────

    def verify_webhook_signature(self, payload: bytes, headers: dict[str, str]) -> bool:
        return self._webhook.verify_signature(payload, headers)

    def handle_webhook(self, payload: bytes, headers: dict[str, str]) -> list[CRMEvent]:
        workspace_id = str(self.connection.workspace_id) if self.connection else ""
        return self._webhook.parse_events(payload, workspace_id)

    # ── Sync orchestration ────────────────────────────────────────────────────

    def historical_sync(self, days_back: int = 180) -> SyncResult:
        from app.models import CRMSyncStateV2
        started = datetime.now(timezone.utc)
        stats_list: list[SyncStats] = []
        workspace_id = str(self.connection.workspace_id)

        try:
            for obj_type, sync_fn in [
                ("account", self.sync_accounts),
                ("contact", self.sync_contacts),
                ("opportunity", self.sync_opportunities),
                ("user", self.sync_users),
            ]:
                t0 = time.monotonic()
                count = 0
                for _ in sync_fn(None):
                    count += 1
                stats_list.append(SyncStats(
                    object_type=obj_type,
                    created=count,
                    duration_seconds=time.monotonic() - t0,
                ))
                # Update sync state
                state = (
                    self.db.query(CRMSyncStateV2)
                    .filter_by(workspace_id=self.connection.workspace_id,
                               provider="hubspot", object_type=obj_type)
                    .first()
                )
                if state is None:
                    state = CRMSyncStateV2(
                        workspace_id=self.connection.workspace_id,
                        provider="hubspot",
                        object_type=obj_type,
                    )
                    self.db.add(state)
                state.historical_import_completed = True
                state.historical_import_completed_at = datetime.now(timezone.utc)
                state.historical_records_imported = count
                state.last_synced_at = datetime.now(timezone.utc)
                self.db.commit()

            return SyncResult(
                provider="hubspot",
                workspace_id=workspace_id,
                sync_type="historical",
                status=SyncStatus.COMPLETED,
                started_at=started,
                completed_at=datetime.now(timezone.utc),
                stats=stats_list,
            )
        except Exception as exc:
            logger.error("hubspot_historical_sync_failed", error=str(exc), workspace_id=workspace_id)
            return SyncResult(
                provider="hubspot",
                workspace_id=workspace_id,
                sync_type="historical",
                status=SyncStatus.FAILED,
                started_at=started,
                completed_at=datetime.now(timezone.utc),
                error=str(exc),
            )

    def incremental_sync(self) -> SyncResult:
        from app.models import CRMSyncStateV2
        started = datetime.now(timezone.utc)
        workspace_id = str(self.connection.workspace_id)
        stats_list: list[SyncStats] = []

        try:
            for obj_type, sync_fn in [
                ("account", self.sync_accounts),
                ("contact", self.sync_contacts),
                ("opportunity", self.sync_opportunities),
            ]:
                state = (
                    self.db.query(CRMSyncStateV2)
                    .filter_by(workspace_id=self.connection.workspace_id,
                               provider="hubspot", object_type=obj_type)
                    .first()
                )
                cursor = state.last_synced_at if state else None
                t0 = time.monotonic()
                count = 0
                for _ in sync_fn(cursor):
                    count += 1
                if state:
                    state.last_synced_at = started
                    state.last_run_created = count
                    state.last_run_status = "completed"
                    self.db.commit()
                stats_list.append(SyncStats(
                    object_type=obj_type,
                    updated=count,
                    duration_seconds=time.monotonic() - t0,
                ))

            self.connection.last_sync_at = datetime.now(timezone.utc)
            self.db.commit()

            return SyncResult(
                provider="hubspot",
                workspace_id=workspace_id,
                sync_type="incremental",
                status=SyncStatus.COMPLETED,
                started_at=started,
                completed_at=datetime.now(timezone.utc),
                stats=stats_list,
            )
        except Exception as exc:
            logger.error("hubspot_incremental_sync_failed", error=str(exc), workspace_id=workspace_id)
            return SyncResult(
                provider="hubspot",
                workspace_id=workspace_id,
                sync_type="incremental",
                status=SyncStatus.FAILED,
                started_at=started,
                completed_at=datetime.now(timezone.utc),
                error=str(exc),
            )
