"""
Weight Optimizer (Phase 5.5.6)
Adjusts buying signal weights, tool selection priorities, and memory reinforcement scores based on accumulated rewards.
"""
from typing import Dict, List

from app.modules.copilot.domain.learning_entities import RewardSignal


class WeightOptimizer:
    def optimize_weights(
        self,
        current_weights: Dict[str, float],
        rewards: List[RewardSignal],
    ) -> Dict[str, float]:
        updated_weights = dict(current_weights)

        for reward in rewards:
            delta = reward.weight_delta
            # Apply momentum adjustment across signal weights
            for key in updated_weights:
                new_val = max(0.1, min(2.5, updated_weights[key] + delta * 0.1))
                updated_weights[key] = round(new_val, 4)

        return updated_weights


weight_optimizer = WeightOptimizer()
