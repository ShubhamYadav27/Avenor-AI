"""Signals routes — view and manage detected buying signals."""
from typing import Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.auth import CurrentUser
from app.db.session import get_db
from app.models import Company, Signal, SignalType, SignalSource

router = APIRouter(prefix="/signals", tags=["signals"])


class ManualSignalRequest(BaseModel):
    company_id: str
    signal_type: str
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    base_strength: float = 0.20


@router.get("")
def list_signals(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    company_id: Optional[str] = Query(None),
    signal_type: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
):
    """List signals for the workspace, optionally filtered by company or type."""
    query = (
        db.query(Signal)
        .join(Company, Signal.company_id == Company.id)
        .filter(Signal.workspace_id == current_user.workspace_id)
    )

    if company_id:
        query = query.filter(Signal.company_id == company_id)
    if signal_type:
        query = query.filter(Signal.signal_type == signal_type)

    total = query.count()
    signals = (
        query
        .order_by(Signal.detected_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "signals": [
            {
                "id": str(s.id),
                "company_id": str(s.company_id),
                "signal_type": s.signal_type,
                "signal_source": s.signal_source,
                "title": s.title,
                "description": s.description,
                "url": s.url,
                "base_strength": round(s.base_strength, 3),
                "decayed_strength": round(s.decayed_strength, 3),
                "detected_at": s.detected_at.isoformat(),
            }
            for s in signals
        ],
    }


@router.post("")
def add_manual_signal(
    req: ManualSignalRequest,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    """Add a manual signal for a company (e.g. a sales rep spotted something)."""
    company = db.get(Company, req.company_id)
    if not company or str(company.workspace_id) != str(current_user.workspace_id):
        raise HTTPException(status_code=404, detail="Company not found")

    valid_types = {t.value for t in SignalType}
    if req.signal_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid signal_type. Valid: {valid_types}")

    signal = Signal(
        workspace_id=current_user.workspace_id,
        company_id=req.company_id,
        signal_type=req.signal_type,
        signal_source=SignalSource.MANUAL,
        title=req.title,
        description=req.description,
        url=req.url,
        base_strength=req.base_strength,
        decayed_strength=req.base_strength,
        detected_at=datetime.now(timezone.utc),
        signal_metadata={"added_by": str(current_user.user_id)},
    )
    db.add(signal)
    db.commit()
    db.refresh(signal)

    return {"success": True, "signal_id": str(signal.id)}


@router.get("/types")
def get_signal_types():
    """Return all valid signal types with descriptions."""
    return {
        "signal_types": [
            {"value": "hiring", "label": "Hiring", "description": "Company posting new roles"},
            {"value": "funding", "label": "Funding", "description": "Investment round announced"},
            {"value": "tech_change", "label": "Tech Change", "description": "Stack changes detected"},
            {"value": "expansion", "label": "Expansion", "description": "New market or office"},
            {"value": "intent", "label": "Intent", "description": "Active research signal"},
            {"value": "leadership_change", "label": "Leadership Change", "description": "New executive hired"},
            {"value": "product_launch", "label": "Product Launch", "description": "New product or feature"},
            {"value": "news", "label": "News", "description": "General news mention"},
        ]
    }
