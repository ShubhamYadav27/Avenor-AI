"""app/crm/providers/zoho/oauth.py"""
from __future__ import annotations

import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.crm.base.auth import BaseOAuthHandler
from app.crm.base.models import OAuthURLResult, OAuthCallbackResult

logger = get_logger(__name__)

SCOPES = "ZohoCRM.modules.ALL ZohoCRM.settings.ALL ZohoCRM.users.ALL"

_DC_AUTH_DOMAINS = {
    "com": "accounts.zoho.com",
    "eu": "accounts.zoho.eu",
    "in": "accounts.zoho.in",
    "au": "accounts.zoho.com.au",
    "jp": "accounts.zoho.jp",
    "ca": "accounts.zohocloud.ca",
}
_DC_API_DOMAINS = {
    "com": "www.zohoapis.com",
    "eu": "www.zohoapis.eu",
    "in": "www.zohoapis.in",
    "au": "www.zohoapis.com.au",
    "jp": "www.zohoapis.jp",
    "ca": "www.zohoapis.ca",
}


class ZohoOAuth(BaseOAuthHandler):
    PROVIDER = "zoho"

    def __init__(self) -> None:
        super().__init__(
            client_id=settings.ZOHO_CLIENT_ID,
            client_secret=settings.ZOHO_CLIENT_SECRET,
        )
        dc = settings.ZOHO_DATA_CENTER or "com"
        auth_domain = _DC_AUTH_DOMAINS.get(dc, _DC_AUTH_DOMAINS["com"])
        self._api_domain = _DC_API_DOMAINS.get(dc, _DC_API_DOMAINS["com"])
        self._auth_url = f"https://{auth_domain}/oauth/v2/auth"
        self.TOKEN_URL = f"https://{auth_domain}/oauth/v2/token"

    def build_auth_url(self, workspace_id: str) -> OAuthURLResult:
        redirect_uri = settings.ZOHO_REDIRECT_URI
        url = (
            f"{self._auth_url}?response_type=code"
            f"&client_id={self.client_id}"
            f"&scope={SCOPES.replace(' ', '%20')}"
            f"&redirect_uri={redirect_uri}"
            f"&state={workspace_id}"
            f"&access_type=offline"
        )
        return OAuthURLResult(auth_url=url, state=workspace_id, redirect_uri=redirect_uri)

    def exchange_code(self, code: str) -> dict:
        return self._post_token_request({
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": settings.ZOHO_REDIRECT_URI,
            "code": code,
        })

    def _build_refresh_payload(self, refresh_token: str) -> dict:
        return {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
        }

    def get_org_info(self, access_token: str) -> dict:
        resp = httpx.get(
            f"https://{self._api_domain}/crm/v7/org",
            headers={"Authorization": f"Zoho-oauthtoken {access_token}"},
            timeout=10,
        )
        resp.raise_for_status()
        orgs = resp.json().get("org", [{}])
        return orgs[0] if orgs else {}

    def exchange_to_callback_result(self, code: str) -> OAuthCallbackResult:
        td = self.exchange_code(code)
        access_token = td["access_token"]
        refresh_token = td.get("refresh_token", "")
        if not refresh_token:
            raise ValueError("Zoho CRM OAuth did not return a refresh token")

        org = self.get_org_info(access_token)
        org_id = str(org.get("id", "")) or td.get("location", "zoho_org")
        org_name = org.get("company_name") or org.get("primary_email", "Zoho Organization")
        return OAuthCallbackResult(
            provider="zoho",
            external_account_id=org_id,
            external_account_name=org_name,
            access_token=access_token,
            refresh_token=refresh_token,
            token_expires_in=td.get("expires_in", 3600),
            scopes=self.parse_scopes(SCOPES),
            provider_metadata={
                "api_domain": self._api_domain,
                "org_name": org_name,
            },
        )
