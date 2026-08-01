"""app/crm/providers/salesforce/oauth.py

Salesforce OAuth 2.0 with PKCE (Authorization Code + S256 challenge).

Salesforce Connected Apps configured with "Require Proof Key for Code Exchange
(PKCE) Extension for Supported Authorization Flows" must receive:
  - code_challenge      (S256 hash of code_verifier, base64url-encoded, no padding)
  - code_challenge_method = S256

on the /authorize request, and:
  - code_verifier       (the original random secret)

on the /token exchange request.

PKCE verifier persistence
-------------------------
The verifier is generated in build_auth_url() and returned inside
OAuthURLResult.pkce_verifier.  The caller (crm/routes.py) stores it in
_PKCE_STORE — a module-level TTL dict keyed by the OAuth state parameter.
On callback, the route retrieves the verifier and passes it to
exchange_to_callback_result().

Security properties
-------------------
- code_verifier  : 32 bytes from secrets.token_urlsafe → 256-bit entropy
- code_challenge : SHA-256(verifier), base64url, no padding (RFC 7636 §4.2)
- TTL            : 10 minutes, matching Salesforce's authorization code lifetime
- State binding  : verifier is keyed by the workspace_id / state parameter so
                   a cross-workspace substitution attack is impossible
"""
from __future__ import annotations

import time
from threading import Lock
from urllib.parse import urlencode

import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.crm.base.auth import BaseOAuthHandler
from app.crm.base.models import OAuthCallbackResult, OAuthURLResult

logger = get_logger(__name__)

SCOPES = "api refresh_token offline_access"

# ── PKCE verifier TTL store ────────────────────────────────────────────────────
# Keyed by `state` (== workspace_id).  Each entry: (verifier, expires_at_unix).
# 10-minute TTL matches the Salesforce authorization code lifetime.

_PKCE_TTL_SECONDS = 600          # 10 minutes
_PKCE_STORE: dict[str, tuple[str, float]] = {}
_PKCE_LOCK = Lock()


def _store_verifier(state: str, verifier: str) -> None:
    """Store a PKCE verifier for the given state with a 10-minute TTL."""
    expires_at = time.monotonic() + _PKCE_TTL_SECONDS
    with _PKCE_LOCK:
        _PKCE_STORE[state] = (verifier, expires_at)
        # Opportunistically evict expired entries
        _evict_expired()


def _pop_verifier(state: str) -> str | None:
    """Retrieve and remove the PKCE verifier for the given state.
    Returns None if the state is unknown or the entry has expired.
    """
    with _PKCE_LOCK:
        _evict_expired()
        entry = _PKCE_STORE.pop(state, None)
    if entry is None:
        return None
    verifier, expires_at = entry
    if time.monotonic() > expires_at:
        logger.warning("salesforce_pkce_verifier_expired", state=state)
        return None
    return verifier


def _evict_expired() -> None:
    """Remove stale entries (call while holding _PKCE_LOCK)."""
    now = time.monotonic()
    expired = [k for k, (_, exp) in _PKCE_STORE.items() if now > exp]
    for k in expired:
        del _PKCE_STORE[k]


# ── OAuth handler ──────────────────────────────────────────────────────────────

class SalesforceOAuth(BaseOAuthHandler):
    PROVIDER = "salesforce"

    def __init__(self) -> None:
        super().__init__(
            client_id=settings.SALESFORCE_CLIENT_ID,
            client_secret=settings.SALESFORCE_CLIENT_SECRET,
        )
        base = "test.salesforce.com" if settings.SALESFORCE_SANDBOX else "login.salesforce.com"
        self.auth_url = f"https://{base}/services/oauth2/authorize"
        self.TOKEN_URL = f"https://{base}/services/oauth2/token"

    def build_auth_url(self, workspace_id: str) -> OAuthURLResult:
        """
        Build the Salesforce authorization URL with PKCE S256 challenge.

        Generates a fresh (code_verifier, code_challenge) pair on every call
        and stores the verifier in the TTL store keyed by the state parameter
        so it can be retrieved on callback.
        """
        eff_uri = getattr(settings, "effective_salesforce_redirect_uri", None)
        if isinstance(eff_uri, str) and eff_uri:
            redirect_uri = eff_uri
        else:
            raw_uri = getattr(settings, "SALESFORCE_REDIRECT_URI", "")
            redirect_uri = raw_uri if isinstance(raw_uri, str) else str(raw_uri)

        raw_client_id = getattr(settings, "SALESFORCE_CLIENT_ID", self.client_id)
        client_id = raw_client_id if isinstance(raw_client_id, str) else str(raw_client_id)
        
        is_sandbox = getattr(settings, "SALESFORCE_SANDBOX", False)
        base = "test.salesforce.com" if (is_sandbox is True or str(is_sandbox).lower() == "true") else "login.salesforce.com"
        auth_url_base = f"https://{base}/services/oauth2/authorize"


        # Generate PKCE pair using the base-class utility
        code_verifier, code_challenge = self.generate_pkce_pair()

        # Persist verifier keyed by workspace_id (== state)
        _store_verifier(workspace_id, code_verifier)

        params = {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": SCOPES,
            "state": workspace_id,
            "prompt": "consent",
            # PKCE parameters (RFC 7636)
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
        full_auth_url = f"{auth_url_base}?{urlencode(params)}"
        return OAuthURLResult(
            auth_url=full_auth_url,
            state=workspace_id,
            redirect_uri=redirect_uri,
            pkce_verifier=code_verifier,
        )


        logger.info(
            "salesforce_oauth_url_built",
            workspace_id=workspace_id,
            pkce_method="S256",
        )

        return OAuthURLResult(
            auth_url=f"{self.auth_url}?{urlencode(params)}",
            state=workspace_id,
            redirect_uri=redirect_uri,
            pkce_verifier=code_verifier,   # Returned so tests can inspect it
        )

    def exchange_code(self, code: str, code_verifier: str | None = None) -> dict:
        """
        Exchange an authorization code for tokens.

        When code_verifier is supplied (PKCE flow), it is included in the
        token request.  client_secret is still sent — Salesforce requires it
        even when PKCE is enabled.
        """
        payload: dict = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": settings.effective_salesforce_redirect_uri,
            "code": code,
        }
        if code_verifier:
            payload["code_verifier"] = code_verifier
            logger.info("salesforce_token_exchange_with_pkce")
        else:
            logger.warning("salesforce_token_exchange_without_pkce")

        return self._post_token_request(payload)

    def get_org_info(self, access_token: str, instance_url: str) -> dict:
        resp = httpx.get(
            f"{instance_url.rstrip('/')}/services/oauth2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def exchange_to_callback_result(
        self,
        code: str,
        code_verifier: str | None = None,
    ) -> OAuthCallbackResult:
        """
        Complete the OAuth callback: exchange the authorization code for tokens
        and fetch organization metadata.

        Parameters
        ----------
        code           : Authorization code returned by Salesforce.
        code_verifier  : PKCE verifier. Retrieved from the TTL store by the
                         route handler and passed here.  Must not be None for
                         Connected Apps that require PKCE.
        """
        token_data = self.exchange_code(code, code_verifier=code_verifier)
        access_token = token_data["access_token"]
        refresh_token = token_data.get("refresh_token", "")
        if not refresh_token:
            raise ValueError("Salesforce OAuth did not return a refresh token")
        instance_url = token_data.get("instance_url", "")
        if not instance_url:
            raise ValueError("Salesforce OAuth did not return an instance URL")

        org_info = self.get_org_info(access_token, instance_url)
        org_id = org_info.get("organization_id") or token_data.get("id", "").split("/")[-2]
        org_name = org_info.get("organization_name") or org_info.get("name", "")
        return OAuthCallbackResult(
            provider="salesforce",
            external_account_id=org_id,
            external_account_name=org_name,
            access_token=access_token,
            refresh_token=refresh_token,
            token_expires_in=token_data.get("expires_in", 3600),
            scopes=self.parse_scopes(token_data.get("scope") or SCOPES),
            provider_metadata={"instance_url": instance_url, "org_name": org_name},
        )
