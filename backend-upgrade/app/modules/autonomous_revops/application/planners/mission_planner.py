"""
Mission Planner (Phase 6.3)
Decomposes quarterly revenue goals into targeted autonomous revenue missions.
"""
from typing import List
import uuid

from app.modules.autonomous_revops.domain.revops_entities import RevenueGoal, RevenueMission
from app.modules.autonomous_revops.domain.revops_value_objects import MissionStatus, MissionType


class MissionPlanner:
    def create_mission(
        self,
        workspace_id: uuid.UUID,
        goal: RevenueGoal,
        mission_type: MissionType,
        target_company_ids: List[str],
    ) -> RevenueMission:
        name = f"Autonomous {mission_type.value.replace('_', ' ').title()} Mission"
        return RevenueMission(
            workspace_id=workspace_id,
            mission_type=mission_type,
            name=name,
            goal_id=goal.goal_id,
            target_company_ids=target_company_ids,
            status=MissionStatus.EXECUTING,
        )


mission_planner = MissionPlanner()
