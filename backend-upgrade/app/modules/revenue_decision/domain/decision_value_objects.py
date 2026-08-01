"""
Decision Value Objects (Phase 6.2)
Domain enums and value objects for Enterprise Revenue Decision Intelligence Engine.
Zero external framework dependencies.
"""
from enum import Enum


class DecisionType(str, Enum):
    NEXT_BEST_ACCOUNT = "next_best_account"
    NEXT_BEST_OPPORTUNITY = "next_best_opportunity"
    NEXT_BEST_CONTACT = "next_best_contact"
    NEXT_BEST_SALES_ACTION = "next_best_sales_action"
    RENEWAL_DECISION = "renewal_decision"
    EXPANSION_DECISION = "expansion_decision"
    RISK_MITIGATION = "risk_mitigation"


class ActionUrgency(str, Enum):
    IMMEDIATE = "immediate"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class OutreachChannel(str, Enum):
    EMAIL = "email"
    LINKEDIN = "linkedin"
    PHONE = "phone"
    CRM_TASK = "crm_task"


class ConstraintType(str, Enum):
    SALES_CAPACITY = "sales_capacity"
    TERRITORY_RULE = "territory_rule"
    ACTIVE_WORKFLOW_LOCK = "active_workflow_lock"
    ROLE_PERMISSION = "role_permission"


class PolicyMode(str, Enum):
    STRICT_ENFORCE = "strict_enforce"
    WARN_ONLY = "warn_only"
    BYPASS_ALLOWED = "bypass_allowed"
