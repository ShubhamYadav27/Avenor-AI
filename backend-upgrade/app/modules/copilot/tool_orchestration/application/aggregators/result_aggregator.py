"""
Result Aggregator (Phase 5.5.3)
Merges ToolExecutionResult items into UnifiedIntelligencePackage with confidence calculation,
provenance tracking, and citation registry mapping.
"""
from typing import List, Optional
import uuid

from app.modules.copilot.domain.context import ContextIntent, UnifiedContext
from app.modules.copilot.domain.tool_value_objects import ExecutionStatus
from app.modules.copilot.domain.tools import ExecutionMetrics, ToolExecutionResult, UnifiedIntelligencePackage


class ResultAggregator:
    def aggregate(
        self,
        workspace_id: uuid.UUID,
        user_query: str,
        intent: ContextIntent,
        results: List[ToolExecutionResult],
        unified_context: Optional[UnifiedContext] = None,
        metrics: Optional[ExecutionMetrics] = None,
        thread_id: Optional[uuid.UUID] = None,
    ) -> UnifiedIntelligencePackage:
        successful_results = [r for r in results if r.status in (ExecutionStatus.COMPLETED, ExecutionStatus.PARTIAL_SUCCESS)]
        
        # Calculate overall confidence
        if successful_results:
            overall_confidence = sum(r.confidence for r in successful_results) / len(successful_results)
        else:
            overall_confidence = 0.85

        # Format Aggregated Text
        formatted_sections: List[str] = []
        provenance_chain: List[str] = []
        citation_registry: dict = {}

        for r in successful_results:
            if r.formatted_text:
                formatted_sections.append(f"--- [{r.tool_name.upper()} | Citation: {r.citation_id}] ---\n{r.formatted_text}")
            provenance_chain.append(r.provenance_id)
            citation_registry[r.citation_id] = f"Tool: {r.tool_name}"

        aggregated_text = "\n\n".join(formatted_sections)

        return UnifiedIntelligencePackage(
            workspace_id=workspace_id,
            thread_id=thread_id,
            intent=intent,
            unified_context=unified_context,
            tool_results=results,
            aggregated_text=aggregated_text,
            overall_confidence_score=round(overall_confidence, 2),
            provenance_chain=provenance_chain,
            citation_registry=citation_registry,
            metrics=metrics or ExecutionMetrics(tools_executed_count=len(results)),
        )


result_aggregator = ResultAggregator()
