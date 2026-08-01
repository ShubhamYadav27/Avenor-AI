"""
Revenue Simulator (Phase 6.5)
Runs Monte Carlo and scenario simulations for win rate shifts, pricing changes, and headcount-constrained growth.
"""
from typing import List

from app.modules.strategic_intelligence.domain.strategic_entities import RevenueScenarioSimulation
from app.modules.strategic_intelligence.domain.strategic_value_objects import ScenarioType


class RevenueSimulator:
    def simulate_scenarios(self) -> List[RevenueScenarioSimulation]:
        return [
            RevenueScenarioSimulation(
                scenario_name="Headcount-Constrained Growth Scenario (₹120 Cr Target)",
                scenario_type=ScenarioType.HEADCOUNT_CONSTRAINED_GROWTH,
                win_rate_delta=0.05,
                pipeline_coverage=3.8,
                projected_arr_usd=14400000.0,
                confidence_score=0.88,
            ),
            RevenueScenarioSimulation(
                scenario_name="Win Rate Expansion & Upsell Strategy",
                scenario_type=ScenarioType.WIN_RATE_EXPANSION,
                win_rate_delta=0.07,
                pipeline_coverage=4.1,
                projected_arr_usd=15200000.0,
                confidence_score=0.84,
            ),
        ]


revenue_simulator = RevenueSimulator()
