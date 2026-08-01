"""
Agent Entities (Phase 5.5.8)
Pure domain entities representing AI agents, capabilities, tasks, agent responses, collaboration sessions, and consensus results.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional
import uuid

from app.modules.copilot.domain.agent_value_objects import CollaborationMode, EnterpriseAgentType, VotingStrategy


@dataclass
class AgentCapability:
    capability_id: str
    name: str
    description: str
    required_tools: List[str] = field(default_factory=list)


@dataclass
class EnterpriseAgent:
    agent_id: str = field(default_factory=lambda: f"agent-{uuid.uuid4().hex[:8]}")
    name: str = ""
    agent_type: EnterpriseAgentType = EnterpriseAgentType.RESEARCH
    capabilities: List[AgentCapability] = field(default_factory=list)
    confidence_score: float = 0.95
    is_active: bool = True


@dataclass
class AgentTask:
    task_id: str = field(default_factory=lambda: f"task-ag-{uuid.uuid4().hex[:8]}")
    assigned_agent_type: EnterpriseAgentType = EnterpriseAgentType.RESEARCH
    user_query: str = ""
    target_entity_id: Optional[str] = None
    status: str = "pending"


@dataclass
class AgentResponse:
    task_id: str
    agent_type: EnterpriseAgentType
    confidence_score: float = 0.90
    insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    citations: List[str] = field(default_factory=list)
    execution_time_ms: float = 0.0


@dataclass
class ConsensusResult:
    session_id: str
    voting_strategy: VotingStrategy = VotingStrategy.WEIGHTED_CONFIDENCE
    overall_confidence: float = 0.94
    aggregated_insights: List[str] = field(default_factory=list)
    key_recommendations: List[str] = field(default_factory=list)
    agent_responses: Dict[EnterpriseAgentType, AgentResponse] = field(default_factory=dict)
    conflict_warnings: List[str] = field(default_factory=list)


@dataclass
class CollaborationSession:
    session_id: str = field(default_factory=lambda: f"collab-{uuid.uuid4().hex[:12]}")
    workspace_id: uuid.UUID = field(default_factory=uuid.uuid4)
    query: str = ""
    mode: CollaborationMode = CollaborationMode.PARALLEL
    tasks: List[AgentTask] = field(default_factory=list)
    consensus: Optional[ConsensusResult] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class AgentPackage:
    session_id: str
    workspace_id: uuid.UUID
    executive_summary: str
    consensus: ConsensusResult
    total_agents_engaged: int
    execution_time_ms: float = 0.0
