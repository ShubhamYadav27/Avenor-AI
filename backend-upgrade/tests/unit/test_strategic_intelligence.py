import uuid
import pytest

from app.modules.strategic_intelligence.application.planners.capacity_planner import capacity_planner
from app.modules.strategic_intelligence.application.planners.territory_planner import territory_planner
from app.modules.strategic_intelligence.application.service import strategic_intelligence_service
from app.modules.strategic_intelligence.application.services.executive_briefing_engine import executive_briefing_engine
from app.modules.strategic_intelligence.application.services.strategic_advisor import strategic_advisor
from app.modules.strategic_intelligence.application.simulators.revenue_simulator import revenue_simulator
from app.modules.strategic_intelligence.domain.strategic_entities import AutonomousOrgPackage
from app.modules.strategic_intelligence.domain.strategic_value_objects import ScenarioType


@pytest.fixture
def anyio_backend():
    return "asyncio"


def test_executive_briefing_engine():
    briefing = executive_briefing_engine.generate_board_briefing()
    assert briefing.title.startswith("Executive Board Briefing")
    assert len(briefing.key_takeaways) == 3


def test_territory_planner():
    plans = territory_planner.create_territory_plans()
    assert len(plans) == 2
    assert plans[0].territory_name == "North America Enterprise"


def test_capacity_planner():
    cap = capacity_planner.evaluate_capacity()
    assert cap.rep_capacity_utilization == 0.82
    assert cap.recommended_headcount_delta == 2


def test_revenue_simulator():
    sims = revenue_simulator.simulate_scenarios()
    assert len(sims) == 2
    assert sims[0].scenario_type == ScenarioType.HEADCOUNT_CONSTRAINED_GROWTH
    assert sims[0].projected_arr_usd == 14400000.0


def test_strategic_advisor():
    trends = strategic_advisor.analyze_market_trends()
    recs = strategic_advisor.generate_recommendations()
    risks = strategic_advisor.analyze_risks()
    opps = strategic_advisor.analyze_opportunities()

    assert len(trends) == 1
    assert len(recs) == 1
    assert len(risks) == 1
    assert len(opps) == 1
    assert recs[0].impact_usd == 650000.0


@pytest.mark.anyio
async def test_strategic_intelligence_service_e2e():
    ws_id = uuid.uuid4()
    pkg = await strategic_intelligence_service.generate_autonomous_org_status(ws_id)

    assert isinstance(pkg, AutonomousOrgPackage)
    assert len(pkg.briefings) == 1
    assert len(pkg.forecasts) == 1
    assert len(pkg.territory_plans) == 2
    assert len(pkg.simulations) == 2
    assert len(pkg.recommendations) == 1
    assert len(pkg.risks) == 1
    assert pkg.capacity_plan.rep_capacity_utilization == 0.82
