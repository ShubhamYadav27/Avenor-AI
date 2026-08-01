"""
Knowledge Graph Value Objects (Phase 6.4)
Domain enums and value objects for Enterprise Revenue Knowledge Graph (ERKG).
Zero external framework dependencies.
"""
from enum import Enum


class NodeType(str, Enum):
    COMPANY = "company"
    CONTACT = "contact"
    OPPORTUNITY = "opportunity"
    BUYING_COMMITTEE = "buying_committee"
    SIGNAL = "signal"
    TECHNOLOGY = "technology"
    PRODUCT = "product"
    COMPETITOR = "competitor"
    INDUSTRY = "industry"
    WORKSPACE = "workspace"
    SALES_REP = "sales_rep"
    MEETING = "meeting"
    EMAIL = "email"
    CONVERSATION = "conversation"
    TASK = "task"
    REVENUE_GOAL = "revenue_goal"
    TERRITORY = "territory"
    PLAYBOOK = "playbook"
    WORKFLOW = "workflow"
    AGENT = "agent"
    MEMORY = "memory"
    CITATION = "citation"


class RelationType(str, Enum):
    WORKS_FOR = "works_for"
    REPORTS_TO = "reports_to"
    KNOWS = "knows"
    BUYS_FROM = "buys_from"
    COMPETES_WITH = "competes_with"
    USES = "uses"
    EVALUATES = "evaluates"
    ATTENDED = "attended"
    EMAILED = "emailed"
    OWNS = "owns"
    MANAGES = "manages"
    PARTICIPATED_IN = "participated_in"
    INFLUENCED = "influenced"
    BLOCKS = "blocks"
    ACCELERATES = "accelerates"
    CREATED = "created"
    GENERATED = "generated"
    RELATED_TO = "related_to"
    BELONGS_TO = "belongs_to"
    SUPPORTS = "supports"
    DEPENDS_ON = "depends_on"


class TraversalDirection(str, Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    BOTH = "both"


class ConfidenceTier(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
