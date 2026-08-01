"""
Learning Engine API Routes (Phase 5.5.6)
Exposes endpoints for submitting explicit user feedback, CRM deal conversion outcomes, and querying learning metrics.
"""
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, status
import uuid

from app.api.auth import AuthenticatedUser, get_current_user
from app.modules.copilot.learning_engine.application.engine import learning_engine

learning_router_api = APIRouter(prefix="", tags=["copilot-learning"])


@learning_router_api.post("/feedback", status_code=status.HTTP_201_CREATED)
async def submit_user_feedback(
    feedback_type: str = "thumbs_up",
    rating: float = 1.0,
    thread_id: Optional[uuid.UUID] = None,
    message_id: Optional[uuid.UUID] = None,
    correction_text: Optional[str] = None,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    reward = await learning_engine.submit_user_feedback(
        workspace_id=current_user.workspace_id,
        feedback_type=feedback_type,
        rating=rating,
        thread_id=thread_id,
        message_id=message_id,
        correction_text=correction_text,
        user_id=current_user.user_id,
    )
    return {
        "status": "processed",
        "reward_id": reward.reward_id,
        "reward_score": reward.reward_score,
        "target": reward.target.value,
        "weight_delta": reward.weight_delta,
    }


@learning_router_api.post("/outcomes", status_code=status.HTTP_201_CREATED)
async def submit_deal_outcome(
    outcome_type: str = "deal_won",
    deal_id: Optional[str] = None,
    amount_usd: float = 0.0,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    reward = await learning_engine.submit_crm_outcome(
        workspace_id=current_user.workspace_id,
        outcome_type=outcome_type,
        deal_id=deal_id,
        amount_usd=amount_usd,
    )
    return {
        "status": "processed",
        "reward_id": reward.reward_id,
        "reward_score": reward.reward_score,
        "target": reward.target.value,
        "weight_delta": reward.weight_delta,
    }


@learning_router_api.get("/learning/metrics", response_model=Dict[str, Any])
async def get_learning_metrics(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    pkg = await learning_engine.process_learning_cycle(current_user.workspace_id)
    return {
        "workspace_id": str(pkg.workspace_id),
        "total_feedback_count": pkg.metrics.total_feedback_count,
        "positive_rate": pkg.metrics.positive_rate,
        "reward_average": pkg.metrics.reward_average,
        "drift_status": pkg.metrics.drift_status.value,
        "active_weights_override": pkg.active_weights_override,
        "optimization_summary": pkg.optimization_summary,
    }
