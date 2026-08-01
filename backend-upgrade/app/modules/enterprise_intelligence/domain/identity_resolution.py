from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from uuid import UUID, uuid4

class EntityAlias(BaseModel):
    alias: str
    source: str
    confidence: float

class MergeCandidate(BaseModel):
    target_id: UUID
    confidence_score: float
    reason: str

class CanonicalEntity(BaseModel):
    """
    Base Canonical Identity representing the universal source of truth for an entity.
    """
    id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    entity_type: str # company, contact, executive, technology, account
    primary_identifier: str # domain for company, email for contact
    canonical_name: str
    
    aliases: List[EntityAlias] = Field(default_factory=list)
    merged_ids: List[UUID] = Field(default_factory=list)
    merge_candidates: List[MergeCandidate] = Field(default_factory=list)
    
    # Audit & Lifecycle
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True
    
    # AI Metadata
    resolution_confidence: float = 1.0
    ai_generated_explanation: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class CompanyIdentity(CanonicalEntity):
    entity_type: str = "company"
    domains: List[str] = Field(default_factory=list)
    parent_company_id: Optional[UUID] = None
    subsidiary_ids: List[UUID] = Field(default_factory=list)
    historical_names: List[str] = Field(default_factory=list)

class ContactIdentity(CanonicalEntity):
    entity_type: str = "contact"
    emails: List[str] = Field(default_factory=list)
    company_id: Optional[UUID] = None
    social_profiles: Dict[str, str] = Field(default_factory=dict)
