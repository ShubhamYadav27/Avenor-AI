"""
Swarm Coordinator (Phase 5.5.7)
Orchestrates parallel execution of specialized sub-agents, aggregates insights, and resolves consensus.
"""
import asyncio
from typing import Dict, List, Optional
import uuid

from app.modules.copilot.domain.swarm_entities import AgentResult, SwarmConsensus
from app.modules.copilot.domain.swarm_value_objects import AgentRole, SwarmStatus
from app.modules.copilot.swarm_engine.agents.specialized_agents import (
    AccountResearchAgent,
    DealRiskAgent,
    LeadQualificationAgent,
    ObjectionHandlingAgent,
    OutreachStrategyAgent,
)


class SwarmCoordinator:
    def __init__(self):
        self.lead_agent = LeadQualificationAgent()
        self.research_agent = AccountResearchAgent()
        self.outreach_agent = OutreachStrategyAgent()
        self.objection_agent = ObjectionHandlingAgent()
        self.risk_agent = DealRiskAgent()

    async def execute_swarm(
        self,
        workspace_id: uuid.UUID,
        user_query: str,
        target_company_id: Optional[str] = None,
        target_deal_id: Optional[str] = None,
    ) -> SwarmConsensus:
        # Run all specialized sub-agents concurrently using asyncio.gather
        tasks = [
            self.lead_agent.evaluate(workspace_id, target_company_id),
            self.research_agent.evaluate(workspace_id, target_company_id),
            self.outreach_agent.evaluate(workspace_id, target_company_id),
            self.objection_agent.evaluate(workspace_id, target_company_id),
            self.risk_agent.evaluate(workspace_id, target_deal_id),
        ]

        results: List[AgentResult] = await asyncio.gather(*tasks)

        agent_results_map: Dict[AgentRole, AgentResult] = {res.agent_role: res for res in results}
        all_recs: List[str] = []
        for res in results:
            all_recs.extend(res.recommendations)

        avg_conf = sum(res.confidence_score for res in results) / len(results) if results else 0.90

        summary = (
            f"Autonomous Revenue Swarm executed across {len(results)} specialized AI agents. "
            f"Consensus reached with {avg_conf * 100:.0f}% confidence."
        )

        return SwarmConsensus(
            workspace_id=workspace_id,
            status=SwarmStatus.CONSENSUS_REACHED,
            overall_confidence_score=round(avg_conf, 4),
            aggregated_summary=summary,
            agent_results=agent_results_map,
            key_recommendations=all_recs,
        )


swarm_coordinator = SwarmCoordinator()
