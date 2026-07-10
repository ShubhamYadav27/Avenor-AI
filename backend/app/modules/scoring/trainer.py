"""
Model trainer.
Recalibrates signal weights from outcome data.
Runs weekly. Replaces rule-based defaults with learned weights as data accumulates.
Minimum 20 outcomes required before updating weights (avoid overfitting on small samples).
"""
from collections import defaultdict
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.core.signal_config import DEFAULT_SIGNAL_WEIGHTS
from app.models import Outcome, OutcomeType, Signal, SignalWeights, Workspace

logger = get_logger(__name__)

MINIMUM_OUTCOMES_FOR_TRAINING = 20
# Use string values — DB columns store enum values as strings
POSITIVE_OUTCOMES = {
    OutcomeType.BECAME_OPPORTUNITY.value,
    OutcomeType.MEETING_BOOKED.value,
    OutcomeType.REPLIED_POSITIVE.value,
    OutcomeType.CLOSED_WON.value,
}


def recalibrate_weights(db: Session, workspace_id: str) -> dict:
    """
    Recalibrate signal weights for one workspace from its outcome data.
    Returns dict with training stats and new weights.
    """
    outcomes = (
        db.query(Outcome)
        .filter_by(workspace_id=workspace_id)
        .all()
    )

    if len(outcomes) < MINIMUM_OUTCOMES_FOR_TRAINING:
        logger.info(
            "training_skipped_insufficient_data",
            workspace_id=workspace_id,
            outcome_count=len(outcomes),
            minimum=MINIMUM_OUTCOMES_FOR_TRAINING,
        )
        return {
            "skipped": True,
            "reason": f"Need {MINIMUM_OUTCOMES_FOR_TRAINING} outcomes, have {len(outcomes)}",
        }

    # Separate positive and negative outcomes
    positive_company_ids = {
        str(o.company_id) for o in outcomes if o.outcome_type in POSITIVE_OUTCOMES
    }
    negative_company_ids = {
        str(o.company_id) for o in outcomes if o.outcome_type not in POSITIVE_OUTCOMES
    }

    # Count signal type occurrences in positive vs negative outcomes
    signal_type_counts: dict[str, dict[str, int]] = defaultdict(lambda: {"positive": 0, "negative": 0})
    combination_counts: dict[str, dict[str, int]] = defaultdict(lambda: {"positive": 0, "negative": 0})

    all_company_ids = positive_company_ids | negative_company_ids
    for company_id in all_company_ids:
        signals = db.query(Signal).filter_by(company_id=company_id).all()
        signal_types = {s.signal_type for s in signals}
        label = "positive" if company_id in positive_company_ids else "negative"

        for st in signal_types:
            signal_type_counts[st][label] += 1

        # Track combinations (pairs)
        signal_list = sorted(signal_types)
        for i in range(len(signal_list)):
            for j in range(i + 1, len(signal_list)):
                combo_key = f"{signal_list[i]}+{signal_list[j]}"
                combination_counts[combo_key][label] += 1

    # Compute new weights via positive rate
    new_weights = {}
    for signal_type, counts in signal_type_counts.items():
        total = counts["positive"] + counts["negative"]
        if total < 5:  # not enough data for this signal type
            new_weights[signal_type] = DEFAULT_SIGNAL_WEIGHTS.get(signal_type, 0.10)
            continue

        positive_rate = counts["positive"] / total
        # Blend learned rate with prior (Bayesian-style smoothing)
        prior = DEFAULT_SIGNAL_WEIGHTS.get(signal_type, 0.10)
        blend_factor = min(total / 50, 1.0)  # full trust at 50+ samples
        learned_weight = (positive_rate * 0.5)  # scale rate to weight range
        new_weights[signal_type] = round(
            (learned_weight * blend_factor) + (prior * (1 - blend_factor)), 4
        )

    # Compute combination accuracy
    combination_accuracy = {}
    for combo, counts in combination_counts.items():
        total = counts["positive"] + counts["negative"]
        if total >= 5:
            combination_accuracy[combo] = round(counts["positive"] / total, 3)

    # Compute overall model accuracy
    # Accuracy = fraction of positive outcomes that had score >= 0.5
    true_positives = sum(
        1 for o in outcomes
        if o.outcome_type in POSITIVE_OUTCOMES
        and o.predicted_composite_score is not None
        and o.predicted_composite_score >= 0.5
    )
    positives_with_scores = sum(
        1 for o in outcomes
        if o.outcome_type in POSITIVE_OUTCOMES
        and o.predicted_composite_score is not None
    )
    model_accuracy = (
        round(true_positives / positives_with_scores, 3)
        if positives_with_scores > 0 else None
    )

    # Upsert SignalWeights
    workspace = db.get(Workspace, workspace_id)
    sw = workspace.signal_weights if workspace else None
    if sw is None:
        sw = SignalWeights(workspace_id=workspace_id)
        db.add(sw)

    sw.weights = new_weights
    sw.training_sample_size = len(outcomes)
    sw.model_accuracy = model_accuracy
    sw.last_trained_at = datetime.now(timezone.utc)
    sw.combination_accuracy = combination_accuracy

    db.commit()

    result = {
        "workspace_id": workspace_id,
        "outcomes_used": len(outcomes),
        "new_weights": new_weights,
        "model_accuracy": model_accuracy,
        "combination_accuracy": combination_accuracy,
    }
    logger.info("model_recalibrated", **result)
    return result


def run_model_recalibration_all_workspaces(db: Session) -> list[dict]:
    """Recalibrate weights for every active workspace. Called by weekly scheduler."""
    workspaces = db.query(Workspace).filter_by(is_active=True).all()
    results = []
    for ws in workspaces:
        try:
            result = recalibrate_weights(db, str(ws.id))
            results.append(result)
        except Exception as e:
            logger.error("recalibration_failed", workspace_id=str(ws.id), error=str(e))
            results.append({"workspace_id": str(ws.id), "error": str(e)})
    return results
