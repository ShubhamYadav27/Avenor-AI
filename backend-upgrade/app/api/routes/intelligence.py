"""
app/api/routes/intelligence.py

Phase 4.2 CRM intelligence API routes.
Surfaces outcome attribution, signal effectiveness, and prediction accuracy.
These are the routes that answer "is Avenor actually working?"
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.auth import CurrentUser
from app.db.session import get_db
from app.models import (
    CrmSyncState, HubSpotDeal, OutcomeAttribution,
    SignalEffectiveness,
)

router = APIRouter(prefix="/intelligence", tags=["crm-intelligence"])


@router.get("/attribution")
def get_attribution_summary(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    """
    Attribution summary — evidence that Avenor created value.
    Shows how many deals were predicted, how far ahead, and total attributed revenue.
    """
    from app.modules.outcomes.attribution import get_attribution_summary
    return get_attribution_summary(db, str(current_user.workspace_id))


@router.get("/attribution/deals")
def list_attributed_deals(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    limit: int = Query(20, le=100),
    offset: int = Query(0),
    only_correct: bool = Query(False),
):
    """List individual attribution records — one per predicted outcome."""
    query = (
        db.query(OutcomeAttribution)
        .filter_by(workspace_id=current_user.workspace_id)
    )
    if only_correct:
        query = query.filter(OutcomeAttribution.prediction_was_correct == True)

    total = query.count()
    rows = (
        query
        .order_by(OutcomeAttribution.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    from app.models import Company
    results = []
    for a in rows:
        company = db.get(Company, a.company_id)
        results.append({
            "id": str(a.id),
            "company_name": company.name if company else "Unknown",
            "company_domain": company.domain if company else None,
            "outcome_type": a.outcome_type,
            "predicted_score": a.predicted_score_at_recommendation,
            "predicted_window": a.predicted_window_at_recommendation,
            "prediction_correct": a.prediction_was_correct,
            "deal_value_usd": a.deal_value_usd,
            "days_from_recommendation": a.days_from_recommendation_to_outcome,
            "days_avenor_ahead": a.days_avenor_ahead_of_crm,
            "recommended_at": a.recommended_at.isoformat() if a.recommended_at else None,
            "signals_count": len(a.signals_at_recommendation or []),
            "hubspot_deal_id": a.hubspot_deal_id,
        })

    return {"total": total, "attributions": results}


@router.get("/signal-effectiveness")
def get_signal_effectiveness(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    """
    Signal effectiveness analytics — which signals actually predict revenue?
    Includes lift over baseline and weight recommendations.
    """
    rows = (
        db.query(SignalEffectiveness)
        .filter_by(workspace_id=current_user.workspace_id)
        .order_by(SignalEffectiveness.conversion_rate.desc())
        .all()
    )

    if not rows:
        return {
            "message": "No signal effectiveness data yet. Needs 5+ outcomes per signal type.",
            "signal_effectiveness": [],
        }

    from app.modules.outcomes.feedback_loop import get_scoring_recommendations
    recommendations = get_scoring_recommendations(db, str(current_user.workspace_id))

    return {
        "signal_effectiveness": [
            {
                "signal_type": r.signal_type,
                "total_occurrences": r.total_occurrences,
                "positive_outcomes": r.positive_outcome_count,
                "conversion_rate": r.conversion_rate,
                "lift_over_baseline": r.lift_over_baseline,
                "avg_deal_value_usd": r.avg_deal_value_usd,
                "current_weight": r.current_weight,
                "computed_at": r.computed_at.isoformat(),
            }
            for r in rows
        ],
        "weight_recommendations": recommendations,
    }


@router.get("/accuracy")
def get_prediction_accuracy(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    """
    Full prediction accuracy report.
    Answers: how accurately is Avenor predicting buying cycles?
    """
    from app.modules.outcomes.feedback_loop import get_prediction_accuracy_report
    return get_prediction_accuracy_report(db, str(current_user.workspace_id))


@router.post("/feedback-loop/run")
def trigger_feedback_loop(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    """Manually trigger signal effectiveness computation and attribution for this workspace."""
    current_user.require_admin()

    from app.modules.outcomes.attribution import run_attribution_for_workspace
    attribution_stats = run_attribution_for_workspace(db, str(current_user.workspace_id))

    from app.modules.outcomes.feedback_loop import run_full_feedback_loop
    feedback_result = run_full_feedback_loop(db, str(current_user.workspace_id))

    return {
        "attribution": attribution_stats,
        "feedback_loop": feedback_result,
    }


@router.get("/crm/deals")
def list_crm_deals(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    limit: int = Query(20, le=100),
    offset: int = Query(0),
    closed_won_only: bool = Query(False),
):
    """List HubSpot deals synced into Avenor."""
    query = db.query(HubSpotDeal).filter_by(workspace_id=current_user.workspace_id)
    if closed_won_only:
        query = query.filter(HubSpotDeal.is_closed_won == True)

    total = query.count()
    deals = (
        query
        .order_by(HubSpotDeal.synced_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    from app.models import Company
    return {
        "total": total,
        "deals": [
            {
                "id": str(d.id),
                "hubspot_deal_id": d.hubspot_deal_id,
                "deal_name": d.deal_name,
                "deal_stage": d.deal_stage,
                "amount_usd": d.amount_usd,
                "is_closed_won": d.is_closed_won,
                "is_closed_lost": d.is_closed_lost,
                "days_to_close": d.days_to_close,
                "avenor_predicted_score": d.avenor_predicted_score,
                "avenor_predicted_window": d.avenor_predicted_window,
                "days_ahead_of_crm": d.days_ahead_of_crm,
                "is_historical": d.is_historical,
                "company_name": (
                    db.get(Company, d.company_id).name
                    if d.company_id else None
                ),
                "synced_at": d.synced_at.isoformat(),
            }
            for d in deals
        ],
    }
