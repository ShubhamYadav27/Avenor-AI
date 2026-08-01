"""
Base Tool Implementation (Phase 5.5.3)
Provides standardized execution template, permission checks, timing, and error isolation.
"""
import asyncio
import time
from typing import Any, Optional

from app.modules.copilot.domain.interfaces import ITool
from app.modules.copilot.domain.tool_value_objects import ExecutionStatus, FailureReason
from app.modules.copilot.domain.tools import ToolExecutionRequest, ToolExecutionResult, ToolSpecification


class BaseTool(ITool):
    @property
    def spec(self) -> ToolSpecification:
        raise NotImplementedError("Subclasses must define spec")

    async def can_execute(self, request: ToolExecutionRequest) -> bool:
        # Check basic workspace presence
        if not request.workspace_id:
            return False
        return True

    async def execute(self, request: ToolExecutionRequest, db: Optional[Any] = None) -> ToolExecutionResult:
        start_time = time.perf_counter()
        
        # Check permissions / execution eligibility
        if not await self.can_execute(request):
            return ToolExecutionResult(
                tool_name=self.spec.name,
                status=ExecutionStatus.FAILED,
                failure_reason=FailureReason.PERMISSION_DENIED,
                error_message=f"Execution check failed for tool '{self.spec.name}'",
                confidence=0.0,
            )

        try:
            # Enforce timeout policy
            result = await asyncio.wait_for(
                self._run_tool_logic(request, db),
                timeout=self.spec.timeout_seconds,
            )
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            result.execution_time_ms = round(elapsed_ms, 2)
            return result
            
        except asyncio.TimeoutError:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return ToolExecutionResult(
                tool_name=self.spec.name,
                status=ExecutionStatus.TIMED_OUT,
                failure_reason=FailureReason.TIMEOUT,
                error_message=f"Tool '{self.spec.name}' exceeded timeout of {self.spec.timeout_seconds}s",
                execution_time_ms=round(elapsed_ms, 2),
                confidence=0.0,
            )
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return ToolExecutionResult(
                tool_name=self.spec.name,
                status=ExecutionStatus.FAILED,
                failure_reason=FailureReason.INTERNAL_ERROR,
                error_message=f"Error executing tool '{self.spec.name}': {str(e)}",
                execution_time_ms=round(elapsed_ms, 2),
                confidence=0.0,
            )

    async def _run_tool_logic(self, request: ToolExecutionRequest, db: Optional[Any] = None) -> ToolExecutionResult:
        raise NotImplementedError("Subclasses must implement _run_tool_logic")
