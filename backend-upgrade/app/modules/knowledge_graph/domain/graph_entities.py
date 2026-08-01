"""
Knowledge Graph Entities (Phase 6.4)
Pure domain entities representing graph nodes, relationships, identity fusion, buying committee maps, and packages.
"""
from dataclasses import dataclass, field
from typing import Dict, List
import uuid

from app.modules.knowledge_graph.domain.graph_value_objects import NodeType, RelationType, TraversalDirection


@dataclass
class GraphNode:
    node_id: str
    label: str
    node_type: NodeType = NodeType.COMPANY
    properties: Dict[str, str] = field(default_factory=dict)
    confidence: float = 1.0


@dataclass
class GraphEdge:
    source_id: str
    target_id: str
    relation_type: RelationType = RelationType.WORKS_FOR
    weight: float = 1.0
    properties: Dict[str, str] = field(default_factory=dict)


@dataclass
class BuyingCommitteeMap:
    company_id: str
    champions: List[GraphNode] = field(default_factory=list)
    economic_buyers: List[GraphNode] = field(default_factory=list)
    technical_evaluators: List[GraphNode] = field(default_factory=list)
    blockers: List[GraphNode] = field(default_factory=list)
    total_members: int = 0


@dataclass
class KnowledgeFusionResult:
    primary_node_id: str
    merged_entity_ids: List[str] = field(default_factory=list)
    match_confidence: float = 0.95


@dataclass
class KnowledgeGraphQuery:
    center_node_id: str
    target_node_types: List[NodeType] = field(default_factory=list)
    relation_types: List[RelationType] = field(default_factory=list)
    max_depth: int = 2
    direction: TraversalDirection = TraversalDirection.BOTH
    min_confidence: float = 0.5


@dataclass
class GraphTraversalResult:
    center_node: GraphNode
    connected_nodes: List[GraphNode] = field(default_factory=list)
    edges: List[GraphEdge] = field(default_factory=list)
    max_depth_reached: int = 2


@dataclass
class GraphPackage:
    workspace_id: uuid.UUID
    center_node_id: str
    nodes: List[GraphNode] = field(default_factory=list)
    edges: List[GraphEdge] = field(default_factory=list)
    total_connections: int = 0
    execution_time_ms: float = 0.0
