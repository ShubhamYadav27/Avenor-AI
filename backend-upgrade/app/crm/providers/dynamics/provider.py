"""app/crm/providers/dynamics/provider.py"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any, Generator

from app.core.config import settings
from app.core.exceptions import ExternalServiceError
from app.core.logging import get_logger
from app.crm.base.interfaces import ICRMProvider
from app.crm.base.models import (
    CRMAccount, CRMContact, CRMConnectionState, CRMEvent, CRMLead,
    CRMOpportunity, CRMUser, OAuthCallbackResult, OAuthURLResult,
    ProviderCapabilities, SyncResult,
)
from app.crm.providers.dynamics.client import DynamicsAPIClient
from app.crm.providers.dynamics.oauth import DynamicsOAuth
from app.crm.providers.dynamics.webhook import DynamicsWebhookHandler
from app.utils.encryption import encrypt_token

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

logger = get_logger(__name__)


class DynamicsProvider(ICRMProvider):
    def __init__(self, connection=None, db: "Session | None" = None):
        self.connection = connection
        self.db = db
        self._oauth = DynamicsOAuth()
        self._webhook = DynamicsWebhookHandler()
        self._client: DynamicsAPIClient | None = None

    @property
    def provider_name(self) -> str:
        return "dynamics"

    @property
    def display_name(self) -> str:
        return "Microsoft Dynamics 365"

    def _get_client(self) -> DynamicsAPIClient:
        if self._client is None:
            if not self.connection or not self.db:
                raise ExternalServiceError("Dynamics", "No active connection")
            self._client = DynamicsAPIClient(self.connection, self.db)
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
            supports_webhooks=True,
            supports_webhook_signature_verification=True,
            webhook_event_types=["Create", "Update", "Delete"],
            supports_token_refresh=True,
            supports_token_revocation=False,
        )

    def get_oauth_url(self, workspace_id: str) -> OAuthURLResult:
        if not settings.has_dynamics:
            raise ExternalServiceError("Dynamics", "Dynamics credentials not configured")
        return self._oauth.build_auth_url(workspace_id)

    def handle_oauth_callback(self, code: str, state: str, workspace_id: str, db: "Session") -> OAuthCallbackResult:
        from app.models import CRMConnectionDB, Workspace
        import uuid
        result = self._oauth.exchange_to_callback_result(code)
        ws_uuid = uuid.UUID(workspace_id)
        workspace = db.get(Workspace, ws_uuid)
        if not workspace:
            raise ExternalServiceError("Dynamics", f"Workspace {workspace_id} not found")
        conn = db.query(CRMConnectionDB).filter_by(workspace_id=ws_uuid, provider="dynamics").first()
        if conn is None:
            conn = CRMConnectionDB(workspace_id=ws_uuid, provider="dynamics")
            db.add(conn)
        conn.external_account_id = result.external_account_id
        conn.external_account_name = result.external_account_name
        conn.access_token_encrypted = encrypt_token(result.access_token)
        conn.refresh_token_encrypted = encrypt_token(result.refresh_token)
        conn.token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=result.token_expires_in)
        conn.scopes = result.scopes
        conn.provider_metadata = result.provider_metadata
        conn.is_active = True
        conn.sync_error = None
        workspace.crm_provider = "dynamics"
        db.commit()
        self.connection = conn
        self.db = db
        logger.info("dynamics_oauth_callback_complete", workspace_id=workspace_id)
        return result

    def refresh_token(self) -> None:
        self._get_client()._refresh()

    def disconnect(self, workspace_id: str, db: "Session") -> bool:
        from app.models import CRMConnectionDB, Workspace
        import uuid
        ws_uuid = uuid.UUID(workspace_id)
        conn = db.query(CRMConnectionDB).filter_by(workspace_id=ws_uuid, provider="dynamics").first()
        if conn:
            conn.is_active = False
            conn.sync_error = "Disconnected by user"
        workspace = db.get(Workspace, ws_uuid)
        if workspace and workspace.crm_provider == "dynamics":
            workspace.crm_provider = None
        db.commit()
        return True

    def get_status(self) -> CRMConnectionState:
        if not self.connection:
            return CRMConnectionState(provider="dynamics", is_active=False)
        return CRMConnectionState(
            provider="dynamics", is_active=self.connection.is_active,
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
            raise ExternalServiceError("Dynamics", "No active connection")
        from app.crm.engine import CRMSyncEngine

        return CRMSyncEngine(self.db, self).run_historical_sync(days_back=days_back)

    def incremental_sync(self) -> SyncResult:
        if not self.connection or not self.db:
            raise ExternalServiceError("Dynamics", "No active connection")
        from app.crm.engine import CRMSyncEngine

        return CRMSyncEngine(self.db, self).run_incremental_sync()

    def health_check(self) -> dict[str, Any]:
        if not self.connection:
            return {"healthy": False, "provider": "dynamics", "error": "No active connection"}
        try:
            # Lightweight health check by getting active status
            status = self.get_status()
            return {
                "healthy": status.is_active,
                "provider": "dynamics",
                "last_sync": status.last_sync_at.isoformat() if status.last_sync_at else None,
                "api_version": "v9.2",
            }
        except Exception as exc:
            return {"healthy": False, "provider": "dynamics", "error": str(exc)}
