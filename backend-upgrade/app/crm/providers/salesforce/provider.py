"""app/crm/providers/salesforce/provider.py"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any, Generator

from app.core.config import settings
from app.core.exceptions import ExternalServiceError
from app.core.logging import get_logger
from app.crm.base.interfaces import ICRMProvider
from app.crm.base.models import (
    CRMAccount,
    CRMConnectionState,
    CRMContact,
    CRMEvent,
    CRMLead,
    CRMOpportunity,
    CRMUser,
    OAuthCallbackResult,
    OAuthURLResult,
    ProviderCapabilities,
    SyncResult,
)
from app.crm.providers.salesforce.client import SalesforceAPIClient
from app.crm.providers.salesforce.oauth import SalesforceOAuth, _pop_verifier
from app.crm.providers.salesforce.webhook import SalesforceWebhookHandler
from app.utils.encryption import encrypt_token

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

logger = get_logger(__name__)


class SalesforceProvider(ICRMProvider):
    def __init__(self, connection=None, db: "Session | None" = None):
        self.connection = connection
        self.db = db
        self._oauth = SalesforceOAuth()
        self._webhook = SalesforceWebhookHandler()
        self._client: SalesforceAPIClient | None = None

    @property
    def provider_name(self) -> str:
        return "salesforce"

    @property
    def display_name(self) -> str:
        return "Salesforce"

    def _get_client(self) -> SalesforceAPIClient:
        if self._client is None:
            if not self.connection or not self.db:
                raise ExternalServiceError("Salesforce", "No active connection")
            self._client = SalesforceAPIClient(self.connection, self.db)
        return self._client

    def get_capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_accounts=True,
            supports_contacts=True,
            supports_leads=True,
            supports_opportunities=True,
            supports_users=True,
            supports_incremental_sync=True,
            supports_historical_sync=True,
            supports_bulk_api=True,
            supports_webhooks=True,
            supports_webhook_signature_verification=False,
            webhook_event_types=["created", "updated", "deleted"],
            supports_token_refresh=True,
            supports_token_revocation=False,
        )

    def get_oauth_url(self, workspace_id: str) -> OAuthURLResult:
        if not settings.has_salesforce:
            raise ExternalServiceError("Salesforce", "Salesforce credentials not configured")
        return self._oauth.build_auth_url(workspace_id)

    def handle_oauth_callback(
        self,
        code: str,
        state: str,
        workspace_id: str,
        db: "Session",
    ) -> OAuthCallbackResult:
        from app.models import CRMConnectionDB, Workspace
        import uuid

        # Retrieve and consume the PKCE verifier stored during oauth/start.
        # The state parameter is always workspace_id (set in build_auth_url).
        code_verifier = _pop_verifier(state)
        if code_verifier is None:
            logger.warning(
                "salesforce_pkce_verifier_missing",
                state=state,
                workspace_id=workspace_id,
            )

        result = self._oauth.exchange_to_callback_result(code, code_verifier=code_verifier)
        ws_uuid = uuid.UUID(workspace_id)
        workspace = db.get(Workspace, ws_uuid)
        if not workspace:
            raise ExternalServiceError("Salesforce", f"Workspace {workspace_id} not found")

        conn = (
            db.query(CRMConnectionDB)
            .filter_by(workspace_id=ws_uuid, provider="salesforce")
            .first()
        )
        if conn is None:
            conn = CRMConnectionDB(workspace_id=ws_uuid, provider="salesforce")
            db.add(conn)

        conn.external_account_id = result.external_account_id
        conn.external_account_name = result.external_account_name
        conn.access_token_encrypted = encrypt_token(result.access_token)
        conn.refresh_token_encrypted = encrypt_token(result.refresh_token)
        conn.token_expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=result.token_expires_in,
        )
        conn.scopes = result.scopes
        conn.provider_metadata = result.provider_metadata
        conn.is_active = True
        conn.sync_error = None
        workspace.crm_provider = "salesforce"
        db.commit()
        self.connection = conn
        self.db = db

        logger.info(
            "salesforce_oauth_callback_complete",
            workspace_id=workspace_id,
            org_id=result.external_account_id,
        )

        # Auto-trigger a full historical sync immediately after OAuth.
        # This imports ALL Accounts, Contacts, Leads, Opportunities, and Users
        # from the connected Salesforce org without requiring a manual Force Sync.
        try:
            from app.workers.tasks import crm_historical_sync
            crm_historical_sync.delay(str(ws_uuid), "salesforce")
            logger.info(
                "salesforce_historical_sync_dispatched",
                workspace_id=workspace_id,
                org_id=result.external_account_id,
            )
        except Exception as exc:
            # If Celery is not available (e.g. dev without Redis), log and continue.
            # The user can manually trigger Force Sync from the dashboard.
            logger.warning(
                "salesforce_historical_sync_dispatch_failed",
                workspace_id=workspace_id,
                error=str(exc),
            )

        return result

    def refresh_token(self) -> None:
        self._get_client()._refresh()

    def disconnect(self, workspace_id: str, db: "Session") -> bool:
        from app.models import CRMConnectionDB, Workspace
        import uuid

        ws_uuid = uuid.UUID(workspace_id)
        conn = (
            db.query(CRMConnectionDB)
            .filter_by(workspace_id=ws_uuid, provider="salesforce")
            .first()
        )
        if conn:
            conn.is_active = False
            conn.sync_error = "Disconnected by user"
        workspace = db.get(Workspace, ws_uuid)
        if workspace and workspace.crm_provider == "salesforce":
            workspace.crm_provider = None
        db.commit()
        return True

    def get_status(self) -> CRMConnectionState:
        if not self.connection:
            return CRMConnectionState(provider="salesforce", is_active=False)
        return CRMConnectionState(
            provider="salesforce",
            is_active=self.connection.is_active,
            external_account_id=self.connection.external_account_id,
            external_account_name=self.connection.external_account_name,
            last_sync_at=self.connection.last_sync_at,
            sync_error=self.connection.sync_error,
            token_expires_at=self.connection.token_expires_at,
        )

    def sync_accounts(self, modified_after: datetime | None = None) -> Generator[CRMAccount, None, None]:
        yield from self._get_client().get_accounts(modified_after)

    def sync_contacts(self, modified_after: datetime | None = None) -> Generator[CRMContact, None, None]:
        yield from self._get_client().get_contacts(modified_after)

    def sync_leads(self, modified_after: datetime | None = None) -> Generator[CRMLead, None, None]:
        yield from self._get_client().get_leads(modified_after)

    def sync_opportunities(self, modified_after: datetime | None = None) -> Generator[CRMOpportunity, None, None]:
        yield from self._get_client().get_opportunities(modified_after)

    def sync_users(self) -> Generator[CRMUser, None, None]:
        yield from self._get_client().get_users()

    def verify_webhook_signature(self, payload: bytes, headers: dict[str, str]) -> bool:
        return self._webhook.verify_signature(payload, headers)

    def handle_webhook(self, payload: bytes, headers: dict[str, str]) -> list[CRMEvent]:
        ws_id = str(self.connection.workspace_id) if self.connection else ""
        return self._webhook.parse_events(payload, ws_id)

    def historical_sync(self, days_back: int = 180) -> SyncResult:
        if not self.connection or not self.db:
            raise ExternalServiceError("Salesforce", "No connection")
        from app.crm.engine import CRMSyncEngine

        return CRMSyncEngine(self.db, self).run_historical_sync(days_back=days_back)

    def incremental_sync(self) -> SyncResult:
        if not self.connection or not self.db:
            raise ExternalServiceError("Salesforce", "No connection")
        from app.crm.engine import CRMSyncEngine

        return CRMSyncEngine(self.db, self).run_incremental_sync()

    def health_check(self) -> dict[str, Any]:
        if not self.connection:
            return {"healthy": False, "provider": "salesforce", "error": "No active connection"}
        try:
            limits = self._get_client().get_limits()
            return {
                "healthy": True,
                "provider": "salesforce",
                "last_sync": self.connection.last_sync_at.isoformat()
                if self.connection.last_sync_at
                else None,
                "api_version": "v59.0",
                "limits": list(limits.keys()),
            }
        except Exception as exc:
            return {"healthy": False, "provider": "salesforce", "error": str(exc)}
