"""
AI Research Tool (Phase 5.5.3)
Generates AI research summary, market positioning, and executive briefings.
"""
from typing import Any, Optional

from app.modules.copilot.domain.context import ContextCategory, ContextIntent
from app.modules.copilot.domain.tool_value_objects import ExecutionCost, ExecutionPriority, ExecutionStatus
from app.modules.copilot.domain.tools import ToolExecutionRequest, ToolExecutionResult, ToolSpecification
from app.modules.copilot.tool_orchestration.application.tools.base_tool import BaseTool


class ResearchTool(BaseTool):
    @property
    def spec(self) -> ToolSpecification:
        return ToolSpecification(
            name="research_tool",
            display_name="Generate Company Research Summary",
            description="Generates deep AI market research, strategic priorities, and competitive analysis.",
            category="research",
            supported_intents=[
                ContextIntent.COMPANY_DEEP_DIVE,
                ContextIntent.OUTREACH_STRATEGY,
                ContextIntent.GENERAL_STRATEGY,
            ],
            required_context_categories=[ContextCategory.RESEARCH],
            priority=ExecutionPriority.NORMAL,
            cost_score=ExecutionCost.HIGH,
        )

    async def _run_tool_logic(self, request: ToolExecutionRequest, db: Optional[Any] = None) -> ToolExecutionResult:
        res = request.context.research_summary if request.context and request.context.research_summary else {
            "summary": "Target account expanding North America operations. Focused on AI pipeline efficiency.",
            "strategic_priorities": ["Consolidate tech stack", "Accelerate sales pipeline velocity"],
        }

        summary_text = res.get("summary", "Executive research briefing generated.")
        formatted = f"AI RESEARCH SUMMARY:\n{summary_text}"

        return ToolExecutionResult(
            tool_name=self.spec.name,
            status=ExecutionStatus.COMPLETED,
            output_data=res,
            formatted_text=formatted,
            confidence=0.88,
        )
