"""
Multi-Agent Framework Engine (Phase 5.5.8)
Coordinates Executive Supervisor -> DelegationEngine -> Specialized Enterprise Agents -> ConsensusEngine.
Zero DB ORM coupling.
"""
import asyncio
import time
from typing import List, Optional
import uuid

from app.modules.copilot.agent_framework.agents.enterprise_agents import (
    CitationAgent,
    CrmAgent,
    ForecastAgent,
    MeetingAgent,
    MemoryAgent,
    ResearchAgent,
    SignalAgent,
    StrategyAgent,
    WorkflowAgent,
)
from app.modules.copilot.agent_framework.application.consensus.consensus_engine import consensus_engine
from app.modules.copilot.agent_framework.application.planners.delegation_engine import delegation_engine
from app.modules.copilot.domain.agent_entities import AgentPackage, AgentResponse, CollaborationSession
from app.modules.copilot.domain.agent_value_objects import CollaborationMode, VotingStrategy
from app.modules.copilot.domain.interfaces import IMultiAgentEngine


class MultiAgentEngine(IMultiAgentEngine):
    def __init__(self):
        self.research_agent = ResearchAgent()
        self.crm_agent = CrmAgent()
        self.signal_agent = SignalAgent()
        self.forecast_agent = ForecastAgent()
        self.strategy_agent = StrategyAgent()
        self.meeting_agent = MeetingAgent()
        self.citation_agent = CitationAgent()
        self.memory_agent = MemoryAgent()
        self.workflow_agent = WorkflowAgent()

    async def execute_collaboration(
        self,
        workspace_id: uuid.UUID,
        user_query: str,
        target_entity_id: Optional[str] = None,
    ) -> AgentPackage:
        t0 = time.perf_counter()

        # 1. Decompose Query into Tasks via Delegation Engine
        tasks = delegation_engine.decompose_query_into_tasks(user_query, target_entity_id)

        session = CollaborationSession(
            workspace_id=workspace_id,
            query=user_query,
            mode=CollaborationMode.PARALLEL,
            tasks=tasks,
        )

        # 2. Run Specialized Enterprise Agents Concurrently
        tasks_coros = [
            self.research_agent.run(workspace_id, user_query, target_entity_id),
            self.crm_agent.run(workspace_id, user_query, target_entity_id),
            self.signal_agent.run(workspace_id, user_query, target_entity_id),
            self.forecast_agent.run(workspace_id, user_query, target_entity_id),
            self.strategy_agent.run(workspace_id, user_query, target_entity_id),
            self.meeting_agent.run(workspace_id, user_query, target_entity_id),
            self.citation_agent.run(workspace_id, user_query, target_entity_id),
            self.memory_agent.run(workspace_id, user_query, target_entity_id),
            self.workflow_agent.run(workspace_id, user_query, target_entity_id),
        ]

        responses: List[AgentResponse] = await asyncio.gather(*tasks_coros)

        # 3. Resolve Consensus via Consensus Engine
        consensus_res = consensus_engine.resolve_consensus(
            session_id=session.session_id,
            responses=responses,
            voting_strategy=VotingStrategy.WEIGHTED_CONFIDENCE,
        )

        session.consensus = consensus_res
        total_lat = (time.perf_counter() - t0) * 1000.0

        summary = (
            f"Executive Supervisor Agent orchestrated {len(responses)} specialized AI agents. "
            f"Consensus reached with {consensus_res.overall_confidence * 100:.0f}% confidence."
        )

        return AgentPackage(
            session_id=session.session_id,
            workspace_id=workspace_id,
            executive_summary=summary,
            consensus=consensus_res,
            total_agents_engaged=len(responses),
            execution_time_ms=round(total_lat, 2),
        )


multi_agent_engine = MultiAgentEngine()
