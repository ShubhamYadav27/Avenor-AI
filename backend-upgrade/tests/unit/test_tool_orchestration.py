import uuid
import pytest

from app.modules.copilot.application.orchestrator.prompt_builder import prompt_builder
from app.modules.copilot.domain.context import ContextIntent, UnifiedContext
from app.modules.copilot.domain.tool_value_objects import ExecutionStatus
from app.modules.copilot.domain.tools import (
    ToolExecutionPlan,
    ToolExecutionResult,
    UnifiedIntelligencePackage,
)
from app.modules.copilot.tool_orchestration.application.executors.execution_engine import tool_execution_engine
from app.modules.copilot.tool_orchestration.application.planners.planner import tool_planner
from app.modules.copilot.tool_orchestration.application.recovery.circuit_breaker import CircuitBreaker, CircuitState
from app.modules.copilot.tool_orchestration.application.routers.router import tool_router
from app.modules.copilot.tool_orchestration.infrastructure.registry.registry import tool_registry


@pytest.fixture
def anyio_backend():
    return "asyncio"



def test_tool_registry_discovery():
    all_tools = tool_registry.list_all_tools()
    assert len(all_tools) >= 8

    company_tool = tool_registry.get_tool("company_tool")
    assert company_tool is not None
    assert company_tool.spec.display_name == "Retrieve Company Intelligence"

    signal_tools = tool_registry.get_tools_for_intent(ContextIntent.BUYING_SIGNALS)
    assert len(signal_tools) > 0


def test_tool_planner_selection():
    workspace_id = uuid.uuid4()
    ctx = UnifiedContext(workspace_id=workspace_id, intent=ContextIntent.COMPANY_DEEP_DIVE)
    tools = tool_registry.get_tools_for_intent(ContextIntent.COMPANY_DEEP_DIVE)

    plan = tool_planner.create_plan(ContextIntent.COMPANY_DEEP_DIVE, ctx, tools)
    assert isinstance(plan, ToolExecutionPlan)
    assert "company_tool" in plan.selected_tools


def test_tool_router_dag_stages():
    workspace_id = uuid.uuid4()
    ctx = UnifiedContext(workspace_id=workspace_id, intent=ContextIntent.OUTREACH_STRATEGY)
    tools = tool_registry.list_all_tools()

    plan = tool_planner.create_plan(ContextIntent.OUTREACH_STRATEGY, ctx, tools)
    stages = tool_router.build_execution_stages(plan, tool_registry)

    assert len(stages) >= 1
    # Stage 1 must contain independent tools
    stage_1_names = [node.tool_name for node in stages[0]]
    assert "company_tool" in stage_1_names or "signal_tool" in stage_1_names or "crm_tool" in stage_1_names


def test_circuit_breaker_state_transitions():
    cb = CircuitBreaker(failure_threshold=2, recovery_interval_seconds=1.0)
    tool_name = "test_external_api"

    assert cb.get_state(tool_name) == CircuitState.CLOSED
    cb.record_failure(tool_name)
    assert cb.get_state(tool_name) == CircuitState.CLOSED

    cb.record_failure(tool_name)
    assert cb.get_state(tool_name) == CircuitState.OPEN
    assert not cb.allow_execution(tool_name)

    cb.record_success(tool_name)
    assert cb.get_state(tool_name) == CircuitState.CLOSED
    assert cb.allow_execution(tool_name)


@pytest.mark.anyio
async def test_tool_execution_engine_run():
    workspace_id = uuid.uuid4()
    ctx = UnifiedContext(workspace_id=workspace_id, intent=ContextIntent.COMPANY_DEEP_DIVE)
    
    intel_pkg = await tool_execution_engine.execute_intent(
        workspace_id=workspace_id,
        user_query="Tell me about Acme Corp",
        intent=ContextIntent.COMPANY_DEEP_DIVE,
        context=ctx,
    )

    assert isinstance(intel_pkg, UnifiedIntelligencePackage)
    assert len(intel_pkg.tool_results) > 0
    assert intel_pkg.overall_confidence_score > 0.0
    assert len(intel_pkg.aggregated_text) > 0


def test_prompt_builder_integration_with_intelligence_package():
    workspace_id = uuid.uuid4()
    result = ToolExecutionResult(
        tool_name="company_tool",
        status=ExecutionStatus.COMPLETED,
        formatted_text="COMPANY INTELLIGENCE:\n- Account: Acme Corp\n- ICP Fit: 95/100",
    )
    intel_pkg = UnifiedIntelligencePackage(
        workspace_id=workspace_id,
        intent=ContextIntent.COMPANY_DEEP_DIVE,
        tool_results=[result],
        aggregated_text=result.formatted_text,
    )

    prompt_v1 = prompt_builder.build_system_prompt(unified_context=intel_pkg, prompt_version="v1")
    prompt_v2 = prompt_builder.build_system_prompt(unified_context=intel_pkg, prompt_version="v2")

    assert "STRUCTURED TOOL INTELLIGENCE PACKAGE" in prompt_v1
    assert "Acme Corp" in prompt_v1
    assert "Version 2.0" in prompt_v2
