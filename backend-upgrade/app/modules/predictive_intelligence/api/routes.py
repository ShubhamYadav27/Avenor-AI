"""
Predictive Intelligence API Routes (Phase 6.1)
Exposes endpoints for querying account buying windows, win probabilities, and recommendations.
"""
from typing import Any, Dict
from fastapi import APIRouter, Depends

from app.api.auth import AuthenticatedUser, get_current_user
from app.modules.predictive_intelligence.application.engine import predictive_revenue_engine

predictive_router_api = APIRouter(prefix="", tags=["predictive-revenue-intelligence"])


@predictive_router_api.post("/predictive/account-intelligence", response_model=Dict[str, Any])
async def get_account_predictive_intelligence(
    company_id: str = "comp-101",
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    intel = await predictive_revenue_engine.predict_account_intelligence(
        workspace_id=current_user.workspace_id,
        company_id=company_id,
    )

    return {
        "workspace_id": str(current_user.workspace_id),
        "company_id": intel.company_id,
        "company_name": intel.company_name,
        "icp_score": intel.icp_score,
        "buying_window": {
            "stage": intel.buying_window.stage.value,
            "confidence_score": intel.buying_window.confidence_score,
            "intent_surge_score": intel.buying_window.intent_surge_score,
            "hiring_signal_count": intel.buying_window.hiring_signal_count,
            "estimated_window_days": intel.buying_window.estimated_window_days,
        }
        if intel.buying_window
        else None,
        "opportunity_prediction": {
            "deal_id": intel.opportunity_prediction.deal_id,
            "win_probability": intel.opportunity_prediction.win_probability,
            "risk_level": intel.opportunity_prediction.risk_level.value,
            "expected_arr_usd": intel.opportunity_prediction.expected_arr_usd,
        }
        if intel.opportunity_prediction
        else None,
        "recommendations": [
            {
                "recommendation_id": r.recommendation_id,
                "action_type": r.action_type,
                "title": r.title,
                "description": r.description,
                "priority_score": r.priority_score,
                "evidence_citations": r.evidence_citations,
            }
            for r in intel.recommendations
        ],
    }


@predictive_router_api.get("/predictive/buying-windows", response_model=Dict[str, Any])
async def list_buying_windows(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    pkg = await predictive_revenue_engine.generate_prediction_package(
        workspace_id=current_user.workspace_id,
        company_ids=["comp-101", "comp-102", "comp-103"],
    )

    return {
        "workspace_id": str(pkg.workspace_id),
        "total_accounts_analyzed": len(pkg.account_intelligence_list),
        "overall_pipeline_health_score": pkg.overall_pipeline_health_score,
        "execution_time_ms": pkg.execution_time_ms,
        "active_windows": [
            {
                "company_id": item.company_id,
                "icp_score": item.icp_score,
                "buying_stage": item.buying_window.stage.value if item.buying_window else "unknown",
                "win_probability": item.opportunity_prediction.win_probability if item.opportunity_prediction else 0.0,
            }
            for item in pkg.account_intelligence_list
        ],
    }
