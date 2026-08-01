"""
Revenue OS Entities (Phase 6.6)
Pure domain entities representing the Revenue Operating System Kernel, capabilities, organization health, and executive workspace.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List
import uuid

from app.modules.revenue_os.domain.revenue_os_value_objects import CapabilityStatus, HealthTier, OperatingMode, PolicyLevel, ProgramStatus


@dataclass
class RevenueOrganization:
    org_id: str = field(default_factory=lambda: f"org-{uuid.uuid4().hex[:8]}")
    workspace_id: uuid.UUID = field(default_factory=uuid.uuid4)
    name: str = "Acme Global Revenue Org"
    fiscal_year: str = "FY2026"
    total_arr_usd: float = 14400000.0
    active_reps_count: int = 10
    health_score: float = 87.0


@dataclass
class RevenueOperatingState:
    state_id: str = field(default_factory=lambda: f"state-{uuid.uuid4().hex[:8]}")
    org_id: str = ""
    operating_mode: OperatingMode = OperatingMode.HYBRID_GOVERNED
    global_health_index: float = 87.0
    active_missions_count: int = 2
    active_agents_count: int = 18
    uptime_percentage: float = 99.98


@dataclass
class OrganizationObjective:
    objective_id: str = field(default_factory=lambda: f"obj-{uuid.uuid4().hex[:8]}")
    title: str = "Achieve $14.4M ARR Target in FY26"
    target_metric: str = "ARR_USD"
    target_value: float = 14400000.0
    current_value: float = 8500000.0
    target_quarter: str = "Q4"


@dataclass
class OrganizationHealth:
    health_id: str = field(default_factory=lambda: f"hlth-{uuid.uuid4().hex[:8]}")
    rep_productivity_index: float = 88.5
    win_rate_velocity: float = 0.285
    pipeline_coverage_ratio: float = 3.1
    churn_risk_index: float = 0.08
    health_tier: HealthTier = HealthTier.HEALTHY


@dataclass
class RevenueProgram:
    program_id: str = field(default_factory=lambda: f"prog-{uuid.uuid4().hex[:8]}")
    name: str = "Enterprise Account Expansion & Win Rate Optimization"
    target_segment: str = "Enterprise B2B SaaS"
    target_arr_usd: float = 2500000.0
    status: ProgramStatus = ProgramStatus.ACTIVE


@dataclass
class RevenueCapability:
    capability_id: str = field(default_factory=lambda: f"cap-{uuid.uuid4().hex[:8]}")
    name: str = "Predictive Intelligence & Decisioning"
    status: CapabilityStatus = CapabilityStatus.OPTIMAL
    health_index: float = 94.0
    readiness_score: float = 96.0


@dataclass
class CapabilityHealth:
    capability_name: str = "Sales Capacity & Demo Scheduling"
    status: CapabilityStatus = CapabilityStatus.BOTTLENECKED
    health_score: float = 72.0
    bottleneck_notes: str = "Demo scheduling bottleneck detected in NA East; AI Workflows deployed."


@dataclass
class OrganizationInsight:
    insight_id: str = field(default_factory=lambda: f"ins-{uuid.uuid4().hex[:8]}")
    category: str = "PIPELINE_WARNING"
    severity: str = "HIGH"
    message: str = "APAC region pipeline coverage is underperforming at 1.8x target."
    recommendation: str = "Reallocate 2 Enterprise Account Executives to APAC territory surge."


@dataclass
class RevenuePolicy:
    policy_id: str = field(default_factory=lambda: f"pol-{uuid.uuid4().hex[:8]}")
    policy_level: PolicyLevel = PolicyLevel.BALANCED
    auto_approval_threshold_usd: float = 100000.0
    required_roles: List[str] = field(default_factory=lambda: ["manager", "admin"])


@dataclass
class RevenueStrategy:
    strategy_id: str = field(default_factory=lambda: f"strat-{uuid.uuid4().hex[:8]}")
    name: str = "Headcount-Constrained Growth Strategy"
    scenario_type: str = "HEADCOUNT_CONSTRAINED_GROWTH"
    projected_impact_usd: float = 5900000.0


@dataclass
class RevenuePlaybook:
    playbook_id: str = field(default_factory=lambda: f"pb-{uuid.uuid4().hex[:8]}")
    name: str = "Series B Scaling Playbook"
    target_vertical: str = "FinTech & B2B SaaS"
    expected_win_rate_lift: float = 0.32


@dataclass
class CoordinationPlan:
    plan_id: str = field(default_factory=lambda: f"coord-{uuid.uuid4().hex[:8]}")
    mission_id: str = "miss-101"
    involved_systems: List[str] = field(default_factory=lambda: ["PredictiveEngine", "DecisionEngine", "WorkflowEngine"])
    approval_gates: int = 1
    status: str = "COORDINATING"


@dataclass
class CoordinationSession:
    session_id: str = field(default_factory=lambda: f"csess-{uuid.uuid4().hex[:8]}")
    active_agents: List[str] = field(default_factory=lambda: ["ResearchAgent", "CrmAgent", "SignalAgent"])
    step_progress: float = 0.85
    status: str = "ACTIVE"


@dataclass
class RevenueSnapshot:
    snapshot_id: str = field(default_factory=lambda: f"snap-{uuid.uuid4().hex[:8]}")
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    total_pipeline_usd: float = 15800000.0
    commit_usd: float = 3400000.0
    best_case_usd: float = 4200000.0
    health_index: float = 87.0


@dataclass
class ExecutiveWorkspace:
    workspace_id: uuid.UUID = field(default_factory=uuid.uuid4)
    title: str = "CEO & CRO Executive Command Center"
    ceo_dashboard_summary: str = "Overall Revenue Org Health 87%; 2 Autonomous Missions in progress; 1 awaiting executive approval."


@dataclass
class OperatingPackage:
    workspace_id: uuid.UUID
    org_state: RevenueOperatingState
    health_metrics: OrganizationHealth
    active_policy: RevenuePolicy
    active_programs: List[RevenueProgram] = field(default_factory=list)
    capabilities: List[RevenueCapability] = field(default_factory=list)
    insights: List[OrganizationInsight] = field(default_factory=list)
    executive_summary: str = "Avenor Revenue OS Active: Unified Intelligence Layer, 18 Subagents & Knowledge Graph operational."
    execution_time_ms: float = 0.0
