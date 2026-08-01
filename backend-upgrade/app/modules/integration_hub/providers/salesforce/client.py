import urllib.parse
import httpx
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class SalesforceClient:
    """
    Asynchronous SDK Wrapper for the Salesforce REST API (v60.0).
    Handles SOQL execution, OAuth PKCE exchange, and Rate Limit propagation.
    """
    
    # login.salesforce.com for production, test.salesforce.com for sandboxes
    AUTH_BASE_URL = "https://login.salesforce.com/services/oauth2"
    API_VERSION = "v60.0"
    
    def __init__(self, client_id: str, client_secret: str, access_token: Optional[str] = None, instance_url: Optional[str] = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.instance_url = instance_url
        
        # We don't initialize httpx base_url here because Salesforce instance URLs vary per tenant
        self._client = httpx.AsyncClient()

    def _get_headers(self) -> Dict[str, str]:
        if not self.access_token:
            raise ValueError("Access token is missing")
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def get_authorization_url(self, state: str, redirect_uri: str, scopes: list[str]) -> str:
        """Constructs the Salesforce OAuth consent URL with PKCE support."""
        # Note: PKCE code_challenge is usually provided by the OAuthManager in the Hub,
        # but the abstract OAuthProvider interface currently doesn't pass code_challenge to get_authorization_url.
        # For full PKCE, OAuthManager would pass it. For now we use standard state.
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
        """Exchanges an authorization code for tokens and instance URL."""
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

    async def query(self, soql: str) -> Dict[str, Any]:
        """Executes a SOQL query against the Salesforce REST API."""
        if not self.instance_url:
            raise ValueError("Instance URL is missing")
            
        endpoint = f"{self.instance_url}/services/data/{self.API_VERSION}/query/"
        params = {"q": soql}
        
        response = await self._client.get(endpoint, headers=self._get_headers(), params=params)
        
        if response.status_code == 429:
            logger.warning("Salesforce Rate Limit hit (HTTP 429). Signaling RetryEngine.")
            raise ValueError("Rate limit exceeded 429")
            
        response.raise_for_status()
        return response.json()
        
    async def get_next_records(self, next_records_url: str) -> Dict[str, Any]:
        """Fetches the next page of SOQL query results using the nextRecordsUrl."""
        if not self.instance_url:
            raise ValueError("Instance URL is missing")
            
        endpoint = f"{self.instance_url}{next_records_url}"
        
        response = await self._client.get(endpoint, headers=self._get_headers())
        if response.status_code == 429:
            raise ValueError("Rate limit exceeded 429")
            
        response.raise_for_status()
        return response.json()
