from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Dict
from datetime import datetime
from uuid import UUID, uuid4

class ExecutiveProfile(BaseModel):
    contact_id: UUID  # Link to ContactIntelligence
    title: str
    role_classification: str # CEO, CFO, CTO, CMO, CRO, COO, VPE, Other
    reports_to_contact_id: Optional[UUID] = None
    influence_score: float = 0.0
    decision_authority: str = "medium" # high, medium, low
    tenure_months: Optional[int] = None
    recent_activity: List[str] = Field(default_factory=list) # press releases, blog posts, etc.
    strategic_priorities: List[str] = Field(default_factory=list)

class ExecutiveIntelligence(BaseModel):
    """
    Domain entity representing aggregated, proprietary intelligence about a company's executive leadership.
    """
    id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    company_id: UUID  # Link to CompanyIntelligence
    company_domain: str
    
    # Core Data
    executives: List[ExecutiveProfile] = Field(default_factory=list)
    recent_leadership_changes: List[str] = Field(default_factory=list)
    
    # Provider Abstractions (Layer 3 reference metadata)
    provider_sources: Dict[str, str] = Field(default_factory=dict)
    
    # Audit & Status
    last_enriched_at: Optional[datetime] = None
    enrichment_status: str = "pending" # pending, enriched, failed
    
    # Proprietary AI derivations
    executive_buying_influence_score: Optional[float] = None
    overall_strategic_priorities: List[str] = Field(default_factory=list)
    executive_risk_analysis: Optional[str] = None
    strategic_opportunity_detection: Optional[str] = None
    recommended_engagement_strategy: Optional[str] = None
    ai_summary: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
