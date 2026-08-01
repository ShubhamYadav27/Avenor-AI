"""
Strategic Intelligence Service (Phase 6.5 & 6.6)
Coordinates ExecutiveBriefingEngine -> TerritoryPlanner -> CapacityPlanner -> RevenueSimulator -> StrategicAdvisor -> AutonomousOrgPackage.
Zero DB ORM coupling.
"""
import time
from typing import List
import uuid

from app.modules.strategic_intelligence.application.planners.capacity_planner import capacity_planner
from app.modules.strategic_intelligence.application.planners.territory_planner import territory_planner
from app.modules.strategic_intelligence.application.services.executive_briefing_engine import executive_briefing_engine
from app.modules.strategic_intelligence.application.services.strategic_advisor import strategic_advisor
from app.modules.strategic_intelligence.application.simulators.revenue_simulator import revenue_simulator
from app.modules.strategic_intelligence.domain.strategic_entities import AutonomousOrgPackage, ExecutiveBriefing, RevenueForecast, RevenueScenarioSimulation, StrategicPlan, StrategicRecommendation
from app.modules.strategic_intelligence.domain.strategic_value_objects import SystemOperatingState


class StrategicIntelligenceService:
    async def generate_autonomous_org_status(self, workspace_id: uuid.UUID) -> AutonomousOrgPackage:
        t0 = time.perf_counter()

        s_plan = StrategicPlan(workspace_id=workspace_id, target_arr_usd=14400000.0, current_arr_usd=8500000.0)
        fcst = RevenueForecast(fiscal_quarter="Q3-FY26", commit_usd=3400000.0, best_case_usd=4200000.0, pipeline_coverage_ratio=3.8, win_rate_percentage=28.5)
        briefing = executive_briefing_engine.generate_board_briefing()
        territories = territory_planner.create_territory_plans()
        capacity = capacity_planner.evaluate_capacity()
        trends = strategic_advisor.analyze_market_trends()
        simulations = revenue_simulator.simulate_scenarios()
        recommendations = strategic_advisor.generate_recommendations()
        risks = strategic_advisor.analyze_risks()
        opportunities = strategic_advisor.analyze_opportunities()

        total_lat = (time.perf_counter() - t0) * 1000.0

        return AutonomousOrgPackage(
            workspace_id=workspace_id,
            operating_state=SystemOperatingState.EXECUTING,
            strategic_plans=[s_plan],
            forecasts=[fcst],
            briefings=[briefing],
            territory_plans=territories,
            capacity_plan=capacity,
            market_trends=trends,
            simulations=simulations,
            recommendations=recommendations,
            risks=risks,
            opportunities=opportunities,
            ai_partner_status="Avenor Autonomous Revenue Operating System Active: Continuously monitoring accounts, predicting pipeline, and executing governed RevOps workflows.",
            execution_time_ms=round(total_lat, 2),
        )

    async def generate_executive_briefing(self, workspace_id: uuid.UUID) -> ExecutiveBriefing:
        return executive_briefing_engine.generate_board_briefing()

    async def run_scenario_simulations(self, workspace_id: uuid.UUID) -> List[RevenueScenarioSimulation]:
        return revenue_simulator.simulate_scenarios()

    async def get_strategic_recommendations(self, workspace_id: uuid.UUID) -> List[StrategicRecommendation]:
        return strategic_advisor.generate_recommendations()

    async def get_quarterly_forecast(self, workspace_id: uuid.UUID) -> RevenueForecast:
        return RevenueForecast(fiscal_quarter="Q3-FY26", commit_usd=3400000.0, best_case_usd=4200000.0, pipeline_coverage_ratio=3.8, win_rate_percentage=28.5)


strategic_intelligence_service = StrategicIntelligenceService()
