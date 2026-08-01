from pydantic import BaseModel, ConfigDict, Field, EmailStr
from typing import List, Optional, Dict
from datetime import datetime
from uuid import UUID, uuid4

class ContactProfile(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    job_title: Optional[str] = None
    seniority: Optional[str] = None  # C-Level, VP, Director, IC
    department: Optional[str] = None
    location: Optional[str] = None

class ContactCommunication(BaseModel):
    email: Optional[EmailStr] = None
    phone_numbers: List[str] = Field(default_factory=list)
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None

class ContactRelationshipSignals(BaseModel):
    last_contacted_date: Optional[datetime] = None
    communication_frequency: Optional[str] = None # high, medium, low
    sentiment_score: Optional[float] = None
    known_colleagues: List[UUID] = Field(default_factory=list)

class ContactIntelligence(BaseModel):
    """
    Domain entity representing aggregated, proprietary intelligence about an individual contact.
    """
    id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    company_id: Optional[UUID] = None  # Link to CompanyIntelligence
    
    # Layer 1: CRM Anchors
    crm_contact_ids: List[str] = Field(default_factory=list)
    
    # Layer 2/3 Data
    profile: ContactProfile = Field(default_factory=ContactProfile)
    communication: ContactCommunication = Field(default_factory=ContactCommunication)
    relationships: ContactRelationshipSignals = Field(default_factory=ContactRelationshipSignals)
    
    # Provider Abstractions (Layer 3 reference metadata)
    provider_sources: Dict[str, str] = Field(default_factory=dict)
    
    # Audit & Status
    last_enriched_at: Optional[datetime] = None
    enrichment_status: str = "pending" # pending, enriched, failed
    
    # Proprietary AI derivations
    influence_score: Optional[float] = None
    ai_summary: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
