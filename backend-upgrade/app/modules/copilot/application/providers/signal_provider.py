"""
Signal Context Provider
Queries active buying signals (hiring, funding, tech changes, intent).
"""
from typing import List, Optional
import uuid
from sqlalchemy.orm import Session

from app.models import Signal
from app.modules.copilot.application.providers.base import BaseContextProvider
from app.modules.copilot.domain.context import ContextCategory, ContextIntent, ContextItem, ContextPriority
from app.modules.copilot.domain.entities import CopilotStateEntity


class SignalContextProvider(BaseContextProvider):
    def __init__(self, db: Session):
        self.db = db

    @property
    def provider_name(self) -> str:
        return "signal_provider"

    @property
    def category(self) -> ContextCategory:
        return ContextCategory.SIGNAL

    def supports_intent(self, intent: ContextIntent) -> bool:
        return intent in [
            ContextIntent.BUYING_SIGNALS,
            ContextIntent.OUTREACH_STRATEGY,
            ContextIntent.COMPANY_DEEP_DIVE,
            ContextIntent.GENERAL_STRATEGY,
        ]

    async def fetch_context(
        self, workspace_id: uuid.UUID, query: str, state: Optional[CopilotStateEntity] = None
    ) -> List[ContextItem]:
        query_builder = self.db.query(Signal).filter(Signal.workspace_id == workspace_id)

        if state and state.current_company_id:
            query_builder = query_builder.filter(Signal.company_id == state.current_company_id)

        signals = query_builder.order_by(Signal.detected_at.desc()).limit(8).all()

        if not signals:
            return []

        lines = ["Recent High-Intent Buying Signals:"]
        for s in signals:
            lines.append(
                f"• [{s.signal_type.upper() if hasattr(s, 'signal_type') else 'SIGNAL'}] "
                f"{s.title or 'Buying Signal Detected'} (Score: {s.score if hasattr(s, 'score') else 'N/A'})"
            )

        item = ContextItem(
            category=ContextCategory.SIGNAL,
            source_provider=self.provider_name,
            priority=ContextPriority.HIGH,
            content="\n".join(lines),
            metadata={"count": len(signals)},
        )
        return [item]
