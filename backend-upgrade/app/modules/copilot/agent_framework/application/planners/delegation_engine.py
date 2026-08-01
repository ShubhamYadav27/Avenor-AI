"""
Delegation Engine (Phase 5.5.8)
Decomposes user queries into sub-goals and assigns tasks to specialized expert agents.
"""
from typing import List, Optional

from app.modules.copilot.domain.agent_entities import AgentTask
from app.modules.copilot.domain.agent_value_objects import EnterpriseAgentType


class DelegationEngine:
    def decompose_query_into_tasks(self, query: str, target_id: Optional[str] = None) -> List[AgentTask]:
        # Always engage top specialized agents for comprehensive revenue intelligence
        return [
            AgentTask(assigned_agent_type=EnterpriseAgentType.RESEARCH, user_query=query, target_entity_id=target_id),
            AgentTask(assigned_agent_type=EnterpriseAgentType.CRM, user_query=query, target_entity_id=target_id),
            AgentTask(assigned_agent_type=EnterpriseAgentType.SIGNAL, user_query=query, target_entity_id=target_id),
            AgentTask(assigned_agent_type=EnterpriseAgentType.FORECAST, user_query=query, target_entity_id=target_id),
            AgentTask(assigned_agent_type=EnterpriseAgentType.STRATEGY, user_query=query, target_entity_id=target_id),
            AgentTask(assigned_agent_type=EnterpriseAgentType.MEETING, user_query=query, target_entity_id=target_id),
            AgentTask(assigned_agent_type=EnterpriseAgentType.CITATION, user_query=query, target_entity_id=target_id),
            AgentTask(assigned_agent_type=EnterpriseAgentType.MEMORY, user_query=query, target_entity_id=target_id),
            AgentTask(assigned_agent_type=EnterpriseAgentType.WORKFLOW, user_query=query, target_entity_id=target_id),
        ]


delegation_engine = DelegationEngine()
