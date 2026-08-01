"""
Pydantic schemas for Message operations.
"""
from typing import Optional
from pydantic import BaseModel, Field


class SendMessageRequest(BaseModel):
    content: str = Field(..., min_length=1)
    preferred_provider: Optional[str] = Field(default=None, description="gemini | openai | mock")
    preferred_model: Optional[str] = Field(default=None)
