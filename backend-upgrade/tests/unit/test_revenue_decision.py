import uuid
import pytest

from app.modules.revenue_decision.application.engine import revenue_decision_engine
from app.modules.revenue_decision.application.engines.action_planner import action_planner
from app.modules.revenue_decision.application.engines.constraint_evaluator import constraint_evaluator
from app.modules.revenue_decision.application.engines.policy_engine import policy_engine
from app.modules.revenue_decision.application.engines.tradeoff_analyzer import tradeoff_analyzer
from app.modules.revenue_decision.domain.decision_entities import DecisionPackage
from app.modules.revenue_decision.domain.decision_value_objects import ActionUrgency, OutreachChannel, PolicyMode


@pytest.fixture
def anyio_backend():
    return "asyncio"


def test_policy_engine_evaluation():
    policies = policy_engine.evaluate_policies("comp-101")
    assert len(policies) == 2
    assert policies[0].mode == PolicyMode.STRICT_ENFORCE


def test_constraint_evaluator():
    constraints = constraint_evaluator.evaluate_constraints("comp-101")
    assert len(constraints) == 3
    assert all(c.is_satisfied for c in constraints)


def test_tradeoff_analyzer():
    exp = tradeoff_analyzer.analyze_tradeoffs("comp-101")
    assert len(exp.trade_offs_considered) == 2
    assert len(exp.evidence_citations) == 3


def test_action_planner():
    plan = action_planner.create_action_plan("comp-101")
    assert plan.urgency == ActionUrgency.HIGH
    assert plan.recommended_channel == OutreachChannel.EMAIL
    assert plan.explanation is not None


@pytest.mark.anyio
async def test_revenue_decision_engine_e2e():
    ws_id = uuid.uuid4()
    pkg = await revenue_decision_engine.decide_next_best_action(ws_id, "comp-101")

    assert isinstance(pkg, DecisionPackage)
    assert pkg.company_id == "comp-101"
    assert len(pkg.decisions) == 1
    assert pkg.action_plan.target_contact.name == "Alex Morgan"
    assert pkg.action_plan.play.play_id == "play-series-b-expansion"
    assert len(pkg.action_plan.explanation.evidence_citations) == 3
