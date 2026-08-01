"""
Knowledge Graph Service (Phase 6.4)
Coordinates EntityResolver -> RelationshipExtractor -> BuyingCommitteeMapper -> GraphBuilder -> GraphQueryEngine -> GraphPackage.
Zero DB ORM coupling.
"""
import time
import uuid

from app.modules.knowledge_graph.application.services.buying_committee_mapper import buying_committee_mapper
from app.modules.knowledge_graph.application.services.graph_builder import graph_builder
from app.modules.knowledge_graph.application.services.graph_query_engine import graph_query_engine
from app.modules.knowledge_graph.domain.graph_entities import BuyingCommitteeMap, GraphPackage, KnowledgeGraphQuery, GraphTraversalResult
from app.modules.knowledge_graph.domain.graph_value_objects import NodeType


class KnowledgeGraphService:
    async def build_account_graph(self, workspace_id: uuid.UUID, company_id: str) -> GraphPackage:
        t0 = time.perf_counter()

        nodes, edges = graph_builder.build_account_subgraph(company_id)
        total_lat = (time.perf_counter() - t0) * 1000.0

        return GraphPackage(
            workspace_id=workspace_id,
            center_node_id=company_id,
            nodes=nodes,
            edges=edges,
            total_connections=len(edges),
            execution_time_ms=round(total_lat, 2),
        )

    async def query_graph(self, workspace_id: uuid.UUID, query: KnowledgeGraphQuery) -> GraphTraversalResult:
        nodes, edges = graph_builder.build_account_subgraph(query.center_node_id)
        return graph_query_engine.traverse_graph(query, nodes, edges)

    async def get_buying_committee(self, workspace_id: uuid.UUID, company_id: str) -> BuyingCommitteeMap:
        nodes, _ = graph_builder.build_account_subgraph(company_id)
        contacts = [n for n in nodes if n.node_type == NodeType.CONTACT]
        return buying_committee_mapper.map_committee(company_id, contacts)


knowledge_graph_service = KnowledgeGraphService()
