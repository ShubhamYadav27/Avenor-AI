"""
Autonomous RevOps Entities (Phase 6.3)
Pure domain entities representing goals, missions, plans, approval requests, checkpoints, and packages.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional
import uuid

from app.modules.autonomous_revops.domain.revops_value_objects import ApprovalState, GoalPriority, MissionStatus, MissionType


@dataclass
class RevenueGoal:
    goal_id: str = field(default_factory=lambda: f"goal-{uuid.uuid4().hex[:8]}")
    workspace_id: uuid.UUID = field(default_factory=uuid.uuid4)
    name: str = "Q3 Enterprise Pipeline Target"
    target_value: float = 5000000.0
    current_value: float = 3800000.0
    metric: str = "ARR_USD"
    priority: GoalPriority = GoalPriority.HIGH


@dataclass
class ApprovalRequest:
    request_id: str = field(default_factory=lambda: f"appr-{uuid.uuid4().hex[:8]}")
    mission_id: str = ""
    action_title: str = ""
    description: str = ""
    required_role: str = "manager"
    approval_state: ApprovalState = ApprovalState.PENDING_APPROVAL


@dataclass
class ExecutionCheckpoint:
    checkpoint_id: str = field(default_factory=lambda: f"chk-{uuid.uuid4().hex[:8]}")
    step_name: str = ""
    status: str = "passed"
    expected_metric: float = 0.85
    actual_metric: float = 0.88


@dataclass
class AutonomousPlan:
    plan_id: str = field(default_factory=lambda: f"plan-{uuid.uuid4().hex[:8]}")
    mission_id: str = ""
    strategy_description: str = ""
    required_workflows: List[str] = field(default_factory=list)
    approval_requests: List[ApprovalRequest] = field(default_factory=list)
    checkpoints: List[ExecutionCheckpoint] = field(default_factory=list)


@dataclass
class RevenueMission:
    mission_id: str = field(default_factory=lambda: f"miss-{uuid.uuid4().hex[:8]}")
    workspace_id: uuid.UUID = field(default_factory=uuid.uuid4)
    mission_type: MissionType = MissionType.PIPELINE_OPTIMIZATION
    name: str = ""
    goal_id: str = ""
    target_company_ids: List[str] = field(default_factory=list)
    plan: Optional[AutonomousPlan] = None
    status: MissionStatus = MissionStatus.EXECUTING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RevOpsPackage:
    session_id: str = field(default_factory=lambda: f"revops-sess-{uuid.uuid4().hex[:8]}")
    workspace_id: uuid.UUID = field(default_factory=uuid.uuid4)
    active_missions: List[RevenueMission] = field(default_factory=list)
    executed_tasks: List[str] = field(default_factory=list)
    pending_approvals: List[ApprovalRequest] = field(default_factory=list)
    execution_time_ms: float = 0.0
