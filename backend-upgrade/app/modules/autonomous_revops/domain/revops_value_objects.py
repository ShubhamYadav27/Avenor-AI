"""
Autonomous RevOps Value Objects (Phase 6.3)
Domain enums and value objects for Enterprise Autonomous Revenue Operations Engine.
Zero external framework dependencies.
"""
from enum import Enum


class MissionType(str, Enum):
    PIPELINE_OPTIMIZATION = "pipeline_optimization"
    HOT_ACCOUNT_MONITORING = "hot_account_monitoring"
    DEAL_RESCUE = "deal_rescue"
    EXPANSION_MISSION = "expansion_mission"
    RENEWAL_MISSION = "renewal_mission"
    TERRITORY_OPTIMIZATION = "territory_optimization"
    PROSPECTING_MISSION = "prospecting_mission"
    COMPETITIVE_WATCH = "competitive_watch"


class GoalPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class MissionStatus(str, Enum):
    PLANNED = "planned"
    AWAITING_APPROVAL = "awaiting_approval"
    EXECUTING = "executing"
    COMPLETED = "completed"
    PAUSED = "paused"
    FAILED = "failed"
    ADAPTED = "adapted"


class ApprovalState(str, Enum):
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    AUTO_EXECUTED = "auto_executed"
    REJECTED = "rejected"
