"""
Enterprise Learning Engine (Phase 5.5.6)
Coordinates Collector -> Processor -> RewardCalculator -> WeightOptimizer -> DriftDetector.
Zero DB ORM coupling.
"""
from typing import Dict, List, Optional
import uuid

from app.modules.copilot.domain.interfaces import ILearningEngine
from app.modules.copilot.domain.learning_entities import LearningPackage, RewardSignal
from app.modules.copilot.domain.learning_value_objects import FeedbackType
from app.modules.copilot.learning_engine.application.collectors.feedback_collector import feedback_collector
from app.modules.copilot.learning_engine.application.detectors.drift_detector import drift_detector
from app.modules.copilot.learning_engine.application.evaluators.reward_calculator import reward_calculator
from app.modules.copilot.learning_engine.application.optimizers.weight_optimizer import weight_optimizer
from app.modules.copilot.learning_engine.application.processors.event_processor import event_processor


class LearningEngine(ILearningEngine):
    def __init__(self):
        self._workspace_weights: Dict[str, Dict[str, float]] = {}

    async def submit_user_feedback(
        self,
        workspace_id: uuid.UUID,
        feedback_type: str = "thumbs_up",
        rating: float = 1.0,
        thread_id: Optional[uuid.UUID] = None,
        message_id: Optional[uuid.UUID] = None,
        correction_text: Optional[str] = None,
        user_id: Optional[uuid.UUID] = None,
    ) -> RewardSignal:
        try:
            fb_type = FeedbackType(feedback_type.lower())
        except ValueError:
            fb_type = FeedbackType.THUMBS_UP

        fb_event = feedback_collector.record_user_feedback(
            workspace_id=workspace_id,
            feedback_type=fb_type,
            rating=rating,
            thread_id=thread_id,
            message_id=message_id,
            correction_text=correction_text,
            user_id=user_id,
        )

        rewards = reward_calculator.calculate_rewards_from_feedback([fb_event])
        reward = rewards[0] if rewards else RewardSignal(workspace_id=workspace_id)

        # Trigger learning cycle for workspace
        await self.process_learning_cycle(workspace_id)
        return reward

    async def submit_crm_outcome(
        self,
        workspace_id: uuid.UUID,
        outcome_type: str = "deal_won",
        deal_id: Optional[str] = None,
        amount_usd: float = 0.0,
        signal_ids: Optional[List[str]] = None,
    ) -> RewardSignal:
        try:
            out_type = FeedbackType(outcome_type.lower())
        except ValueError:
            out_type = FeedbackType.DEAL_WON

        out_event = feedback_collector.record_crm_outcome(
            workspace_id=workspace_id,
            outcome_type=out_type,
            deal_id=deal_id,
            amount_usd=amount_usd,
            signal_ids_attributed=signal_ids,
        )

        rewards = reward_calculator.calculate_rewards_from_outcomes([out_event])
        reward = rewards[0] if rewards else RewardSignal(workspace_id=workspace_id)

        await self.process_learning_cycle(workspace_id)
        return reward

    async def process_learning_cycle(self, workspace_id: uuid.UUID) -> LearningPackage:
        raw_fb = feedback_collector.get_workspace_feedback(workspace_id)
        raw_out = feedback_collector.get_workspace_outcomes(workspace_id)

        valid_fb, valid_out = event_processor.process_pending_events(raw_fb, raw_out)
        rewards_fb = reward_calculator.calculate_rewards_from_feedback(valid_fb)
        rewards_out = reward_calculator.calculate_rewards_from_outcomes(valid_out)

        all_rewards = rewards_fb + rewards_out

        # Baseline signal weights
        ws_key = str(workspace_id)
        current_weights = self._workspace_weights.get(
            ws_key,
            {"funding": 1.0, "hiring": 0.9, "tech_change": 0.8, "intent_surge": 1.1},
        )

        optimized_weights = weight_optimizer.optimize_weights(current_weights, all_rewards)
        self._workspace_weights[ws_key] = optimized_weights

        metrics = drift_detector.compute_metrics_and_drift(all_rewards)

        return LearningPackage(
            workspace_id=workspace_id,
            recent_rewards=all_rewards,
            active_weights_override=optimized_weights,
            optimization_summary=f"Optimized {len(optimized_weights)} signal weights across {len(all_rewards)} reward events.",
            metrics=metrics,
        )


learning_engine = LearningEngine()
