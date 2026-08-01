"""
Autonomous Org API Routes (Phase 6.6)
Exposes endpoints for querying platform operating state, health metrics, and configuring governance modes.
"""
from typing import Any, Dict
from fastapi import APIRouter, Depends

from app.api.auth import AuthenticatedUser, get_current_user
from app.modules.autonomous_org.application.service import autonomous_org_service

autonomous_org_router_api = APIRouter(prefix="", tags=["autonomous-revenue-organization"])


@autonomous_org_router_api.get("/autonomous-org/status", response_model=Dict[str, Any])
async def get_autonomous_org_status(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    pkg = await autonomous_org_service.get_platform_status(current_user.workspace_id)
    return {
        "workspace_id": str(pkg.workspace_id),
        "ai_partner_status": pkg.ai_partner_status,
        "execution_time_ms": pkg.execution_time_ms,
        "org_state": {
            "state_id": pkg.org_state.state_id,
            "operating_mode": pkg.org_state.operating_mode.value,
            "active_agents_count": pkg.org_state.active_agents_count,
            "active_missions_count": pkg.org_state.active_missions_count,
            "total_arr_monitored_usd": pkg.org_state.total_arr_monitored_usd,
            "system_uptime_percentage": pkg.org_state.system_uptime_percentage,
        },
        "health_metrics": {
            "rep_productivity_index": pkg.health_metrics.rep_productivity_index,
            "win_rate_velocity": pkg.health_metrics.win_rate_velocity,
            "pipeline_coverage_ratio": pkg.health_metrics.pipeline_coverage_ratio,
            "churn_risk_index": pkg.health_metrics.churn_risk_index,
            "health_tier": pkg.health_metrics.health_tier.value,
        },
        "active_policy": {
            "policy_id": pkg.active_policy.policy_id,
            "auto_approval_threshold_usd": pkg.active_policy.auto_approval_threshold_usd,
            "required_roles_for_overrides": pkg.active_policy.required_roles_for_overrides,
        },
    }


@autonomous_org_router_api.get("/autonomous-org/health", response_model=Dict[str, Any])
async def get_org_health_metrics(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    pkg = await autonomous_org_service.get_platform_status(current_user.workspace_id)
    return {
        "workspace_id": str(current_user.workspace_id),
        "health_metrics": {
            "rep_productivity_index": pkg.health_metrics.rep_productivity_index,
            "win_rate_velocity": pkg.health_metrics.win_rate_velocity,
            "pipeline_coverage_ratio": pkg.health_metrics.pipeline_coverage_ratio,
            "churn_risk_index": pkg.health_metrics.churn_risk_index,
            "health_tier": pkg.health_metrics.health_tier.value,
        },
    }


@autonomous_org_router_api.post("/autonomous-org/mode", response_model=Dict[str, Any])
async def set_org_operating_mode(
    mode: str = "hybrid_governed",
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    pkg = await autonomous_org_service.update_operating_mode(current_user.workspace_id, mode)
    return {
        "workspace_id": str(current_user.workspace_id),
        "operating_mode": pkg.org_state.operating_mode.value,
        "message": f"Autonomous Revenue Organization operating mode updated to {pkg.org_state.operating_mode.value}.",
    }
