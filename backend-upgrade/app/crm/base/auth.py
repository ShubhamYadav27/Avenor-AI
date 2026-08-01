"""
app/crm/base/auth.py

BaseOAuthHandler — shared OAuth logic for all CRM providers.

All providers extend this class and call super() for common operations:
  - Token encryption / decryption (Fernet)
  - Token expiry checking
  - Token refresh with retry + backoff
  - State parameter generation
  - PKCE support

Provider-specific OAuth URL construction and token exchange
are implemented in each provider's oauth.py.
"""
from __future__ import annotations

import hashlib
import secrets
from base64 import urlsafe_b64encode
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.exceptions import ExternalServiceError
from app.core.logging import get_logger
from app.utils.encryption import decrypt_token, encrypt_token

if TYPE_CHECKING:
    pass

logger = get_logger(__name__)

# Token considered expired if it expires within this window
_TOKEN_REFRESH_BUFFER_MINUTES = 5


class BaseOAuthHandler:
    """
    Shared OAuth utilities for all CRM provider OAuth implementations.

    Usage in a provider:
        class HubSpotOAuth(BaseOAuthHandler):
            PROVIDER = "hubspot"
            TOKEN_URL = "https://api.hubapi.com/oauth/v1/token"

            def build_auth_url(self, workspace_id: str, redirect_uri: str) -> str:
                ...

            def exchange_code(self, code: str, redirect_uri: str) -> dict:
                return self._post_token_request({
                    "grant_type": "authorization_code",
                    "code": code,
                    ...
                })
    """

    PROVIDER: str = ""              # Must be set by subclass
    TOKEN_URL: str = ""             # Must be set by subclass
    TOKEN_TIMEOUT: float = 15.0

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret

    # ── Token encryption ───────────────────────────────────────────────────────

    @staticmethod
    def encrypt(token: str) -> str:
        """Encrypt a token using Fernet symmetric encryption."""
        return encrypt_token(token)

    @staticmethod
    def decrypt(encrypted: str) -> str:
        """Decrypt a Fernet-encrypted token."""
        return decrypt_token(encrypted)

    # ── Token expiry ───────────────────────────────────────────────────────────

    @staticmethod
    def is_near_expiry(expires_at: datetime) -> bool:
        """True if the token expires within the refresh buffer window."""
        now = datetime.now(timezone.utc)
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        return expires_at - now < timedelta(minutes=_TOKEN_REFRESH_BUFFER_MINUTES)

    @staticmethod
    def expires_at_from_seconds(expires_in: int) -> datetime:
        """Calculate expiry datetime from expires_in seconds."""
        return datetime.now(timezone.utc) + timedelta(seconds=expires_in)

    # ── State & PKCE ───────────────────────────────────────────────────────────

    @staticmethod
    def generate_state() -> str:
        """Generate a secure random state parameter for OAuth."""
        return secrets.token_urlsafe(32)

    @staticmethod
    def generate_pkce_pair() -> tuple[str, str]:
        """
        Generate a PKCE code_verifier and code_challenge pair.
        Returns: (code_verifier, code_challenge)
        """
        code_verifier = secrets.token_urlsafe(32)
        code_challenge = (
            urlsafe_b64encode(
                hashlib.sha256(code_verifier.encode()).digest()
            )
            .decode()
            .rstrip("=")
        )
        return code_verifier, code_challenge

    # ── HTTP helpers ───────────────────────────────────────────────────────────

    @retry(
        retry=retry_if_exception_type(httpx.HTTPStatusError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=30),
    )
    def _post_token_request(
        self,
        data: dict[str, Any],
        headers: dict[str, str] | None = None,
        json_body: bool = False,
    ) -> dict[str, Any]:
        """
        POST to the provider's token endpoint.
        Handles retries on 5xx errors. Raises ExternalServiceError on 4xx.
        """
        try:
            if json_body:
                resp = httpx.post(
                    self.TOKEN_URL,
                    json=data,
                    headers=headers or {"Content-Type": "application/json"},
                    timeout=self.TOKEN_TIMEOUT,
                )
            else:
                resp = httpx.post(
                    self.TOKEN_URL,
                    data=data,
                    headers=headers or {},
                    timeout=self.TOKEN_TIMEOUT,
                )

            if resp.status_code >= 500:
                logger.warning(
                    "oauth_token_endpoint_server_error",
                    provider=self.PROVIDER,
                    status=resp.status_code,
                )
                resp.raise_for_status()  # Trigger tenacity retry

            if resp.status_code >= 400:
                logger.error(
                    "oauth_token_request_failed",
                    provider=self.PROVIDER,
                    status=resp.status_code,
                    body=resp.text[:500],
                )
                raise ExternalServiceError(
                    self.PROVIDER,
                    f"OAuth token error {resp.status_code}: {resp.text[:200]}",
                )

            return resp.json()

        except ExternalServiceError:
            raise
        except httpx.HTTPStatusError:
            raise
        except Exception as exc:
            raise ExternalServiceError(
                self.PROVIDER,
                f"OAuth request failed: {exc}",
            ) from exc

    def _build_refresh_payload(self, refresh_token: str) -> dict[str, Any]:
        """
        Build the token refresh request payload.
        Override in subclasses that use different grant types (e.g. Zoho).
        """
        return {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
        }

    def refresh_access_token(self, refresh_token: str) -> dict[str, Any]:
        """
        Use the refresh token to get a new access token.
        Returns the raw token response dict.
        """
        logger.info("refreshing_oauth_token", provider=self.PROVIDER)
        payload = self._build_refresh_payload(refresh_token)
        return self._post_token_request(payload)

    # ── Webhook signature verification ─────────────────────────────────────────

    @staticmethod
    def constant_time_compare(a: str, b: str) -> bool:
        """Timing-safe string comparison for signature verification."""
        return secrets.compare_digest(a.encode(), b.encode())

    # ── Scopes helper ──────────────────────────────────────────────────────────

    @staticmethod
    def parse_scopes(scopes_str: str | list[str]) -> list[str]:
        """Normalize scopes to a list, handling space-separated or list formats."""
        if isinstance(scopes_str, list):
            return scopes_str
        return [s.strip() for s in scopes_str.split() if s.strip()]

