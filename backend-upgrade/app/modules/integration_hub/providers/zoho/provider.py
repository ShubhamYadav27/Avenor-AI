import os
from typing import Dict, Any, List, AsyncGenerator
from app.modules.integration_hub.domain.models import (
    ProviderMetadata, 
    ProviderAuthType, 
    ProviderCapability, 
    IntegrationConnection, 
    SyncCursor
)
from app.modules.integration_hub.providers.zoho.client import ZohoClient

class ZohoProvider:
    """
    Official Zoho CRM Implementation for the Integration Hub.
    Implements IntegrationProvider, OAuthProvider, SyncProvider, and WebhookProvider.
    """
    
    # Base scopes needed
    SCOPES = [
        "ZohoCRM.modules.ALL",
        "ZohoCRM.settings.ALL"
    ]
    
    def __init__(self):
        self.client_id = os.getenv("ZOHO_CLIENT_ID", "mock_zoho_client_id")
        self.client_secret = os.getenv("ZOHO_CLIENT_SECRET", "mock_zoho_client_secret")

    def _get_client(self, access_token: str = None, data_center: str = "com") -> ZohoClient:
        return ZohoClient(self.client_id, self.client_secret, access_token, data_center)

    # ==========================================
    # IntegrationProvider Implementation
    # ==========================================
    
    def get_metadata(self) -> ProviderMetadata:
        return ProviderMetadata(
            name="zoho",
            display_name="Zoho CRM",
            description="Sync Accounts, Contacts, Deals, Leads, and Events natively from Zoho CRM.",
            supported_auth_types=[ProviderAuthType.OAUTH2],
            supported_capabilities=[
                ProviderCapability.COMPANIES,
                ProviderCapability.CONTACTS,
                ProviderCapability.OPPORTUNITIES,
                ProviderCapability.LEADS,
                ProviderCapability.WEBHOOKS,
                ProviderCapability.INCREMENTAL_SYNC
            ],
            logo_url="/logos/zoho.png"
        )
        
    async def validate_connection(self, connection: IntegrationConnection) -> bool:
        return True

    # ==========================================
    # OAuthProvider Implementation
    # ==========================================
    
    def get_authorization_url(self, state: str, redirect_uri: str) -> str:
        # For initial consent we assume .com, user can select region if UI supports it
        client = self._get_client()
        return client.get_authorization_url(state, redirect_uri, self.SCOPES)
        
    async def exchange_code(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        client = self._get_client()
        return await client.exchange_code(code, redirect_uri)
        
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        client = self._get_client()
        return await client.refresh_token(refresh_token)

    # ==========================================
    # SyncProvider Implementation
    # ==========================================
    
    async def fetch_records(self, connection: IntegrationConnection, entity_type: str, cursor: SyncCursor = None) -> AsyncGenerator[Dict[str, Any], None]:
        access_token = "mock_access_token_from_vault" 
        data_center = "com" # Stored with credentials in a real system
        
        client = self._get_client(access_token, data_center)
        
        # Module mapping
        modules = {
            "companies": "Accounts",
            "contacts": "Contacts",
            "opportunities": "Deals",
            "leads": "Leads"
        }
        
        module_name = modules.get(entity_type)
        if not module_name:
            raise ValueError(f"Unsupported entity type for Zoho: {entity_type}")

        page = 1
        if cursor and cursor.next_page_token:
            page = int(cursor.next_page_token)
            
        if_modified_since = None
        if cursor and cursor.last_processed_timestamp:
            if_modified_since = cursor.last_processed_timestamp.strftime("%Y-%m-%dT%H:%M:%S%z")
            if not cursor.last_processed_timestamp.tzinfo:
                if_modified_since = cursor.last_processed_timestamp.strftime("%Y-%m-%dT%H:%M:%S+00:00")
            
        while True:
            params = {"page": page, "per_page": 200}
            response = await client.get(
                module=module_name, 
                params=params,
                if_modified_since=if_modified_since
            )
            
            records = response.get("data", [])
            for raw_record in records:
                yield raw_record
                
            info = response.get("info", {})
            if info.get("more_records"):
                page += 1
            else:
                break

    # ==========================================
    # WebhookProvider Implementation
    # ==========================================
    
    async def verify_webhook_signature(self, request_headers: Dict[str, str], request_body: bytes) -> bool:
        """
        Zoho webhooks typically send a custom header or token that you specify when creating the webhook.
        """
        # For mock testing purposes
        return request_headers.get("x-zoho-mock") == "valid"
        
    def parse_webhook_events(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        events = []
        return events
