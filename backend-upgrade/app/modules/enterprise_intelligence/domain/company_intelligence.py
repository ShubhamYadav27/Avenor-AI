from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4

class CompanyOverview(BaseModel):
    description: Optional[str] = None
    mission_statement: Optional[str] = None
    year_founded: Optional[int] = None
    employee_count: Optional[int] = None
    headquarters: Optional[str] = None

class CompanyFinancials(BaseModel):
    estimated_revenue: Optional[float] = None
    funding_total: Optional[float] = None
    last_funding_round: Optional[str] = None
    last_funding_date: Optional[datetime] = None
    is_public: bool = False
    stock_ticker: Optional[str] = None

class CompanySocialPresence(BaseModel):
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    github_url: Optional[str] = None
    follower_count: Optional[int] = None

class CompanyIntelligence(BaseModel):
    """
    Domain entity representing aggregated, proprietary intelligence about a company.
    """
    id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    company_domain: str
    
    # Layer 1: CRM Anchors
    crm_account_ids: List[str] = Field(default_factory=list)
    
    # Layer 2/3 Data
    overview: CompanyOverview = Field(default_factory=CompanyOverview)
    financials: CompanyFinancials = Field(default_factory=CompanyFinancials)
    social: CompanySocialPresence = Field(default_factory=CompanySocialPresence)
    
    # Provider Abstractions (Layer 3 reference metadata)
    provider_sources: Dict[str, str] = Field(default_factory=dict)
    
    # Audit & Status
    last_enriched_at: Optional[datetime] = None
    enrichment_status: str = "pending" # pending, enriched, failed
    
    # Proprietary AI derivations
    ai_summary: Optional[str] = None
    buying_intent_score: Optional[float] = None
    
    model_config = ConfigDict(from_attributes=True)
