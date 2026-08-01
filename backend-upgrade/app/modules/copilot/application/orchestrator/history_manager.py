"""
History Manager
Manages message history trimming, token budgeting, and sliding windows.
"""
from typing import List
from app.modules.copilot.domain.entities import CopilotMessageEntity


class HistoryManager:
    def __init__(self, max_token_budget: int = 8000, max_messages: int = 20):
        self.max_token_budget = max_token_budget
        self.max_messages = max_messages

    def prepare_messages(
        self, messages: List[CopilotMessageEntity], token_budget: int | None = None
    ) -> List[CopilotMessageEntity]:
        budget = token_budget or self.max_token_budget
        
        # Take at most max_messages
        trimmed = messages[-self.max_messages :] if len(messages) > self.max_messages else messages

        # Simple token estimation (~4 chars per token)
        total_tokens = 0
        result = []
        for msg in reversed(trimmed):
            estimated_tokens = len(msg.content) // 4 + 10
            if total_tokens + estimated_tokens > budget and result:
                break
            total_tokens += estimated_tokens
            result.insert(0, msg)

        return result


history_manager = HistoryManager()
