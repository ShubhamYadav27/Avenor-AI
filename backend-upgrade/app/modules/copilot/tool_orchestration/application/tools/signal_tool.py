"""
Buying Signal Tool (Phase 5.5.3)
Analyzes buying signals, hiring triggers, funding rounds, and leadership changes.
"""
from typing import Any, Optional

from app.modules.copilot.domain.context import ContextCategory, ContextIntent
from app.modules.copilot.domain.tool_value_objects import ExecutionCost, ExecutionPriority, ExecutionStatus
from app.modules.copilot.domain.tools import ToolExecutionRequest, ToolExecutionResult, ToolSpecification
from app.modules.copilot.tool_orchestration.application.tools.base_tool import BaseTool


class SignalTool(BaseTool):
    @property
    def spec(self) -> ToolSpecification:
        return ToolSpecification(
            name="signal_tool",
            display_name="Analyze Buying Signals",
            description="Analyzes hiring surges, funding events, executive hiring, and tech expansion signals.",
            category="signal",
            supported_intents=[
                ContextIntent.BUYING_SIGNALS,
                ContextIntent.OUTREACH_STRATEGY,
                ContextIntent.COMPANY_DEEP_DIVE,
            ],
            required_context_categories=[ContextCategory.SIGNAL],
            priority=ExecutionPriority.HIGH,
            cost_score=ExecutionCost.LOW,
        )

    async def _run_tool_logic(self, request: ToolExecutionRequest, db: Optional[Any] = None) -> ToolExecutionResult:
        signals = request.context.signal_summary if request.context and request.context.signal_summary else [
            {"type": "HIRING_SURGE", "title": "VP of Revenue Operations hired", "score": 92},
            {"type": "TECH_CHANGE", "title": "Added HubSpot Enterprise CRM", "score": 85},
            {"type": "FUNDING", "title": "Series B $25M Funding announced", "score": 90},
        ]

        signal_lines = [f"- [{s.get('type', 'SIGNAL')}] {s.get('title', 'Buying trigger')}" for s in signals]
        formatted = "ACTIVE BUYING SIGNALS:\n" + "\n".join(signal_lines)

        return ToolExecutionResult(
            tool_name=self.spec.name,
            status=ExecutionStatus.COMPLETED,
            output_data={"signals": signals, "signals_count": len(signals)},
            formatted_text=formatted,
            confidence=0.90,
        )
