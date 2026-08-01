"""
SQLAlchemy State Repository
Manages transient and persistent ConversationState for threads.
"""
from typing import Optional
import uuid
from sqlalchemy.orm import Session

from app.models import CopilotStateModel
from app.modules.copilot.domain.entities import CopilotStateEntity
from app.modules.copilot.domain.interfaces import IStateRepository


class SQLAlchemyStateRepository(IStateRepository):
    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, model: CopilotStateModel) -> CopilotStateEntity:
        return CopilotStateEntity(
            id=model.id,
            workspace_id=model.workspace_id,
            thread_id=model.thread_id,
            current_company_id=model.current_company_id,
            current_deal_id=model.current_deal_id,
            current_contact_id=model.current_contact_id,
            active_workspace_context=model.active_workspace_context or {},
            active_recommendation=model.active_recommendation or {},
            active_prompt_context=model.active_prompt_context,
            token_budget=model.token_budget or 8000,
            last_tool_used=model.last_tool_used,
            updated_at=model.updated_at,
        )

    async def get_state(self, thread_id: uuid.UUID, workspace_id: uuid.UUID) -> Optional[CopilotStateEntity]:
        model = (
            self.db.query(CopilotStateModel)
            .filter(
                CopilotStateModel.thread_id == thread_id,
                CopilotStateModel.workspace_id == workspace_id,
            )
            .first()
        )
        if not model:
            return None
        return self._to_entity(model)

    async def upsert_state(self, state: CopilotStateEntity) -> CopilotStateEntity:
        model = (
            self.db.query(CopilotStateModel)
            .filter(
                CopilotStateModel.thread_id == state.thread_id,
                CopilotStateModel.workspace_id == state.workspace_id,
            )
            .first()
        )
        if not model:
            model = CopilotStateModel(
                id=state.id or uuid.uuid4(),
                workspace_id=state.workspace_id,
                thread_id=state.thread_id,
            )
            self.db.add(model)

        model.current_company_id = state.current_company_id
        model.current_deal_id = state.current_deal_id
        model.current_contact_id = state.current_contact_id
        model.active_workspace_context = state.active_workspace_context
        model.active_recommendation = state.active_recommendation
        model.active_prompt_context = state.active_prompt_context
        model.token_budget = state.token_budget
        model.last_tool_used = state.last_tool_used
        model.updated_at = state.updated_at

        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)
