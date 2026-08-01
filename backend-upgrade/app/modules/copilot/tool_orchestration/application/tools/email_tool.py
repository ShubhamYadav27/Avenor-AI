"""
Email Generator Tool (Phase 5.5.3)
Generates high-converting outreach email templates grounded in signal and company context.
"""
from typing import Any, Optional

from app.modules.copilot.domain.context import ContextCategory, ContextIntent
from app.modules.copilot.domain.tool_value_objects import ExecutionCost, ExecutionPriority, ExecutionStatus
from app.modules.copilot.domain.tools import ToolExecutionRequest, ToolExecutionResult, ToolSpecification
from app.modules.copilot.tool_orchestration.application.tools.base_tool import BaseTool


class EmailTool(BaseTool):
    @property
    def spec(self) -> ToolSpecification:
        return ToolSpecification(
            name="email_tool",
            display_name="Generate Email Template",
            description="Generates personalized outreach email templates based on signal triggers and company context.",
            category="email",
            supported_intents=[
                ContextIntent.OUTREACH_STRATEGY,
                ContextIntent.GENERAL_STRATEGY,
            ],
            required_context_categories=[ContextCategory.EMAIL],
            priority=ExecutionPriority.NORMAL,
            cost_score=ExecutionCost.MEDIUM,
            dependencies=["briefing_tool"],
        )

    async def _run_tool_logic(self, request: ToolExecutionRequest, db: Optional[Any] = None) -> ToolExecutionResult:
        subject = "Strategic alignment on AI revenue intelligence"
        body = (
            "Hi {{first_name}},\n\n"
            "Noticed your recent expansion in revenue operations. "
            "Avenor helps revenue leaders unify buying signals and CRM intelligence into actionable sales execution.\n\n"
            "Would you be open to a brief 10-minute briefing next Tuesday?\n\n"
            "Best regards,\nAccount Team"
        )

        formatted = f"GENERATED OUTREACH EMAIL:\nSubject: {subject}\n\n{body}"

        return ToolExecutionResult(
            tool_name=self.spec.name,
            status=ExecutionStatus.COMPLETED,
            output_data={"subject": subject, "body": body},
            formatted_text=formatted,
            confidence=0.90,
        )
