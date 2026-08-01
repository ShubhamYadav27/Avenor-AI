"""
Tool Router & DAG Execution Optimizer (Phase 5.5.3)
Constructs Directed Acyclic Graph (DAG) execution stages, validates no cycle loops,
and schedules parallel batching vs sequential dependency chains.
"""
from typing import Dict, List, Set

from app.modules.copilot.domain.interfaces import ITool, IToolRegistry, IToolRouter
from app.modules.copilot.domain.tools import ExecutionNode, ToolExecutionPlan


class ToolRouter(IToolRouter):
    def build_execution_stages(
        self,
        plan: ToolExecutionPlan,
        registry: IToolRegistry,
    ) -> List[List[ExecutionNode]]:
        tools_dict: Dict[str, ITool] = {
            t.spec.name: t for t in registry.list_all_tools() if t.spec.name in plan.selected_tools
        }

        # Step 1: Validate No Circular Dependencies
        self._validate_no_cycles(tools_dict)

        # Step 2: Separate into Stage 1 (Independent / Parallel) and Stage 2 (Dependent / Sequential)
        stage_1_nodes: List[ExecutionNode] = []
        stage_2_nodes: List[ExecutionNode] = []

        for name, tool in tools_dict.items():
            deps = [d for d in tool.spec.dependencies if d in tools_dict]
            node = ExecutionNode(
                tool_name=name,
                spec=tool.spec,
                dependencies=deps,
            )
            if not deps:
                node.stage = 1
                stage_1_nodes.append(node)
            else:
                node.stage = 2
                stage_2_nodes.append(node)

        stages: List[List[ExecutionNode]] = []
        if stage_1_nodes:
            stages.append(stage_1_nodes)
        if stage_2_nodes:
            stages.append(stage_2_nodes)

        plan.execution_stages = stages
        return stages

    def _validate_no_cycles(self, tools: Dict[str, ITool]) -> None:
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def dfs(node: str):
            visited.add(node)
            rec_stack.add(node)

            tool = tools.get(node)
            if tool:
                for dep in tool.spec.dependencies:
                    if dep in tools:
                        if dep not in visited:
                            dfs(dep)
                        elif dep in rec_stack:
                            raise ValueError(f"Circular dependency detected in execution graph involving '{node}' and '{dep}'")

            rec_stack.remove(node)

        for name in tools:
            if name not in visited:
                dfs(name)


tool_router = ToolRouter()
