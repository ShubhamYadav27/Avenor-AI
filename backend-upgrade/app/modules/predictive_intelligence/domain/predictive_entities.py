"""
Predictive Entities (Phase 6.1)
Pure domain entities representing revenue features, buying windows, opportunity predictions, and recommendations.
"""
from dataclasses import dataclass, field
from typing import List, Optional
import uuid

from app.modules.predictive_intelligence.domain.predictive_value_objects import BuyingWindowStage, RiskLevel


@dataclass
class RevenueFeature:
    feature_name: str
    value: float
    weight: float = 1.0
    source: str = "signal_engine"
    freshness_score: float = 1.0


@dataclass
class BuyingWindow:
    company_id: str
    stage: BuyingWindowStage = BuyingWindowStage.ACTIVE_WINDOW
    confidence_score: float = 0.92
    intent_surge_score: float = 94.0
    hiring_signal_count: int = 14
    funding_signal_count: int = 2
    estimated_window_days: int = 45


@dataclass
class OpportunityPrediction:
    deal_id: str
    company_id: str
    win_probability: float = 0.85
    risk_level: RiskLevel = RiskLevel.LOW
    risk_factors: List[str] = field(default_factory=list)
    expected_arr_usd: float = 180000.0


@dataclass
class RevenueRecommendation:
    recommendation_id: str = field(default_factory=lambda: f"rec-{uuid.uuid4().hex[:8]}")
    action_type: str = "OUTREACH"
    title: str = ""
    description: str = ""
    priority_score: float = 95.0
    evidence_citations: List[str] = field(default_factory=list)


@dataclass
class AccountIntelligence:
    company_id: str
    company_name: str
    icp_score: float = 92.0
    buying_window: Optional[BuyingWindow] = None
    opportunity_prediction: Optional[OpportunityPrediction] = None
    recommendations: List[RevenueRecommendation] = field(default_factory=list)


@dataclass
class PredictionPackage:
    workspace_id: uuid.UUID
    account_intelligence_list: List[AccountIntelligence] = field(default_factory=list)
    overall_pipeline_health_score: float = 88.0
    execution_time_ms: float = 0.0
