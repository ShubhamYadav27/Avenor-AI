"""
Memory Package Builder (Phase 5.5.4)
Assembles MemoryPackage with structured text, provenance chain, and citation registry mappings.
"""
from typing import List, Optional
import uuid

from app.modules.copilot.domain.context import ContextIntent
from app.modules.copilot.domain.memory_entities import MemoryItem, MemoryMetrics, MemoryPackage


class MemoryPackageBuilder:
    def build_package(
        self,
        workspace_id: uuid.UUID,
        intent: ContextIntent,
        memories: List[MemoryItem],
        metrics: Optional[MemoryMetrics] = None,
        thread_id: Optional[uuid.UUID] = None,
    ) -> MemoryPackage:
        provenance_chain: List[str] = []
        citation_registry: dict = {}
        formatted_sections: List[str] = []

        for item in memories:
            provenance_chain.append(item.provenance_id)
            citation_registry[item.citation_id] = f"Memory: {item.category.value.upper()}"
            formatted_sections.append(
                f"- [{item.category.value.upper()} MEMORY | Citation: {item.citation_id} | Confidence: {item.confidence_score*100:.0f}%]\n  {item.content}"
            )

        if memories:
            avg_confidence = sum(m.confidence_score for m in memories) / len(memories)
        else:
            avg_confidence = 0.95

        summary_text = "\n".join(formatted_sections)

        return MemoryPackage(
            workspace_id=workspace_id,
            thread_id=thread_id,
            intent=intent,
            memories=memories,
            summary_text=summary_text,
            overall_confidence_score=round(avg_confidence, 2),
            provenance_chain=provenance_chain,
            citation_registry=citation_registry,
            metrics=metrics or MemoryMetrics(memories_retrieved_count=len(memories)),
        )


memory_package_builder = MemoryPackageBuilder()
