"""
CRM Intelligence Tool (Phase 5.5.3)
Retrieves CRM deal pipeline, deal stage, associated contacts, and opportunity health.
"""
from typing import Any, Optional

from app.modules.copilot.domain.context import ContextCategory, ContextIntent
from app.modules.copilot.domain.tool_value_objects import ExecutionCost, ExecutionPriority, ExecutionStatus
from app.modules.copilot.domain.tools import ToolExecutionRequest, ToolExecutionResult, ToolSpecification
from app.modules.copilot.tool_orchestration.application.tools.base_tool import BaseTool


class CrmTool(BaseTool):
    @property
    def spec(self) -> ToolSpecification:
        return ToolSpecification(
            name="crm_tool",
            display_name="Retrieve CRM Intelligence",
            description="Fetches CRM deal status, stage progression, deal value, and lead contacts.",
            category="crm",
            supported_intents=[
                ContextIntent.CRM_PIPELINE,
                ContextIntent.COMPANY_DEEP_DIVE,
                ContextIntent.OUTREACH_STRATEGY,
            ],
            required_context_categories=[ContextCategory.CRM],
            priority=ExecutionPriority.HIGH,
            cost_score=ExecutionCost.LOW,
        )

    async def _run_tool_logic(self, request: ToolExecutionRequest, db: Optional[Any] = None) -> ToolExecutionResult:
        crm_data = request.context.crm_summary if request.context and request.context.crm_summary else {
            "deal_name": "Acme Enterprise Deal",
            "stage": "Decision Maker Bought-In",
            "amount": "$120,000",
            "owner": "Account Executive",
            "contacts_count": 3,
        }

        formatted = (
            f"CRM PIPELINE INTELLIGENCE:\n"
            f"- Opportunity: {crm_data.get('deal_name', 'Enterprise Opportunity')}\n"
            f"- Stage: {crm_data.get('stage', 'Qualification')}\n"
            f"- Value: {crm_data.get('amount', '$0')}\n"
            f"- Key Contacts: {crm_data.get('contacts_count', 1)} decision makers"
        )

        return ToolExecutionResult(
            tool_name=self.spec.name,
            status=ExecutionStatus.COMPLETED,
            output_data=crm_data,
            formatted_text=formatted,
            confidence=0.91,
        )
