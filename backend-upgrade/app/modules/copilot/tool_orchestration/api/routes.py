"""
Tool Orchestration API Routes (Phase 5.5.3)
Exposes endpoints for querying registered tools and tool execution engine metrics.
"""
from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException

from app.modules.copilot.tool_orchestration.infrastructure.registry.registry import tool_registry

tool_router_api = APIRouter(prefix="/tools", tags=["copilot-tools"])


@tool_router_api.get("", response_model=List[Dict[str, Any]])
def list_tools():
    tools = tool_registry.list_all_tools()
    return [
        {
            "name": t.spec.name,
            "display_name": t.spec.display_name,
            "description": t.spec.description,
            "category": t.spec.category,
            "priority": t.spec.priority.name,
            "cost_score": t.spec.cost_score.name,
            "dependencies": t.spec.dependencies,
            "supported_intents": [i.value for i in t.spec.supported_intents],
        }
        for t in tools
    ]


@tool_router_api.get("/{tool_name}", response_model=Dict[str, Any])
def get_tool_details(tool_name: str):
    tool = tool_registry.get_tool(tool_name)
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    return {
        "name": tool.spec.name,
        "display_name": tool.spec.display_name,
        "description": tool.spec.description,
        "category": tool.spec.category,
        "priority": tool.spec.priority.name,
        "cost_score": tool.spec.cost_score.name,
        "dependencies": tool.spec.dependencies,
        "timeout_seconds": tool.spec.timeout_seconds,
        "supported_intents": [i.value for i in tool.spec.supported_intents],
    }
