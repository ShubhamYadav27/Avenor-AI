from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Dict
from datetime import datetime
from uuid import UUID, uuid4

class Investor(BaseModel):
    name: str
    is_lead: bool = False
    portfolio_size: Optional[int] = None
    focus_areas: List[str] = Field(default_factory=list)

class FundingRound(BaseModel):
    round_type: str  # Seed, Series A, Series B, Growth, IPO, Debt
    amount_raised: Optional[float] = None
    valuation: Optional[float] = None
    date_announced: datetime
    investors: List[Investor] = Field(default_factory=list)

class FundingIntelligence(BaseModel):
    """
    Domain entity representing aggregated, proprietary intelligence about a company's funding history.
    """
    id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    company_id: UUID  # Link to CompanyIntelligence
    company_domain: str
    
    # Core Data
    total_funding: float = 0.0
    funding_rounds: List[FundingRound] = Field(default_factory=list)
    last_funding_date: Optional[datetime] = None
    
    # Provider Abstractions (Layer 3 reference metadata)
    provider_sources: Dict[str, str] = Field(default_factory=dict)
    
    # Audit & Status
    last_enriched_at: Optional[datetime] = None
    enrichment_status: str = "pending" # pending, enriched, failed
    
    # Proprietary AI derivations
    capital_growth_trend: Optional[str] = None # accelerating, stable, slowing
    revenue_expansion_probability: Optional[float] = None
    hiring_probability: Optional[float] = None
    technology_investment_probability: Optional[float] = None
    sales_readiness_score: Optional[float] = None
    buying_window_impact: Optional[str] = None # high, medium, low
    funding_risk_assessment: Optional[str] = None
    growth_opportunity_detection: Optional[str] = None
    ai_summary: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
