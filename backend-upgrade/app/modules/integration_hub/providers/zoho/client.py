import urllib.parse
import httpx
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ZohoClient:
    """
    Asynchronous SDK Wrapper for the Zoho CRM API (v6).
    Handles regional data centers, OAuth PKCE exchange, and strict Rate Limit propagation.
    """
    
    API_VERSION = "v6"
    
    # Maps top-level domains to their respective API bases
    DC_MAP = {
        "com": "www.zohoapis.com",
        "eu": "www.zohoapis.eu",
        "in": "www.zohoapis.in",
        "com.au": "www.zohoapis.com.au",
        "jp": "www.zohoapis.jp"
    }
    
    def __init__(self, client_id: str, client_secret: str, access_token: Optional[str] = None, data_center: str = "com"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.data_center = data_center # e.g. "com", "eu"
        
        self.auth_base_url = f"https://accounts.zoho.{self.data_center}/oauth/v2"
        api_domain = self.DC_MAP.get(self.data_center, "www.zohoapis.com")
        self.api_base_url = f"https://{api_domain}/crm/{self.API_VERSION}"
        
        self._client = httpx.AsyncClient()

    def _get_headers(self, if_modified_since: str = None) -> Dict[str, str]:
        if not self.access_token:
            raise ValueError("Access token is missing")
        headers = {
            "Authorization": f"Zoho-oauthtoken {self.access_token}",
            "Content-Type": "application/json"
        }
        if if_modified_since:
            # Zoho expects ISO 8601 format e.g., 2023-01-01T10:00:00+00:00
            headers["If-Modified-Since"] = if_modified_since
        return headers

    def get_authorization_url(self, state: str, redirect_uri: str, scopes: list[str], prompt: str = "consent", access_type: str = "offline") -> str:
        """Constructs the Zoho OAuth consent URL."""
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "scope": ",".join(scopes),
            "state": state,
            "prompt": prompt,
            "access_type": access_type
        }
        query_string = urllib.parse.urlencode(params)
        return f"{self.auth_base_url}/auth?{query_string}"

    async def exchange_code(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchanges an authorization code for tokens."""
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": redirect_uri,
            "code": code
        }
        response = await self._client.post(f"{self.auth_base_url}/token", data=data)
        response.raise_for_status()
        return response.json()

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refreshes the OAuth access token."""
        data = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token
        }
        response = await self._client.post(f"{self.auth_base_url}/token", data=data)
        response.raise_for_status()
        return response.json()

    async def get(self, module: str, params: Optional[Dict[str, Any]] = None, if_modified_since: str = None) -> Dict[str, Any]:
        """Executes a GET request against the Zoho CRM API."""
        endpoint = f"{self.api_base_url}/{module}"
        
        response = await self._client.get(endpoint, headers=self._get_headers(if_modified_since), params=params)
        
        # Zoho returns 304 if not modified (when using If-Modified-Since)
        if response.status_code == 304:
            return {"data": []}
            
        # 429 means API limits exceeded
        if response.status_code == 429:
            logger.warning("Zoho Rate Limit hit (HTTP 429). Signaling RetryEngine.")
            raise ValueError("Rate limit exceeded 429")
            
        response.raise_for_status()
        return response.json()
