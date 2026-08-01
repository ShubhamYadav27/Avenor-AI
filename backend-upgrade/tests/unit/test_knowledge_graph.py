import uuid
import pytest

from app.modules.knowledge_graph.application.service import knowledge_graph_service
from app.modules.knowledge_graph.application.services.buying_committee_mapper import buying_committee_mapper
from app.modules.knowledge_graph.application.services.entity_resolver import entity_resolver
from app.modules.knowledge_graph.application.services.graph_builder import graph_builder
from app.modules.knowledge_graph.application.services.relationship_extractor import relationship_extractor
from app.modules.knowledge_graph.domain.graph_entities import GraphNode, GraphPackage
from app.modules.knowledge_graph.domain.graph_value_objects import NodeType, RelationType


@pytest.fixture
def anyio_backend():
    return "asyncio"


def test_entity_resolver():
    nodes = [
        GraphNode(node_id="n1", label="Acme Corp"),
        GraphNode(node_id="n2", label="Acme Corporation"),
    ]
    fusion = entity_resolver.resolve_identities(nodes)
    assert fusion.primary_node_id == "n1"
    assert fusion.merged_entity_ids == ["n2"]
    assert fusion.match_confidence == 0.96


def test_relationship_extractor():
    edges = relationship_extractor.extract_relationships("comp-101")
    assert len(edges) == 6
    assert edges[0].relation_type == RelationType.WORKS_FOR


def test_buying_committee_mapper():
    contacts = [
        GraphNode(node_id="cnt-1", label="Alex Morgan", node_type=NodeType.CONTACT, properties={"title": "VP RevOps"}),
        GraphNode(node_id="cnt-2", label="Jane Doe", node_type=NodeType.CONTACT, properties={"title": "CFO"}),
    ]
    comm = buying_committee_mapper.map_committee("comp-101", contacts)
    assert comm.total_members == 2
    assert len(comm.champions) == 1
    assert len(comm.economic_buyers) == 1


def test_graph_builder():
    nodes, edges = graph_builder.build_account_subgraph("comp-101")
    assert len(nodes) == 7
    assert len(edges) == 6


@pytest.mark.anyio
async def test_knowledge_graph_service_e2e():
    ws_id = uuid.uuid4()
    pkg = await knowledge_graph_service.build_account_graph(ws_id, "comp-101")
    assert isinstance(pkg, GraphPackage)
    assert pkg.center_node_id == "comp-101"

    comm = await knowledge_graph_service.get_buying_committee(ws_id, "comp-101")
    assert comm.company_id == "comp-101"
    assert comm.total_members >= 1
