from fastapi import APIRouter
from typing import List, Dict, Any

from app.modules.workflow_builder.domain.models import Workflow, Node, Edge, NodeType
from app.modules.workflow_builder.application.services import WorkflowEngine

router = APIRouter(prefix="/v1/workflows", tags=["Enterprise Automation - Workflows"])

# Global mock engine
_engine = WorkflowEngine()

# Pre-seed a demonstration workflow
_mock_workflow = Workflow(
    id="wf_001",
    workspace_id="ws_001",
    name="High Intent Lead Follow-up",
    is_active=True,
    nodes=[
        Node(id="n1", type=NodeType.TRIGGER, operation="signal.created", config={}),
        Node(id="n2", type=NodeType.CONDITION, operation="if_else", config={"expression": "{{trigger.payload.score}} > 80"}),
        Node(id="n3", type=NodeType.ACTION, operation="create_task", config={"assignee": "sales_rep"}),
        Node(id="n4", type=NodeType.ACTION, operation="http_request", config={"url": "https://hooks.slack.com/..."})
    ],
    edges=[
        Edge(id="e1", source_node_id="n1", target_node_id="n2"),
        Edge(id="e2", source_node_id="n2", target_node_id="n3", condition_label="true"),
        Edge(id="e3", source_node_id="n2", target_node_id="n4", condition_label="false")
    ]
)

@router.get("/")
async def list_workflows(workspace_id: str) -> List[dict]:
    """List all workflows in the workspace."""
    if workspace_id == "ws_001":
        return [{"id": _mock_workflow.id, "name": _mock_workflow.name, "is_active": _mock_workflow.is_active}]
    return []

@router.post("/{workflow_id}/execute")
async def execute_workflow(workflow_id: str, payload: Dict[str, Any]) -> dict:
    """Manually trigger a workflow execution for testing."""
    if workflow_id != _mock_workflow.id:
        return {"error": "Workflow not found"}
        
    log = _engine.trigger_workflow(_mock_workflow, payload)
    return {
        "execution_id": log.id,
        "status": log.status,
        "started_at": log.started_at,
        "completed_at": log.completed_at
    }
