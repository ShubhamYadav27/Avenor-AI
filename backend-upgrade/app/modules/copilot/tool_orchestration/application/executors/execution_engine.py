"""
Tool Execution Engine (Phase 5.5.3)
Coordinates concurrent execution of platform business tools, stage-by-stage scheduling,
circuit breaker enforcement, fault isolation, and result aggregation into UnifiedIntelligencePackage.
"""
import asyncio
import time
from typing import Any, List, Optional

from app.modules.copilot.domain.interfaces import IToolExecutionEngine
from app.modules.copilot.domain.tool_value_objects import ExecutionStatus, FailureReason
from app.modules.copilot.domain.tools import (
    ExecutionMetrics,
    ToolExecutionPlan,
    ToolExecutionRequest,
    ToolExecutionResult,
    UnifiedIntelligencePackage,
)
from app.modules.copilot.tool_orchestration.application.aggregators.result_aggregator import result_aggregator
from app.modules.copilot.tool_orchestration.application.planners.planner import tool_planner
from app.modules.copilot.tool_orchestration.application.recovery.circuit_breaker import circuit_breaker
from app.modules.copilot.tool_orchestration.application.routers.router import tool_router
from app.modules.copilot.tool_orchestration.infrastructure.registry.registry import tool_registry


class ToolExecutionEngine(IToolExecutionEngine):
    async def execute_plan(
        self,
        plan: ToolExecutionPlan,
        request: ToolExecutionRequest,
        db: Optional[Any] = None,
    ) -> UnifiedIntelligencePackage:
        start_time = time.perf_counter()
        
        # 1. Build DAG execution stages
        stages = tool_router.build_execution_stages(plan, tool_registry)
        
        all_results: List[ToolExecutionResult] = []
        metrics = ExecutionMetrics(parallel_batches_count=len(stages))

        # 2. Execute Stage by Stage
        for stage_index, stage_nodes in enumerate(stages, start=1):
            tasks = []
            for node in stage_nodes:
                tool = tool_registry.get_tool(node.tool_name)
                if not tool:
                    all_results.append(
                        ToolExecutionResult(
                            tool_name=node.tool_name,
                            status=ExecutionStatus.FAILED,
                            failure_reason=FailureReason.SERVICE_UNAVAILABLE,
                            error_message=f"Tool '{node.tool_name}' not registered",
                        )
                    )
                    metrics.tools_failed_count += 1
                    continue

                # Circuit breaker check
                if not circuit_breaker.allow_execution(node.tool_name):
                    all_results.append(
                        ToolExecutionResult(
                            tool_name=node.tool_name,
                            status=ExecutionStatus.SKIPPED,
                            failure_reason=FailureReason.CIRCUIT_OPEN,
                            error_message=f"Circuit breaker is open for tool '{node.tool_name}'",
                        )
                    )
                    continue

                node.status = ExecutionStatus.RUNNING
                sub_request = ToolExecutionRequest(
                    tool_name=node.tool_name,
                    workspace_id=request.workspace_id,
                    thread_id=request.thread_id,
                    user_id=request.user_id,
                    user_query=request.user_query,
                    intent=request.intent,
                    context=request.context,
                    parameters=request.parameters,
                    correlation_id=request.correlation_id,
                )
                tasks.append((node, tool, sub_request))

            # Run parallel execution batch
            if tasks:
                batch_futures = [t[1].execute(t[2], db=db) for t in tasks]
                results = await asyncio.gather(*batch_futures, return_exceptions=True)

                for (node, tool, sub_req), res in zip(tasks, results):
                    if isinstance(res, ToolExecutionResult):
                        if res.status == ExecutionStatus.COMPLETED:
                            circuit_breaker.record_success(node.tool_name)
                            node.status = ExecutionStatus.COMPLETED
                        else:
                            circuit_breaker.record_failure(node.tool_name)
                            node.status = res.status
                            metrics.tools_failed_count += 1
                        all_results.append(res)
                        metrics.tools_executed_count += 1
                    else:
                        circuit_breaker.record_failure(node.tool_name)
                        node.status = ExecutionStatus.FAILED
                        metrics.tools_failed_count += 1
                        all_results.append(
                            ToolExecutionResult(
                                tool_name=node.tool_name,
                                status=ExecutionStatus.FAILED,
                                failure_reason=FailureReason.INTERNAL_ERROR,
                                error_message=f"Unhandled tool exception: {str(res)}",
                            )
                        )

        total_ms = (time.perf_counter() - start_time) * 1000.0
        metrics.total_execution_ms = round(total_ms, 2)

        # 3. Aggregate results into UnifiedIntelligencePackage
        return result_aggregator.aggregate(
            workspace_id=request.workspace_id,
            user_query=request.user_query,
            intent=request.intent,
            results=all_results,
            unified_context=request.context,
            metrics=metrics,
            thread_id=request.thread_id,
        )

    async def execute_intent(
        self,
        workspace_id: Any,
        user_query: str,
        intent: Any,
        context: Any,
        thread_id: Optional[Any] = None,
        db: Optional[Any] = None,
    ) -> UnifiedIntelligencePackage:
        available_tools = tool_registry.get_tools_for_intent(intent)
        plan = tool_planner.create_plan(intent, context, available_tools)
        request = ToolExecutionRequest(
            tool_name="orchestrator",
            workspace_id=workspace_id,
            thread_id=thread_id,
            user_query=user_query,
            intent=intent,
            context=context,
        )
        return await self.execute_plan(plan, request, db=db)


tool_execution_engine = ToolExecutionEngine()
