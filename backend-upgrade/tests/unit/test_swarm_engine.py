import uuid
import pytest

from app.modules.copilot.domain.swarm_entities import SwarmConsensus
from app.modules.copilot.domain.swarm_value_objects import AgentRole, SwarmStatus
from app.modules.copilot.swarm_engine.agents.specialized_agents import (
    LeadQualificationAgent,
)
from app.modules.copilot.swarm_engine.coordinator.swarm_coordinator import swarm_coordinator


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_individual_agents_evaluation():
    ws_id = uuid.uuid4()
    lead_agent = LeadQualificationAgent()
    res = await lead_agent.evaluate(ws_id)

    assert res.agent_role == AgentRole.LEAD_QUALIFIER
    assert res.confidence_score >= 0.90
    assert len(res.insights) > 0
    assert len(res.recommendations) > 0


@pytest.mark.anyio
async def test_swarm_coordinator_parallel_execution():
    ws_id = uuid.uuid4()
    consensus = await swarm_coordinator.execute_swarm(
        workspace_id=ws_id,
        user_query="Run strategy swarm for target account",
    )

    assert isinstance(consensus, SwarmConsensus)
    assert consensus.status == SwarmStatus.CONSENSUS_REACHED
    assert consensus.overall_confidence_score >= 0.90
    assert len(consensus.agent_results) == 5
    assert AgentRole.LEAD_QUALIFIER in consensus.agent_results
    assert AgentRole.ACCOUNT_RESEARCHER in consensus.agent_results
    assert AgentRole.OUTREACH_STRATEGIST in consensus.agent_results
    assert AgentRole.OBJECTION_HANDLER in consensus.agent_results
    assert AgentRole.DEAL_RISK_ANALYST in consensus.agent_results

    assert len(consensus.key_recommendations) >= 5
