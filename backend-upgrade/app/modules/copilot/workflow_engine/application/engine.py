"""
Enterprise Workflow Engine (Phase 5.5.7)
Coordinates WorkflowPlanner -> StepExecutor -> ActionDispatcher -> SagaManager.
Zero DB ORM coupling.
"""
import time
from typing import Any, Dict, Optional
import uuid

from app.modules.copilot.domain.interfaces import IWorkflowEngine
from app.modules.copilot.domain.workflow_entities import WorkflowExecution, WorkflowPackage
from app.modules.copilot.domain.workflow_value_objects import WorkflowStatus
from app.modules.copilot.workflow_engine.application.compensation.saga_manager import saga_manager
from app.modules.copilot.workflow_engine.application.executors.step_executor import step_executor
from app.modules.copilot.workflow_engine.application.planners.workflow_planner import workflow_planner


class WorkflowEngine(IWorkflowEngine):
    async def execute_workflow(
        self,
        workspace_id: uuid.UUID,
        workflow_name: str,
        context_data: Optional[Dict[str, Any]] = None,
    ) -> WorkflowPackage:
        t0 = time.perf_counter()
        ctx = context_data or {}

        # 1. Resolve Workflow Definition from Planner
        definition = workflow_planner.get_definition(workflow_name)
        if not definition:
            return WorkflowPackage(
                execution_id=f"wf-exec-{uuid.uuid4().hex[:12]}",
                workspace_id=workspace_id,
                workflow_name=workflow_name,
                status=WorkflowStatus.FAILED,
                summary=f"Workflow definition '{workflow_name}' not found.",
                steps_completed=0,
                total_steps=0,
            )

        execution = WorkflowExecution(
            workflow_id=definition.id,
            workspace_id=workspace_id,
            context_data=ctx,
        )

        executed_steps = []
        step_results = []

        # 2. Execute Steps Sequentially / Parallel
        for step in definition.steps:
            res = await step_executor.execute_step(step, workspace_id, ctx)
            step_results.append(res)
            executed_steps.append(step)

            if res.status != WorkflowStatus.COMPLETED:
                execution.status = WorkflowStatus.FAILED
                # Trigger Saga Compensation
                await saga_manager.compensate_execution(executed_steps, step_results, workspace_id)
                break

        if execution.status != WorkflowStatus.FAILED:
            execution.status = WorkflowStatus.COMPLETED

        total_lat = (time.perf_counter() - t0) * 1000.0

        summary = (
            f"Successfully executed '{definition.name}' across {len(step_results)} steps. "
            f"Status: {execution.status.value.upper()}."
        )

        return WorkflowPackage(
            execution_id=execution.execution_id,
            workspace_id=workspace_id,
            workflow_name=definition.name,
            status=execution.status,
            summary=summary,
            steps_completed=len(step_results),
            total_steps=len(definition.steps),
            execution_time_ms=round(total_lat, 2),
        )


workflow_engine = WorkflowEngine()
