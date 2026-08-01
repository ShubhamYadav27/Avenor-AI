"""
Memory Retrieval Planner (Phase 5.5.4)
Intent-driven planning of target memory categories, token budgets, and retrieval strategies.
"""
import uuid
from typing import List

from app.modules.copilot.domain.context import ContextIntent
from app.modules.copilot.domain.interfaces import IMemoryPlanner
from app.modules.copilot.domain.memory_entities import MemoryRetrievalPlan
from app.modules.copilot.domain.memory_value_objects import MemoryCategory, RetrievalStrategy


class MemoryRetrievalPlanner(IMemoryPlanner):
    def create_retrieval_plan(
        self,
        workspace_id: uuid.UUID,
        query: str,
        intent: ContextIntent,
    ) -> MemoryRetrievalPlan:
        categories: List[MemoryCategory] = []

        if intent == ContextIntent.COMPANY_DEEP_DIVE:
            categories = [MemoryCategory.COMPANY, MemoryCategory.WORKSPACE, MemoryCategory.KNOWLEDGE]
        elif intent == ContextIntent.OUTREACH_STRATEGY:
            categories = [MemoryCategory.CONTACT, MemoryCategory.COMPANY, MemoryCategory.USER]
        elif intent == ContextIntent.OBJECTION_HANDLING:
            categories = [MemoryCategory.KNOWLEDGE, MemoryCategory.USER, MemoryCategory.OPPORTUNITY]
        elif intent == ContextIntent.CRM_PIPELINE:
            categories = [MemoryCategory.OPPORTUNITY, MemoryCategory.COMPANY, MemoryCategory.CONTACT]
        else:
            categories = [MemoryCategory.WORKSPACE, MemoryCategory.CONVERSATION, MemoryCategory.COMPANY]

        return MemoryRetrievalPlan(
            workspace_id=workspace_id,
            intent=intent,
            target_categories=categories,
            strategy=RetrievalStrategy.HYBRID,
            max_items=8,
            min_confidence=0.50,
            token_budget=2000,
        )


memory_planner = MemoryRetrievalPlanner()
