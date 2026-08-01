"""
Autonomous Org Entities (Phase 6.6)
Pure domain entities representing operating states, health metrics, governance policies, and platform packages.
"""
from dataclasses import dataclass, field
from typing import List
import uuid

from app.modules.autonomous_org.domain.org_value_objects import OrgHealthTier, OrgOperatingMode


@dataclass
class AutonomousOrgState:
    state_id: str = field(default_factory=lambda: f"orgstate-{uuid.uuid4().hex[:8]}")
    workspace_id: uuid.UUID = field(default_factory=uuid.uuid4)
    operating_mode: OrgOperatingMode = OrgOperatingMode.HYBRID_GOVERNED
    active_agents_count: int = 18
    active_missions_count: int = 4
    total_arr_monitored_usd: float = 14400000.0
    system_uptime_percentage: float = 99.98


@dataclass
class OrgHealthMetrics:
    rep_productivity_index: float = 88.5
    win_rate_velocity: float = 0.285
    pipeline_coverage_ratio: float = 3.8
    churn_risk_index: float = 0.08
    health_tier: OrgHealthTier = OrgHealthTier.HEALTHY


@dataclass
class OrgGovernancePolicy:
    policy_id: str = field(default_factory=lambda: f"orgpolicy-{uuid.uuid4().hex[:8]}")
    auto_approval_threshold_usd: float = 100000.0
    required_roles_for_overrides: List[str] = field(default_factory=lambda: ["manager", "admin"])


@dataclass
class AutonomousOrgPlatformPackage:
    workspace_id: uuid.UUID
    org_state: AutonomousOrgState
    health_metrics: OrgHealthMetrics
    active_policy: OrgGovernancePolicy
    ai_partner_status: str = "Avenor Autonomous Revenue Organization Operating System Active & Self-Governing"
    execution_time_ms: float = 0.0
