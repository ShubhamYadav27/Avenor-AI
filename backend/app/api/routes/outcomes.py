"""
Outcomes routes — log and retrieve buying outcome feedback.
This is the fuel for the data moat. Every logged outcome trains the model.
"""
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.auth import CurrentUser
from app.db.session import get_db
from app.models import Company, Outcome, OutcomeType, OutcomeSource, Signal

router = APIRouter(prefix="/outcomes", tags=["outcomes"])


class LogOutcomeRequest(BaseModel):
    company_id: str
    outcome_type: str
    notes: Optional[str] = None
    deal_value_usd: Optional[float] = None
    days_ahead_of_organic_discovery: Optional[int] = None
    occurred_at: Optional[datetime] = None


@router.post("")
def log_outcome(
    req: LogOutcomeRequest,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    """
    Log an outcome for a company.
    This is the single most important action a user can take —
    every outcome trains the predictive model.
    """
    valid_types = {t.value for t in OutcomeType}
    if req.outcome_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid outcome_type. Valid: {valid_types}")

    company = db.get(Company, req.company_id)
    if not company or str(company.workspace_id) != str(current_user.workspace_id):
        raise HTTPException(status_code=404, detail="Company not found")

    # Snapshot current signals for training data
    signals = db.query(Signal).filter_by(company_id=req.company_id).all()
    signals_snapshot = [
        {"type": s.signal_type, "strength": s.decayed_strength, "detected_at": s.detected_at.isoformat()}
        for s in signals
    ]

    # Days from first signal to outcome
    days_from_first = None
    if signals:
        earliest = min(s.detected_at for s in signals)
        earliest_aware = earliest if earliest.tzinfo else earliest.replace(tzinfo=timezone.utc)
        days_from_first = (datetime.now(timezone.utc) - earliest_aware).days

    outcome = Outcome(
        workspace_id=current_user.workspace_id,
        company_id=req.company_id,
        outcome_type=req.outcome_type,
        outcome_source=OutcomeSource.MANUAL,
        predicted_composite_score=company.composite_score,
        predicted_buying_window=company.buying_window,
        active_signals_snapshot=signals_snapshot,
        days_from_first_signal=days_from_first,
        days_ahead_of_organic_discovery=req.days_ahead_of_organic_discovery,
        deal_value_usd=req.deal_value_usd,
        notes=req.notes,
        occurred_at=req.occurred_at or datetime.now(timezone.utc),
    )
    db.add(outcome)

    # Update company status for positive outcomes
    positive_values = {
        OutcomeType.BECAME_OPPORTUNITY.value, OutcomeType.MEETING_BOOKED.value,
        OutcomeType.REPLIED_POSITIVE.value, OutcomeType.CLOSED_WON.value,
    }
    if req.outcome_type in positive_values:
        from app.models import CompanyStatus
        company.status = CompanyStatus.CONVERTED

    db.commit()
    db.refresh(outcome)

    return {
        "success": True,
        "outcome_id": str(outcome.id),
        "message": "Outcome logged. This data will improve your model accuracy.",
        "training_data_point": {
            "company": company.name,
            "predicted_score": company.composite_score,
            "predicted_window": company.buying_window,
            "actual_outcome": req.outcome_type,
            "signals_active": len(signals_snapshot),
        },
    }


@router.get("")
def list_outcomes(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    outcome_type: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
):
    """List outcomes for the workspace."""
    query = db.query(Outcome).filter_by(workspace_id=current_user.workspace_id)
    if outcome_type:
        query = query.filter(Outcome.outcome_type == outcome_type)

    total = query.count()
    outcomes = (
        query
        .order_by(Outcome.occurred_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "outcomes": [
            {
                "id": str(o.id),
                "company_id": str(o.company_id),
                "outcome_type": o.outcome_type,
                "outcome_source": o.outcome_source,
                "predicted_score": o.predicted_composite_score,
                "predicted_window": o.predicted_buying_window,
                "deal_value_usd": o.deal_value_usd,
                "days_from_first_signal": o.days_from_first_signal,
                "days_ahead_of_organic_discovery": o.days_ahead_of_organic_discovery,
                "notes": o.notes,
                "occurred_at": o.occurred_at.isoformat(),
            }
            for o in outcomes
        ],
    }


@router.get("/model-accuracy")
def get_model_accuracy(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    """
    Show model accuracy stats for this workspace.
    Answers: how often did Avenor correctly predict a buying window?
    """
    from sqlalchemy import func

    outcomes = db.query(Outcome).filter_by(workspace_id=current_user.workspace_id).all()

    if not outcomes:
        return {
            "message": "No outcomes logged yet. Start logging outcomes to see model accuracy.",
            "outcomes_needed": 20,
            "outcomes_logged": 0,
        }

    positive_types = {
        OutcomeType.BECAME_OPPORTUNITY.value, OutcomeType.MEETING_BOOKED.value,
        OutcomeType.REPLIED_POSITIVE.value, OutcomeType.CLOSED_WON.value,
    }

    total = len(outcomes)
    positive = [o for o in outcomes if o.outcome_type in positive_types]
    with_scores = [o for o in positive if o.predicted_composite_score is not None]

    # Precision: how many high-score predictions were actually positive?
    high_score_positives = sum(
        1 for o in positive if o.predicted_composite_score and o.predicted_composite_score >= 0.5
    )
    high_score_total = sum(
        1 for o in outcomes if o.predicted_composite_score and o.predicted_composite_score >= 0.5
    )

    precision = round(high_score_positives / high_score_total, 3) if high_score_total > 0 else None

    avg_days_ahead = None
    if any(o.days_ahead_of_organic_discovery for o in outcomes):
        vals = [o.days_ahead_of_organic_discovery for o in outcomes if o.days_ahead_of_organic_discovery]
        avg_days_ahead = round(sum(vals) / len(vals), 1)

    sw = current_user.workspace.signal_weights
    return {
        "total_outcomes": total,
        "positive_outcomes": len(positive),
        "positive_rate": round(len(positive) / total, 3),
        "model_precision": precision,
        "avg_days_ahead_of_organic_discovery": avg_days_ahead,
        "model_trained": sw.last_trained_at.isoformat() if sw and sw.last_trained_at else None,
        "model_accuracy": sw.model_accuracy if sw else None,
        "training_sample_size": sw.training_sample_size if sw else 0,
        "outcomes_until_training": max(0, 20 - total),
    }
