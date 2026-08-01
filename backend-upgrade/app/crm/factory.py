"""
app/crm/factory.py

CRMFactory — the single entry point for obtaining provider instances.

Business logic must NEVER instantiate provider classes directly.
Always use CRMFactory to get a configured provider.

Usage:
  # Get provider for a workspace (reads workspace.crm_provider)
  provider = CRMFactory.get_for_workspace(workspace_id, db)
  if provider:
      result = provider.incremental_sync()

  # Get a specific provider by name (with a pre-fetched connection)
  provider = CRMFactory.get_provider("hubspot", connection, db)

  # Get OAuth URL for a provider (before connection exists)
  result = CRMFactory.get_oauth_url("salesforce", workspace_id)
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from app.core.logging import get_logger
from app.crm.registry import CRMProviderRegistry

if TYPE_CHECKING:
    from sqlalchemy.orm import Session
    from app.crm.base.interfaces import ICRMProvider
    from app.crm.base.models import OAuthURLResult

logger = get_logger(__name__)


class CRMFactory:
    """
    Factory for creating configured CRM provider instances.

    Depends on:
      - CRMProviderRegistry (for provider class lookup)
      - Database session (to fetch connection state)
      - Workspace record (to determine which provider to use)
    """

    @staticmethod
    def get_provider(
        provider_name: str,
        connection: Any,          # CRMConnectionDB SQLAlchemy model
        db: "Session",
    ) -> "ICRMProvider":
        """
        Instantiate and return a configured provider for a known connection.

        Args:
            provider_name: Lowercase slug (e.g. "hubspot", "salesforce")
            connection: CRMConnectionDB record from the database
            db: Active database session

        Returns:
            Configured ICRMProvider instance

        Raises:
            ValueError: If the provider is not registered
        """
        provider_cls = CRMProviderRegistry.get(provider_name)
        logger.debug(
            "crm_factory_get_provider",
            provider=provider_name,
            workspace_id=str(connection.workspace_id) if connection else "unknown",
        )
        return provider_cls(connection=connection, db=db)

    @staticmethod
    def get_for_workspace(
        workspace_id: str,
        db: "Session",
    ) -> "ICRMProvider | None":
        """
        Get the active CRM provider for a workspace.

        Reads workspace.crm_provider to determine which provider to use,
        then fetches the CRMConnectionDB record and instantiates the provider.

        Returns:
            Configured ICRMProvider, or None if the workspace has no CRM connected.
        """
        from app.models import Workspace, CRMConnectionDB

        import uuid
        try:
            ws_uuid = uuid.UUID(str(workspace_id))
        except (ValueError, AttributeError):
            logger.error("crm_factory_invalid_workspace_id", workspace_id=workspace_id)
            return None

        workspace = db.get(Workspace, ws_uuid)
        if not workspace:
            logger.warning("crm_factory_workspace_not_found", workspace_id=workspace_id)
            return None

        provider_name = workspace.crm_provider
        if not provider_name:
            return None

        if not CRMProviderRegistry.is_registered(provider_name):
            logger.error(
                "crm_factory_provider_not_registered",
                provider=provider_name,
                workspace_id=workspace_id,
            )
            return None

        connection = (
            db.query(CRMConnectionDB)
            .filter_by(
                workspace_id=ws_uuid,
                provider=provider_name,
                is_active=True,
            )
            .first()
        )

        if not connection:
            logger.debug(
                "crm_factory_no_active_connection",
                provider=provider_name,
                workspace_id=workspace_id,
            )
            return None

        return CRMFactory.get_provider(provider_name, connection, db)

    @staticmethod
    def get_oauth_url(
        provider_name: str,
        workspace_id: str,
    ) -> "OAuthURLResult":
        """
        Get the OAuth authorization URL for a provider.
        Called before a connection exists (no connection object needed).

        The provider is instantiated with no connection in this case — each
        provider's __init__ must handle connection=None gracefully.
        """
        provider_cls = CRMProviderRegistry.get(provider_name)
        # Instantiate with no connection — OAuth initiation doesn't need one
        provider = provider_cls(connection=None, db=None)
        return provider.get_oauth_url(workspace_id)

    @staticmethod
    def list_providers() -> list[dict]:
        """Return metadata for all registered providers."""
        return CRMProviderRegistry.list_all()

    @staticmethod
    def is_provider_available(provider_name: str) -> bool:
        """Check if a provider is registered and available."""
        return CRMProviderRegistry.is_registered(provider_name)
