from typing import Protocol, Optional, List, Dict, Any, AsyncGenerator, runtime_checkable
from uuid import UUID
from app.modules.integration_hub.domain.models import (
    IntegrationConnection, 
    ProviderMetadata, 
    SyncCursor
)

@runtime_checkable
class IntegrationProvider(Protocol):
    """
    Base interface that all external integrations must implement.
    Guarantees that the Hub can manage the lifecycle of any provider dynamically.
    """
    def get_metadata(self) -> ProviderMetadata:
        """Returns the static metadata and capabilities of the provider."""
        ...
        
    async def validate_connection(self, connection: IntegrationConnection) -> bool:
        """Tests the current credentials to ensure the connection is healthy."""
        ...

@runtime_checkable
class OAuthProvider(Protocol):
    """
    Interface for providers that require OAuth 2.0 PKCE auth flows.
    """
    def get_authorization_url(self, state: str, redirect_uri: str) -> str:
        """Generates the OAuth consent URL."""
        ...
        
    async def exchange_code(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchanges the authorization code for an access and refresh token."""
        ...
        
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refreshes an expired access token using the stored refresh token."""
        ...

@runtime_checkable
class SyncProvider(Protocol):
    """
    Interface for syncing data out of a provider into the hub.
    """
    async def fetch_records(
        self, 
        connection: IntegrationConnection, 
        entity_type: str, 
        cursor: Optional[SyncCursor] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Yields raw records from the provider API, handling pagination natively.
        The Normalization Layer intercepts these to map to Canonical Entities.
        """
        ...
        
@runtime_checkable
class WebhookProvider(Protocol):
    """
    Interface for parsing and verifying inbound provider webhooks.
    """
    async def verify_webhook_signature(self, request_headers: Dict[str, str], request_body: bytes) -> bool:
        """Cryptographically verifies the webhook originated from the provider."""
        ...
        
    def parse_webhook_events(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parses the provider's specific webhook payload into a generic list of events."""
        ...
