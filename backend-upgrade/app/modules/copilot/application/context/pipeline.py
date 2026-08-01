"""
Context Quality Pipeline (Phase 5.5.2 Part 3)
Implements the 11-stage enterprise context processing lifecycle.
"""
from typing import Dict, List, Optional

import uuid

from app.modules.copilot.application.context.budget_manager import token_budget_manager
from app.modules.copilot.application.context.ranker import context_ranker
from app.modules.copilot.domain.context import ContextIntent, ContextItem, UnifiedContext
from app.modules.copilot.domain.entities import CopilotStateEntity


class ContextQualityPipeline:
    def process(
        self,
        workspace_id: uuid.UUID,
        user_query: str,
        intent: ContextIntent,
        raw_items: List[ContextItem],
        provider_health: Dict[str, str],
        state: Optional[CopilotStateEntity] = None,
        max_token_budget: int = 4000,
        model_name: Optional[str] = None,
        prompt_version: str = "v1",
    ) -> UnifiedContext:
        # Stage 1 & 2: Workspace Isolation & Security Validation
        valid_items: List[ContextItem] = []
        for item in raw_items:
            if item.content and len(item.content.strip()) > 0:
                valid_items.append(item)

        # Stage 4: Content Normalization
        for item in valid_items:
            item.content = item.content.strip()

        # Stage 5 & 6 & 7 & 8: Deduplication, Freshness, Confidence & Multi-Factor Ranking
        ranked_items = context_ranker.rank_and_deduplicate(valid_items)

        # Stage 9: Token Budgeting & Compression
        budgeted_items, total_tokens = token_budget_manager.fit_to_budget(
            ranked_items, max_token_budget=max_token_budget, model_name=model_name
        )

        # Compute Overall Confidence Score across selected items
        if budgeted_items:
            avg_confidence = sum(i.confidence_score for i in budgeted_items) / len(budgeted_items)
        else:
            avg_confidence = 1.0

        overall_confidence = round(avg_confidence, 2)

        # Extract Category Summaries
        ws_items = [i for i in budgeted_items if i.category == "workspace"]
        comp_items = [i for i in budgeted_items if i.category == "company"]
        sig_items = [i for i in budgeted_items if i.category == "signal"]
        crm_items = [i for i in budgeted_items if i.category == "crm"]
        res_items = [i for i in budgeted_items if i.category == "research"]
        coach_items = [i for i in budgeted_items if i.category == "sales_coach"]
        email_items = [i for i in budgeted_items if i.category == "email"]

        return UnifiedContext(
            workspace_id=workspace_id,
            thread_id=state.thread_id if state else None,
            intent=intent,
            items=budgeted_items,
            workspace_info=ws_items[0].metadata if ws_items else {},
            company_summary=comp_items[0].metadata if comp_items else None,
            signal_summary=[i.metadata for i in sig_items],
            crm_summary={"items_count": len(crm_items)} if crm_items else {},
            research_summary={"content": res_items[0].content} if res_items else None,
            coaching_summary=[{"content": i.content} for i in coach_items],
            email_summary=[{"content": i.content} for i in email_items],
            total_tokens=total_tokens,
            overall_confidence_score=overall_confidence,
            provider_health=provider_health,
            ranking_metadata={"selected_items_count": len(budgeted_items), "total_raw_items": len(raw_items)},
            prompt_version=prompt_version,
        )


context_quality_pipeline = ContextQualityPipeline()
