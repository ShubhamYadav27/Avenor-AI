from fastapi import APIRouter, HTTPException, Header
from typing import List, Dict, Any, Optional

from app.modules.prompt_studio.domain.models import (
    PromptTemplate, PromptVersion, PromptStatus, ModelProvider, MessageRole, PromptMessage
)
from app.modules.prompt_studio.application.services import PromptManager

router = APIRouter(prefix="/v1/prompts", tags=["Enterprise Prompt Studio"])

_manager = PromptManager()

# Pre-seed for demonstration
_template = PromptTemplate(id="pt_1", workspace_id="ws_001", name="sales.executive_brief", description="Generates a prep brief for sales calls.")
_version = PromptVersion(
    id="pv_1", template_id="pt_1", semantic_version="v1.0.0", status=PromptStatus.DRAFT,
    model_provider=ModelProvider.GEMINI, model_name="gemini-1.5-pro",
    messages=[
        PromptMessage(role=MessageRole.SYSTEM, content="You are a senior sales strategist at AVENOR."),
        PromptMessage(role=MessageRole.USER, content="Generate a brief for {{company.name}}.")
    ]
)
_manager.create_template(_template)
_manager.add_version(_version)
_manager.publish_version("pt_1", "pv_1", user_role="admin")

@router.get("/")
async def list_templates(workspace_id: str) -> List[dict]:
    """List all prompt templates."""
    return [{"id": t.id, "name": t.name, "active_version_id": t.active_version_id} 
            for t in _manager._templates.values() if t.workspace_id == workspace_id]

@router.post("/{template_id}/render")
async def render_prompt(template_id: str, payload: Dict[str, Any]) -> dict:
    """Renders the active published version of a prompt with the provided context variables."""
    try:
        rendered = _manager.get_active_rendered_prompt(template_id, payload.get("context", {}))
        return {
            "model": f"{rendered.model_provider.value}/{rendered.model_name}",
            "messages": rendered.messages,
            "parameters": {
                "temperature": rendered.parameters.temperature,
                "max_tokens": rendered.parameters.max_tokens
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
