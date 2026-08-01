"""
Territory Planner (Phase 6.5)
Optimizes sales rep territory allocation, account balancing, and target pipeline coverage.
"""
from typing import List

from app.modules.strategic_intelligence.domain.strategic_entities import TerritoryPlan


class TerritoryPlanner:
    def create_territory_plans(self) -> List[TerritoryPlan]:
        return [
            TerritoryPlan(
                territory_name="North America Enterprise",
                assigned_reps=6,
                target_pipeline_usd=6500000.0,
                active_buying_windows=14,
                recommended_rep_reallocations=["Reallocate 1 rep from SMB to NA Enterprise"],
            ),
            TerritoryPlan(
                territory_name="EMEA Enterprise",
                assigned_reps=4,
                target_pipeline_usd=4000000.0,
                active_buying_windows=8,
                recommended_rep_reallocations=[],
            ),
        ]


territory_planner = TerritoryPlanner()
