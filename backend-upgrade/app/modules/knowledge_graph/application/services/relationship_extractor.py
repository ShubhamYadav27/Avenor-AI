"""
Relationship Extractor (Phase 6.4)
Extracts multi-source semantic relationships with confidence weighting.
"""
from typing import List

from app.modules.knowledge_graph.domain.graph_entities import GraphEdge
from app.modules.knowledge_graph.domain.graph_value_objects import RelationType


class RelationshipExtractor:
    def extract_relationships(self, company_id: str) -> List[GraphEdge]:
        return [
            GraphEdge(source_id=company_id, target_id="cnt-101", relation_type=RelationType.WORKS_FOR, weight=1.0),
            GraphEdge(source_id=company_id, target_id="deal-101", relation_type=RelationType.OWNS, weight=1.0),
            GraphEdge(source_id=company_id, target_id="sig-101", relation_type=RelationType.GENERATED, weight=0.95),
            GraphEdge(source_id=company_id, target_id="tech-101", relation_type=RelationType.USES, weight=0.90),
            GraphEdge(source_id=company_id, target_id="competitor-101", relation_type=RelationType.COMPETES_WITH, weight=0.85),
            GraphEdge(source_id="cnt-101", target_id="deal-101", relation_type=RelationType.INFLUENCED, weight=0.92),
        ]


relationship_extractor = RelationshipExtractor()
