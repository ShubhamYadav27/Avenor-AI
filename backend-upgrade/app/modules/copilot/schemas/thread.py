"""
Pydantic schemas for Thread management.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field


class CreateThreadRequest(BaseModel):
    title: Optional[str] = Field(default="New Strategic Session", max_length=255)


class UpdateThreadRequest(BaseModel):
    title: Optional[str] = Field(default=None, max_length=255)
    status: Optional[str] = Field(default=None, description="active | archived")


class StateResponse(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    thread_id: uuid.UUID
    current_company_id: Optional[uuid.UUID] = None
    current_deal_id: Optional[str] = None
    current_contact_id: Optional[uuid.UUID] = None
    active_workspace_context: Dict[str, Any] = Field(default_factory=dict)
    active_recommendation: Dict[str, Any] = Field(default_factory=dict)
    token_budget: int = 8000
    last_tool_used: Optional[str] = None
    updated_at: datetime


class MessageResponse(BaseModel):
    id: uuid.UUID
    thread_id: uuid.UUID
    role: str
    content: str
    model_provider: Optional[str] = None
    model_name: Optional[str] = None
    token_count: int = 0
    extra_metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class ThreadResponse(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    user_id: uuid.UUID
    title: str
    status: str
    extra_metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = Field(default_factory=list)
    state: Optional[StateResponse] = None
