import uuid
import pytest

from app.modules.knowledge_graph.application.service import knowledge_graph_service
from app.modules.knowledge_graph.application.services.graph_builder import graph_builder
from app.modules.knowledge_graph.domain.graph_entities import KnowledgeGraphQuery
from app.modules.knowledge_graph.domain.graph_value_objects import NodeType
from app.modules.strategic_intelligence.application.planners.capacity_planner import capacity_planner
from app.modules.strategic_intelligence.application.planners.territory_planner import territory_planner
from app.modules.strategic_intelligence.application.service import strategic_intelligence_service
from app.modules.strategic_intelligence.application.services.strategic_advisor import strategic_advisor
from app.modules.strategic_intelligence.domain.strategic_entities import AutonomousOrgPackage


@pytest.fixture
def anyio_backend():
    return "asyncio"


def test_graph_builder():
    nodes, edges = graph_builder.build_account_subgraph("comp-101")
    assert len(nodes) == 7
    assert len(edges) == 6
    assert nodes[0].node_type == NodeType.COMPANY


@pytest.mark.anyio
async def test_knowledge_graph_query():
    ws_id = uuid.uuid4()
    query = KnowledgeGraphQuery(center_node_id="comp-101", target_node_types=[], max_depth=2)
    res = await knowledge_graph_service.query_graph(ws_id, query)

    assert res.center_node.node_id == "comp-101"
    assert len(res.connected_nodes) == 6


def test_territory_planner():
    plans = territory_planner.create_territory_plans()
    assert len(plans) == 2
    assert plans[0].territory_name == "North America Enterprise"
    assert plans[0].target_pipeline_usd == 6500000.0


def test_capacity_planner():
    cap = capacity_planner.evaluate_capacity()
    assert cap.rep_capacity_utilization == 0.82
    assert cap.recommended_headcount_delta == 2


def test_strategic_advisor():
    trends = strategic_advisor.analyze_market_trends()
    assert len(trends) == 1
    assert trends[0].topic == "AI Revenue Intelligence Adoption"


@pytest.mark.anyio
async def test_strategic_intelligence_service_complete():
    ws_id = uuid.uuid4()
    pkg = await strategic_intelligence_service.generate_autonomous_org_status(ws_id)

    assert isinstance(pkg, AutonomousOrgPackage)
    assert len(pkg.territory_plans) == 2
    assert len(pkg.market_trends) == 1
    assert pkg.capacity_plan.rep_capacity_utilization == 0.82
