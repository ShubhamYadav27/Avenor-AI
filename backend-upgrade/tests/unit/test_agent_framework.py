import uuid
import pytest

from app.modules.copilot.agent_framework.agents.enterprise_agents import ResearchAgent
from app.modules.copilot.agent_framework.application.consensus.consensus_engine import consensus_engine
from app.modules.copilot.agent_framework.application.engine import multi_agent_engine
from app.modules.copilot.agent_framework.application.planners.delegation_engine import delegation_engine
from app.modules.copilot.agent_framework.application.registry.agent_registry import agent_registry
from app.modules.copilot.domain.agent_entities import AgentPackage, AgentResponse
from app.modules.copilot.domain.agent_value_objects import EnterpriseAgentType


@pytest.fixture
def anyio_backend():
    return "asyncio"


def test_agent_registry_discovery():
    agents = agent_registry.list_agents()
    assert len(agents) == 15
    research = agent_registry.get_agent(EnterpriseAgentType.RESEARCH)
    assert research.name == "Research Agent"


def test_delegation_engine_decomposition():
    tasks = delegation_engine.decompose_query_into_tasks("Prepare meeting briefing for Stripe")
    assert len(tasks) == 9
    assert tasks[0].assigned_agent_type == EnterpriseAgentType.RESEARCH


def test_consensus_engine_resolution():
    res1 = AgentResponse(task_id="t1", agent_type=EnterpriseAgentType.RESEARCH, confidence_score=0.95, insights=["Grew 18%"])
    res2 = AgentResponse(task_id="t2", agent_type=EnterpriseAgentType.CRM, confidence_score=0.90, insights=["Proposal Sent"])

    consensus = consensus_engine.resolve_consensus(session_id="collab-1", responses=[res1, res2])
    assert consensus.overall_confidence == 0.925
    assert len(consensus.aggregated_insights) == 2


@pytest.mark.anyio
async def test_specialized_agent_run():
    ws_id = uuid.uuid4()
    agent = ResearchAgent()
    res = await agent.run(ws_id, "Analyze account")

    assert res.agent_type == EnterpriseAgentType.RESEARCH
    assert res.confidence_score >= 0.95
    assert len(res.insights) > 0


@pytest.mark.anyio
async def test_multi_agent_engine_e2e_collaboration():
    ws_id = uuid.uuid4()
    pkg = await multi_agent_engine.execute_collaboration(
        workspace_id=ws_id,
        user_query="Prepare me for tomorrow's meeting with Stripe",
    )

    assert isinstance(pkg, AgentPackage)
    assert pkg.total_agents_engaged == 9
    assert pkg.consensus.overall_confidence >= 0.90
    assert "Executive Supervisor Agent" in pkg.executive_summary
    assert EnterpriseAgentType.RESEARCH in pkg.consensus.agent_responses
    assert EnterpriseAgentType.CRM in pkg.consensus.agent_responses
