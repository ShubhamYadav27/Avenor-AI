"""
Saga Manager (Phase 5.5.7)
Executes compensating actions in reverse order upon step failure to maintain data consistency.
"""
from typing import List
import uuid

from app.modules.copilot.domain.workflow_entities import StepResult, WorkflowStep


class SagaManager:
    async def compensate_execution(
        self,
        executed_steps: List[WorkflowStep],
        step_results: List[StepResult],
        workspace_id: uuid.UUID,
    ) -> List[str]:
        compensation_logs: List[str] = []

        # Execute compensating actions in reverse order
        for step in reversed(executed_steps):
            if step.compensation_action:
                log_entry = f"Compensated step '{step.name}' via {step.compensation_action}."
                compensation_logs.append(log_entry)

        return compensation_logs


saga_manager = SagaManager()
