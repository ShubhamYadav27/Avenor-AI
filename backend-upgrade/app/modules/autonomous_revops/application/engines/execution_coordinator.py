"""
Execution Coordinator (Phase 6.3)
Supervises mission execution lifecycle, monitors checkpoints, and validates approval gates.
"""

from app.modules.autonomous_revops.domain.revops_entities import RevenueMission
from app.modules.autonomous_revops.domain.revops_value_objects import MissionStatus


class ExecutionCoordinator:
    def supervise_mission(self, mission: RevenueMission) -> RevenueMission:
        if mission.plan and mission.plan.approval_requests:
            pending = any(a.approval_state.value == "pending_approval" for a in mission.plan.approval_requests)
            if pending:
                mission.status = MissionStatus.AWAITING_APPROVAL
            else:
                mission.status = MissionStatus.EXECUTING
        return mission


execution_coordinator = ExecutionCoordinator()
