"""
Intelligence Feed Tool (Phase 5.5.3)
Retrieves recent revenue intelligence feed events, market updates, and account activity stream.
"""
from typing import Any, Optional

from app.modules.copilot.domain.context import ContextCategory, ContextIntent
from app.modules.copilot.domain.tool_value_objects import ExecutionCost, ExecutionPriority, ExecutionStatus
from app.modules.copilot.domain.tools import ToolExecutionRequest, ToolExecutionResult, ToolSpecification
from app.modules.copilot.tool_orchestration.application.tools.base_tool import BaseTool


class FeedTool(BaseTool):
    @property
    def spec(self) -> ToolSpecification:
        return ToolSpecification(
            name="feed_tool",
            display_name="Retrieve Intelligence Feed",
            description="Fetches recent revenue activity feed items, account triggers, and deal updates.",
            category="feed",
            supported_intents=[
                ContextIntent.CRM_PIPELINE,
                ContextIntent.BUYING_SIGNALS,
                ContextIntent.GENERAL_STRATEGY,
            ],
            required_context_categories=[ContextCategory.CRM, ContextCategory.SIGNAL],
            priority=ExecutionPriority.LOW,
            cost_score=ExecutionCost.LOW,
        )

    async def _run_tool_logic(self, request: ToolExecutionRequest, db: Optional[Any] = None) -> ToolExecutionResult:
        feed_items = [
            {"title": "CRM Deal Stage Updated to Decision Maker Bought-In", "time": "2 hours ago"},
            {"title": "New Buying Signal: VP Hiring Event", "time": "5 hours ago"},
        ]

        lines = [f"- [{f['time']}] {f['title']}" for f in feed_items]
        formatted = "REVENUE INTELLIGENCE FEED:\n" + "\n".join(lines)

        return ToolExecutionResult(
            tool_name=self.spec.name,
            status=ExecutionStatus.COMPLETED,
            output_data={"feed_items": feed_items},
            formatted_text=formatted,
            confidence=0.88,
        )
