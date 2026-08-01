from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Dict
from datetime import datetime
from uuid import UUID, uuid4

class JobPosting(BaseModel):
    title: str
    department: str  # Engineering, Sales, Marketing, Customer Success, RevOps, AI/ML, Security, Leadership
    location: str
    is_remote: bool = False
    is_leadership: bool = False
    date_posted: datetime

class HiringIntelligence(BaseModel):
    """
    Domain entity representing aggregated, proprietary intelligence about a company's hiring trends.
    """
    id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    company_id: UUID  # Link to CompanyIntelligence
    company_domain: str
    
    # Core Data
    open_roles: List[JobPosting] = Field(default_factory=list)
    total_open_roles: int = 0
    department_counts: Dict[str, int] = Field(default_factory=dict)
    
    # Provider Abstractions (Layer 3 reference metadata)
    provider_sources: Dict[str, str] = Field(default_factory=dict)
    
    # Audit & Status
    last_enriched_at: Optional[datetime] = None
    enrichment_status: str = "pending" # pending, enriched, failed
    
    # Proprietary AI derivations
    hiring_velocity: Optional[str] = None # accelerating, stable, slowing, frozen
    hiring_growth_trend: Optional[str] = None
    organizational_expansion_score: Optional[float] = None
    hiring_momentum_score: Optional[float] = None
    buying_window_impact: Optional[str] = None # high, medium, low
    
    # Signals
    technology_adoption_indicators: List[str] = Field(default_factory=list)
    revenue_expansion_indicators: List[str] = Field(default_factory=list)
    geographic_expansion: List[str] = Field(default_factory=list)
    
    # Summaries
    ai_summary: Optional[str] = None
    hiring_risk_analysis: Optional[str] = None
    growth_opportunity_detection: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
