import uuid
import pytest

from app.modules.autonomous_revops.application.service import autonomous_revops_service
from app.modules.autonomous_revops.domain.revops_entities import RevOpsPackage
from app.modules.knowledge_graph.application.service import knowledge_graph_service
from app.modules.knowledge_graph.domain.graph_entities import GraphPackage
from app.modules.strategic_intelligence.application.service import strategic_intelligence_service
from app.modules.strategic_intelligence.domain.strategic_entities import AutonomousOrgPackage


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_autonomous_revops_service():
    ws_id = uuid.uuid4()
    pkg = await autonomous_revops_service.execute_operations(ws_id, "comp-101")

    assert isinstance(pkg, RevOpsPackage)
    assert len(pkg.active_missions) == 1
    assert len(pkg.pending_approvals) == 1


@pytest.mark.anyio
async def test_knowledge_graph_service():
    ws_id = uuid.uuid4()
    pkg = await knowledge_graph_service.build_account_graph(ws_id, "comp-101")

    assert isinstance(pkg, GraphPackage)
    assert pkg.center_node_id == "comp-101"
    assert len(pkg.nodes) == 7
    assert len(pkg.edges) == 6


@pytest.mark.anyio
async def test_strategic_intelligence_service():
    ws_id = uuid.uuid4()
    pkg = await strategic_intelligence_service.generate_autonomous_org_status(ws_id)

    assert isinstance(pkg, AutonomousOrgPackage)
    assert len(pkg.territory_plans) == 2
    assert pkg.capacity_plan.rep_capacity_utilization == 0.82
    assert "Avenor Autonomous Revenue Operating System Active" in pkg.ai_partner_status
