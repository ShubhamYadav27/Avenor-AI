import secrets
import hashlib
import base64
from typing import Dict, Any, Optional
from uuid import UUID
import logging

from app.modules.integration_hub.application.provider_registry import provider_registry
from app.modules.integration_hub.domain.ports import OAuthProvider

logger = logging.getLogger(__name__)

class OAuthManager:
    """
    Application Service responsible for orchestrating OAuth 2.0 PKCE authentication.
    Interfaces with the Provider Registry to route authentication calls to the correct SDK.
    """
    
    def __init__(self):
        # In a real enterprise system, this would be backed by Redis or a secure DB
        self._pkce_state_store: Dict[str, str] = {}
        # In a real enterprise system, this would be AWS KMS or HashiCorp Vault
        self._credentials_vault: Dict[UUID, Dict[str, Any]] = {}

    def generate_pkce_pair(self) -> tuple[str, str]:
        """Generates a cryptographic PKCE code_verifier and code_challenge."""
        code_verifier = secrets.token_urlsafe(64)
        hashed = hashlib.sha256(code_verifier.encode('ascii')).digest()
        code_challenge = base64.urlsafe_b64encode(hashed).decode('ascii').rstrip('=')
        return code_verifier, code_challenge

    def get_authorization_url(self, provider_name: str, redirect_uri: str) -> Optional[str]:
        """
        Builds the secure consent URL for the given provider and caches the state payload.
        """
        provider = provider_registry.get_provider(provider_name)
        if not provider or not isinstance(provider, OAuthProvider):
            logger.error(f"Provider {provider_name} does not support OAuth2")
            return None

        state = secrets.token_urlsafe(32)
        code_verifier, code_challenge = self.generate_pkce_pair()
        
        # Store state -> code_verifier mapping for the callback exchange
        self._pkce_state_store[state] = code_verifier
        
        # Inject PKCE params into the provider's URL generation logic dynamically
        # In practice, we might pass code_challenge to provider.get_authorization_url
        # For simplicity, we assume the provider supports state and redirects.
        auth_url = provider.get_authorization_url(state=state, redirect_uri=redirect_uri)
        return auth_url

    async def exchange_callback(self, provider_name: str, code: str, state: str, redirect_uri: str, tenant_id: UUID) -> UUID:
        """
        Exchanges the authorization code for an access token using the stored PKCE verifier.
        """
        code_verifier = self._pkce_state_store.pop(state, None)
        if not code_verifier:
            raise ValueError("Invalid or expired OAuth state")

        provider = provider_registry.get_provider(provider_name)
        if not provider or not isinstance(provider, OAuthProvider):
            raise ValueError(f"Provider {provider_name} does not support OAuth2")

        # In practice, provider.exchange_code would accept the code_verifier.
        # It's simplified here for architectural demonstration.
        token_payload = await provider.exchange_code(code=code, redirect_uri=redirect_uri)
        
        # Store tokens securely in the vault and return a reference ID
        import uuid
        credentials_id = uuid.uuid4()
        self._credentials_vault[credentials_id] = token_payload
        
        logger.info(f"Successfully authenticated tenant {tenant_id} with {provider_name}")
        return credentials_id
