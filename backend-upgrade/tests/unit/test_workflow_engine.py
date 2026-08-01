import uuid
import pytest

from app.modules.copilot.domain.workflow_entities import WorkflowPackage, WorkflowStep
from app.modules.copilot.domain.workflow_value_objects import StepType, WorkflowStatus
from app.modules.copilot.workflow_engine.application.compensation.saga_manager import saga_manager
from app.modules.copilot.workflow_engine.application.engine import workflow_engine
from app.modules.copilot.workflow_engine.application.executors.step_executor import step_executor
from app.modules.copilot.workflow_engine.application.planners.workflow_planner import workflow_planner


@pytest.fixture
def anyio_backend():
    return "asyncio"


def test_workflow_planner_preset_definitions():
    presets = workflow_planner.get_preset_definitions()
    assert "meeting_prep" in presets
    assert "hot_account" in presets
    assert "deal_review" in presets

    defn = workflow_planner.get_definition("meeting_prep")
    assert defn is not None
    assert len(defn.steps) == 5


@pytest.mark.anyio
async def test_step_executor_tool_action():
    ws_id = uuid.uuid4()
    step = WorkflowStep(name="Fetch CRM History", type=StepType.TOOL_ACTION, action_name="CrmTool")
    res = await step_executor.execute_step(step, ws_id, {})

    assert res.status == WorkflowStatus.COMPLETED
    assert res.output_data["action_executed"] == "CrmTool"
    assert res.latency_ms >= 0.0


@pytest.mark.anyio
async def test_saga_manager_compensation():
    ws_id = uuid.uuid4()
    step1 = WorkflowStep(name="Create CRM Task", type=StepType.CRM_MUTATION, compensation_action="DeleteCRMTask")
    step2 = WorkflowStep(name="Send Email", type=StepType.TOOL_ACTION, compensation_action="CancelEmail")

    logs = await saga_manager.compensate_execution([step1, step2], [], ws_id)
    assert len(logs) == 2
    assert "CancelEmail" in logs[0]  # Reverse order execution
    assert "DeleteCRMTask" in logs[1]


@pytest.mark.anyio
async def test_workflow_engine_e2e_meeting_prep():
    ws_id = uuid.uuid4()
    pkg = await workflow_engine.execute_workflow(
        workspace_id=ws_id,
        workflow_name="meeting_prep",
    )

    assert isinstance(pkg, WorkflowPackage)
    assert pkg.status == WorkflowStatus.COMPLETED
    assert pkg.steps_completed == 5
    assert pkg.total_steps == 5
    assert "Successfully executed" in pkg.summary
