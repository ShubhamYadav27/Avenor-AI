"""
Strategic Intelligence API Routes (Phase 6.5 & 6.6)
Exposes endpoints for executive advisory, board briefings, strategic revenue planning, territory optimization, scenario simulations, and forecasts.
"""
from typing import Any, Dict
from fastapi import APIRouter, Depends

from app.api.auth import AuthenticatedUser, get_current_user
from app.modules.strategic_intelligence.application.service import strategic_intelligence_service

strategic_router_api = APIRouter(prefix="", tags=["strategic-revenue-intelligence"])


@strategic_router_api.get("/strategic/autonomous-status", response_model=Dict[str, Any])
async def get_autonomous_revenue_org_status(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    pkg = await strategic_intelligence_service.generate_autonomous_org_status(current_user.workspace_id)
    return {
        "workspace_id": str(pkg.workspace_id),
        "operating_state": pkg.operating_state.value,
        "ai_partner_status": pkg.ai_partner_status,
        "execution_time_ms": pkg.execution_time_ms,
        "capacity_plan": {
            "rep_capacity_utilization": pkg.capacity_plan.rep_capacity_utilization,
            "recommended_headcount_delta": pkg.capacity_plan.recommended_headcount_delta,
            "avg_deals_per_rep": pkg.capacity_plan.avg_deals_per_rep,
            "bottleneck_risk": pkg.capacity_plan.bottleneck_risk,
        }
        if pkg.capacity_plan
        else None,
        "territory_plans": [
            {
                "territory_name": t.territory_name,
                "assigned_reps": t.assigned_reps,
                "target_pipeline_usd": t.target_pipeline_usd,
                "active_buying_windows": t.active_buying_windows,
                "recommended_rep_reallocations": t.recommended_rep_reallocations,
            }
            for t in pkg.territory_plans
        ],
        "simulations": [
            {
                "scenario_id": s.scenario_id,
                "scenario_name": s.scenario_name,
                "scenario_type": s.scenario_type.value,
                "win_rate_delta": s.win_rate_delta,
                "pipeline_coverage": s.pipeline_coverage,
                "projected_arr_usd": s.projected_arr_usd,
                "confidence_score": s.confidence_score,
            }
            for s in pkg.simulations
        ],
        "recommendations": [
            {
                "recommendation_id": r.recommendation_id,
                "title": r.title,
                "impact_usd": r.impact_usd,
                "urgency": r.urgency,
                "rationale": r.rationale,
                "confidence_score": r.confidence_score,
            }
            for r in pkg.recommendations
        ],
        "risks": [
            {
                "risk_id": r.risk_id,
                "category": r.category.value,
                "severity": r.severity,
                "impacted_pipeline_usd": r.impacted_pipeline_usd,
                "mitigation_strategy": r.mitigation_strategy,
            }
            for r in pkg.risks
        ],
    }


@strategic_router_api.post("/strategic/briefing", response_model=Dict[str, Any])
async def generate_executive_board_briefing(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    briefing = await strategic_intelligence_service.generate_executive_briefing(current_user.workspace_id)
    return {
        "workspace_id": str(current_user.workspace_id),
        "briefing_id": briefing.briefing_id,
        "title": briefing.title,
        "summary": briefing.summary,
        "key_takeaways": briefing.key_takeaways,
        "risk_summary": briefing.risk_summary,
        "recommended_initiatives": briefing.recommended_initiatives,
        "generated_at": briefing.generated_at.isoformat(),
    }


@strategic_router_api.post("/strategic/simulate-scenario", response_model=Dict[str, Any])
async def simulate_revenue_scenarios(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    sims = await strategic_intelligence_service.run_scenario_simulations(current_user.workspace_id)
    return {
        "workspace_id": str(current_user.workspace_id),
        "simulations_count": len(sims),
        "simulations": [
            {
                "scenario_id": s.scenario_id,
                "scenario_name": s.scenario_name,
                "scenario_type": s.scenario_type.value,
                "win_rate_delta": s.win_rate_delta,
                "pipeline_coverage": s.pipeline_coverage,
                "projected_arr_usd": s.projected_arr_usd,
                "confidence_score": s.confidence_score,
            }
            for s in sims
        ],
    }


@strategic_router_api.get("/strategic/forecast", response_model=Dict[str, Any])
async def get_quarterly_forecast(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    fcst = await strategic_intelligence_service.get_quarterly_forecast(current_user.workspace_id)
    return {
        "workspace_id": str(current_user.workspace_id),
        "forecast_id": fcst.forecast_id,
        "fiscal_quarter": fcst.fiscal_quarter,
        "commit_usd": fcst.commit_usd,
        "best_case_usd": fcst.best_case_usd,
        "pipeline_coverage_ratio": fcst.pipeline_coverage_ratio,
        "win_rate_percentage": fcst.win_rate_percentage,
    }


@strategic_router_api.get("/strategic/recommendations", response_model=Dict[str, Any])
async def get_strategic_recommendations(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    recs = await strategic_intelligence_service.get_strategic_recommendations(current_user.workspace_id)
    return {
        "workspace_id": str(current_user.workspace_id),
        "recommendations_count": len(recs),
        "recommendations": [
            {
                "recommendation_id": r.recommendation_id,
                "title": r.title,
                "impact_usd": r.impact_usd,
                "urgency": r.urgency,
                "rationale": r.rationale,
                "confidence_score": r.confidence_score,
            }
            for r in recs
        ],
    }
