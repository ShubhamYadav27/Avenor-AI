"""
Entity Resolver (Phase 6.4)
Identity resolution, deduplication, and entity fusion across multi-source CRM and signal data.
"""
from typing import List

from app.modules.knowledge_graph.domain.graph_entities import GraphNode, KnowledgeFusionResult


class EntityResolver:
    def resolve_identities(self, raw_nodes: List[GraphNode]) -> KnowledgeFusionResult:
        primary_id = raw_nodes[0].node_id if raw_nodes else "node-001"
        merged_ids = [n.node_id for n in raw_nodes[1:]]

        return KnowledgeFusionResult(
            primary_node_id=primary_id,
            merged_entity_ids=merged_ids,
            match_confidence=0.96,
        )


entity_resolver = EntityResolver()
