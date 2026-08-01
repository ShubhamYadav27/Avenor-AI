"""
Agent Registry (Phase 5.5.8)
Discovers, registers, and tracks capabilities of all 18 enterprise AI agents.
"""
from typing import Dict, List

from app.modules.copilot.domain.agent_entities import AgentCapability, EnterpriseAgent
from app.modules.copilot.domain.agent_value_objects import EnterpriseAgentType


class AgentRegistry:
    def __init__(self):
        self._agents: Dict[EnterpriseAgentType, EnterpriseAgent] = {}
        self._register_default_agents()

    def _register_default_agents(self):
        for agent_type in EnterpriseAgentType:
            name = agent_type.value.replace("_", " ").title() + " Agent"
            agent = EnterpriseAgent(
                name=name,
                agent_type=agent_type,
                capabilities=[
                    AgentCapability(
                        capability_id=f"cap-{agent_type.value}",
                        name=f"{name} Core Intelligence",
                        description=f"Executes specialized {agent_type.value} reasoning tasks.",
                    )
                ],
                confidence_score=0.95,
            )
            self._agents[agent_type] = agent

    def list_agents(self) -> List[EnterpriseAgent]:
        return list(self._agents.values())

    def get_agent(self, agent_type: EnterpriseAgentType) -> EnterpriseAgent:
        return self._agents.get(agent_type) or self._agents[EnterpriseAgentType.RESEARCH]


agent_registry = AgentRegistry()
