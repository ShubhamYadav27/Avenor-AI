"""
app/crm/base/interfaces.py

The ICRMProvider interface.

Every CRM provider MUST implement this interface.
The core sync engine and all business logic ONLY interact through this interface.
Provider-specific details must NEVER leak outside app/crm/providers/{name}/.

Adding a new CRM provider:
  1. Create app/crm/providers/{name}/ with oauth.py, client.py, sync.py, webhook.py
  2. Implement ICRMProvider in the provider class
  3. Register: CRMProviderRegistry.register("name", ProviderClass)
  4. Add enum: CRMProvider.NAME = "name"
  5. Add config vars: NAME_CLIENT_ID, NAME_CLIENT_SECRET, etc.

That is ALL that is required. Zero core changes.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING, Any, Generator

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from app.crm.base.models import (
    CRMAccount,
    CRMContact,
    CRMLead,
    CRMOpportunity,
    CRMUser,
    CRMEvent,
    CRMConnectionState,
    ProviderCapabilities,
    OAuthURLResult,
    OAuthCallbackResult,
    SyncResult,
)


class ICRMProvider(ABC):
    """
    Abstract base class for all CRM provider implementations.

    Every method must be implemented. Providers that do not support a feature
    (e.g., leads in HubSpot) must return an empty iterator — never raise NotImplementedError
    for supported interface methods. Use ProviderCapabilities to declare what is supported.
    """

    # ── Provider identity ──────────────────────────────────────────────────────

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Unique lowercase slug. Must match CRMProvider enum value."""
        ...

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable name shown in the UI."""
        ...

    # ── Capability detection ───────────────────────────────────────────────────

    @abstractmethod
    def get_capabilities(self) -> ProviderCapabilities:
        """
        Return the capability profile for this provider.
        The sync engine uses this to skip unsupported operations gracefully.
        """
        ...

    # ── OAuth flow ─────────────────────────────────────────────────────────────

    @abstractmethod
    def get_oauth_url(self, workspace_id: str) -> OAuthURLResult:
        """
        Build the OAuth authorization URL that the user is redirected to.
        Returns the URL and any state/PKCE verifier that must be stored.
        """
        ...

    @abstractmethod
    def handle_oauth_callback(
        self,
        code: str,
        state: str,
        workspace_id: str,
        db: "Session",
    ) -> OAuthCallbackResult:
        """
        Exchange the OAuth code for tokens. Store tokens encrypted in DB.
        Returns connection state that the caller should persist.
        """
        ...

    # ── Connection lifecycle ───────────────────────────────────────────────────

    @abstractmethod
    def refresh_token(self) -> None:
        """
        Refresh the access token using the stored refresh token.
        Must update the connection record in the DB.
        Raises ExternalServiceError on unrecoverable failure.
        """
        ...

    @abstractmethod
    def disconnect(self, workspace_id: str, db: "Session") -> bool:
        """
        Disconnect this CRM from the workspace.
        Should revoke tokens with the provider if supported.
        Must mark the connection inactive in the DB.
        Returns True if disconnect was successful.
        """
        ...

    @abstractmethod
    def get_status(self) -> CRMConnectionState:
        """Return current connection and sync state."""
        ...

    # ── Object sync ────────────────────────────────────────────────────────────

    @abstractmethod
    def sync_accounts(
        self,
        modified_after: datetime | None = None,
    ) -> Generator[CRMAccount, None, None]:
        """
        Yield canonical CRMAccount records from the provider.
        If modified_after is provided, only yield records modified since that time.
        Implementations must handle pagination transparently.
        """
        ...

    @abstractmethod
    def sync_contacts(
        self,
        modified_after: datetime | None = None,
    ) -> Generator[CRMContact, None, None]:
        """Yield canonical CRMContact records."""
        ...

    @abstractmethod
    def sync_leads(
        self,
        modified_after: datetime | None = None,
    ) -> Generator[CRMLead, None, None]:
        """
        Yield canonical CRMLead records.
        Providers without a native Lead concept (e.g. HubSpot) must return an empty generator.
        """
        ...

    @abstractmethod
    def sync_opportunities(
        self,
        modified_after: datetime | None = None,
    ) -> Generator[CRMOpportunity, None, None]:
        """Yield canonical CRMOpportunity records (Deals, Opportunities, etc.)."""
        ...

    @abstractmethod
    def sync_users(self) -> Generator[CRMUser, None, None]:
        """Yield canonical CRMUser records (Owners, Sales Reps, etc.)."""
        ...

    # ── Sync orchestration ────────────────────────────────────────────────────

    @abstractmethod
    def historical_sync(self, days_back: int = 180) -> SyncResult:
        """
        Pull full history going back `days_back` days.
        Called once on initial connection. May take minutes for large CRMs.
        Must be idempotent — safe to re-run.
        """
        ...

    @abstractmethod
    def incremental_sync(self) -> SyncResult:
        """
        Pull only records modified since the last successful sync.
        Called on schedule (default: every 30 minutes).
        Must be idempotent.
        """
        ...

    # ── Webhooks ──────────────────────────────────────────────────────────────

    @abstractmethod
    def verify_webhook_signature(
        self,
        payload: bytes,
        headers: dict[str, str],
    ) -> bool:
        """
        Verify the webhook payload signature.
        Return False to reject the request (results in 401).
        Providers without webhook support must return True (accept everything, validate upstream).
        """
        ...

    @abstractmethod
    def handle_webhook(
        self,
        payload: bytes,
        headers: dict[str, str],
    ) -> list[CRMEvent]:
        """
        Parse a webhook payload and return a list of generic CRMEvents.
        The sync engine will process these events.
        Return an empty list if the event is not relevant.
        """
        ...

    # ── Health ─────────────────────────────────────────────────────────────────

    def health_check(self) -> dict[str, Any]:
        """
        Perform a lightweight health check (e.g., fetch current user).
        Default implementation tries to get status. Override for a real API ping.
        """
        try:
            status = self.get_status()
            return {
                "healthy": status.is_active,
                "provider": self.provider_name,
                "last_sync": status.last_sync_at.isoformat() if status.last_sync_at else None,
            }
        except Exception as exc:
            return {
                "healthy": False,
                "provider": self.provider_name,
                "error": str(exc),
            }
