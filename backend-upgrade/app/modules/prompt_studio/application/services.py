import re
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.modules.prompt_studio.domain.models import (
    PromptTemplate, PromptVersion, PromptStatus, RenderedPrompt
)

class PromptRenderer:
    """Compiles a PromptVersion with live context variables into a RenderedPrompt."""
    
    @staticmethod
    def render(version: PromptVersion, context: Dict[str, Any]) -> RenderedPrompt:
        rendered_messages = []
        
        for msg in version.messages:
            # Simple {{var.path}} replacement engine
            def replace_match(match):
                path = match.group(1)
                parts = path.split(".")
                val = context
                for part in parts:
                    if isinstance(val, dict) and part in val:
                        val = val[part]
                    else:
                        raise ValueError(f"Missing required context variable: '{path}'")
                return str(val)
                
            content = re.sub(r"\{\{([\w\.]+)\}\}", replace_match, msg.content)
            rendered_messages.append({
                "role": msg.role.value,
                "content": content
            })
            
        return RenderedPrompt(
            version_id=version.id,
            messages=rendered_messages,
            parameters=version.parameters,
            model_provider=version.model_provider,
            model_name=version.model_name
        )

class PromptManager:
    """Governs Prompt lifecycles, versions, and active deployments."""
    
    def __init__(self):
        self._templates: Dict[str, PromptTemplate] = {}
        self._versions: Dict[str, PromptVersion] = {}
        
    def create_template(self, template: PromptTemplate) -> None:
        self._templates[template.id] = template
        
    def add_version(self, version: PromptVersion) -> None:
        self._versions[version.id] = version
        
    def publish_version(self, template_id: str, version_id: str, user_role: str) -> None:
        """Governance: Only Admins can publish prompts to production."""
        if user_role != "admin":
            raise PermissionError("Only administrators can publish prompt versions.")
            
        if template_id not in self._templates or version_id not in self._versions:
            raise ValueError("Template or Version not found.")
            
        version = self._versions[version_id]
        if version.template_id != template_id:
            raise ValueError("Version does not belong to this template.")
            
        version.status = PromptStatus.PUBLISHED
        version.published_at = datetime.utcnow()
        
        template = self._templates[template_id]
        template.active_version_id = version.id

    def get_active_rendered_prompt(self, template_id: str, context: Dict[str, Any]) -> RenderedPrompt:
        template = self._templates.get(template_id)
        if not template or not template.active_version_id:
            raise ValueError("Template has no active published version.")
            
        version = self._versions[template.active_version_id]
        return PromptRenderer.render(version, context)
