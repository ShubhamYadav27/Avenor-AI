from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime

class NodeType(str, Enum):
    TRIGGER = "trigger"
    ACTION = "action"
    CONDITION = "condition"
    AI = "ai"
    INTEGRATION = "integration"

class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUSPENDED = "suspended"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Node:
    """A single step in a Workflow."""
    id: str
    type: NodeType
    operation: str # e.g., 'company.created', 'send_slack_message', 'if_else'
    config: Dict[str, Any] # e.g., {'channel': '#sales', 'message': '{{company.name}} created!'}
    name: str = ""

@dataclass
class Edge:
    """Directed connection between two Nodes."""
    id: str
    source_node_id: str
    target_node_id: str
    condition_label: Optional[str] = None # e.g., 'true', 'false' (for branching)

@dataclass
class Workflow:
    """A Directed Acyclic Graph (DAG) representing an automation sequence."""
    id: str
    workspace_id: str
    name: str
    nodes: List[Node]
    edges: List[Edge]
    is_active: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def get_trigger_nodes(self) -> List[Node]:
        return [n for n in self.nodes if n.type == NodeType.TRIGGER]
        
    def get_outgoing_edges(self, node_id: str) -> List[Edge]:
        return [e for e in self.edges if e.source_node_id == node_id]
        
    def get_node(self, node_id: str) -> Optional[Node]:
        for n in self.nodes:
            if n.id == node_id: return n
        return None

@dataclass
class ExecutionContext:
    """State carrier passed between nodes during execution."""
    execution_id: str
    workflow_id: str
    variables: Dict[str, Any] = field(default_factory=dict)
    
    def get_variable(self, path: str) -> Any:
        """
        Retrieves a variable by dot notation (e.g., trigger.payload.company.id).
        A real Expression Engine handles complex evaluation.
        """
        parts = path.split(".")
        val = self.variables
        for part in parts:
            if isinstance(val, dict) and part in val:
                val = val[part]
            else:
                return None
        return val

@dataclass
class ExecutionLog:
    id: str
    workflow_id: str
    status: ExecutionStatus
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
