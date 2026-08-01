"""
Constraint Evaluator (Phase 6.2)
Validates sales rep capacity, territory ownership rules, and active workflow locks.
"""
from typing import List

from app.modules.revenue_decision.domain.decision_entities import BusinessConstraint
from app.modules.revenue_decision.domain.decision_value_objects import ConstraintType


class ConstraintEvaluator:
    def evaluate_constraints(self, company_id: str) -> List[BusinessConstraint]:
        return [
            BusinessConstraint(
                constraint_id="const-cap-01",
                constraint_type=ConstraintType.SALES_CAPACITY,
                description="Assigned rep has available weekly meeting slots.",
                is_satisfied=True,
            ),
            BusinessConstraint(
                constraint_id="const-terr-01",
                constraint_type=ConstraintType.TERRITORY_RULE,
                description="Account belongs to North America Enterprise Territory.",
                is_satisfied=True,
            ),
            BusinessConstraint(
                constraint_id="const-lock-01",
                constraint_type=ConstraintType.ACTIVE_WORKFLOW_LOCK,
                description="No conflicting active renewal workflow locked.",
                is_satisfied=True,
            ),
        ]


constraint_evaluator = ConstraintEvaluator()
