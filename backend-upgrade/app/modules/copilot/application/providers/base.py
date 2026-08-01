"""
Base Context Provider
Abstract implementation of IContextProvider with built-in safety and logging.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
import uuid

from app.modules.copilot.domain.context import ContextIntent, ContextItem
from app.modules.copilot.domain.entities import CopilotStateEntity
from app.modules.copilot.domain.interfaces import IContextProvider


class BaseContextProvider(IContextProvider, ABC):
    def supports_intent(self, intent: ContextIntent) -> bool:
        # Default: supports all intents unless overridden
        return True

    @abstractmethod
    async def fetch_context(
        self, workspace_id: uuid.UUID, query: str, state: Optional[CopilotStateEntity] = None
    ) -> List[ContextItem]:
        pass
