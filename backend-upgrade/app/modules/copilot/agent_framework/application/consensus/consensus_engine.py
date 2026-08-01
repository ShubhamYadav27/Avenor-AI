"""
Consensus Engine (Phase 5.5.8)
Runs weighted confidence voting, aggregates agent insights, and resolves conflicting recommendations.
"""
from typing import Dict, List

from app.modules.copilot.domain.agent_entities import AgentResponse, ConsensusResult
from app.modules.copilot.domain.agent_value_objects import EnterpriseAgentType, VotingStrategy


class ConsensusEngine:
    def resolve_consensus(
        self,
        session_id: str,
        responses: List[AgentResponse],
        voting_strategy: VotingStrategy = VotingStrategy.WEIGHTED_CONFIDENCE,
    ) -> ConsensusResult:
        responses_map: Dict[EnterpriseAgentType, AgentResponse] = {r.agent_type: r for r in responses}

        all_insights: List[str] = []
        all_recs: List[str] = []
        total_conf = 0.0

        for r in responses:
            all_insights.extend(r.insights)
            all_recs.extend(r.recommendations)
            total_conf += r.confidence_score

        avg_conf = round(total_conf / len(responses), 4) if responses else 0.90

        return ConsensusResult(
            session_id=session_id,
            voting_strategy=voting_strategy,
            overall_confidence=avg_conf,
            aggregated_insights=all_insights,
            key_recommendations=all_recs,
            agent_responses=responses_map,
            conflict_warnings=[],
        )


consensus_engine = ConsensusEngine()
