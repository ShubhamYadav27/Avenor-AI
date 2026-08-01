"""
Autonomous RevOps Engine (Phase 6.3)
Coordinates GoalManager -> MissionPlanner -> StrategyEngine -> ExecutionCoordinator.
Zero DB ORM coupling.
"""
import time
from typing import List
import uuid

from app.modules.autonomous_revops.application.engines.execution_coordinator import execution_coordinator
from app.modules.autonomous_revops.application.engines.strategy_engine import strategy_engine
from app.modules.autonomous_revops.application.managers.goal_manager import goal_manager
from app.modules.autonomous_revops.application.planners.mission_planner import mission_planner
from app.modules.autonomous_revops.domain.revops_entities import ApprovalRequest, RevOpsPackage
from app.modules.autonomous_revops.domain.revops_value_objects import MissionType
from app.modules.copilot.domain.interfaces import IAutonomousRevOpsEngine


class AutonomousRevOpsEngine(IAutonomousRevOpsEngine):
    async def plan_and_execute_mission(
        self,
        workspace_id: uuid.UUID,
        mission_type: str,
        target_company_ids: List[str],
    ) -> RevOpsPackage:
        t0 = time.perf_counter()

        m_type = MissionType.PIPELINE_OPTIMIZATION
        try:
            m_type = MissionType(mission_type)
        except ValueError:
            pass

        # 1. Retrieve Active Revenue Goal
        goal = goal_manager.get_active_goal(workspace_id)

        # 2. Plan Mission
        mission = mission_planner.create_mission(workspace_id, goal, m_type, target_company_ids)

        # 3. Build Strategy & Plan
        plan = strategy_engine.build_autonomous_plan(mission.mission_id, target_company_ids)
        mission.plan = plan

        # 4. Supervise Execution & Approval Gates
        mission = execution_coordinator.supervise_mission(mission)

        total_lat = (time.perf_counter() - t0) * 1000.0

        executed_tasks = [
            f"Mission {mission.name} initialized",
            "Target accounts mapped to research and tool engines",
        ]

        pending_approvals: List[ApprovalRequest] = plan.approval_requests if plan else []

        return RevOpsPackage(
            workspace_id=workspace_id,
            active_missions=[mission],
            executed_tasks=executed_tasks,
            pending_approvals=pending_approvals,
            execution_time_ms=round(total_lat, 2),
        )


autonomous_revops_engine = AutonomousRevOpsEngine()
