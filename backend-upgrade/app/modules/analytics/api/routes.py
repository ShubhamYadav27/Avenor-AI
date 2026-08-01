"""
Analytics API Routes (Phase 5.6)
Exposes endpoints for predictive pipeline forecasting and account buying intent heatmaps.
"""
from typing import Any, Dict
from fastapi import APIRouter, Depends

from app.api.auth import AuthenticatedUser, get_current_user
from app.modules.analytics.application.services.forecast_service import forecast_service
from app.modules.analytics.application.services.heatmap_service import heatmap_service

analytics_router_api = APIRouter(prefix="", tags=["analytics"])


@analytics_router_api.get("/analytics/pipeline-forecast", response_model=Dict[str, Any])
async def get_pipeline_forecast(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    forecast = forecast_service.calculate_predictive_forecast(current_user.workspace_id)
    return {
        "workspace_id": str(forecast.workspace_id),
        "total_pipeline_usd": forecast.total_pipeline_usd,
        "commit_usd": forecast.commit_usd,
        "best_case_usd": forecast.best_case_usd,
        "weighted_forecast_usd": forecast.weighted_forecast_usd,
        "win_probability_avg": forecast.win_probability_avg,
    }


@analytics_router_api.get("/analytics/intent-heatmap", response_model=Dict[str, Any])
async def get_intent_heatmap(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    heatmaps = heatmap_service.get_workspace_intent_heatmaps(current_user.workspace_id)
    return {
        "workspace_id": str(current_user.workspace_id),
        "total_accounts": len(heatmaps),
        "heatmaps": [
            {
                "company_id": h.company_id,
                "company_name": h.company_name,
                "intent_score": h.intent_score,
                "signal_count": h.signal_count,
                "surge_tier": h.surge_tier.value,
                "primary_topic": h.primary_topic,
            }
            for h in heatmaps
        ],
    }
