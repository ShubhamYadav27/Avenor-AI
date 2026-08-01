import uuid
import pytest

from app.modules.autonomous_revops.application.engine import autonomous_revops_engine
from app.modules.autonomous_revops.application.engines.execution_coordinator import execution_coordinator
from app.modules.autonomous_revops.application.engines.strategy_engine import strategy_engine
from app.modules.autonomous_revops.application.managers.goal_manager import goal_manager
from app.modules.autonomous_revops.application.planners.mission_planner import mission_planner
from app.modules.autonomous_revops.domain.revops_entities import RevOpsPackage
from app.modules.autonomous_revops.domain.revops_value_objects import MissionStatus, MissionType


@pytest.fixture
def anyio_backend():
    return "asyncio"


def test_goal_manager():
    ws_id = uuid.uuid4()
    goal = goal_manager.get_active_goal(ws_id)
    assert goal.target_value == 5000000.0
    assert goal.metric == "ARR_USD"


def test_mission_planner():
    ws_id = uuid.uuid4()
    goal = goal_manager.get_active_goal(ws_id)
    mission = mission_planner.create_mission(ws_id, goal, MissionType.PIPELINE_OPTIMIZATION, ["comp-101"])
    assert mission.mission_type == MissionType.PIPELINE_OPTIMIZATION
    assert mission.target_company_ids == ["comp-101"]


def test_strategy_engine():
    plan = strategy_engine.build_autonomous_plan("m-101", ["comp-101"])
    assert len(plan.required_workflows) == 3
    assert len(plan.approval_requests) == 1
    assert len(plan.checkpoints) == 2


def test_execution_coordinator():
    ws_id = uuid.uuid4()
    goal = goal_manager.get_active_goal(ws_id)
    mission = mission_planner.create_mission(ws_id, goal, MissionType.PIPELINE_OPTIMIZATION, ["comp-101"])
    plan = strategy_engine.build_autonomous_plan(mission.mission_id, ["comp-101"])
    mission.plan = plan

    supervised = execution_coordinator.supervise_mission(mission)
    assert supervised.status == MissionStatus.AWAITING_APPROVAL


@pytest.mark.anyio
async def test_autonomous_revops_engine_e2e():
    ws_id = uuid.uuid4()
    pkg = await autonomous_revops_engine.plan_and_execute_mission(
        workspace_id=ws_id,
        mission_type="pipeline_optimization",
        target_company_ids=["comp-101", "comp-102"],
    )

    assert isinstance(pkg, RevOpsPackage)
    assert len(pkg.active_missions) == 1
    assert pkg.active_missions[0].status == MissionStatus.AWAITING_APPROVAL
    assert len(pkg.pending_approvals) == 1
    assert pkg.pending_approvals[0].required_role == "manager"
