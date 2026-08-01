"""
Revenue Decision API Routes (Phase 6.2)
Exposes endpoints for Next Best Action decisions, policy inspection, and action plans.
"""
from typing import Any, Dict
from fastapi import APIRouter, Depends

from app.api.auth import AuthenticatedUser, get_current_user
from app.modules.revenue_decision.application.engine import revenue_decision_engine
from app.modules.revenue_decision.application.engines.policy_engine import policy_engine

decision_router_api = APIRouter(prefix="", tags=["revenue-decisions"])


@decision_router_api.post("/decisions/next-best-action", response_model=Dict[str, Any])
async def get_next_best_action_decision(
    company_id: str = "comp-101",
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    pkg = await revenue_decision_engine.decide_next_best_action(
        workspace_id=current_user.workspace_id,
        company_id=company_id,
    )

    act = pkg.action_plan

    return {
        "session_id": pkg.session_id,
        "workspace_id": str(pkg.workspace_id),
        "company_id": pkg.company_id,
        "execution_time_ms": pkg.execution_time_ms,
        "primary_action": {
            "plan_id": act.plan_id,
            "urgency": act.urgency.value,
            "recommended_channel": act.recommended_channel.value,
            "optimal_timing": act.optimal_timing,
            "target_contact": {
                "contact_id": act.target_contact.contact_id,
                "name": act.target_contact.name,
                "title": act.target_contact.title,
                "persona_match_score": act.target_contact.persona_match_score,
                "decision_reason": act.target_contact.decision_reason,
            }
            if act.target_contact
            else None,
            "recommended_play": {
                "play_id": act.play.play_id,
                "play_name": act.play.play_name,
                "description": act.play.description,
                "recommended_collateral": act.play.recommended_collateral,
                "expected_conversion_lift": act.play.expected_conversion_lift,
            }
            if act.play
            else None,
            "explanation": {
                "summary": act.explanation.summary,
                "trade_offs_considered": act.explanation.trade_offs_considered,
                "primary_rationale": act.explanation.primary_rationale,
                "evidence_citations": act.explanation.evidence_citations,
            }
            if act.explanation
            else None,
        },
    }


@decision_router_api.get("/decisions/policies", response_model=Dict[str, Any])
async def get_active_decision_policies(
    company_id: str = "comp-101",
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    policies = policy_engine.evaluate_policies(company_id)
    return {
        "workspace_id": str(current_user.workspace_id),
        "total_active_policies": len(policies),
        "policies": [
            {
                "policy_id": p.policy_id,
                "policy_name": p.policy_name,
                "mode": p.mode.value,
                "rule_expression": p.rule_expression,
                "is_active": p.is_active,
            }
            for p in policies
        ],
    }
