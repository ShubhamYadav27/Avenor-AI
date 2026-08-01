"""
Tool Registry (Phase 5.5.3 Infrastructure)
Dynamic tool discovery and registration without modifying orchestration logic.
"""
from typing import Dict, List, Optional

from app.modules.copilot.domain.context import ContextIntent
from app.modules.copilot.domain.interfaces import ITool, IToolRegistry
from app.modules.copilot.tool_orchestration.application.tools.briefing_tool import BriefingTool
from app.modules.copilot.tool_orchestration.application.tools.company_tool import CompanyTool
from app.modules.copilot.tool_orchestration.application.tools.crm_tool import CrmTool
from app.modules.copilot.tool_orchestration.application.tools.email_tool import EmailTool
from app.modules.copilot.tool_orchestration.application.tools.feed_tool import FeedTool
from app.modules.copilot.tool_orchestration.application.tools.research_tool import ResearchTool
from app.modules.copilot.tool_orchestration.application.tools.sales_coach_tool import SalesCoachTool
from app.modules.copilot.tool_orchestration.application.tools.signal_tool import SignalTool


class ToolRegistry(IToolRegistry):
    def __init__(self):
        self._tools: Dict[str, ITool] = {}

    def register_tool(self, tool: ITool) -> None:
        self._tools[tool.spec.name] = tool

    def get_tool(self, name: str) -> Optional[ITool]:
        return self._tools.get(name)

    def get_tools_for_intent(self, intent: ContextIntent) -> List[ITool]:
        matching: List[ITool] = []
        for tool in self._tools.values():
            if not tool.spec.supported_intents or intent in tool.spec.supported_intents:
                matching.append(tool)
        return matching

    def list_all_tools(self) -> List[ITool]:
        return list(self._tools.values())

    @classmethod
    def create_default_registry(cls) -> "ToolRegistry":
        registry = cls()
        registry.register_tool(CompanyTool())
        registry.register_tool(SignalTool())
        registry.register_tool(CrmTool())
        registry.register_tool(ResearchTool())
        registry.register_tool(BriefingTool())
        registry.register_tool(SalesCoachTool())
        registry.register_tool(EmailTool())
        registry.register_tool(FeedTool())
        return registry


tool_registry = ToolRegistry.create_default_registry()
