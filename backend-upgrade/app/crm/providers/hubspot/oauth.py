"""app/crm/providers/hubspot/oauth.py
HubSpot OAuth 2.0 implementation.
"""
from __future__ import annotations

import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.crm.base.auth import BaseOAuthHandler
from app.crm.base.models import OAuthURLResult, OAuthCallbackResult

logger = get_logger(__name__)

HUBSPOT_AUTH_URL = "https://app.hubspot.com/oauth/authorize"
HUBSPOT_TOKEN_URL = "https://api.hubapi.com/oauth/v1/token"
HUBSPOT_API_BASE = "https://api.hubapi.com"

HUBSPOT_SCOPES = (
    "crm.objects.deals.read "
    "crm.objects.companies.read "
    "crm.objects.contacts.read "
    "crm.objects.owners.read "
    "oauth"
)


class HubSpotOAuth(BaseOAuthHandler):
    PROVIDER = "hubspot"
    TOKEN_URL = HUBSPOT_TOKEN_URL

    def __init__(self) -> None:
        super().__init__(
            client_id=settings.HUBSPOT_APP_CLIENT_ID,
            client_secret=settings.HUBSPOT_APP_CLIENT_SECRET,
        )

    def build_auth_url(self, workspace_id: str) -> OAuthURLResult:
        redirect_uri = settings.effective_hubspot_redirect_uri
        state = workspace_id  # Use workspace_id as state for callback validation
        auth_url = (
            f"{HUBSPOT_AUTH_URL}"
            f"?client_id={self.client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&scope={HUBSPOT_SCOPES.replace(' ', '%20')}"
            f"&state={state}"
        )
        return OAuthURLResult(auth_url=auth_url, state=state, redirect_uri=redirect_uri)

    def exchange_code(self, code: str) -> dict:
        """Exchange authorization code for tokens."""
        return self._post_token_request({
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": settings.effective_hubspot_redirect_uri,
            "code": code,
        })

    def get_hub_info(self, access_token: str) -> tuple[str, str]:
        """Return (hub_id, hub_domain) for the connected portal."""
        resp = httpx.get(
            f"{HUBSPOT_API_BASE}/oauth/v1/access-tokens/{access_token}",
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        hub_id = str(data.get("hub_id", ""))
        hub_domain = data.get("hub_domain", "") or ""
        return hub_id, hub_domain

    def exchange_to_callback_result(self, code: str) -> OAuthCallbackResult:
        token_data = self.exchange_code(code)
        access_token = token_data["access_token"]
        refresh_token = token_data["refresh_token"]
        expires_in = token_data.get("expires_in", 1800)
        hub_id, hub_domain = self.get_hub_info(access_token)
        return OAuthCallbackResult(
            provider="hubspot",
            external_account_id=hub_id,
            external_account_name=hub_domain,
            access_token=access_token,
            refresh_token=refresh_token,
            token_expires_in=expires_in,
            scopes=self.parse_scopes(HUBSPOT_SCOPES),
            provider_metadata={"hub_id": hub_id, "hub_domain": hub_domain},
        )
