"""
SQLAlchemy Thread Repository
Enforces tenant and workspace isolation on all queries.
"""
from typing import List, Optional
import uuid
from sqlalchemy.orm import Session

from app.models import CopilotThreadModel, CopilotStateModel
from app.modules.copilot.domain.entities import (
    CopilotMessageEntity,
    CopilotRole,
    CopilotStateEntity,
    CopilotThreadEntity,
    ThreadStatus,
)
from app.modules.copilot.domain.interfaces import IThreadRepository


class SQLAlchemyThreadRepository(IThreadRepository):
    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, model: CopilotThreadModel) -> CopilotThreadEntity:
        messages = [
            CopilotMessageEntity(
                id=m.id,
                thread_id=m.thread_id,
                role=CopilotRole(m.role),
                content=m.content,
                model_provider=m.model_provider,
                model_name=m.model_name,
                token_count=m.token_count or 0,
                extra_metadata=m.extra_metadata or {},
                created_at=m.created_at,
            )
            for m in (model.messages or [])
        ]
        
        state_entity = None
        if model.state:
            s = model.state
            state_entity = CopilotStateEntity(
                id=s.id,
                workspace_id=s.workspace_id,
                thread_id=s.thread_id,
                current_company_id=s.current_company_id,
                current_deal_id=s.current_deal_id,
                current_contact_id=s.current_contact_id,
                active_workspace_context=s.active_workspace_context or {},
                active_recommendation=s.active_recommendation or {},
                active_prompt_context=s.active_prompt_context,
                token_budget=s.token_budget or 8000,
                last_tool_used=s.last_tool_used,
                updated_at=s.updated_at,
            )

        return CopilotThreadEntity(
            id=model.id,
            workspace_id=model.workspace_id,
            user_id=model.user_id,
            title=model.title,
            status=ThreadStatus(model.status),
            extra_metadata=model.extra_metadata or {},
            created_at=model.created_at,
            updated_at=model.updated_at,
            messages=messages,
            state=state_entity,
        )

    async def create(self, thread: CopilotThreadEntity) -> CopilotThreadEntity:
        model = CopilotThreadModel(
            id=thread.id,
            workspace_id=thread.workspace_id,
            user_id=thread.user_id,
            title=thread.title,
            status=thread.status.value,
            extra_metadata=thread.extra_metadata,
            created_at=thread.created_at,
            updated_at=thread.updated_at,
        )
        self.db.add(model)
        
        # Initial conversation state
        state_model = CopilotStateModel(
            id=uuid.uuid4(),
            workspace_id=thread.workspace_id,
            thread_id=thread.id,
            active_workspace_context={},
            active_recommendation={},
            token_budget=8000,
        )
        self.db.add(state_model)
        
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, thread_id: uuid.UUID, workspace_id: uuid.UUID) -> Optional[CopilotThreadEntity]:
        model = (
            self.db.query(CopilotThreadModel)
            .filter(
                CopilotThreadModel.id == thread_id,
                CopilotThreadModel.workspace_id == workspace_id,
            )
            .first()
        )
        if not model:
            return None
        return self._to_entity(model)

    async def list_by_workspace(
        self, workspace_id: uuid.UUID, user_id: Optional[uuid.UUID] = None, limit: int = 50, offset: int = 0
    ) -> List[CopilotThreadEntity]:
        query = self.db.query(CopilotThreadModel).filter(
            CopilotThreadModel.workspace_id == workspace_id,
            CopilotThreadModel.status != ThreadStatus.ARCHIVED.value,
        )
        if user_id:
            query = query.filter(CopilotThreadModel.user_id == user_id)
            
        models = query.order_by(CopilotThreadModel.updated_at.desc()).offset(offset).limit(limit).all()
        return [self._to_entity(m) for m in models]

    async def update(self, thread: CopilotThreadEntity) -> CopilotThreadEntity:
        model = (
            self.db.query(CopilotThreadModel)
            .filter(
                CopilotThreadModel.id == thread.id,
                CopilotThreadModel.workspace_id == thread.workspace_id,
            )
            .first()
        )
        if not model:
            raise ValueError("Thread not found for update")

        model.title = thread.title
        model.status = thread.status.value
        model.extra_metadata = thread.extra_metadata
        model.updated_at = thread.updated_at

        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    async def delete(self, thread_id: uuid.UUID, workspace_id: uuid.UUID) -> bool:
        model = (
            self.db.query(CopilotThreadModel)
            .filter(
                CopilotThreadModel.id == thread_id,
                CopilotThreadModel.workspace_id == workspace_id,
            )
            .first()
        )
        if not model:
            return False

        self.db.delete(model)
        self.db.commit()
        return True
