import urllib.parse
import httpx
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class HubSpotClient:
    """
    Asynchronous SDK Wrapper for the HubSpot v3 API.
    Handles HTTP communication, rate limiting signals, and authentication injection.
    """
    
    BASE_URL = "https://api.hubapi.com"
    
    def __init__(self, client_id: str, client_secret: str, access_token: Optional[str] = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        # Provide a configured httpx client. We will rely on Integration Hub's 
        # RetryEngine for handling 429 rate limits, so we don't catch them silently here,
        # but we do raise them explicitly.
        self._client = httpx.AsyncClient(base_url=self.BASE_URL)

    def _get_headers(self) -> Dict[str, str]:
        if not self.access_token:
            raise ValueError("Access token is missing")
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def get_authorization_url(self, state: str, redirect_uri: str, scopes: list[str]) -> str:
        """Constructs the HubSpot OAuth consent URL."""
        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "scope": " ".join(scopes),
            "state": state
        }
        query_string = urllib.parse.urlencode(params)
        return f"https://app.hubspot.com/oauth/authorize?{query_string}"

    async def exchange_code(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchanges an authorization code for tokens."""
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": redirect_uri,
            "code": code
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.BASE_URL}/oauth/v1/token", data=data)
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
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.BASE_URL}/oauth/v1/token", data=data)
            response.raise_for_status()
            return response.json()

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Executes a GET request against the HubSpot API."""
        response = await self._client.get(endpoint, headers=self._get_headers(), params=params)
        
        if response.status_code == 429:
            logger.warning("HubSpot Rate Limit hit (HTTP 429). Signaling RetryEngine.")
            raise ValueError("Rate limit exceeded 429")
            
        response.raise_for_status()
        return response.json()
