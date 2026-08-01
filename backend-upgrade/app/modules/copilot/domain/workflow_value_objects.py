"""
Workflow Value Objects (Phase 5.5.7)
Domain enums and value objects for Enterprise Workflow & Automation Engine.
Zero external framework dependencies.
"""
from enum import Enum


class WorkflowStatus(str, Enum):
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED_FOR_APPROVAL = "paused_for_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATED = "compensated"


class StepType(str, Enum):
    AI_DECISION = "ai_decision"
    TOOL_ACTION = "tool_action"
    CRM_MUTATION = "crm_mutation"
    NOTIFICATION = "notification"
    APPROVAL_GATE = "approval_gate"


class TriggerType(str, Enum):
    MANUAL = "manual"
    SCHEDULED_CRON = "scheduled_cron"
    BUYING_SIGNAL_SURGE = "buying_signal_surge"
    CRM_EVENT = "crm_event"
    WEBHOOK = "webhook"
