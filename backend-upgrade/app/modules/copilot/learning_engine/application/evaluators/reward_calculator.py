"""
Reward Calculator (Phase 5.5.6)
Calculates numerical reward signals R in [-1.0, 1.0] from explicit user feedback and CRM deal conversion outcomes.
"""
from typing import List

from app.modules.copilot.domain.learning_entities import FeedbackEvent, OutcomeEvent, RewardSignal
from app.modules.copilot.domain.learning_value_objects import FeedbackType, OptimizationTarget, RewardType


class RewardCalculator:
    def calculate_rewards_from_feedback(self, feedback_events: List[FeedbackEvent]) -> List[RewardSignal]:
        rewards: List[RewardSignal] = []
        for fb in feedback_events:
            score = fb.rating
            if fb.feedback_type == FeedbackType.THUMBS_DOWN:
                score = -1.0
            elif fb.feedback_type == FeedbackType.THUMBS_UP:
                score = 1.0

            rewards.append(
                RewardSignal(
                    workspace_id=fb.workspace_id,
                    reward_type=RewardType.EXPLICIT_USER,
                    reward_score=score,
                    target=OptimizationTarget.PROMPT_STRATEGY,
                    weight_delta=round(score * 0.05, 4),
                    reasoning=f"Explicit feedback: {fb.feedback_type.value}",
                )
            )
        return rewards

    def calculate_rewards_from_outcomes(self, outcome_events: List[OutcomeEvent]) -> List[RewardSignal]:
        rewards: List[RewardSignal] = []
        for out in outcome_events:
            score = 1.0 if out.outcome_type == FeedbackType.DEAL_WON else -0.5
            rewards.append(
                RewardSignal(
                    workspace_id=out.workspace_id,
                    reward_type=RewardType.CRM_OUTCOME,
                    reward_score=score,
                    target=OptimizationTarget.SIGNAL_WEIGHT,
                    weight_delta=round(score * 0.10, 4),
                    reasoning=f"CRM Deal Outcome ({out.outcome_type.value}): ${out.amount_usd:,.0f}",
                )
            )
        return rewards


reward_calculator = RewardCalculator()
