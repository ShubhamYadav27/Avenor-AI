"""
Graph Builder (Phase 6.4)
Ingests CRM objects, signals, tech stacks, competitors, and memory into graph nodes and weighted edges.
"""
from typing import List, Tuple

from app.modules.knowledge_graph.domain.graph_entities import GraphEdge, GraphNode
from app.modules.knowledge_graph.domain.graph_value_objects import NodeType, RelationType


class GraphBuilder:
    def build_account_subgraph(self, company_id: str) -> Tuple[List[GraphNode], List[GraphEdge]]:
        n_comp = GraphNode(node_id=company_id, label="Acme Corp", node_type=NodeType.COMPANY, properties={"industry": "SaaS"})
        n_cnt = GraphNode(node_id="cnt-101", label="Alex Morgan", node_type=NodeType.CONTACT, properties={"title": "VP RevOps"})
        n_deal = GraphNode(node_id="deal-101", label="Proposal $180k ARR", node_type=NodeType.OPPORTUNITY, properties={"amount": "180000"})
        n_sig = GraphNode(node_id="sig-101", label="Intent Surge", node_type=NodeType.SIGNAL, properties={"topic": "Revenue Intelligence"})
        n_tech = GraphNode(node_id="tech-101", label="Snowflake & Salesforce", node_type=NodeType.TECHNOLOGY)
        n_comp_rel = GraphNode(node_id="competitor-101", label="Gong & Clari", node_type=NodeType.COMPETITOR)
        n_mem = GraphNode(node_id="mem-101", label="Prefers SOC2 Package Upfront", node_type=NodeType.MEMORY)

        e1 = GraphEdge(source_id=company_id, target_id="cnt-101", relation_type=RelationType.WORKS_FOR, weight=1.0)
        e2 = GraphEdge(source_id=company_id, target_id="deal-101", relation_type=RelationType.OWNS, weight=1.0)
        e3 = GraphEdge(source_id=company_id, target_id="sig-101", relation_type=RelationType.GENERATED, weight=0.95)
        e4 = GraphEdge(source_id=company_id, target_id="tech-101", relation_type=RelationType.USES, weight=0.90)
        e5 = GraphEdge(source_id=company_id, target_id="competitor-101", relation_type=RelationType.COMPETES_WITH, weight=0.85)
        e6 = GraphEdge(source_id=company_id, target_id="mem-101", relation_type=RelationType.RELATED_TO, weight=0.92)

        nodes = [n_comp, n_cnt, n_deal, n_sig, n_tech, n_comp_rel, n_mem]
        edges = [e1, e2, e3, e4, e5, e6]
        return nodes, edges


graph_builder = GraphBuilder()
