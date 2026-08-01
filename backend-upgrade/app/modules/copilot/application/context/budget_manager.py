"""
Model-Aware Token Budget Engine (Phase 5.5.2 Part 3)
Enforces model-specific context window budgets, per-provider token caps, and dynamic compression.
"""
from typing import Dict, List, Optional, Tuple

from app.modules.copilot.domain.context import ContextItem

MODEL_BUDGET_PRESETS: Dict[str, int] = {
    "gemini-1.5-pro": 12000,
    "gemini-1.5-flash": 12000,
    "gpt-4o": 8000,
    "gpt-4o-mini": 8000,
    "mock-model": 4000,
}

PER_PROVIDER_TOKEN_CAP: int = 3000


class TokenBudgetManager:
    def resolve_model_budget(self, model_name: str | None = None, fallback_budget: int = 4000) -> int:
        if not model_name:
            return fallback_budget
        return MODEL_BUDGET_PRESETS.get(model_name.lower(), fallback_budget)

    def fit_to_budget(
        self,
        items: List[ContextItem],
        max_token_budget: int = 4000,
        model_name: Optional[str] = None,
    ) -> Tuple[List[ContextItem], int]:
        budget = self.resolve_model_budget(model_name, max_token_budget)
        selected: List[ContextItem] = []
        total_tokens = 0

        # Track per-provider token usage to prevent single-source starvation
        provider_usage: Dict[str, int] = {}

        for item in items:
            p_name = item.source_provider
            current_p_used = provider_usage.get(p_name, 0)
            item_tokens = item.token_count or (len(item.content) // 4 + 5)

            # Per-provider token cap check
            if current_p_used + item_tokens > PER_PROVIDER_TOKEN_CAP:
                item.exclusion_reason = f"Provider '{p_name}' exceeded per-provider token cap ({PER_PROVIDER_TOKEN_CAP})"
                continue

            if total_tokens + item_tokens <= budget:
                selected.append(item)
                total_tokens += item_tokens
                provider_usage[p_name] = current_p_used + item_tokens
            else:
                remaining = budget - total_tokens
                if remaining > 50:
                    truncated_content = (
                        item.content[: remaining * 4] + "\n...[Context compressed due to model token budget]"
                    )
                    item.content = truncated_content
                    item.token_count = remaining
                    selected.append(item)
                    total_tokens += remaining
                    provider_usage[p_name] = current_p_used + remaining
                else:
                    item.exclusion_reason = f"Exceeded overall context token budget ({budget})"
                break

        return selected, total_tokens


token_budget_manager = TokenBudgetManager()
