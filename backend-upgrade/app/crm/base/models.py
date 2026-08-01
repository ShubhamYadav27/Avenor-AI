"""
app/crm/base/models.py

Canonical CRM domain models (Pydantic).

These are the ONLY CRM data structures that business logic should ever see.
Provider-specific field names (e.g. "dealstage", "StageName", "statuscode") must
be mapped to these models INSIDE provider adapters.

Mapping examples:
  HubSpot Deal         -> CRMOpportunity
  Salesforce Opportunity -> CRMOpportunity
  Dynamics Opportunity -> CRMOpportunity
  Zoho Deal            -> CRMOpportunity

  HubSpot Company      -> CRMAccount
  Salesforce Account   -> CRMAccount
  Dynamics Account     -> CRMAccount
  Zoho Account         -> CRMAccount
"""
from __future__ import annotations

import enum
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# ── Enums ─────────────────────────────────────────────────────────────────────

class SyncStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class CRMObjectType(str, enum.Enum):
    ACCOUNT = "account"
    CONTACT = "contact"
    LEAD = "lead"
    OPPORTUNITY = "opportunity"
    USER = "user"


class CRMEventType(str, enum.Enum):
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    STAGE_CHANGED = "stage_changed"
    WON = "won"
    LOST = "lost"
    ASSIGNED = "assigned"


# ── Provider Capabilities ─────────────────────────────────────────────────────

class ProviderCapabilities(BaseModel):
    """
    Declares what features a provider supports.
    The sync engine reads this to skip unsupported operations gracefully.
    """
    # Object sync support
    supports_accounts: bool = True
    supports_contacts: bool = True
    supports_leads: bool = False      # HubSpot has no native leads
    supports_opportunities: bool = True
    supports_users: bool = True

    # Sync capabilities
    supports_incremental_sync: bool = True
    supports_historical_sync: bool = True
    supports_bulk_api: bool = False    # Salesforce Bulk API 2.0

    # Webhook capabilities
    supports_webhooks: bool = True
    supports_webhook_signature_verification: bool = True
    webhook_event_types: list[str] = Field(default_factory=list)

    # OAuth capabilities
    supports_token_refresh: bool = True
    supports_token_revocation: bool = False
    requires_pkce: bool = False

    # Field capabilities
    supports_custom_fields: bool = True
    supports_pipeline_stages: bool = True


# ── OAuth models ───────────────────────────────────────────────────────────────

class OAuthURLResult(BaseModel):
    """Result of get_oauth_url()."""
    auth_url: str
    state: str
    redirect_uri: str
    pkce_verifier: str | None = None  # Only for PKCE flows


class OAuthCallbackResult(BaseModel):
    """Result of handle_oauth_callback()."""
    provider: str
    external_account_id: str           # org ID, hub ID, tenant ID
    external_account_name: str | None = None
    access_token: str                  # will be encrypted before DB write
    refresh_token: str                 # will be encrypted before DB write
    token_expires_in: int = 3600
    scopes: list[str] = Field(default_factory=list)
    provider_metadata: dict[str, Any] = Field(default_factory=dict)


# ── Canonical CRM objects ─────────────────────────────────────────────────────

class CRMAccount(BaseModel):
    """
    Generic CRM Account.
    Maps to: HubSpot Company, Salesforce Account, Dynamics Account, Zoho Account.
    """
    external_id: str                   # Provider-native ID (e.g. HS company ID)
    provider: str                      # "hubspot", "salesforce", etc.
    name: str
    domain: str | None = None
    website: str | None = None
    industry: str | None = None
    employee_count: int | None = None
    location_city: str | None = None
    location_state: str | None = None
    location_country: str | None = None
    founded_year: int | None = None
    description: str | None = None
    annual_revenue: float | None = None
    phone: str | None = None
    linkedin_url: str | None = None
    created_at: datetime | None = None
    modified_at: datetime | None = None
    raw_data: dict[str, Any] = Field(default_factory=dict)


class CRMContact(BaseModel):
    """
    Generic CRM Contact.
    Maps to: HubSpot Contact, Salesforce Contact, Dynamics Contact, Zoho Contact.
    """
    external_id: str
    provider: str
    first_name: str | None = None
    last_name: str | None = None
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    title: str | None = None
    department: str | None = None
    seniority: str | None = None
    linkedin_url: str | None = None
    account_external_id: str | None = None  # Link to CRMAccount
    owner_external_id: str | None = None
    created_at: datetime | None = None
    modified_at: datetime | None = None
    raw_data: dict[str, Any] = Field(default_factory=dict)


class CRMLead(BaseModel):
    """
    Generic CRM Lead.
    Maps to: Salesforce Lead, Dynamics Lead, Zoho Lead.
    HubSpot has no native Lead — providers should return empty generator for sync_leads().
    """
    external_id: str
    provider: str
    first_name: str | None = None
    last_name: str | None = None
    full_name: str | None = None
    email: str | None = None
    company_name: str | None = None
    title: str | None = None
    phone: str | None = None
    status: str | None = None
    source: str | None = None
    owner_external_id: str | None = None
    converted: bool = False
    converted_account_id: str | None = None
    converted_contact_id: str | None = None
    converted_opportunity_id: str | None = None
    created_at: datetime | None = None
    modified_at: datetime | None = None
    raw_data: dict[str, Any] = Field(default_factory=dict)


class CRMOpportunity(BaseModel):
    """
    Generic CRM Opportunity.
    Maps to:
      HubSpot Deal          -> dealstage, amount, closedate
      Salesforce Opportunity -> StageName, Amount, CloseDate
      Dynamics Opportunity   -> statuscode, estimatedvalue, estimatedclosedate
      Zoho Deal              -> Stage, Amount, Closing_Date
    """
    external_id: str
    provider: str
    name: str | None = None
    stage: str | None = None           # Normalized stage name
    pipeline: str | None = None
    amount_usd: float | None = None
    probability: float | None = None   # 0.0 - 1.0
    close_date: datetime | None = None
    is_closed_won: bool = False
    is_closed_lost: bool = False
    closed_at: datetime | None = None
    account_external_id: str | None = None
    contact_external_ids: list[str] = Field(default_factory=list)
    owner_external_id: str | None = None
    created_at: datetime | None = None
    modified_at: datetime | None = None
    raw_data: dict[str, Any] = Field(default_factory=dict)


class CRMUser(BaseModel):
    """
    Generic CRM User / Owner.
    Maps to: HubSpot Owner, Salesforce User, Dynamics SystemUser, Zoho User.
    """
    external_id: str
    provider: str
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    full_name: str | None = None
    is_active: bool = True
    role: str | None = None
    raw_data: dict[str, Any] = Field(default_factory=dict)


# ── Connection & Sync state ───────────────────────────────────────────────────

class CRMConnectionState(BaseModel):
    """Current state of a CRM connection (returned by get_status())."""
    provider: str
    is_active: bool
    external_account_id: str | None = None
    external_account_name: str | None = None
    last_sync_at: datetime | None = None
    sync_error: str | None = None
    token_expires_at: datetime | None = None


class SyncStats(BaseModel):
    """Statistics for one object type in a sync run."""
    object_type: str
    fetched: int = 0
    created: int = 0
    updated: int = 0
    skipped: int = 0
    failed: int = 0
    api_requests: int = 0
    duration_seconds: float = 0.0


class SyncResult(BaseModel):
    """Result of a complete sync run (historical or incremental)."""
    provider: str
    workspace_id: str
    sync_type: str                     # "historical" or "incremental"
    status: SyncStatus = SyncStatus.COMPLETED
    started_at: datetime
    completed_at: datetime | None = None
    stats: list[SyncStats] = Field(default_factory=list)
    error: str | None = None

    @property
    def total_fetched(self) -> int:
        return sum(s.fetched for s in self.stats)

    @property
    def total_created(self) -> int:
        return sum(s.created for s in self.stats)

    @property
    def total_updated(self) -> int:
        return sum(s.updated for s in self.stats)

    @property
    def total_failed(self) -> int:
        return sum(s.failed for s in self.stats)


# ── Webhook / Events ──────────────────────────────────────────────────────────

class CRMEvent(BaseModel):
    """
    Generic CRM event produced by handle_webhook().
    The sync engine processes these events to trigger targeted re-syncs.
    """
    provider: str
    event_type: CRMEventType
    object_type: CRMObjectType
    external_id: str
    workspace_id: str | None = None    # Set by webhook dispatcher after matching
    payload: dict[str, Any] = Field(default_factory=dict)
    occurred_at: datetime | None = None
    raw_payload: dict[str, Any] = Field(default_factory=dict)
