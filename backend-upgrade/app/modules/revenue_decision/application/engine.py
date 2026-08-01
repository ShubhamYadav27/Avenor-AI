"""
Revenue Decision Intelligence Engine (Phase 6.2)
Coordinates PolicyEngine -> ConstraintEvaluator -> TradeoffAnalyzer -> ActionPlanner -> DecisionPackage.
Zero DB ORM coupling.
"""
import time
import uuid

from app.modules.copilot.domain.interfaces import IRevenueDecisionEngine
from app.modules.revenue_decision.application.engines.action_planner import action_planner
from app.modules.revenue_decision.application.engines.constraint_evaluator import constraint_evaluator
from app.modules.revenue_decision.application.engines.policy_engine import policy_engine
from app.modules.revenue_decision.domain.decision_entities import DecisionPackage, RevenueDecision
from app.modules.revenue_decision.domain.decision_value_objects import DecisionType


class RevenueDecisionEngine(IRevenueDecisionEngine):
    async def decide_next_best_action(
        self,
        workspace_id: uuid.UUID,
        company_id: str,
    ) -> DecisionPackage:
        t0 = time.perf_counter()

        # 1. Evaluate Workspace Policies
        policies = policy_engine.evaluate_policies(company_id)

        # 2. Validate Business Constraints
        constraints = constraint_evaluator.evaluate_constraints(company_id)

        # 3. Build Action Plan with Trade-off Rationale & Evidence
        plan = action_planner.create_action_plan(company_id)

        # 4. Compile Decision
        decision = RevenueDecision(
            decision_type=DecisionType.NEXT_BEST_SALES_ACTION,
            recommended_action=plan,
            alternative_actions=[],
            confidence_score=0.95,
            satisfied_constraints=constraints,
        )

        total_lat = (time.perf_counter() - t0) * 1000.0

        return DecisionPackage(
            workspace_id=workspace_id,
            company_id=company_id,
            decisions=[decision],
            action_plan=plan,
            execution_time_ms=round(total_lat, 2),
        )


revenue_decision_engine = RevenueDecisionEngine()
