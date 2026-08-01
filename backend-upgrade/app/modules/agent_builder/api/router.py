from fastapi import APIRouter
from typing import List, Dict, Any

from app.modules.agent_builder.domain.models import Agent, AgentStatus, TaskStatus
from app.modules.agent_builder.application.services import AgentOrchestrator

router = APIRouter(prefix="/v1/agents", tags=["Enterprise Agent Builder"])

# Pre-seed for demonstration
_agents = [
    Agent(
        id="ag_research",
        workspace_id="ws_001",
        name="Company Intelligence Agent",
        role="Senior Research Analyst",
        prompt_id="pt_research",
        allowed_tools=["public_api.get_company"]
    ),
    Agent(
        id="ag_writer",
        workspace_id="ws_001",
        name="Executive Briefing Agent",
        role="Strategic Content Writer",
        prompt_id="pt_writer",
        allowed_tools=["workflow.start_approval"]
    )
]

_orchestrator = AgentOrchestrator(agents=_agents)

@router.get("/")
async def list_agents(workspace_id: str) -> List[dict]:
    """List all configured autonomous agents."""
    return [{"id": a.id, "name": a.name, "role": a.role} 
            for a in _orchestrator.agents.values() if a.workspace_id == workspace_id]

@router.post("/execute")
async def dispatch_goal(payload: Dict[str, Any]) -> dict:
    """Dispatches a high-level goal to the Multi-Agent Team."""
    goal = payload.get("goal")
    if not goal:
        return {"error": "Goal is required."}
        
    plan = _orchestrator.dispatch_goal(goal)
    
    return {
        "plan_id": plan.id,
        "status": plan.status.value,
        "tasks": [
            {
                "id": t.id,
                "description": t.description,
                "assigned_agent": _orchestrator.agents[t.assigned_agent_id].name,
                "status": t.status.value,
                "result": t.result
            } for t in plan.tasks
        ]
    }
