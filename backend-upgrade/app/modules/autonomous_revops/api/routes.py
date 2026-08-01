"""
Autonomous RevOps API Routes (Phase 6.3)
Exposes endpoints for creating autonomous missions, listing active missions, and approving pending requests.
"""
from typing import Any, Dict, List
from fastapi import APIRouter, Depends

from app.api.auth import AuthenticatedUser, get_current_user
from app.modules.autonomous_revops.application.engine import autonomous_revops_engine

revops_router_api = APIRouter(prefix="", tags=["autonomous-revops"])


@revops_router_api.post("/revops/missions/create", response_model=Dict[str, Any])
async def create_autonomous_mission(
    mission_type: str = "pipeline_optimization",
    target_company_ids: List[str] = ["comp-101", "comp-102"],
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    pkg = await autonomous_revops_engine.plan_and_execute_mission(
        workspace_id=current_user.workspace_id,
        mission_type=mission_type,
        target_company_ids=target_company_ids,
    )

    mission = pkg.active_missions[0] if pkg.active_missions else None

    return {
        "session_id": pkg.session_id,
        "workspace_id": str(pkg.workspace_id),
        "execution_time_ms": pkg.execution_time_ms,
        "executed_tasks": pkg.executed_tasks,
        "mission": {
            "mission_id": mission.mission_id,
            "name": mission.name,
            "mission_type": mission.mission_type.value,
            "status": mission.status.value,
            "target_company_ids": mission.target_company_ids,
            "strategy": mission.plan.strategy_description if mission.plan else "",
        }
        if mission
        else None,
        "pending_approvals": [
            {
                "request_id": req.request_id,
                "action_title": req.action_title,
                "description": req.description,
                "required_role": req.required_role,
                "approval_state": req.approval_state.value,
            }
            for req in pkg.pending_approvals
        ],
    }


@revops_router_api.get("/revops/missions", response_model=Dict[str, Any])
async def list_active_missions(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    pkg = await autonomous_revops_engine.plan_and_execute_mission(
        workspace_id=current_user.workspace_id,
        mission_type="pipeline_optimization",
        target_company_ids=["comp-101"],
    )

    return {
        "workspace_id": str(current_user.workspace_id),
        "total_active_missions": len(pkg.active_missions),
        "missions": [
            {
                "mission_id": m.mission_id,
                "name": m.name,
                "mission_type": m.mission_type.value,
                "status": m.status.value,
                "target_companies_count": len(m.target_company_ids),
            }
            for m in pkg.active_missions
        ],
    }
