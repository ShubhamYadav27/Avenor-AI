import uuid
import re
from typing import List, Dict, Any, Tuple
from datetime import datetime

from app.modules.workflow_builder.domain.models import (
    Workflow, Node, Edge, NodeType, ExecutionContext, ExecutionLog, ExecutionStatus
)

class ExpressionEngine:
    """Evaluates templated strings like '{{trigger.payload.amount}} > 5000'."""
    @staticmethod
    def render_string(template: str, context: ExecutionContext) -> str:
        # Extremely simplified variable replacement for {{var.path}}
        def replace_match(match):
            path = match.group(1)
            val = context.get_variable(path)
            return str(val) if val is not None else ""
            
        return re.sub(r"\{\{([\w\.]+)\}\}", replace_match, template)
        
    @staticmethod
    def evaluate_condition(condition: str, context: ExecutionContext) -> bool:
        # Simplified condition engine supporting "value operator value"
        rendered = ExpressionEngine.render_string(condition, context)
        parts = rendered.split(" ")
        if len(parts) == 3:
            left, op, right = parts
            if op == "==": return left == right
            if op == "!=": return left != right
            if op == ">": return float(left) > float(right)
            if op == "<": return float(left) < float(right)
        return False

class NodeExecutor:
    """Handles business logic execution for specific node operations."""
    @staticmethod
    def execute(node: Node, context: ExecutionContext) -> Dict[str, Any]:
        rendered_config = {
            k: ExpressionEngine.render_string(str(v), context) if isinstance(v, str) else v 
            for k, v in node.config.items()
        }
        
        if node.type == NodeType.ACTION:
            if node.operation == "http_request":
                # Simulated HTTP request
                return {"status": 200, "response": "Success"}
            if node.operation == "create_task":
                return {"task_id": "tsk_999", "status": "created"}
                
        if node.type == NodeType.CONDITION:
            # Evaluate condition and return the boolean branch to take
            is_true = ExpressionEngine.evaluate_condition(rendered_config.get("expression", ""), context)
            return {"result": is_true}
            
        # Default empty output
        return {"executed": True}

class WorkflowEngine:
    """Orchestrates the DAG traversal and manages execution state."""
    
    def trigger_workflow(self, workflow: Workflow, trigger_payload: Dict[str, Any]) -> ExecutionLog:
        exec_id = f"exec_{uuid.uuid4().hex[:8]}"
        log = ExecutionLog(id=exec_id, workflow_id=workflow.id, status=ExecutionStatus.RUNNING)
        
        context = ExecutionContext(
            execution_id=exec_id,
            workflow_id=workflow.id,
            variables={"trigger": {"payload": trigger_payload}}
        )
        
        # Find trigger node (assume 1 for simplicity)
        triggers = workflow.get_trigger_nodes()
        if not triggers:
            log.status = ExecutionStatus.FAILED
            log.error_message = "No trigger node found"
            return log
            
        current_nodes = [triggers[0]]
        
        try:
            # Breadth-first traversal
            while current_nodes:
                next_nodes = []
                for node in current_nodes:
                    # Execute Node
                    output = NodeExecutor.execute(node, context)
                    
                    # Store output in context (namespaced by node.id)
                    context.variables[node.id] = {"output": output}
                    
                    # Determine next edges
                    edges = workflow.get_outgoing_edges(node.id)
                    for edge in edges:
                        # Conditional Branching
                        if node.type == NodeType.CONDITION:
                            branch_condition = str(output.get("result")).lower()
                            if edge.condition_label and edge.condition_label.lower() != branch_condition:
                                continue # Skip this branch
                        
                        target = workflow.get_node(edge.target_node_id)
                        if target:
                            next_nodes.append(target)
                            
                current_nodes = next_nodes
                
            log.status = ExecutionStatus.COMPLETED
            log.completed_at = datetime.utcnow()
            
        except Exception as e:
            log.status = ExecutionStatus.FAILED
            log.error_message = str(e)
            
        return log
