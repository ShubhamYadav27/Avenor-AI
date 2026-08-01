import uuid
import pytest

from app.modules.copilot.domain.learning_entities import FeedbackEvent, OutcomeEvent, RewardSignal
from app.modules.copilot.domain.learning_value_objects import DriftStatus, FeedbackType
from app.modules.copilot.learning_engine.application.collectors.feedback_collector import feedback_collector
from app.modules.copilot.learning_engine.application.detectors.drift_detector import drift_detector
from app.modules.copilot.learning_engine.application.engine import learning_engine
from app.modules.copilot.learning_engine.application.evaluators.reward_calculator import reward_calculator
from app.modules.copilot.learning_engine.application.optimizers.weight_optimizer import weight_optimizer


@pytest.fixture
def anyio_backend():
    return "asyncio"


def test_feedback_collector_recording():
    ws_id = uuid.uuid4()
    fb_event = feedback_collector.record_user_feedback(
        workspace_id=ws_id,
        feedback_type=FeedbackType.THUMBS_UP,
        rating=1.0,
    )
    assert fb_event.id.startswith("fb-")
    assert fb_event.workspace_id == ws_id

    out_event = feedback_collector.record_crm_outcome(
        workspace_id=ws_id,
        outcome_type=FeedbackType.DEAL_WON,
        amount_usd=150000.0,
    )
    assert out_event.id.startswith("out-")
    assert out_event.amount_usd == 150000.0


def test_reward_calculator_and_weight_optimizer():
    ws_id = uuid.uuid4()
    fb = FeedbackEvent(workspace_id=ws_id, feedback_type=FeedbackType.THUMBS_UP, rating=1.0)
    out = OutcomeEvent(workspace_id=ws_id, outcome_type=FeedbackType.DEAL_WON, amount_usd=50000.0)

    rewards_fb = reward_calculator.calculate_rewards_from_feedback([fb])
    rewards_out = reward_calculator.calculate_rewards_from_outcomes([out])

    assert len(rewards_fb) == 1
    assert rewards_fb[0].reward_score == 1.0
    assert len(rewards_out) == 1
    assert rewards_out[0].reward_score == 1.0

    current_weights = {"funding": 1.0, "hiring": 0.9}
    updated_weights = weight_optimizer.optimize_weights(current_weights, rewards_fb + rewards_out)
    assert updated_weights["funding"] > 1.0
    assert updated_weights["hiring"] > 0.9


def test_drift_detector():
    r1 = RewardSignal(reward_score=1.0)
    r2 = RewardSignal(reward_score=1.0)
    r3 = RewardSignal(reward_score=-1.0)

    metrics_stable = drift_detector.compute_metrics_and_drift([r1, r2])
    assert metrics_stable.drift_status == DriftStatus.STABLE
    assert metrics_stable.positive_rate == 1.0

    metrics_drift = drift_detector.compute_metrics_and_drift([r3, r3])
    assert metrics_drift.drift_status == DriftStatus.SIGNIFICANT_DRIFT
    assert metrics_drift.positive_rate == 0.0


@pytest.mark.anyio
async def test_learning_engine_e2e_cycle():
    ws_id = uuid.uuid4()

    reward_user = await learning_engine.submit_user_feedback(
        workspace_id=ws_id,
        feedback_type="thumbs_up",
        rating=1.0,
    )
    assert reward_user.reward_score == 1.0

    reward_crm = await learning_engine.submit_crm_outcome(
        workspace_id=ws_id,
        outcome_type="deal_won",
        amount_usd=250000.0,
    )
    assert reward_crm.reward_score == 1.0

    pkg = await learning_engine.process_learning_cycle(ws_id)
    assert pkg.workspace_id == ws_id
    assert len(pkg.recent_rewards) >= 2
    assert pkg.metrics.positive_rate == 1.0
    assert "Optimized" in pkg.optimization_summary
