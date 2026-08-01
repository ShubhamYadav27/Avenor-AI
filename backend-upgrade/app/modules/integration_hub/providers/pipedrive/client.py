import urllib.parse
import httpx
import logging
import base64
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class PipedriveClient:
    """
    Asynchronous SDK Wrapper for the Pipedrive REST API (v1).
    Handles API endpoints, OAuth exchange (Basic Auth for token), and Rate Limit propagation.
    """
    
    AUTH_BASE_URL = "https://oauth.pipedrive.com/oauth"
    API_BASE_URL = "https://api.pipedrive.com/v1"
    
    def __init__(self, client_id: str, client_secret: str, access_token: Optional[str] = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        
        self._client = httpx.AsyncClient(base_url=self.API_BASE_URL)

    def _get_headers(self) -> Dict[str, str]:
        if not self.access_token:
            raise ValueError("Access token is missing")
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
    def _get_auth_headers(self) -> Dict[str, str]:
        auth_string = f"{self.client_id}:{self.client_secret}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        return {
            "Authorization": f"Basic {encoded_auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

    def get_authorization_url(self, state: str, redirect_uri: str) -> str:
        """Constructs the Pipedrive OAuth consent URL."""
        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "state": state
        }
        query_string = urllib.parse.urlencode(params)
        return f"{self.AUTH_BASE_URL}/authorize?{query_string}"

    async def exchange_code(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchanges an authorization code for tokens using Basic Auth."""
        data = {
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
            "code": code
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.AUTH_BASE_URL}/token", 
                data=data, 
                headers=self._get_auth_headers()
            )
            response.raise_for_status()
            return response.json()

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refreshes the OAuth access token using Basic Auth."""
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.AUTH_BASE_URL}/token", 
                data=data, 
                headers=self._get_auth_headers()
            )
            response.raise_for_status()
            return response.json()

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Executes a GET request against the Pipedrive API."""
        response = await self._client.get(endpoint, headers=self._get_headers(), params=params)
        
        if response.status_code == 429:
            logger.warning("Pipedrive Rate Limit hit (HTTP 429). Signaling RetryEngine.")
            raise ValueError("Rate limit exceeded 429")
            
        response.raise_for_status()
        return response.json()
