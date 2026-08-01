"""
SQLAlchemy Message Repository
Handles saving and retrieving individual conversation messages.
"""
from typing import List
import uuid
from sqlalchemy.orm import Session

from app.models import CopilotMessageModel, CopilotThreadModel
from app.modules.copilot.domain.entities import CopilotMessageEntity, CopilotRole
from app.modules.copilot.domain.interfaces import IMessageRepository


class SQLAlchemyMessageRepository(IMessageRepository):
    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, model: CopilotMessageModel) -> CopilotMessageEntity:
        return CopilotMessageEntity(
            id=model.id,
            thread_id=model.thread_id,
            role=CopilotRole(model.role),
            content=model.content,
            model_provider=model.model_provider,
            model_name=model.model_name,
            token_count=model.token_count or 0,
            extra_metadata=model.extra_metadata or {},
            created_at=model.created_at,
        )

    async def add_message(self, message: CopilotMessageEntity) -> CopilotMessageEntity:
        model = CopilotMessageModel(
            id=message.id,
            thread_id=message.thread_id,
            role=message.role.value,
            content=message.content,
            model_provider=message.model_provider,
            model_name=message.model_name,
            token_count=message.token_count,
            extra_metadata=message.extra_metadata,
            created_at=message.created_at,
        )
        self.db.add(model)
        
        # Touch thread updated_at
        thread = self.db.query(CopilotThreadModel).filter(CopilotThreadModel.id == message.thread_id).first()
        if thread:
            thread.updated_at = message.created_at

        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    async def get_messages(self, thread_id: uuid.UUID, limit: int = 100) -> List[CopilotMessageEntity]:
        models = (
            self.db.query(CopilotMessageModel)
            .filter(CopilotMessageModel.thread_id == thread_id)
            .order_by(CopilotMessageModel.created_at.asc())
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]
