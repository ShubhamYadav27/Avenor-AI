"""
Policy Engine (Phase 6.2)
Evaluates workspace business policies (e.g. enterprise accounts first, max 3 active threads per rep).
"""
from typing import List

from app.modules.revenue_decision.domain.decision_entities import DecisionPolicy
from app.modules.revenue_decision.domain.decision_value_objects import PolicyMode


class PolicyEngine:
    def evaluate_policies(self, company_id: str) -> List[DecisionPolicy]:
        return [
            DecisionPolicy(
                policy_id="pol-enterprise-first",
                policy_name="Enterprise Accounts Priority",
                mode=PolicyMode.STRICT_ENFORCE,
                rule_expression="account.type == 'ENTERPRISE'",
            ),
            DecisionPolicy(
                policy_id="pol-thread-cap",
                policy_name="Max 3 Active Threads Per Rep",
                mode=PolicyMode.STRICT_ENFORCE,
                rule_expression="rep.active_threads <= 3",
            ),
        ]


policy_engine = PolicyEngine()
