"""
Strategic Intelligence Entities (Phase 6.5 & 6.6)
Pure domain entities representing strategic plans, executive briefings, forecasts, risks, opportunities, scenarios, and autonomous org packages.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional
import uuid

from app.modules.strategic_intelligence.domain.strategic_value_objects import ExecutiveRole, RiskCategory, ScenarioType, SystemOperatingState


@dataclass
class StrategicPlan:
    plan_id: str = field(default_factory=lambda: f"splan-{uuid.uuid4().hex[:8]}")
    workspace_id: uuid.UUID = field(default_factory=uuid.uuid4)
    title: str = "FY2026 Executive Revenue Strategy"
    fiscal_year: str = "FY2026"
    target_arr_usd: float = 14400000.0  # Equivalent to ₹120 Cr ARR target
    current_arr_usd: float = 8500000.0
    status: str = "ACTIVE"


@dataclass
class StrategicObjective:
    objective_id: str = field(default_factory=lambda: f"obj-{uuid.uuid4().hex[:8]}")
    title: str = "Achieve $14.4M ARR without Headcount Increase"
    metric: str = "ARR_USD"
    target_value: float = 14400000.0
    current_value: float = 8500000.0
    target_quarter: str = "Q4"


@dataclass
class StrategicInitiative:
    initiative_id: str = field(default_factory=lambda: f"init-{uuid.uuid4().hex[:8]}")
    name: str = "Enterprise Account Expansion & Win Rate Optimization"
    owner_role: ExecutiveRole = ExecutiveRole.VP_SALES
    estimated_impact_usd: float = 2500000.0
    status: str = "IN_PROGRESS"


@dataclass
class ExecutiveBriefing:
    briefing_id: str = field(default_factory=lambda: f"brief-{uuid.uuid4().hex[:8]}")
    title: str = "Executive Board Briefing: FY26 Growth Trajectory & Capacity Assessment"
    summary: str = "Feasibility study for achieving ₹120 Cr ($14.4M) ARR target with existing 10 enterprise sales reps."
    key_takeaways: List[str] = field(default_factory=list)
    risk_summary: str = "Capacity bottleneck in Q3 demo scheduling; win rate expansion required from 24% to 29%."
    recommended_initiatives: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class StrategicRecommendation:
    recommendation_id: str = field(default_factory=lambda: f"rec-{uuid.uuid4().hex[:8]}")
    title: str = "Reallocate 2 Enterprise Reps to NA East Buying Window Surge"
    impact_usd: float = 650000.0
    urgency: str = "HIGH"
    rationale: str = "NA East accounts emitted 14 active buying window signals in the past 7 days."
    confidence_score: float = 0.92
    evidence_citations: List[str] = field(default_factory=list)


@dataclass
class RevenueScenarioSimulation:
    scenario_id: str = field(default_factory=lambda: f"scen-{uuid.uuid4().hex[:8]}")
    scenario_name: str = "Headcount Constrained Growth Strategy"
    scenario_type: ScenarioType = ScenarioType.HEADCOUNT_CONSTRAINED_GROWTH
    win_rate_delta: float = 0.05
    pipeline_coverage: float = 3.8
    projected_arr_usd: float = 14400000.0
    confidence_score: float = 0.88


@dataclass
class RevenueForecast:
    forecast_id: str = field(default_factory=lambda: f"fcst-{uuid.uuid4().hex[:8]}")
    fiscal_quarter: str = "Q3-FY26"
    commit_usd: float = 3400000.0
    best_case_usd: float = 4200000.0
    pipeline_coverage_ratio: float = 3.8
    win_rate_percentage: float = 28.5


@dataclass
class BusinessRisk:
    risk_id: str = field(default_factory=lambda: f"risk-{uuid.uuid4().hex[:8]}")
    category: RiskCategory = RiskCategory.CAPACITY_BOTTLENECK
    severity: str = "HIGH"
    impacted_pipeline_usd: float = 1200000.0
    mitigation_strategy: str = "Deploy AI Meeting Prep Workflow to increase rep demo capacity by 35%."


@dataclass
class BusinessOpportunity:
    opportunity_id: str = field(default_factory=lambda: f"opp-{uuid.uuid4().hex[:8]}")
    category: str = "EXPANSION_UPSELL"
    potential_value_usd: float = 1800000.0
    time_to_realization_days: int = 45


@dataclass
class MarketTrendAnalysis:
    trend_id: str = field(default_factory=lambda: f"trnd-{uuid.uuid4().hex[:8]}")
    topic: str = "AI Revenue Intelligence Adoption"
    growth_rate: str = "+42% YoY"
    strategic_threat_level: str = "LOW"
    recommended_positioning: str = "Emphasize 14-day ROI proof points and automated CRM sync."


@dataclass
class OrganizationHealth:

    health_id: str = field(default_factory=lambda: f"hlth-{uuid.uuid4().hex[:8]}")
    rep_utilization_ratio: float = 0.82
    attrition_risk_score: float = 0.12
    quota_attainment_percentage: float = 78.5


@dataclass
class CapacityPlan:
    rep_capacity_utilization: float = 0.82
    recommended_headcount_delta: int = 0  # Zero headcount increase requirement checked
    avg_deals_per_rep: int = 9
    bottleneck_risk: str = "Demo Scheduling Bottleneck in NA East"


@dataclass
class TerritoryPlan:
    territory_name: str
    assigned_reps: int = 5
    target_pipeline_usd: float = 5000000.0
    active_buying_windows: int = 12
    recommended_rep_reallocations: List[str] = field(default_factory=list)


@dataclass
class AutonomousOrgPackage:
    workspace_id: uuid.UUID
    operating_state: SystemOperatingState = SystemOperatingState.EXECUTING
    strategic_plans: List[StrategicPlan] = field(default_factory=list)
    forecasts: List[RevenueForecast] = field(default_factory=list)
    briefings: List[ExecutiveBriefing] = field(default_factory=list)
    territory_plans: List[TerritoryPlan] = field(default_factory=list)
    capacity_plan: Optional[CapacityPlan] = None
    market_trends: List[MarketTrendAnalysis] = field(default_factory=list)
    simulations: List[RevenueScenarioSimulation] = field(default_factory=list)
    recommendations: List[StrategicRecommendation] = field(default_factory=list)
    risks: List[BusinessRisk] = field(default_factory=list)
    opportunities: List[BusinessOpportunity] = field(default_factory=list)
    ai_partner_status: str = "Avenor Autonomous Revenue Operating System Active & Continuously Monitoring Accounts"
    execution_time_ms: float = 0.0
