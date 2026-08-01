from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime

class AgentStatus(str, Enum):
    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    TOOL_WAIT = "tool_wait"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class ToolCall:
    """Represents an LLM requesting to use a permitted tool."""
    id: str
    tool_name: str
    arguments: Dict[str, Any]

@dataclass
class Agent:
    """An autonomous actor capable of executing tasks."""
    id: str
    workspace_id: str
    name: str # e.g., 'Company Intelligence Agent'
    role: str # e.g., 'Senior Research Analyst'
    prompt_id: str # Link to Prompt Studio canonical template
    allowed_tools: List[str] # e.g., ['public_api.get_company', 'workflow.start_enrichment']
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Task:
    """A decomposed step of a larger goal."""
    id: str
    description: str
    expected_output: str
    assigned_agent_id: str
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[str] = None
    tool_calls: List[ToolCall] = field(default_factory=list)

@dataclass
class ExecutionPlan:
    """A Directed Acyclic Graph (or list) of Tasks created by the Planner."""
    id: str
    goal: str
    tasks: List[Task]
    status: AgentStatus = AgentStatus.IDLE
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
