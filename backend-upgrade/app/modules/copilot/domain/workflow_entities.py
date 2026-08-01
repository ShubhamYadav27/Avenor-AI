"""
Workflow Entities (Phase 5.5.7)
Pure domain entities representing workflow definitions, steps, step execution results, and workflow packages.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid

from app.modules.copilot.domain.workflow_value_objects import StepType, TriggerType, WorkflowStatus


@dataclass
class WorkflowStep:
    step_id: str = field(default_factory=lambda: f"step-{uuid.uuid4().hex[:8]}")
    name: str = ""
    type: StepType = StepType.TOOL_ACTION
    action_name: str = ""
    params: Dict[str, Any] = field(default_factory=dict)
    condition_expression: Optional[str] = None
    max_retries: int = 3
    compensation_action: Optional[str] = None


@dataclass
class WorkflowDefinition:
    id: str = field(default_factory=lambda: f"wf-def-{uuid.uuid4().hex[:8]}")
    name: str = ""
    description: str = ""
    trigger_type: TriggerType = TriggerType.MANUAL
    steps: List[WorkflowStep] = field(default_factory=list)
    is_active: bool = True
    version: str = "1.0.0"


@dataclass
class StepResult:
    step_id: str
    status: WorkflowStatus = WorkflowStatus.COMPLETED
    output_data: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    latency_ms: float = 0.0


@dataclass
class WorkflowExecution:
    execution_id: str = field(default_factory=lambda: f"wf-exec-{uuid.uuid4().hex[:12]}")
    workflow_id: str = ""
    workspace_id: uuid.UUID = field(default_factory=uuid.uuid4)
    status: WorkflowStatus = WorkflowStatus.RUNNING
    current_step_index: int = 0
    step_results: List[StepResult] = field(default_factory=list)
    context_data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class WorkflowPackage:
    execution_id: str
    workspace_id: uuid.UUID
    workflow_name: str
    status: WorkflowStatus
    summary: str
    steps_completed: int
    total_steps: int
    execution_time_ms: float = 0.0
