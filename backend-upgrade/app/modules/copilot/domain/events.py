"""
Copilot Domain Events (Phase 5.5.1 Architecture)
Events for future audit logging, usage tracking, and observability.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import uuid


@dataclass
class CopilotDomainEvent:
    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    event_type: str = "copilot.event"
    workspace_id: Optional[uuid.UUID] = None
    thread_id: Optional[uuid.UUID] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ThreadCreatedEvent(CopilotDomainEvent):
    event_type: str = "copilot.thread.created"


@dataclass
class ThreadDeletedEvent(CopilotDomainEvent):
    event_type: str = "copilot.thread.deleted"


@dataclass
class MessageSentEvent(CopilotDomainEvent):
    event_type: str = "copilot.message.sent"


@dataclass
class GenerationStartedEvent(CopilotDomainEvent):
    event_type: str = "copilot.generation.started"


@dataclass
class GenerationCompletedEvent(CopilotDomainEvent):
    event_type: str = "copilot.generation.completed"


@dataclass
class ProviderChangedEvent(CopilotDomainEvent):
    event_type: str = "copilot.provider.changed"
