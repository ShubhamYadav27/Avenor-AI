"""
Tool Planner (Phase 5.5.3)
Intent-driven selection of minimum necessary platform business tools.
"""
from typing import List

from app.modules.copilot.domain.context import ContextIntent, UnifiedContext
from app.modules.copilot.domain.interfaces import ITool, IToolPlanner
from app.modules.copilot.domain.tools import ToolExecutionPlan


class ToolPlanner(IToolPlanner):
    def create_plan(
        self,
        intent: ContextIntent,
        context: UnifiedContext,
        available_tools: List[ITool],
    ) -> ToolExecutionPlan:
        selected_tools: List[ITool] = []

        for tool in available_tools:
            if tool.spec.supported_intents and intent in tool.spec.supported_intents:
                selected_tools.append(tool)

        # Fallback if no specific tool matches intent
        if not selected_tools:
            selected_tools = [t for t in available_tools if t.spec.name in ["company_tool", "crm_tool"]]

        selected_names = [t.spec.name for t in selected_tools]
        total_cost = sum(t.spec.cost_score.value for t in selected_tools)

        return ToolExecutionPlan(
            workspace_id=context.workspace_id,
            intent=intent,
            selected_tools=selected_names,
            estimated_total_cost=total_cost,
            estimated_latency_ms=150.0,
        )


tool_planner = ToolPlanner()
