"""
Workflow Engine API Routes (Phase 5.5.7)
Exposes endpoints for executing enterprise workflows and listing workflow definitions.
"""
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends

from app.api.auth import AuthenticatedUser, get_current_user
from app.modules.copilot.workflow_engine.application.engine import workflow_engine
from app.modules.copilot.workflow_engine.application.planners.workflow_planner import workflow_planner

workflow_router_api = APIRouter(prefix="", tags=["copilot-workflows"])


@workflow_router_api.post("/workflows/execute", response_model=Dict[str, Any])
async def execute_workflow(
    workflow_name: str = "meeting_prep",
    context_data: Optional[Dict[str, Any]] = None,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    pkg = await workflow_engine.execute_workflow(
        workspace_id=current_user.workspace_id,
        workflow_name=workflow_name,
        context_data=context_data,
    )

    return {
        "execution_id": pkg.execution_id,
        "workspace_id": str(pkg.workspace_id),
        "workflow_name": pkg.workflow_name,
        "status": pkg.status.value,
        "summary": pkg.summary,
        "steps_completed": pkg.steps_completed,
        "total_steps": pkg.total_steps,
        "execution_time_ms": pkg.execution_time_ms,
    }


@workflow_router_api.get("/workflows/definitions", response_model=Dict[str, Any])
async def list_workflow_definitions(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    presets = workflow_planner.get_preset_definitions()
    return {
        "workspace_id": str(current_user.workspace_id),
        "total_definitions": len(presets),
        "workflows": [
            {
                "id": defn.id,
                "name": defn.name,
                "description": defn.description,
                "trigger_type": defn.trigger_type.value,
                "total_steps": len(defn.steps),
                "is_active": defn.is_active,
                "version": defn.version,
            }
            for defn in presets.values()
        ],
    }
