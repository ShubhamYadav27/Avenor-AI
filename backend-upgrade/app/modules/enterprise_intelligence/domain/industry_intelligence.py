from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Dict
from datetime import datetime
from uuid import UUID, uuid4

class IndustryKPI(BaseModel):
    name: str
    benchmark_value: str
    description: str

class IndustryIntelligence(BaseModel):
    """
    Domain entity representing aggregated, proprietary intelligence about a specific industry.
    """
    id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    industry_name: str # e.g., SaaS, FinTech, Healthcare
    
    # Core Data
    lifecycle_stage: str = "mature" # emerging, growth, mature, declining
    market_size_estimate: str = "Unknown"
    growth_rate: str = "Unknown"
    average_sales_cycle_days: int = 90
    average_deal_size: str = "Unknown"
    
    kpis: List[IndustryKPI] = Field(default_factory=list)
    regulatory_environment: str = "medium" # high, medium, low
    key_challenges: List[str] = Field(default_factory=list)
    key_opportunities: List[str] = Field(default_factory=list)
    
    # Provider Abstractions (Layer 3 reference metadata)
    provider_sources: Dict[str, str] = Field(default_factory=dict)
    
    # Audit & Status
    last_enriched_at: Optional[datetime] = None
    enrichment_status: str = "pending" # pending, enriched, failed
    
    # Proprietary AI derivations
    industry_maturity_score: Optional[float] = None
    digital_transformation_score: Optional[float] = None
    opportunity_score: Optional[float] = None
    risk_score: Optional[float] = None
    readiness_score: Optional[float] = None
    buying_patterns: List[str] = Field(default_factory=list)
    best_practices: List[str] = Field(default_factory=list)
    strategic_recommendations: Optional[str] = None
    ai_summary: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
