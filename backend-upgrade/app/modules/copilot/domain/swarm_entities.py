"""
Swarm Entities (Phase 5.5.7)
Pure domain entities representing specialized agent results, swarm tasks, and consensus objects.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional
import uuid

from app.modules.copilot.domain.swarm_value_objects import AgentRole, SwarmStatus


@dataclass
class AgentResult:
    agent_role: AgentRole
    confidence_score: float = 0.90
    insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    citations: List[str] = field(default_factory=list)
    execution_time_ms: float = 0.0


@dataclass
class SwarmTask:
    task_id: str = field(default_factory=lambda: f"task-sw-{uuid.uuid4().hex[:8]}")
    workspace_id: uuid.UUID = field(default_factory=uuid.uuid4)
    target_company_id: Optional[str] = None
    target_deal_id: Optional[str] = None
    user_query: str = ""
    required_agents: List[AgentRole] = field(default_factory=list)


@dataclass
class SwarmConsensus:
    swarm_id: str = field(default_factory=lambda: f"sw-{uuid.uuid4().hex[:12]}")
    workspace_id: uuid.UUID = field(default_factory=uuid.uuid4)
    status: SwarmStatus = SwarmStatus.CONSENSUS_REACHED
    overall_confidence_score: float = 0.92
    aggregated_summary: str = ""
    agent_results: Dict[AgentRole, AgentResult] = field(default_factory=dict)
    key_recommendations: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
