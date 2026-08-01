"""
Swarm Engine API Routes (Phase 5.5.7)
Exposes REST endpoint for triggering autonomous multi-agent revenue swarms.
"""
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends

from app.api.auth import AuthenticatedUser, get_current_user
from app.modules.copilot.swarm_engine.coordinator.swarm_coordinator import swarm_coordinator

swarm_router_api = APIRouter(prefix="", tags=["copilot-swarm"])


@swarm_router_api.post("/swarm/run", response_model=Dict[str, Any])
async def run_revenue_swarm(
    user_query: str = "Analyze target company and generate revenue strategy",
    target_company_id: Optional[str] = None,
    target_deal_id: Optional[str] = None,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    consensus = await swarm_coordinator.execute_swarm(
        workspace_id=current_user.workspace_id,
        user_query=user_query,
        target_company_id=target_company_id,
        target_deal_id=target_deal_id,
    )

    return {
        "swarm_id": consensus.swarm_id,
        "workspace_id": str(consensus.workspace_id),
        "status": consensus.status.value,
        "overall_confidence_score": consensus.overall_confidence_score,
        "aggregated_summary": consensus.aggregated_summary,
        "key_recommendations": consensus.key_recommendations,
        "agent_outputs": {
            role.value: {
                "confidence": res.confidence_score,
                "insights": res.insights,
                "recommendations": res.recommendations,
                "execution_time_ms": res.execution_time_ms,
            }
            for role, res in consensus.agent_results.items()
        },
    }
