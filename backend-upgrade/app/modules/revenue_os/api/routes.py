"""
Revenue OS API Routes (Phase 6.6)
Exposes endpoints for Revenue OS Kernel status, Executive Command Center, Capability Assessment, and Policy Configuration.
"""
from typing import Any, Dict
from fastapi import APIRouter, Depends

from app.api.auth import AuthenticatedUser, get_current_user
from app.modules.revenue_os.application.coordinators.executive_coordination_engine import executive_coordination_engine
from app.modules.revenue_os.application.coordinators.intelligence_coordinator import intelligence_coordinator
from app.modules.revenue_os.application.engine import revenue_os_engine
from app.modules.revenue_os.application.managers.capability_manager import capability_manager

revenue_os_router_api = APIRouter(prefix="", tags=["avenor-revenue-operating-system"])


@revenue_os_router_api.get("/revenue-os/kernel/status", response_model=Dict[str, Any])
async def get_revenue_os_kernel_status(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    pkg = await revenue_os_engine.get_operating_system_status(current_user.workspace_id)
    subsystems = intelligence_coordinator.get_subsystem_health()

    return {
        "workspace_id": str(pkg.workspace_id),
        "executive_summary": pkg.executive_summary,
        "execution_time_ms": pkg.execution_time_ms,
        "org_state": {
            "state_id": pkg.org_state.state_id,
            "operating_mode": pkg.org_state.operating_mode.value,
            "global_health_index": pkg.org_state.global_health_index,
            "active_missions_count": pkg.org_state.active_missions_count,
            "active_agents_count": pkg.org_state.active_agents_count,
            "uptime_percentage": pkg.org_state.uptime_percentage,
        },
        "health_metrics": {
            "rep_productivity_index": pkg.health_metrics.rep_productivity_index,
            "win_rate_velocity": pkg.health_metrics.win_rate_velocity,
            "pipeline_coverage_ratio": pkg.health_metrics.pipeline_coverage_ratio,
            "churn_risk_index": pkg.health_metrics.churn_risk_index,
            "health_tier": pkg.health_metrics.health_tier.value,
        },
        "subsystems_health": subsystems,
    }


@revenue_os_router_api.get("/revenue-os/executive/command-center", response_model=Dict[str, Any])
async def get_executive_command_center(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    cmd = executive_coordination_engine.generate_command_center_snapshot(current_user.workspace_id)
    insights = executive_coordination_engine.get_executive_insights()

    return {
        "workspace_id": str(current_user.workspace_id),
        "title": cmd.title,
        "summary": cmd.ceo_dashboard_summary,
        "insights_count": len(insights),
        "insights": [
            {
                "insight_id": ins.insight_id,
                "category": ins.category,
                "severity": ins.severity,
                "message": ins.message,
                "recommendation": ins.recommendation,
            }
            for ins in insights
        ],
    }


@revenue_os_router_api.get("/revenue-os/capabilities", response_model=Dict[str, Any])
async def get_organization_capabilities(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    caps = capability_manager.get_capabilities()
    bottlenecks = capability_manager.get_capability_health()

    return {
        "workspace_id": str(current_user.workspace_id),
        "capabilities_count": len(caps),
        "capabilities": [
            {
                "capability_id": c.capability_id,
                "name": c.name,
                "status": c.status.value,
                "health_index": c.health_index,
                "readiness_score": c.readiness_score,
            }
            for c in caps
        ],
        "bottlenecks": [
            {
                "capability_name": b.capability_name,
                "status": b.status.value,
                "health_score": b.health_score,
                "bottleneck_notes": b.bottleneck_notes,
            }
            for b in bottlenecks
        ],
    }


@revenue_os_router_api.post("/revenue-os/policy/configure", response_model=Dict[str, Any])
async def configure_revenue_policy(
    mode: str = "hybrid_governed",
    auto_approval_threshold_usd: float = 100000.0,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    pkg = await revenue_os_engine.update_operating_mode(current_user.workspace_id, mode)
    return {
        "workspace_id": str(current_user.workspace_id),
        "operating_mode": pkg.org_state.operating_mode.value,
        "auto_approval_threshold_usd": auto_approval_threshold_usd,
        "message": f"Revenue OS Policy updated to {pkg.org_state.operating_mode.value} with auto-approval threshold ${auto_approval_threshold_usd:,.2f}.",
    }
