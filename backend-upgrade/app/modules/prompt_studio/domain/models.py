from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime

class PromptStatus(str, Enum):
    DRAFT = "draft"
    REVIEW = "review"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class ModelProvider(str, Enum):
    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE = "azure"

class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

@dataclass
class PromptMessage:
    role: MessageRole
    content: str # Can contain {{variables}}

@dataclass
class PromptParameters:
    temperature: float = 0.7
    max_tokens: int = 2048
    top_p: float = 1.0

@dataclass
class PromptVersion:
    """An immutable semantic version of a Prompt."""
    id: str
    template_id: str
    semantic_version: str # e.g., 'v1.0.0'
    status: PromptStatus
    messages: List[PromptMessage]
    model_provider: ModelProvider
    model_name: str # e.g., 'gemini-1.5-pro'
    parameters: PromptParameters = field(default_factory=PromptParameters)
    created_at: datetime = field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = None
    author_id: Optional[str] = None

@dataclass
class PromptTemplate:
    """The canonical identity of a prompt across versions."""
    id: str
    workspace_id: str
    name: str # e.g., 'sales.executive_brief'
    description: str
    active_version_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class RenderedPrompt:
    """The final compiled prompt sent to the LLM adapter."""
    version_id: str
    messages: List[Dict[str, str]]
    parameters: PromptParameters
    model_provider: ModelProvider
    model_name: str
