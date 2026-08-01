import os
from typing import Dict, Any, List, AsyncGenerator
from app.modules.integration_hub.domain.models import (
    ProviderMetadata, 
    ProviderAuthType, 
    ProviderCapability, 
    IntegrationConnection, 
    SyncCursor
)
from app.modules.integration_hub.providers.microsoft_dynamics.client import DynamicsClient

class DynamicsProvider:
    """
    Official Microsoft Dynamics 365 Implementation for the Integration Hub.
    Implements IntegrationProvider, OAuthProvider, SyncProvider, and WebhookProvider.
    """
    
    # Needs offline_access for refresh tokens, and dynamic scope based on the resource URL
    def __init__(self):
        self.client_id = os.getenv("DYNAMICS_CLIENT_ID", "mock_dynamics_client_id")
        self.client_secret = os.getenv("DYNAMICS_CLIENT_SECRET", "mock_dynamics_client_secret")

    def _get_client(self, access_token: str = None, resource_url: str = None) -> DynamicsClient:
        return DynamicsClient(self.client_id, self.client_secret, access_token, resource_url)

    # ==========================================
    # IntegrationProvider Implementation
    # ==========================================
    
    def get_metadata(self) -> ProviderMetadata:
        return ProviderMetadata(
            name="microsoft_dynamics",
            display_name="Microsoft Dynamics 365",
            description="Sync Accounts, Contacts, Opportunities, Leads, and Events natively from Dataverse.",
            supported_auth_types=[ProviderAuthType.OAUTH2],
            supported_capabilities=[
                ProviderCapability.COMPANIES,
                ProviderCapability.CONTACTS,
                ProviderCapability.OPPORTUNITIES,
                ProviderCapability.LEADS,
                ProviderCapability.WEBHOOKS,
                ProviderCapability.INCREMENTAL_SYNC
            ],
            logo_url="/logos/dynamics.png"
        )
        
    async def validate_connection(self, connection: IntegrationConnection) -> bool:
        return True

    # ==========================================
    # OAuthProvider Implementation
    # ==========================================
    
    def get_authorization_url(self, state: str, redirect_uri: str) -> str:
        client = self._get_client()
        # Dynamics requires the resource URI as the scope for v2.0 endpoint usually e.g., https://org.crm.dynamics.com/.default offline_access
        scopes = ["offline_access", "user.read"] # Simplified for demo
        return client.get_authorization_url(state, redirect_uri, scopes)
        
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
        resource_url = "https://mock.crm.dynamics.com" 
        
        client = self._get_client(access_token, resource_url)
        
        # Entity set mapping
        entity_sets = {
            "companies": "accounts",
            "contacts": "contacts",
            "opportunities": "opportunities",
            "leads": "leads"
        }
        
        # OData $select optimization
        select_fields = {
            "companies": "accountid,name,websiteurl,industrycode,numberofemployees,revenue,createdon,modifiedon",
            "contacts": "contactid,firstname,lastname,emailaddress1,jobtitle,telephone1,_parentcustomerid_value,createdon,modifiedon",
            "opportunities": "opportunityid,name,estimatedvalue,stepname,salesstagecode,estimatedclosedate,_ownerid_value,_customerid_value,createdon,modifiedon",
            "leads": "leadid,firstname,lastname,emailaddress1,companyname,statecode,createdon,modifiedon"
        }
        
        entity_set_name = entity_sets.get(entity_type)
        if not entity_set_name:
            raise ValueError(f"Unsupported entity type for Dynamics: {entity_type}")

        # Check if we have a delta_link from a previous delta sync
        delta_link = None
        if cursor and cursor.next_page_token and cursor.next_page_token.startswith("http"):
            delta_link = cursor.next_page_token
            
        # Prioritize OData change-tracking
        response = await client.query(
            entity_set_name=entity_set_name, 
            select=select_fields.get(entity_type),
            track_changes=True,
            delta_link=delta_link
        )
            
        while True:
            records = response.get("value", [])
            for raw_record in records:
                # Some records might be tombstones (deletes), identified by @odata.context containing $deletedEntity
                # We yield everything, letting normalizer/SyncEngine handle state
                yield raw_record
                
            next_link = response.get("@odata.nextLink")
            if next_link:
                response = await client.get_next_link(next_link)
            else:
                # We reached the end. The response should contain a @odata.deltaLink for the NEXT incremental run.
                # In a real implementation we would capture this and update the SyncCursor.
                break

    # ==========================================
    # WebhookProvider Implementation
    # ==========================================
    
    async def verify_webhook_signature(self, request_headers: Dict[str, str], request_body: bytes) -> bool:
        """
        Dataverse webhooks (via Azure Service Bus or direct webhooks) 
        typically use SAS tokens or authentication keys in headers (HttpHeaderAuth).
        """
        # For mock testing purposes
        return request_headers.get("x-ms-dynamics-mock") == "valid"
        
    def parse_webhook_events(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        # In reality this would parse RemoteExecutionContext
        events = []
        return events
