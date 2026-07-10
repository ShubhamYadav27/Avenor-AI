"""
app/modules/outcomes/attribution.py

Outcome Attribution Engine.
Connects every closed CRM deal back to:
  - The original buying signals that triggered the recommendation
  - The composite score Avenor assigned at prediction time
  - The specific intelligence feed item the seller saw
  - How far ahead of the CRM Avenor detected the account

This is the evidence layer: it proves Avenor created value, not just observed it.
Runs after every HubSpot sync that closes deals.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models import (
    Company, HubSpotDeal, IntelligenceFeedItem, Outcome,
    OutcomeAttribution, Signal, Workspace,
)

logger = get_logger(__name__)

POSITIVE_OUTCOME_TYPES = {
    "became_opportunity", "meeting_booked",
    "replied_positive", "closed_won",
}


def attribute_outcome(
    db: Session,
    workspace_id: str,
    outcome: Outcome,
) -> OutcomeAttribution | None:
    """
    Create an OutcomeAttribution for a single Outcome record.
    Finds the most relevant IntelligenceFeedItem and builds the attribution chain.
    Returns None if the company has no Avenor signals (pure CRM-originated deal).
    """
    company = db.get(Company, outcome.company_id)
    if not company:
        return None

    # Check for existing attribution (idempotent)
    existing = (
        db.query(OutcomeAttribution)
        .filter_by(workspace_id=workspace_id, outcome_id=outcome.id)
        .first()
    )
    if existing:
        return existing

    # Find signals active at recommendation time
    signals = db.query(Signal).filter_by(company_id=outcome.company_id).all()
    if not signals:
        # No Avenor signals means we can't attribute — it's a pure CRM deal
        logger.debug(
            "attribution_skipped_no_signals",
            company=company.name,
            outcome_id=str(outcome.id),
        )
        return None

    signals_at_rec = [
        {
            "type": s.signal_type,
            "title": s.title,
            "strength": round(s.decayed_strength, 3),
            "detected_at": s.detected_at.isoformat(),
        }
        for s in sorted(signals, key=lambda x: x.decayed_strength, reverse=True)[:5]
    ]

    # Find the most recent IntelligenceFeedItem for this company
    feed_item = (
        db.query(IntelligenceFeedItem)
        .filter_by(company_id=outcome.company_id)
        .order_by(IntelligenceFeedItem.generated_at.desc())
        .first()
    )

    recommended_at = feed_item.generated_at if feed_item else None
    predicted_score = (
        outcome.predicted_composite_score
        or (feed_item.composite_score if feed_item else None)
        or company.composite_score
    )
    predicted_window = (
        outcome.predicted_buying_window
        or (feed_item.buying_window if feed_item else None)
        or company.buying_window
    )

    # Days from recommendation to outcome
    days_from_rec = None
    if recommended_at and outcome.occurred_at:
        rec_dt = recommended_at.replace(tzinfo=timezone.utc) if recommended_at.tzinfo is None else recommended_at
        occ_dt = outcome.occurred_at.replace(tzinfo=timezone.utc) if outcome.occurred_at.tzinfo is None else outcome.occurred_at
        days_from_rec = max((occ_dt - rec_dt).days, 0)

    # Days Avenor was ahead of CRM discovery
    days_ahead = outcome.days_ahead_of_organic_discovery
    if days_ahead is None:
        # Try from HubSpotDeal
        hs_deal = (
            db.query(HubSpotDeal)
            .filter_by(
                workspace_id=workspace_id,
                hubspot_deal_id=outcome.hubspot_deal_id,
            )
            .first()
        ) if outcome.hubspot_deal_id else None
        if hs_deal:
            days_ahead = hs_deal.days_ahead_of_crm

    # Was prediction correct?
    # Prediction correct = Avenor scored > 0.5 AND it converted positively
    prediction_correct = (
        predicted_score is not None
        and predicted_score >= 0.5
        and outcome.outcome_type in POSITIVE_OUTCOME_TYPES
    )

    attribution = OutcomeAttribution(
        workspace_id=workspace_id,
        company_id=outcome.company_id,
        outcome_id=outcome.id,
        hubspot_deal_id=outcome.hubspot_deal_id,
        feed_item_id=feed_item.id if feed_item else None,
        predicted_score_at_recommendation=predicted_score,
        predicted_window_at_recommendation=predicted_window,
        recommended_at=recommended_at,
        signals_at_recommendation=signals_at_rec,
        outcome_type=outcome.outcome_type,
        deal_value_usd=outcome.deal_value_usd,
        days_from_recommendation_to_outcome=days_from_rec,
        days_avenor_ahead_of_crm=days_ahead,
        prediction_was_correct=prediction_correct,
    )
    db.add(attribution)
    db.flush()

    logger.info(
        "outcome_attributed",
        company=company.name,
        outcome_type=outcome.outcome_type,
        predicted_score=predicted_score,
        prediction_correct=prediction_correct,
        days_ahead=days_ahead,
        workspace_id=workspace_id,
    )
    return attribution


def run_attribution_for_workspace(db: Session, workspace_id: str) -> dict:
    """
    Attribute all un-attributed outcomes for a workspace.
    Safe to run repeatedly — idempotent per outcome.
    """
    # Find outcomes without attribution
    attributed_outcome_ids = {
        str(a.outcome_id)
        for a in db.query(OutcomeAttribution)
        .filter_by(workspace_id=workspace_id)
        .all()
        if a.outcome_id
    }

    all_outcomes = (
        db.query(Outcome)
        .filter_by(workspace_id=workspace_id)
        .all()
    )

    unattributed = [
        o for o in all_outcomes
        if str(o.id) not in attributed_outcome_ids
    ]

    stats = {"processed": 0, "attributed": 0, "skipped": 0, "errors": 0}

    for outcome in unattributed:
        stats["processed"] += 1
        try:
            result = attribute_outcome(db, workspace_id, outcome)
            if result:
                stats["attributed"] += 1
            else:
                stats["skipped"] += 1
        except Exception as e:
            stats["errors"] += 1
            logger.error(
                "attribution_error",
                outcome_id=str(outcome.id),
                error=str(e),
            )

    db.commit()
    logger.info("attribution_run_complete", workspace_id=workspace_id, **stats)
    return stats


def get_attribution_summary(db: Session, workspace_id: str) -> dict:
    """
    Return attribution summary metrics for the workspace.
    Used by the API and dashboard to show ROI evidence.
    """
    attributions = (
        db.query(OutcomeAttribution)
        .filter_by(workspace_id=workspace_id)
        .all()
    )

    if not attributions:
        return {
            "total_attributions": 0,
            "message": "No attributed outcomes yet. Log outcomes to see attribution data.",
        }

    total = len(attributions)
    correct = [a for a in attributions if a.prediction_was_correct]
    positive = [
        a for a in attributions
        if a.outcome_type in POSITIVE_OUTCOME_TYPES
    ]
    with_deal_value = [a for a in positive if a.deal_value_usd and a.deal_value_usd > 0]
    with_days_ahead = [a for a in attributions if a.days_avenor_ahead_of_crm is not None]

    avg_deal_value = (
        sum(a.deal_value_usd for a in with_deal_value) / len(with_deal_value)
        if with_deal_value else None
    )
    total_attributed_revenue = (
        sum(a.deal_value_usd for a in with_deal_value)
        if with_deal_value else None
    )
    avg_days_ahead = (
        sum(a.days_avenor_ahead_of_crm for a in with_days_ahead) / len(with_days_ahead)
        if with_days_ahead else None
    )

    return {
        "total_attributions": total,
        "positive_outcomes": len(positive),
        "prediction_accuracy": round(len(correct) / total, 3) if total > 0 else None,
        "attributed_revenue_usd": round(total_attributed_revenue, 2) if total_attributed_revenue else None,
        "avg_deal_value_usd": round(avg_deal_value, 2) if avg_deal_value else None,
        "avg_days_avenor_ahead_of_crm": round(avg_days_ahead, 1) if avg_days_ahead else None,
        "accounts_with_positive_prediction": len([a for a in correct if a.outcome_type in POSITIVE_OUTCOME_TYPES]),
    }
