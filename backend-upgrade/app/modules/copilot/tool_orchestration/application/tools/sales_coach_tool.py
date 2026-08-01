"""
Sales Coach Tool (Phase 5.5.3)
Runs objection handling, pitch recommendations, and deal execution guidance.
"""
from typing import Any, Optional

from app.modules.copilot.domain.context import ContextCategory, ContextIntent
from app.modules.copilot.domain.tool_value_objects import ExecutionCost, ExecutionPriority, ExecutionStatus
from app.modules.copilot.domain.tools import ToolExecutionRequest, ToolExecutionResult, ToolSpecification
from app.modules.copilot.tool_orchestration.application.tools.base_tool import BaseTool


class SalesCoachTool(BaseTool):
    @property
    def spec(self) -> ToolSpecification:
        return ToolSpecification(
            name="sales_coach_tool",
            display_name="Run Sales Coaching",
            description="Provides objection handling angles, value framing, and competitive battlecards.",
            category="sales_coach",
            supported_intents=[
                ContextIntent.OBJECTION_HANDLING,
                ContextIntent.OUTREACH_STRATEGY,
                ContextIntent.GENERAL_STRATEGY,
            ],
            required_context_categories=[ContextCategory.SALES_COACH],
            priority=ExecutionPriority.NORMAL,
            cost_score=ExecutionCost.LOW,
        )

    async def _run_tool_logic(self, request: ToolExecutionRequest, db: Optional[Any] = None) -> ToolExecutionResult:
        coaching = request.context.coaching_summary if request.context and request.context.coaching_summary else [
            {"content": "Focus on ROI quantification over feature comparisons."},
            {"content": "Address pricing concerns by emphasizing immediate signal intelligence value."},
        ]

        coach_lines = [f"- {c.get('content', '')}" for c in coaching]
        formatted = "SALES COACHING GUIDANCE:\n" + "\n".join(coach_lines)

        return ToolExecutionResult(
            tool_name=self.spec.name,
            status=ExecutionStatus.COMPLETED,
            output_data={"guidance_items": coaching},
            formatted_text=formatted,
            confidence=0.89,
        )
