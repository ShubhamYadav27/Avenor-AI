import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.modules.agent_builder.api.router import router, _agents
from app.modules.agent_builder.domain.models import AgentStatus, TaskStatus, ToolCall
from app.modules.agent_builder.application.services import ToolAdapter, ExecutionEngine, AgentOrchestrator

app = FastAPI()
app.include_router(router)
client = TestClient(app)

def test_tool_adapter_success():
    agent = _agents[0] # Has 'public_api.get_company'
    tool_call = ToolCall(id="t1", tool_name="public_api.get_company", arguments={"domain": "avnor.ai"})
    result = ToolAdapter.execute_tool(agent, tool_call)
    assert "Revenue $50M" in result

def test_tool_adapter_security_sandbox():
    agent = _agents[1] # Only has 'workflow.start_approval'
    # Agent 2 maliciously attempts to use get_company
    tool_call = ToolCall(id="t2", tool_name="public_api.get_company", arguments={"domain": "avnor.ai"})
    
    with pytest.raises(PermissionError) as exc_info:
        ToolAdapter.execute_tool(agent, tool_call)
        
    assert "not authorized to use tool" in str(exc_info.value)

def test_agent_orchestrator_dispatch():
    res = client.post("/v1/agents/execute", json={"goal": "Research Google and draft a brief"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == AgentStatus.COMPLETED.value
    assert len(data["tasks"]) == 2
    
    # Task 1 (Research)
    assert data["tasks"][0]["status"] == TaskStatus.COMPLETED.value
    assert data["tasks"][0]["assigned_agent"] == "Company Intelligence Agent"
    assert "Revenue $50M" in data["tasks"][0]["result"] # Tool was successfully observed
    
    # Task 2 (Write)
    assert data["tasks"][1]["status"] == TaskStatus.COMPLETED.value
    assert data["tasks"][1]["assigned_agent"] == "Executive Briefing Agent"
    assert "not authorized" in data["tasks"][1]["result"] # Since the mock forces all tasks to use get_company, Agent 2 fails the sandbox!
