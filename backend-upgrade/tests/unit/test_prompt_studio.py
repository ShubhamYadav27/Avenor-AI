import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.modules.prompt_studio.api.router import router, _manager
from app.modules.prompt_studio.domain.models import PromptTemplate, PromptVersion, PromptStatus, ModelProvider, MessageRole, PromptMessage
from app.modules.prompt_studio.application.services import PromptManager, PromptRenderer

app = FastAPI()
app.include_router(router)
client = TestClient(app)

def test_prompt_rendering_success():
    res = client.post("/v1/prompts/pt_1/render", json={
        "context": {"company": {"name": "Acme Corp"}}
    })
    assert res.status_code == 200
    data = res.json()
    assert data["model"] == "gemini/gemini-1.5-pro"
    assert len(data["messages"]) == 2
    assert data["messages"][1]["content"] == "Generate a brief for Acme Corp."

def test_prompt_rendering_missing_variable():
    res = client.post("/v1/prompts/pt_1/render", json={
        "context": {"user": "Alice"} # Missing company.name
    })
    assert res.status_code == 400
    assert "Missing required context variable" in res.json()["detail"]

def test_governance_publish_denied_for_non_admins():
    manager = PromptManager()
    pt = PromptTemplate(id="t1", workspace_id="ws1", name="test", description="t")
    pv = PromptVersion(id="v1", template_id="t1", semantic_version="v1", status=PromptStatus.DRAFT, messages=[], model_provider=ModelProvider.OPENAI, model_name="gpt-4o")
    
    manager.create_template(pt)
    manager.add_version(pv)
    
    with pytest.raises(PermissionError):
        manager.publish_version("t1", "v1", user_role="developer")
        
    assert pt.active_version_id is None
    assert pv.status == PromptStatus.DRAFT

def test_governance_publish_success_for_admins():
    manager = PromptManager()
    pt = PromptTemplate(id="t1", workspace_id="ws1", name="test", description="t")
    pv = PromptVersion(id="v1", template_id="t1", semantic_version="v1", status=PromptStatus.DRAFT, messages=[], model_provider=ModelProvider.OPENAI, model_name="gpt-4o")
    
    manager.create_template(pt)
    manager.add_version(pv)
    
    manager.publish_version("t1", "v1", user_role="admin")
        
    assert pt.active_version_id == "v1"
    assert pv.status == PromptStatus.PUBLISHED
