"""app/crm/providers/dynamics/oauth.py"""
from __future__ import annotations

import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.crm.base.auth import BaseOAuthHandler
from app.crm.base.models import OAuthURLResult, OAuthCallbackResult

logger = get_logger(__name__)

DISCOVERY_URL = "https://globaldisco.crm.dynamics.com/api/discovery/v2.0/Instances"
SCOPES = "https://admin.services.crm.dynamics.com/user_impersonation offline_access"


class DynamicsOAuth(BaseOAuthHandler):
    PROVIDER = "dynamics"

    def __init__(self) -> None:
        super().__init__(
            client_id=settings.DYNAMICS_CLIENT_ID,
            client_secret=settings.DYNAMICS_CLIENT_SECRET,
        )
        tenant = settings.DYNAMICS_TENANT_ID or "common"
        self.auth_url = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize"
        self.TOKEN_URL = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"

    def build_auth_url(self, workspace_id: str) -> OAuthURLResult:
        redirect_uri = settings.DYNAMICS_REDIRECT_URI
        url = (
            f"{self.auth_url}?response_type=code"
            f"&client_id={self.client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&scope={SCOPES.replace(' ', '%20')}"
            f"&state={workspace_id}"
            f"&response_mode=query"
        )
        return OAuthURLResult(auth_url=url, state=workspace_id, redirect_uri=redirect_uri)

    def exchange_code(self, code: str) -> dict:
        return self._post_token_request({
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": settings.DYNAMICS_REDIRECT_URI,
            "code": code,
            "scope": SCOPES,
        })

    def discover_crm_url(self, access_token: str) -> tuple[str, str, str]:
        """Returns (api_url, friendly_name, unique_name)."""
        try:
            resp = httpx.get(
                DISCOVERY_URL,
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=15,
            )
            resp.raise_for_status()
            instances = resp.json().get("value", [])
            if instances:
                first = instances[0]
                return first.get("ApiUrl", ""), first.get("FriendlyName", ""), first.get("UniqueName", "")
        except Exception as exc:
            logger.warning("dynamics_discovery_failed", error=str(exc))
        return "", "Dynamics 365 Organization", "dynamics_org"

    def exchange_to_callback_result(self, code: str) -> OAuthCallbackResult:
        td = self.exchange_code(code)
        access_token = td["access_token"]
        refresh_token = td.get("refresh_token", "")
        if not refresh_token:
            raise ValueError("Microsoft Dynamics OAuth did not return a refresh token")

        crm_url, org_name, org_id = self.discover_crm_url(access_token)
        return OAuthCallbackResult(
            provider="dynamics",
            external_account_id=org_id,
            external_account_name=org_name,
            access_token=access_token,
            refresh_token=refresh_token,
            token_expires_in=td.get("expires_in", 3600),
            scopes=self.parse_scopes(SCOPES),
            provider_metadata={"crm_url": crm_url, "org_name": org_name},
        )
