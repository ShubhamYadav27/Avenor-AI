"""
Thread Service
Handles thread lifecycle management (CRUD, archive, rename, list) with workspace isolation.
"""
from typing import List, Optional
import uuid

from app.modules.copilot.domain.entities import CopilotThreadEntity, ThreadStatus
from app.modules.copilot.domain.exceptions import ThreadNotFoundError
from app.modules.copilot.domain.interfaces import IThreadRepository


class ThreadService:
    def __init__(self, thread_repo: IThreadRepository):
        self.thread_repo = thread_repo

    async def create_thread(
        self, workspace_id: uuid.UUID, user_id: uuid.UUID, title: str = "New Strategic Session"
    ) -> CopilotThreadEntity:
        thread = CopilotThreadEntity(
            id=uuid.uuid4(),
            workspace_id=workspace_id,
            user_id=user_id,
            title=title,
            status=ThreadStatus.ACTIVE,
        )
        return await self.thread_repo.create(thread)

    async def get_thread(self, thread_id: uuid.UUID, workspace_id: uuid.UUID) -> CopilotThreadEntity:
        thread = await self.thread_repo.get_by_id(thread_id, workspace_id)
        if not thread:
            raise ThreadNotFoundError(str(thread_id))
        return thread

    async def list_threads(
        self, workspace_id: uuid.UUID, user_id: Optional[uuid.UUID] = None, limit: int = 50, offset: int = 0
    ) -> List[CopilotThreadEntity]:
        return await self.thread_repo.list_by_workspace(workspace_id, user_id, limit, offset)

    async def rename_thread(
        self, thread_id: uuid.UUID, workspace_id: uuid.UUID, new_title: str
    ) -> CopilotThreadEntity:
        thread = await self.get_thread(thread_id, workspace_id)
        thread.title = new_title
        return await self.thread_repo.update(thread)

    async def archive_thread(
        self, thread_id: uuid.UUID, workspace_id: uuid.UUID
    ) -> CopilotThreadEntity:
        thread = await self.get_thread(thread_id, workspace_id)
        thread.status = ThreadStatus.ARCHIVED
        return await self.thread_repo.update(thread)

    async def delete_thread(self, thread_id: uuid.UUID, workspace_id: uuid.UUID) -> bool:
        return await self.thread_repo.delete(thread_id, workspace_id)
