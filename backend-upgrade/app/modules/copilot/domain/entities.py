"""
Copilot Domain Entities & Value Objects
Pure Python dataclasses with zero framework coupling.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
import enum
from typing import Any, Dict, List, Optional
import uuid


class CopilotRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ThreadStatus(str, enum.Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"


@dataclass
class CopilotMessageEntity:
    id: uuid.UUID
    thread_id: uuid.UUID
    role: CopilotRole
    content: str
    model_provider: Optional[str] = None
    model_name: Optional[str] = None
    token_count: int = 0
    extra_metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class CopilotStateEntity:
    id: uuid.UUID
    workspace_id: uuid.UUID
    thread_id: uuid.UUID
    current_company_id: Optional[uuid.UUID] = None
    current_deal_id: Optional[str] = None
    current_contact_id: Optional[uuid.UUID] = None
    active_workspace_context: Dict[str, Any] = field(default_factory=dict)
    active_recommendation: Dict[str, Any] = field(default_factory=dict)
    active_prompt_context: Optional[str] = None
    token_budget: int = 8000
    last_tool_used: Optional[str] = None
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class CopilotThreadEntity:
    id: uuid.UUID
    workspace_id: uuid.UUID
    user_id: uuid.UUID
    title: str = "New Strategic Session"
    status: ThreadStatus = ThreadStatus.ACTIVE
    extra_metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    messages: List[CopilotMessageEntity] = field(default_factory=list)
    state: Optional[CopilotStateEntity] = None


@dataclass
class ModelCapability:
    supports_streaming: bool = True
    supports_tools: bool = False
    supports_vision: bool = False
    supports_system_prompt: bool = True
    context_window_size: int = 128000
    cost_per_1k_tokens: float = 0.0015


@dataclass
class ModelDescriptor:
    provider: str  # e.g., "gemini", "openai", "mock"
    name: str      # e.g., "gemini-1.5-pro", "gpt-4o", "mock-model"
    capabilities: ModelCapability = field(default_factory=ModelCapability)
    is_active: bool = True


@dataclass
class ProviderConfig:
    provider_name: str
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    timeout_seconds: int = 30
    max_retries: int = 3
