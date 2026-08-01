from enum import Enum
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class ProviderAuthType(str, Enum):
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    BASIC = "basic"

class IntegrationState(str, Enum):
    PENDING = "pending"
    AUTHENTICATED = "authenticated"
    SYNCING = "syncing"
    ERROR = "error"
    DISCONNECTED = "disconnected"

class ProviderCapability(str, Enum):
    COMPANIES = "companies"
    CONTACTS = "contacts"
    OPPORTUNITIES = "opportunities"
    SIGNALS = "signals"
    WEBHOOKS = "webhooks"
    INCREMENTAL_SYNC = "incremental_sync"
    BIDIRECTIONAL_SYNC = "bidirectional_sync"

class IntegrationConnection(BaseModel):
    """
    Represents an active connection between a tenant and a provider.
    """
    id: UUID
    tenant_id: UUID
    provider_name: str
    state: IntegrationState = IntegrationState.PENDING
    
    # Auth specifics
    auth_type: ProviderAuthType
    credentials_id: UUID  # Reference to securely vaulted credentials
    
    # Sync specifics
    enabled_capabilities: List[ProviderCapability] = Field(default_factory=list)
    last_sync_at: Optional[datetime] = None
    next_sync_scheduled_at: Optional[datetime] = None
    
    # Health and Error Tracking
    error_count: int = 0
    last_error_message: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class SyncCursor(BaseModel):
    """
    Tracks sync pagination or timestamp boundaries for incremental syncs.
    """
    connection_id: UUID
    entity_type: str
    last_processed_timestamp: Optional[datetime] = None
    next_page_token: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class ProviderMetadata(BaseModel):
    """
    Static metadata describing a provider's identity and capabilities in the registry.
    """
    name: str
    display_name: str
    description: str
    supported_auth_types: List[ProviderAuthType]
    supported_capabilities: List[ProviderCapability]
    logo_url: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
