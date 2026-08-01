from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Dict
from datetime import datetime
from uuid import UUID, uuid4

class MarketTrend(BaseModel):
    name: str
    impact: str # positive, negative, neutral
    description: str

class MarketIntelligence(BaseModel):
    """
    Domain entity representing aggregated, proprietary intelligence about a company's market and industry.
    """
    id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    company_id: UUID  # Link to CompanyIntelligence
    company_domain: str
    industry: str
    
    # Core Data
    market_trends: List[MarketTrend] = Field(default_factory=list)
    macro_economic_indicators: List[str] = Field(default_factory=list)
    regulatory_changes: List[str] = Field(default_factory=list)
    
    # Provider Abstractions (Layer 3 reference metadata)
    provider_sources: Dict[str, str] = Field(default_factory=dict)
    
    # Audit & Status
    last_enriched_at: Optional[datetime] = None
    enrichment_status: str = "pending" # pending, enriched, failed
    
    # Proprietary AI derivations
    market_risk_score: Optional[float] = None
    opportunity_score: Optional[float] = None
    market_sentiment: str = "neutral" # bullish, bearish, neutral
    expansion_opportunities: List[str] = Field(default_factory=list)
    seasonal_buying_patterns: List[str] = Field(default_factory=list)
    strategic_market_recommendations: Optional[str] = None
    ai_summary: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
