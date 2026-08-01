from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from uuid import UUID, uuid4

class NormalizedSignal(BaseModel):
    """
    Represents a single, atomic, normalized signal flowing into the system.
    """
    id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    source_type: str # e.g., CRM, external_provider, web
    signal_type: str # e.g., buying, risk, growth, competitive, executive, hiring, funding, technology, market, industry
    signal_name: str
    description: str
    
    # Context
    company_id: Optional[UUID] = None
    company_domain: Optional[str] = None
    contact_id: Optional[UUID] = None
    
    # Metadata & Payload
    raw_payload: Dict[str, Any] = Field(default_factory=dict)
    
    # Provenance & Lifecycle
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    is_active: bool = True
    
    # Scoring
    confidence_score: float = 1.0
    reliability_score: float = 1.0
    impact_score: float = 1.0
    
    model_config = ConfigDict(from_attributes=True)

class SignalIntelligence(BaseModel):
    """
    Domain entity representing aggregated, correlated signal intelligence for a target entity.
    """
    id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    company_id: UUID
    company_domain: str
    
    # Normalized signals collected for this entity
    active_signals: List[NormalizedSignal] = Field(default_factory=list)
    historical_signals: List[NormalizedSignal] = Field(default_factory=list)
    
    # Correlated events grouped by AI
    correlated_events: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Audit & Status
    last_processed_at: Optional[datetime] = None
    processing_status: str = "pending" # pending, processed, failed
    
    # Proprietary AI derivations
    composite_buying_window_score: float = 0.0
    risk_indicator_score: float = 0.0
    growth_indicator_score: float = 0.0
    ai_generated_summary: Optional[str] = None
    ai_explanations: List[str] = Field(default_factory=list)
    strategic_prioritization_tier: int = 3 # 1 (Highest), 2, 3 (Lowest)
    
    model_config = ConfigDict(from_attributes=True)
