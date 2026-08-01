"""
Agent Framework API Routes (Phase 5.5.8)
Exposes endpoints for executing enterprise multi-agent collaborations and inspecting agent registries.
"""
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends

from app.api.auth import AuthenticatedUser, get_current_user
from app.modules.copilot.agent_framework.application.engine import multi_agent_engine
from app.modules.copilot.agent_framework.application.registry.agent_registry import agent_registry

agent_framework_router_api = APIRouter(prefix="", tags=["copilot-agent-framework"])


@agent_framework_router_api.post("/agents/collaborate", response_model=Dict[str, Any])
async def execute_multi_agent_collaboration(
    user_query: str = "Prepare executive meeting strategy for target account",
    target_entity_id: Optional[str] = None,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    pkg = await multi_agent_engine.execute_collaboration(
        workspace_id=current_user.workspace_id,
        user_query=user_query,
        target_entity_id=target_entity_id,
    )

    return {
        "session_id": pkg.session_id,
        "workspace_id": str(pkg.workspace_id),
        "executive_summary": pkg.executive_summary,
        "total_agents_engaged": pkg.total_agents_engaged,
        "overall_confidence": pkg.consensus.overall_confidence,
        "key_recommendations": pkg.consensus.key_recommendations,
        "execution_time_ms": pkg.execution_time_ms,
        "agent_outputs": {
            role.value: {
                "confidence": res.confidence_score,
                "insights": res.insights,
                "recommendations": res.recommendations,
                "citations": res.citations,
                "execution_time_ms": res.execution_time_ms,
            }
            for role, res in pkg.consensus.agent_responses.items()
        },
    }


@agent_framework_router_api.get("/agents/registry", response_model=Dict[str, Any])
async def list_registered_agents(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    agents = agent_registry.list_agents()
    return {
        "workspace_id": str(current_user.workspace_id),
        "total_agents": len(agents),
        "agents": [
            {
                "agent_id": a.agent_id,
                "name": a.name,
                "agent_type": a.agent_type.value,
                "confidence_score": a.confidence_score,
                "is_active": a.is_active,
                "capabilities": [
                    {"id": c.capability_id, "name": c.name, "description": c.description}
                    for c in a.capabilities
                ],
            }
            for a in agents
        ],
    }
