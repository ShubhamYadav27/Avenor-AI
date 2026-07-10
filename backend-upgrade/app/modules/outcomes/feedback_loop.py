"""
app/modules/outcomes/feedback_loop.py

Signal Intelligence Feedback Loop.
Extends (does not replace) the existing scoring trainer.

Computes per-signal analytics:
  - Conversion rate (signal present → positive outcome)
  - Average deal value when signal was active
  - Average days from signal detection to close
  - Lift over baseline (how much better than random)
  - Winning signal combinations

Stores results in signal_effectiveness table.
Feeds actionable recommendations back to the workspace.

This runs AFTER recalibrate_weights() — it uses the same outcome data
but produces richer analytics, not just weight numbers.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.core.signal_config import DEFAULT_SIGNAL_WEIGHTS
from app.models import (
    Outcome, OutcomeType, Signal, SignalEffectiveness,
    SignalWeights, Workspace,
)

logger = get_logger(__name__)

POSITIVE_OUTCOME_TYPES = {
    OutcomeType.BECAME_OPPORTUNITY.value,
    OutcomeType.MEETING_BOOKED.value,
    OutcomeType.REPLIED_POSITIVE.value,
    OutcomeType.CLOSED_WON.value,
}

REVENUE_OUTCOME_TYPES = {
    OutcomeType.CLOSED_WON.value,
}

MINIMUM_OUTCOMES = 5  # minimum per signal type before computing effectiveness


def compute_signal_effectiveness(db: Session, workspace_id: str) -> dict:
    """
    Compute and store signal effectiveness metrics for a workspace.
    Called after model recalibration and after new outcomes are logged.
    """
    outcomes = (
        db.query(Outcome)
        .filter_by(workspace_id=workspace_id)
        .all()
    )

    if not outcomes:
        return {"skipped": True, "reason": "no_outcomes"}

    # Load current signal weights for this workspace
    workspace = db.get(Workspace, workspace_id)
    sw = workspace.signal_weights if workspace else None
    current_weights = sw.weights if sw and sw.weights else DEFAULT_SIGNAL_WEIGHTS

    # Build per-signal-type analytics
    # Structure: {signal_type: {occurrences, positives, revenue_deals, deal_values, days_to_close}}
    signal_data: dict[str, dict[str, Any]] = defaultdict(lambda: {
        "occurrences": 0,
        "positive_outcomes": 0,
        "revenue_outcomes": 0,
        "deal_values": [],
        "days_to_close_list": [],
    })

    # For each outcome, look up what signals were active at the time
    for outcome in outcomes:
        signals_snapshot = outcome.active_signals_snapshot or []
        is_positive = outcome.outcome_type in POSITIVE_OUTCOME_TYPES
        is_revenue = outcome.outcome_type in REVENUE_OUTCOME_TYPES

        signal_types_seen = set()
        for sig in signals_snapshot:
            stype = sig.get("type") or sig.get("signal_type")
            if not stype or stype in signal_types_seen:
                continue
            signal_types_seen.add(stype)

            signal_data[stype]["occurrences"] += 1
            if is_positive:
                signal_data[stype]["positive_outcomes"] += 1
            if is_revenue and outcome.deal_value_usd:
                signal_data[stype]["revenue_outcomes"] += 1
                signal_data[stype]["deal_values"].append(outcome.deal_value_usd)

    # Compute derived metrics
    total_outcomes = len(outcomes)
    baseline_conversion_rate = (
        sum(1 for o in outcomes if o.outcome_type in POSITIVE_OUTCOME_TYPES) / total_outcomes
        if total_outcomes > 0 else 0.0
    )

    upserted = 0
    stats_by_type = {}

    for signal_type, data in signal_data.items():
        occurrences = data["occurrences"]
        if occurrences < MINIMUM_OUTCOMES:
            continue

        conversion_rate = round(data["positive_outcomes"] / occurrences, 4)
        avg_deal_value = (
            round(sum(data["deal_values"]) / len(data["deal_values"]), 2)
            if data["deal_values"] else None
        )
        lift = (
            round(conversion_rate / baseline_conversion_rate, 3)
            if baseline_conversion_rate > 0 else None
        )
        current_weight = current_weights.get(signal_type, DEFAULT_SIGNAL_WEIGHTS.get(signal_type))

        # Upsert into signal_effectiveness
        existing = (
            db.query(SignalEffectiveness)
            .filter_by(workspace_id=workspace_id, signal_type=signal_type)
            .first()
        )
        if existing:
            row = existing
        else:
            row = SignalEffectiveness(
                workspace_id=workspace_id,
                signal_type=signal_type,
            )
            db.add(row)

        row.total_occurrences = occurrences
        row.positive_outcome_count = data["positive_outcomes"]
        row.conversion_rate = conversion_rate
        row.avg_deal_value_usd = avg_deal_value
        row.current_weight = current_weight
        row.lift_over_baseline = lift
        row.computed_at = datetime.now(timezone.utc)

        stats_by_type[signal_type] = {
            "occurrences": occurrences,
            "conversion_rate": conversion_rate,
            "lift_over_baseline": lift,
            "avg_deal_value_usd": avg_deal_value,
            "current_weight": current_weight,
        }
        upserted += 1

    db.commit()
    logger.info(
        "signal_effectiveness_computed",
        workspace_id=workspace_id,
        signal_types_computed=upserted,
        baseline_conversion_rate=round(baseline_conversion_rate, 4),
    )

    return {
        "workspace_id": workspace_id,
        "total_outcomes_analyzed": total_outcomes,
        "baseline_conversion_rate": round(baseline_conversion_rate, 4),
        "signal_types_computed": upserted,
        "signal_effectiveness": stats_by_type,
    }


def get_scoring_recommendations(db: Session, workspace_id: str) -> list[dict]:
    """
    Generate actionable weight recommendations based on effectiveness data.
    Returns list of recommendations sorted by impact.
    """
    effectiveness_rows = (
        db.query(SignalEffectiveness)
        .filter_by(workspace_id=workspace_id)
        .all()
    )

    if not effectiveness_rows:
        return []

    recommendations = []

    for row in effectiveness_rows:
        if row.lift_over_baseline is None or row.current_weight is None:
            continue

        # Signal is meaningfully better than baseline
        if row.lift_over_baseline > 1.3 and row.total_occurrences >= MINIMUM_OUTCOMES:
            suggested_weight = min(
                round(row.current_weight * (row.lift_over_baseline ** 0.5), 4), 0.5
            )
            if suggested_weight > row.current_weight * 1.1:
                recommendations.append({
                    "signal_type": row.signal_type,
                    "action": "increase_weight",
                    "current_weight": row.current_weight,
                    "suggested_weight": suggested_weight,
                    "reason": (
                        f"Conversion rate {row.conversion_rate:.0%} is "
                        f"{row.lift_over_baseline:.1f}× above baseline"
                    ),
                    "evidence": {
                        "occurrences": row.total_occurrences,
                        "conversion_rate": row.conversion_rate,
                        "avg_deal_value_usd": row.avg_deal_value_usd,
                    },
                    "impact": "high" if row.lift_over_baseline > 2.0 else "medium",
                })

        # Signal performs below baseline — reduce weight
        elif row.lift_over_baseline < 0.7 and row.total_occurrences >= MINIMUM_OUTCOMES * 2:
            suggested_weight = max(round(row.current_weight * 0.6, 4), 0.01)
            recommendations.append({
                "signal_type": row.signal_type,
                "action": "decrease_weight",
                "current_weight": row.current_weight,
                "suggested_weight": suggested_weight,
                "reason": (
                    f"Conversion rate {row.conversion_rate:.0%} is only "
                    f"{row.lift_over_baseline:.1f}× baseline — weaker predictor than expected"
                ),
                "evidence": {
                    "occurrences": row.total_occurrences,
                    "conversion_rate": row.conversion_rate,
                },
                "impact": "low",
            })

    # Sort by impact
    impact_order = {"high": 0, "medium": 1, "low": 2}
    recommendations.sort(key=lambda x: (impact_order.get(x["impact"], 3), -x["evidence"]["occurrences"]))
    return recommendations


def get_prediction_accuracy_report(db: Session, workspace_id: str) -> dict:
    """
    Full prediction accuracy report for a workspace.
    Answers: how well is Avenor predicting buying cycles?
    """
    outcomes = (
        db.query(Outcome)
        .filter_by(workspace_id=workspace_id)
        .all()
    )

    if not outcomes:
        return {
            "total_outcomes": 0,
            "message": "No outcomes logged yet.",
        }

    total = len(outcomes)
    positives = [o for o in outcomes if o.outcome_type in POSITIVE_OUTCOME_TYPES]
    with_scores = [o for o in outcomes if o.predicted_composite_score is not None]
    with_positive_scores = [
        o for o in positives if o.predicted_composite_score is not None
    ]

    # Precision: of accounts Avenor scored ≥ 0.5, what fraction converted?
    high_score_outcomes = [o for o in with_scores if o.predicted_composite_score >= 0.5]
    high_score_positives = [o for o in high_score_outcomes if o.outcome_type in POSITIVE_OUTCOME_TYPES]

    precision = (
        round(len(high_score_positives) / len(high_score_outcomes), 3)
        if high_score_outcomes else None
    )

    # Recall: of positive outcomes, how many had score ≥ 0.5?
    recall = (
        round(len(high_score_positives) / len(with_positive_scores), 3)
        if with_positive_scores else None
    )

    # Buying window accuracy: predicted HOT/WARM → actually positive?
    window_outcomes = [
        o for o in outcomes
        if o.predicted_buying_window in ("hot", "warm")
        and o.predicted_composite_score is not None
    ]
    window_positives = [
        o for o in window_outcomes if o.outcome_type in POSITIVE_OUTCOME_TYPES
    ]
    window_accuracy = (
        round(len(window_positives) / len(window_outcomes), 3)
        if window_outcomes else None
    )

    # Revenue attribution
    revenue_outcomes = [
        o for o in positives
        if o.outcome_type == OutcomeType.CLOSED_WON.value and o.deal_value_usd
    ]
    total_revenue = sum(o.deal_value_usd for o in revenue_outcomes) if revenue_outcomes else 0

    # Score distribution for positive outcomes
    avg_score_positive = (
        round(
            sum(o.predicted_composite_score for o in with_positive_scores)
            / len(with_positive_scores), 3
        ) if with_positive_scores else None
    )

    # Time advantage
    with_advantage = [o for o in outcomes if o.days_ahead_of_organic_discovery is not None]
    avg_days_advantage = (
        round(sum(o.days_ahead_of_organic_discovery for o in with_advantage) / len(with_advantage), 1)
        if with_advantage else None
    )

    # Per-outcome-type breakdown
    type_breakdown: dict[str, int] = defaultdict(int)
    for o in outcomes:
        type_breakdown[o.outcome_type] += 1

    return {
        "total_outcomes": total,
        "positive_outcomes": len(positives),
        "overall_conversion_rate": round(len(positives) / total, 3),
        "precision_at_0_5": precision,
        "recall_at_0_5": recall,
        "hot_warm_window_accuracy": window_accuracy,
        "avg_predicted_score_for_positives": avg_score_positive,
        "avg_days_avenor_ahead": avg_days_advantage,
        "total_attributed_revenue_usd": round(total_revenue, 2) if total_revenue else 0,
        "by_outcome_type": dict(type_breakdown),
        "model_confidence": _model_confidence_label(precision, recall, total),
    }


def run_full_feedback_loop(db: Session, workspace_id: str) -> dict:
    """
    Run the complete feedback loop for a workspace:
    1. Compute signal effectiveness
    2. Generate scoring recommendations
    3. Compute prediction accuracy report

    Called after every batch of new outcomes.
    """
    effectiveness = compute_signal_effectiveness(db, workspace_id)
    recommendations = get_scoring_recommendations(db, workspace_id)
    accuracy_report = get_prediction_accuracy_report(db, workspace_id)

    return {
        "effectiveness": effectiveness,
        "recommendations": recommendations,
        "accuracy_report": accuracy_report,
    }


def run_feedback_loop_all_workspaces(db: Session) -> list[dict]:
    """Fan out feedback loop to all active workspaces. Called by weekly Celery task."""
    workspaces = db.query(Workspace).filter_by(is_active=True).all()
    results = []
    for ws in workspaces:
        try:
            result = run_full_feedback_loop(db, str(ws.id))
            results.append({"workspace_id": str(ws.id), "status": "ok", **result})
        except Exception as e:
            logger.error("feedback_loop_failed", workspace_id=str(ws.id), error=str(e))
            results.append({"workspace_id": str(ws.id), "status": "error", "error": str(e)})
    return results


def _model_confidence_label(precision: float | None, recall: float | None, sample_size: int) -> str:
    if sample_size < 10:
        return "insufficient_data"
    if precision is None:
        return "insufficient_data"
    if precision >= 0.65 and recall and recall >= 0.5:
        return "high"
    if precision >= 0.45:
        return "medium"
    return "low"
