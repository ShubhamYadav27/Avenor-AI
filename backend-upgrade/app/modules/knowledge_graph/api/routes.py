"""
Knowledge Graph API Routes (Phase 6.4)
Exposes endpoints for querying, traversing, and extracting buying committees from the Enterprise Revenue Knowledge Graph.
"""
from typing import Any, Dict
from fastapi import APIRouter, Depends

from app.api.auth import AuthenticatedUser, get_current_user
from app.modules.knowledge_graph.application.service import knowledge_graph_service
from app.modules.knowledge_graph.domain.graph_entities import KnowledgeGraphQuery
from app.modules.knowledge_graph.domain.graph_value_objects import NodeType, TraversalDirection

graph_router_api = APIRouter(prefix="", tags=["revenue-knowledge-graph"])


@graph_router_api.get("/graph/account/{company_id}", response_model=Dict[str, Any])
async def get_account_knowledge_graph(
    company_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    pkg = await knowledge_graph_service.build_account_graph(current_user.workspace_id, company_id)
    return {
        "workspace_id": str(pkg.workspace_id),
        "center_node_id": pkg.center_node_id,
        "total_connections": pkg.total_connections,
        "execution_time_ms": pkg.execution_time_ms,
        "nodes": [
            {
                "node_id": n.node_id,
                "label": n.label,
                "node_type": n.node_type.value,
                "properties": n.properties,
            }
            for n in pkg.nodes
        ],
        "edges": [
            {
                "source_id": e.source_id,
                "target_id": e.target_id,
                "relation_type": e.relation_type.value,
                "weight": e.weight,
            }
            for e in pkg.edges
        ],
    }


@graph_router_api.post("/graph/query", response_model=Dict[str, Any])
async def query_knowledge_graph(
    company_id: str = "comp-101",
    max_depth: int = 2,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    query = KnowledgeGraphQuery(
        center_node_id=company_id,
        target_node_types=[NodeType.CONTACT, NodeType.OPPORTUNITY, NodeType.SIGNAL],
        max_depth=max_depth,
        direction=TraversalDirection.BOTH,
    )
    res = await knowledge_graph_service.query_graph(current_user.workspace_id, query)

    return {
        "center_node": {
            "node_id": res.center_node.node_id,
            "label": res.center_node.label,
            "node_type": res.center_node.node_type.value,
        },
        "max_depth_reached": res.max_depth_reached,
        "connected_nodes_count": len(res.connected_nodes),
        "connected_nodes": [
            {
                "node_id": n.node_id,
                "label": n.label,
                "node_type": n.node_type.value,
            }
            for n in res.connected_nodes
        ],
    }


@graph_router_api.get("/graph/buying-committee/{company_id}", response_model=Dict[str, Any])
async def get_buying_committee(
    company_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    comm = await knowledge_graph_service.get_buying_committee(current_user.workspace_id, company_id)
    return {
        "company_id": comm.company_id,
        "total_members": comm.total_members,
        "champions": [{"node_id": c.node_id, "label": c.label, "title": c.properties.get("title", "")} for c in comm.champions],
        "economic_buyers": [{"node_id": c.node_id, "label": c.label, "title": c.properties.get("title", "")} for c in comm.economic_buyers],
        "technical_evaluators": [{"node_id": c.node_id, "label": c.label, "title": c.properties.get("title", "")} for c in comm.technical_evaluators],
        "blockers": [{"node_id": c.node_id, "label": c.label, "title": c.properties.get("title", "")} for c in comm.blockers],
    }
