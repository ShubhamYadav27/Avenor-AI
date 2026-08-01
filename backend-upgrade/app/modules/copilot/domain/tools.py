"""
Tool Orchestration Domain Entities (Phase 5.5.3 Architecture)
Defines ToolSpecification, ToolExecutionRequest, ToolExecutionResult,
ToolExecutionPlan, ExecutionNode, and UnifiedIntelligencePackage.
Zero framework or database coupling.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid

from app.modules.copilot.domain.context import ContextCategory, ContextIntent, UnifiedContext
from app.modules.copilot.domain.tool_value_objects import (
    ExecutionCost,
    ExecutionPriority,
    ExecutionStatus,
    FailureReason,
)


@dataclass
class ToolSpecification:
    name: str
    display_name: str
    description: str
    category: str
    supported_intents: List[ContextIntent] = field(default_factory=list)
    required_context_categories: List[ContextCategory] = field(default_factory=list)
    priority: ExecutionPriority = ExecutionPriority.NORMAL
    cost_score: ExecutionCost = ExecutionCost.LOW
    dependencies: List[str] = field(default_factory=list)  # Names of dependent tools
    required_permissions: List[str] = field(default_factory=list)
    timeout_seconds: float = 3.0
    retry_count: int = 2
    supports_caching: bool = True
    supports_parallel: bool = True


@dataclass
class ToolExecutionRequest:
    tool_name: str
    workspace_id: uuid.UUID
    thread_id: Optional[uuid.UUID] = None
    user_id: Optional[str] = None
    user_query: str = ""
    intent: ContextIntent = ContextIntent.GENERAL_STRATEGY
    context: Optional[UnifiedContext] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    execution_id: uuid.UUID = field(default_factory=uuid.uuid4)
    correlation_id: str = field(default_factory=lambda: f"corr-{uuid.uuid4()}")


@dataclass
class ToolExecutionResult:
    tool_name: str
    status: ExecutionStatus = ExecutionStatus.COMPLETED
    output_data: Dict[str, Any] = field(default_factory=dict)
    formatted_text: str = ""
    confidence: float = 0.90
    execution_time_ms: float = 0.0
    provenance_id: str = field(default_factory=lambda: f"prov-tool-{uuid.uuid4()}")
    citation_id: str = field(default_factory=lambda: f"cit-tool-{uuid.uuid4()}")
    failure_reason: Optional[FailureReason] = None
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ExecutionNode:
    tool_name: str
    spec: ToolSpecification
    stage: int = 1  # 1 = Independent/Parallel, 2 = Dependency, 3 = Aggregation
    dependencies: List[str] = field(default_factory=list)
    status: ExecutionStatus = ExecutionStatus.PENDING


@dataclass
class ToolExecutionPlan:
    plan_id: uuid.UUID = field(default_factory=uuid.uuid4)
    workspace_id: Optional[uuid.UUID] = None
    intent: ContextIntent = ContextIntent.GENERAL_STRATEGY
    selected_tools: List[str] = field(default_factory=list)
    execution_stages: List[List[ExecutionNode]] = field(default_factory=list)
    estimated_total_cost: int = 0
    estimated_latency_ms: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ExecutionMetrics:
    total_planning_ms: float = 0.0
    total_execution_ms: float = 0.0
    total_aggregation_ms: float = 0.0
    parallel_batches_count: int = 0
    tools_executed_count: int = 0
    tools_failed_count: int = 0
    tools_retried_count: int = 0


@dataclass
class UnifiedIntelligencePackage:
    workspace_id: uuid.UUID
    thread_id: Optional[uuid.UUID] = None
    intent: ContextIntent = ContextIntent.GENERAL_STRATEGY
    unified_context: Optional[UnifiedContext] = None
    tool_results: List[ToolExecutionResult] = field(default_factory=list)
    aggregated_text: str = ""
    overall_confidence_score: float = 0.95
    provenance_chain: List[str] = field(default_factory=list)
    citation_registry: Dict[str, str] = field(default_factory=dict)  # citation_id -> title/source
    metrics: ExecutionMetrics = field(default_factory=ExecutionMetrics)
    assembled_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
