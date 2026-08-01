"""
Message Service
Handles message persistence, history retrieval, and message operations.
"""
from typing import List, Optional
import uuid

from app.modules.copilot.domain.entities import CopilotMessageEntity, CopilotRole
from app.modules.copilot.domain.interfaces import IMessageRepository, IThreadRepository
from app.modules.copilot.domain.exceptions import ThreadNotFoundError


class MessageService:
    def __init__(self, message_repo: IMessageRepository, thread_repo: IThreadRepository):
        self.message_repo = message_repo
        self.thread_repo = thread_repo

    async def add_user_message(
        self, thread_id: uuid.UUID, workspace_id: uuid.UUID, content: str
    ) -> CopilotMessageEntity:
        thread = await self.thread_repo.get_by_id(thread_id, workspace_id)
        if not thread:
            raise ThreadNotFoundError(str(thread_id))

        message = CopilotMessageEntity(
            id=uuid.uuid4(),
            thread_id=thread_id,
            role=CopilotRole.USER,
            content=content,
        )
        return await self.message_repo.add_message(message)

    async def add_assistant_message(
        self,
        thread_id: uuid.UUID,
        workspace_id: uuid.UUID,
        content: str,
        provider_name: Optional[str] = None,
        model_name: Optional[str] = None,
        token_count: int = 0,
    ) -> CopilotMessageEntity:
        thread = await self.thread_repo.get_by_id(thread_id, workspace_id)
        if not thread:
            raise ThreadNotFoundError(str(thread_id))

        message = CopilotMessageEntity(
            id=uuid.uuid4(),
            thread_id=thread_id,
            role=CopilotRole.ASSISTANT,
            content=content,
            model_provider=provider_name,
            model_name=model_name,
            token_count=token_count,
        )
        return await self.message_repo.add_message(message)

    async def get_conversation_history(
        self, thread_id: uuid.UUID, workspace_id: uuid.UUID, limit: int = 100
    ) -> List[CopilotMessageEntity]:
        thread = await self.thread_repo.get_by_id(thread_id, workspace_id)
        if not thread:
            raise ThreadNotFoundError(str(thread_id))
        return await self.message_repo.get_messages(thread_id, limit)
