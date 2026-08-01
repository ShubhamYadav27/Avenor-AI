import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.modules.workflow_builder.api.router import router, _mock_workflow
from app.modules.workflow_builder.domain.models import ExecutionContext, ExecutionStatus, NodeType
from app.modules.workflow_builder.application.services import ExpressionEngine, WorkflowEngine

app = FastAPI()
app.include_router(router)
client = TestClient(app)

def test_workflow_list_endpoint():
    res = client.get("/v1/workflows/?workspace_id=ws_001")
    assert res.status_code == 200
    assert res.json()[0]["id"] == "wf_001"

def test_expression_engine_string_render():
    ctx = ExecutionContext(execution_id="1", workflow_id="1", variables={"user": {"name": "Alice"}})
    result = ExpressionEngine.render_string("Hello {{user.name}}", ctx)
    assert result == "Hello Alice"

def test_expression_engine_condition_eval():
    ctx = ExecutionContext(execution_id="1", workflow_id="1", variables={"trigger": {"payload": {"score": 90}}})
    is_true = ExpressionEngine.evaluate_condition("{{trigger.payload.score}} > 80", ctx)
    assert is_true is True
    
    is_false = ExpressionEngine.evaluate_condition("{{trigger.payload.score}} < 80", ctx)
    assert is_false is False

from unittest.mock import patch

def test_workflow_engine_traversal_true_branch():
    engine = WorkflowEngine()
    
    with patch("app.modules.workflow_builder.application.services.NodeExecutor.execute", return_value={"result": "true"}) as mock_execute:
        # We must simulate the return values correctly because the branches depend on the output.
        # But wait, mocking the entire executor means the condition won't evaluate correctly unless we mock smartly.
        # Instead of mocking execute, let's just spy on it using patch.object.
        pass

from unittest.mock import MagicMock
def test_workflow_engine_traversal_true_branch_patch():
    engine = WorkflowEngine()
    original_execute = engine.__class__.__module__ + ".NodeExecutor.execute"
    
    with patch(original_execute, side_effect=lambda n, c: {"result": True, "executed": True} if n.type == NodeType.CONDITION else {"executed": True}) as spy:
        payload = {"score": 90}
        log = engine.trigger_workflow(_mock_workflow, payload)
        
        assert log.error_message is None
        assert log.status == ExecutionStatus.COMPLETED
        assert spy.call_count == 3
        executed_node_ids = [call.args[0].id for call in spy.call_args_list]
        assert "n1" in executed_node_ids
        assert "n2" in executed_node_ids
        assert "n3" in executed_node_ids
        assert "n4" not in executed_node_ids # skipped

def test_workflow_engine_traversal_false_branch_patch():
    engine = WorkflowEngine()
    original_execute = engine.__class__.__module__ + ".NodeExecutor.execute"
    
    with patch(original_execute, side_effect=lambda n, c: {"result": False, "executed": True} if n.type == NodeType.CONDITION else {"executed": True}) as spy:
        payload = {"score": 50}
        log = engine.trigger_workflow(_mock_workflow, payload)
        
        assert log.error_message is None
        assert log.status == ExecutionStatus.COMPLETED
        assert spy.call_count == 3
        executed_node_ids = [call.args[0].id for call in spy.call_args_list]
        assert "n3" not in executed_node_ids # skipped
        assert "n4" in executed_node_ids
