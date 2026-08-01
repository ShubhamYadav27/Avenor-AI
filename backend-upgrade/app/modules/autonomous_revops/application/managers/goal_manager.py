"""
Goal Manager (Phase 6.3)
Tracks quarterly revenue goals, target pipeline coverage, and capacity metrics.
"""
import uuid

from app.modules.autonomous_revops.domain.revops_entities import RevenueGoal
from app.modules.autonomous_revops.domain.revops_value_objects import GoalPriority


class GoalManager:
    def get_active_goal(self, workspace_id: uuid.UUID) -> RevenueGoal:
        return RevenueGoal(
            workspace_id=workspace_id,
            name="Q3 Enterprise Pipeline Target",
            target_value=5000000.0,
            current_value=3800000.0,
            metric="ARR_USD",
            priority=GoalPriority.HIGH,
        )


goal_manager = GoalManager()
