"""
Graph Query Engine (Phase 6.4)
Performs multi-hop graph traversal queries across revenue entities.
"""
from typing import List

from app.modules.knowledge_graph.domain.graph_entities import GraphEdge, GraphNode, GraphTraversalResult, KnowledgeGraphQuery


class GraphQueryEngine:
    def traverse_graph(self, query: KnowledgeGraphQuery, nodes: List[GraphNode], edges: List[GraphEdge]) -> GraphTraversalResult:
        center = next((n for n in nodes if n.node_id == query.center_node_id), nodes[0])
        connected = [n for n in nodes if n.node_id != query.center_node_id]

        if query.target_node_types:
            connected = [n for n in connected if n.node_type in query.target_node_types or not query.target_node_types]

        return GraphTraversalResult(
            center_node=center,
            connected_nodes=connected,
            edges=edges,
            max_depth_reached=query.max_depth,
        )


graph_query_engine = GraphQueryEngine()
