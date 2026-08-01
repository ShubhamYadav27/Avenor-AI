import urllib.parse
import httpx
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class DynamicsClient:
    """
    Asynchronous SDK Wrapper for the Microsoft Dynamics 365 Dataverse Web API (v9.2).
    Handles OData queries, OAuth PKCE exchange via Microsoft Identity Platform, 
    and Rate Limit propagation.
    """
    
    # Microsoft Identity Platform OAuth v2.0 endpoint
    AUTH_BASE_URL = "https://login.microsoftonline.com/common/oauth2/v2.0"
    API_VERSION = "v9.2"
    
    def __init__(self, client_id: str, client_secret: str, access_token: Optional[str] = None, resource_url: Optional[str] = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.resource_url = resource_url # e.g. https://org123.crm.dynamics.com
        
        self._client = httpx.AsyncClient()

    def _get_headers(self, prefer_track_changes: bool = False) -> Dict[str, str]:
        if not self.access_token:
            raise ValueError("Access token is missing")
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
            "Accept": "application/json"
        }
        if prefer_track_changes:
            headers["Prefer"] = "odata.track-changes"
        return headers

    def get_authorization_url(self, state: str, redirect_uri: str, scopes: list[str]) -> str:
        """Constructs the Microsoft Identity Platform OAuth consent URL."""
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "scope": " ".join(scopes),
            "state": state
        }
        query_string = urllib.parse.urlencode(params)
        return f"{self.AUTH_BASE_URL}/authorize?{query_string}"

    async def exchange_code(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchanges an authorization code for tokens."""
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": redirect_uri,
            "code": code
        }
        response = await self._client.post(f"{self.AUTH_BASE_URL}/token", data=data)
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
        response = await self._client.post(f"{self.AUTH_BASE_URL}/token", data=data)
        response.raise_for_status()
        return response.json()

    async def query(self, entity_set_name: str, select: str = None, track_changes: bool = False, delta_link: str = None) -> Dict[str, Any]:
        """Executes an OData query against the Dataverse Web API."""
        if not self.resource_url:
            raise ValueError("Resource URL (Instance URL) is missing")
            
        # If delta_link is provided, it contains the full URL with the deltatoken
        if delta_link:
            endpoint = delta_link
        else:
            endpoint = f"{self.resource_url}/api/data/{self.API_VERSION}/{entity_set_name}"
            
        params = {}
        if select and not delta_link:
            params["$select"] = select
            
        headers = self._get_headers(prefer_track_changes=track_changes)
        
        response = await self._client.get(endpoint, headers=headers, params=params)
        
        if response.status_code == 429:
            logger.warning("Dynamics Rate Limit hit (HTTP 429). Signaling RetryEngine.")
            raise ValueError("Rate limit exceeded 429")
            
        response.raise_for_status()
        return response.json()
        
    async def get_next_link(self, next_link: str) -> Dict[str, Any]:
        """Fetches the next page of OData query results using @odata.nextLink."""
        response = await self._client.get(next_link, headers=self._get_headers())
        if response.status_code == 429:
            raise ValueError("Rate limit exceeded 429")
            
        response.raise_for_status()
        return response.json()
