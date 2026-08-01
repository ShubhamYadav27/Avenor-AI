"""
Action Planner (Phase 6.2)
Generates structured execution action plans detailing timing, channel, contact, and evidence.
"""

from app.modules.revenue_decision.application.engines.contact_decision_engine import contact_decision_engine
from app.modules.revenue_decision.application.engines.play_recommendation_engine import play_recommendation_engine
from app.modules.revenue_decision.application.engines.timing_decision_engine import timing_decision_engine
from app.modules.revenue_decision.application.engines.tradeoff_analyzer import tradeoff_analyzer
from app.modules.revenue_decision.domain.decision_entities import ActionPlan
from app.modules.revenue_decision.domain.decision_value_objects import ActionUrgency


class ActionPlanner:
    def create_action_plan(self, company_id: str) -> ActionPlan:
        contact = contact_decision_engine.select_optimal_contact(company_id)
        play = play_recommendation_engine.recommend_sales_play(company_id)
        channel, timing = timing_decision_engine.optimize_channel_and_timing(company_id)
        explanation = tradeoff_analyzer.analyze_tradeoffs(company_id)

        return ActionPlan(
            company_id=company_id,
            target_contact=contact,
            play=play,
            recommended_channel=channel,
            optimal_timing=timing,
            urgency=ActionUrgency.HIGH,
            explanation=explanation,
        )


action_planner = ActionPlanner()
