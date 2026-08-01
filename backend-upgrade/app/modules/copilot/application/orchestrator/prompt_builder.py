"""
Prompt Builder (Phase 5.5.5 Architecture)
Consumes UnifiedContext, UnifiedIntelligencePackage, MemoryPackage, AND CitationPackage.
Zero DB or ORM coupling.
"""
from typing import Any, Dict, Optional, Union
from app.modules.copilot.domain.citation_entities import CitationPackage
from app.modules.copilot.domain.context import UnifiedContext
from app.modules.copilot.domain.memory_entities import MemoryPackage
from app.modules.copilot.domain.tools import UnifiedIntelligencePackage

DEFAULT_STRATEGIST_SYSTEM_PROMPT_V1 = """You are the Avenor AI Revenue Copilot, an elite executive revenue strategist for B2B sales teams.

CORE PHILOSOPHY:
- Always base your recommendations on the structured business context, tool intelligence, long-term memory, and verified citation package provided below.
- Prefer utilizing existing Avenor platform intelligence over generic AI generation.
- Be evidence-based, context-aware, business-focused, actionable, transparent, and professional.
- Avoid conversational fluff. Provide direct, high-impact revenue intelligence.
- Speak with the authority and precision of a Vice President of Revenue Operations.
- If information is unavailable, clearly state it rather than hallucinating details.
"""

DEFAULT_STRATEGIST_SYSTEM_PROMPT_V2 = """You are the Avenor AI Revenue Intelligence Orchestrator (Version 2.0).

STRICT GROUNDED REASONING RULES:
1. Every recommendation must cite evidence using bracketed citation markers (e.g., [cit-crm-123], [cit-sig-456]) from the structured citation package provided below.
2. Ground your output strictly in verified buying signals, CRM deal stages, sales coaching angles, and historical memory items.
3. Include clear, transparent rationale and actionable next steps for sales execution.
4. If business intelligence for an area is missing or degraded, state the uncertainty explicitly.
"""


class PromptBuilder:
    def __init__(self):
        self.default_prompt_v1 = DEFAULT_STRATEGIST_SYSTEM_PROMPT_V1
        self.default_prompt_v2 = DEFAULT_STRATEGIST_SYSTEM_PROMPT_V2

    def build_system_prompt(
        self,
        unified_context: Optional[Union[UnifiedIntelligencePackage, UnifiedContext, Dict[str, Any]]] = None,
        memory_package: Optional[MemoryPackage] = None,
        citation_package: Optional[CitationPackage] = None,
        workspace_context: Optional[Dict[str, Any]] = None,
        custom_instructions: Optional[str] = None,
        prompt_version: str = "v1",
    ) -> str:
        ctx = unified_context or workspace_context

        base_prompt = self.default_prompt_v2 if prompt_version == "v2" else self.default_prompt_v1
        prompt_parts = [base_prompt]

        # 1. Attach Citation Package & Grounding Footnotes if present
        if isinstance(citation_package, CitationPackage) and citation_package.evidence_items:
            prompt_parts.append("\nVERIFIED EVIDENCE & CITATION REGISTRY:")
            prompt_parts.append(f"Grounding Status: {citation_package.grounding_status.value.upper()}")
            prompt_parts.append(f"Overall Grounding Confidence: {citation_package.overall_confidence_score * 100:.0f}%")
            if citation_package.formatted_footnotes:
                prompt_parts.append(citation_package.formatted_footnotes)

        # 2. Attach Memory Package if present
        if isinstance(memory_package, MemoryPackage) and memory_package.memories:
            prompt_parts.append("\nHISTORICAL ENTERPRISE MEMORY PACKAGE:")
            prompt_parts.append(f"Memory Confidence Score: {memory_package.overall_confidence_score * 100:.0f}%")
            if memory_package.summary_text:
                prompt_parts.append(memory_package.summary_text)

        # 3. Attach UnifiedIntelligencePackage or UnifiedContext
        if isinstance(ctx, UnifiedIntelligencePackage):
            prompt_parts.append(f"\nQUERY INTENT: {ctx.intent.value.upper()}")
            prompt_parts.append(f"OVERALL INTELLIGENCE CONFIDENCE SCORE: {ctx.overall_confidence_score * 100:.0f}%")
            prompt_parts.append("\nSTRUCTURED TOOL INTELLIGENCE PACKAGE:")
            
            if ctx.aggregated_text:
                prompt_parts.append(ctx.aggregated_text)

            if ctx.unified_context and ctx.unified_context.items:
                prompt_parts.append("\nBASELINE PLATFORM CONTEXT ITEMS:")
                for item in ctx.unified_context.items:
                    prompt_parts.append(
                        f"\n--- [{item.category.value.upper()} | Citation: {item.citation_id}] ---\n{item.content}"
                    )

        elif isinstance(ctx, UnifiedContext):
            prompt_parts.append(f"\nQUERY INTENT: {ctx.intent.value.upper()}")
            prompt_parts.append(f"OVERALL CONTEXT CONFIDENCE SCORE: {ctx.overall_confidence_score * 100:.0f}%")
            prompt_parts.append("\nSTRUCTURED BUSINESS INTELLIGENCE PACKAGE:")
            
            for item in ctx.items:
                prompt_parts.append(
                    f"\n--- [{item.category.value.upper()} CONTEXT | Citation ID: {item.citation_id} | Score: {item.final_score:.2f}] ---"
                )
                prompt_parts.append(f"Inclusion Reason: {item.inclusion_reason}")
                prompt_parts.append(item.content)

        elif isinstance(ctx, dict):
            workspace_name = ctx.get("name", "Active Workspace")
            tier = ctx.get("tier", "Enterprise")
            crm = ctx.get("crm_provider", "None connected")
            prompt_parts.append(
                f"\nWORKSPACE CONTEXT:\n- Workspace: {workspace_name}\n- Tier: {tier}\n- CRM Provider: {crm}"
            )

        if custom_instructions:
            prompt_parts.append(f"\nADDITIONAL INSTRUCTIONS:\n{custom_instructions}")

        return "\n".join(prompt_parts)


prompt_builder = PromptBuilder()
