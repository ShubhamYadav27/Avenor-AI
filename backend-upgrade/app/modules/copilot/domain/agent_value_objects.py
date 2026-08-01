"""
Agent Value Objects (Phase 5.5.8)
Domain enums and value objects for Enterprise Multi-Agent Collaboration Framework.
Zero external framework dependencies.
"""
from enum import Enum


class EnterpriseAgentType(str, Enum):
    RESEARCH = "research"
    CRM = "crm"
    SIGNAL = "signal"
    FORECAST = "forecast"
    STRATEGY = "strategy"
    MEETING = "meeting"
    COMPETITIVE = "competitive"
    HEALTH = "health"
    EXPANSION = "expansion"
    RENEWAL = "renewal"
    WORKFLOW = "workflow"
    MEMORY = "memory"
    CITATION = "citation"
    LEARNING = "learning"
    EXECUTIVE_SUPERVISOR = "executive_supervisor"


class VotingStrategy(str, Enum):
    MAJORITY = "majority"
    WEIGHTED_CONFIDENCE = "weighted_confidence"
    SUPERVISOR_DECISION = "supervisor_decision"


class CollaborationMode(str, Enum):
    PARALLEL = "parallel"
    SEQUENTIAL = "sequential"
    ADAPTIVE = "adaptive"
