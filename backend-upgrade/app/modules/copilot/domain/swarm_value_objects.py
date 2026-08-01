"""
Swarm Value Objects (Phase 5.5.7)
Domain enums and value objects for Multi-Agent Autonomous Revenue Swarm Engine.
Zero external framework dependencies.
"""
from enum import Enum


class AgentRole(str, Enum):
    LEAD_QUALIFIER = "lead_qualifier"
    ACCOUNT_RESEARCHER = "account_researcher"
    OUTREACH_STRATEGIST = "outreach_strategist"
    OBJECTION_HANDLER = "objection_handler"
    DEAL_RISK_ANALYST = "deal_risk_analyst"
    SWARM_COORDINATOR = "swarm_coordinator"


class SwarmStatus(str, Enum):
    INITIALIZING = "initializing"
    EXECUTING = "executing"
    CONSENSUS_REACHED = "consensus_reached"
    COMPLETED = "completed"
    DEGRADED = "degraded"
