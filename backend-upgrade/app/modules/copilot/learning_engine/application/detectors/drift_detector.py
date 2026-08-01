"""
Drift Detector (Phase 5.5.6)
Monitors feedback trends, model accuracy drift, and computes workspace learning metrics.
"""
from typing import List

from app.modules.copilot.domain.learning_entities import LearningMetrics, RewardSignal
from app.modules.copilot.domain.learning_value_objects import DriftStatus


class DriftDetector:
    def compute_metrics_and_drift(self, rewards: List[RewardSignal]) -> LearningMetrics:
        if not rewards:
            return LearningMetrics()

        positive_count = sum(1 for r in rewards if r.reward_score > 0.0)
        positive_rate = positive_count / len(rewards)
        avg_reward = sum(r.reward_score for r in rewards) / len(rewards)

        if positive_rate < 0.50:
            status = DriftStatus.SIGNIFICANT_DRIFT
        elif positive_rate < 0.75:
            status = DriftStatus.SLIGHT_DRIFT
        else:
            status = DriftStatus.STABLE

        return LearningMetrics(
            total_feedback_count=len(rewards),
            positive_rate=round(positive_rate, 2),
            reward_average=round(avg_reward, 2),
            weight_updates_count=len(rewards),
            drift_status=status,
        )


drift_detector = DriftDetector()
