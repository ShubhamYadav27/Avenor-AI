from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Dict
from datetime import datetime
from uuid import UUID, uuid4

class TechnologyItem(BaseModel):
    name: str
    category: str  # e.g., CRM, Framework, Cloud Provider
    first_detected_at: Optional[datetime] = None
    last_detected_at: Optional[datetime] = None
    confidence_score: float = 1.0

class TechnologyStack(BaseModel):
    languages: List[TechnologyItem] = Field(default_factory=list)
    frameworks: List[TechnologyItem] = Field(default_factory=list)
    cloud_providers: List[TechnologyItem] = Field(default_factory=list)
    infrastructure: List[TechnologyItem] = Field(default_factory=list)
    devops: List[TechnologyItem] = Field(default_factory=list)
    crm: List[TechnologyItem] = Field(default_factory=list)
    marketing: List[TechnologyItem] = Field(default_factory=list)
    security: List[TechnologyItem] = Field(default_factory=list)
    analytics: List[TechnologyItem] = Field(default_factory=list)
    ai_ml: List[TechnologyItem] = Field(default_factory=list)
    data_platforms: List[TechnologyItem] = Field(default_factory=list)
    productivity: List[TechnologyItem] = Field(default_factory=list)
    collaboration: List[TechnologyItem] = Field(default_factory=list)

class TechnologyIntelligence(BaseModel):
    """
    Domain entity representing aggregated, proprietary intelligence about a company's technology landscape.
    """
    id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    company_id: UUID  # Link to CompanyIntelligence
    company_domain: str
    
    # Core Data
    stack: TechnologyStack = Field(default_factory=TechnologyStack)
    
    # Provider Abstractions (Layer 3 reference metadata)
    provider_sources: Dict[str, str] = Field(default_factory=dict)
    
    # Audit & Status
    last_enriched_at: Optional[datetime] = None
    enrichment_status: str = "pending" # pending, enriched, failed
    
    # Proprietary AI derivations
    maturity_score: Optional[float] = None
    fit_score: Optional[float] = None
    ai_summary: Optional[str] = None
    risk_analysis: Optional[str] = None
    opportunity_detection: Optional[str] = None
    competitive_comparison: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
