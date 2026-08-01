from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Dict
from datetime import datetime
from uuid import UUID, uuid4

class Competitor(BaseModel):
    name: str
    domain: str
    is_direct: bool = True
    market_position: str = "established" # leader, challenger, visionary, niche, emerging
    key_differentiators: List[str] = Field(default_factory=list)
    recent_launches: List[str] = Field(default_factory=list)

class CompetitiveIntelligence(BaseModel):
    """
    Domain entity representing aggregated, proprietary intelligence about a company's competitive landscape.
    """
    id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    company_id: UUID  # Link to CompanyIntelligence
    company_domain: str
    
    # Core Data
    competitors: List[Competitor] = Field(default_factory=list)
    
    # Provider Abstractions (Layer 3 reference metadata)
    provider_sources: Dict[str, str] = Field(default_factory=dict)
    
    # Audit & Status
    last_enriched_at: Optional[datetime] = None
    enrichment_status: str = "pending" # pending, enriched, failed
    
    # Proprietary AI derivations
    competitive_risk_score: Optional[float] = None
    displacement_opportunities: List[str] = Field(default_factory=list)
    feature_gaps: List[str] = Field(default_factory=list)
    recommended_positioning: Optional[str] = None
    strategic_opportunity_detection: Optional[str] = None
    ai_summary: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
