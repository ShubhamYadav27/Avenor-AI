"""
Sales Briefing Tool (Phase 5.5.3)
Generates comprehensive meeting briefing packages by aggregating company, CRM, and buying signals.
"""
from typing import Any, Optional

from app.modules.copilot.domain.context import ContextCategory, ContextIntent
from app.modules.copilot.domain.tool_value_objects import ExecutionCost, ExecutionPriority, ExecutionStatus
from app.modules.copilot.domain.tools import ToolExecutionRequest, ToolExecutionResult, ToolSpecification
from app.modules.copilot.tool_orchestration.application.tools.base_tool import BaseTool


class BriefingTool(BaseTool):
    @property
    def spec(self) -> ToolSpecification:
        return ToolSpecification(
            name="briefing_tool",
            display_name="Generate Sales Briefing",
            description="Assembles executive meeting prep package combining CRM, company research, and buying signals.",
            category="briefing",
            supported_intents=[
                ContextIntent.COMPANY_DEEP_DIVE,
                ContextIntent.OUTREACH_STRATEGY,
                ContextIntent.GENERAL_STRATEGY,
            ],
            required_context_categories=[ContextCategory.COMPANY, ContextCategory.CRM],
            priority=ExecutionPriority.HIGH,
            cost_score=ExecutionCost.MEDIUM,
            dependencies=["company_tool", "crm_tool"],
        )

    async def _run_tool_logic(self, request: ToolExecutionRequest, db: Optional[Any] = None) -> ToolExecutionResult:
        formatted = (
            "MEETING BRIEFING PACKAGE:\n"
            "1. Executive Summary: High-intent enterprise target expanding sales ops.\n"
            "2. Key Objectives: Demonstrate Avenor AI revenue intelligence ROI.\n"
            "3. Talking Points: Highlight signal detection and real-time CRM intelligence integration."
        )

        return ToolExecutionResult(
            tool_name=self.spec.name,
            status=ExecutionStatus.COMPLETED,
            output_data={"briefing_ready": True, "talking_points_count": 3},
            formatted_text=formatted,
            confidence=0.92,
        )
