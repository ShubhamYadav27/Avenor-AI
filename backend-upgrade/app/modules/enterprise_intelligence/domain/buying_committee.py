from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Dict
from datetime import datetime
from uuid import UUID, uuid4

class CommitteeMemberRole(BaseModel):
    is_decision_maker: bool = False
    is_economic_buyer: bool = False
    is_technical_buyer: bool = False
    is_champion: bool = False
    is_influencer: bool = False
    is_blocker: bool = False
    is_procurement: bool = False
    is_legal: bool = False
    is_executive_sponsor: bool = False

class CommitteeMember(BaseModel):
    contact_id: UUID  # Link to ContactIntelligence
    roles: CommitteeMemberRole = Field(default_factory=CommitteeMemberRole)
    reports_to_contact_id: Optional[UUID] = None
    influence_score: float = 0.0
    decision_power: float = 0.0
    relationship_strength: float = 0.0
    engagement_level: str = "low" # high, medium, low, none
    notes: Optional[str] = None

class BuyingCommitteeIntelligence(BaseModel):
    """
    Domain entity representing aggregated, proprietary intelligence about a company's buying committee.
    """
    id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    company_id: UUID  # Link to CompanyIntelligence
    
    members: List[CommitteeMember] = Field(default_factory=list)
    
    # Audit & Status
    last_enriched_at: Optional[datetime] = None
    enrichment_status: str = "pending" # pending, enriched, failed
    
    # Proprietary AI derivations
    committee_completeness_score: Optional[float] = None
    multi_threading_score: Optional[float] = None
    buying_risk_analysis: Optional[str] = None
    missing_stakeholders: List[str] = Field(default_factory=list)
    next_contact_recommendation: Optional[UUID] = None
    ai_summary: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
