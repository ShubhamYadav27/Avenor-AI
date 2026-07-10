"""ICP configuration routes — create, read, update."""
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth import CurrentUser
from app.db.session import get_db
from app.models import ICPConfig

router = APIRouter(prefix="/icp", tags=["icp"])


class ICPConfigRequest(BaseModel):
    industries: list[str] = []
    min_employees: int = 50
    max_employees: int = 500
    locations: list[str] = []
    technologies: list[str] = []
    excluded_technologies: list[str] = []
    funding_stages: list[str] = []
    competitor_names: list[str] = []
    keywords: list[str] = []
    product_name: str | None = None
    product_description: str | None = None
    key_pain_points: list[str] = []
    customer_personas: list[str] = []
    active_score_threshold: float = 0.60
    watch_score_threshold: float = 0.30


@router.get("")
def get_icp(current_user: CurrentUser, db: Session = Depends(get_db)):
    """Get the current workspace ICP configuration."""
    icp = db.query(ICPConfig).filter_by(workspace_id=current_user.workspace_id).first()
    if not icp:
        raise HTTPException(status_code=404, detail="ICP not configured yet")
    return {
        "id": str(icp.id),
        "industries": icp.industries,
        "min_employees": icp.min_employees,
        "max_employees": icp.max_employees,
        "locations": icp.locations,
        "technologies": icp.technologies,
        "excluded_technologies": icp.excluded_technologies,
        "funding_stages": icp.funding_stages,
        "competitor_names": icp.competitor_names,
        "keywords": icp.keywords,
        "product_name": icp.product_name,
        "product_description": icp.product_description,
        "key_pain_points": icp.key_pain_points,
        "customer_personas": icp.customer_personas,
        "active_score_threshold": icp.active_score_threshold,
        "watch_score_threshold": icp.watch_score_threshold,
        "updated_at": icp.updated_at.isoformat(),
    }


@router.put("")
def upsert_icp(req: ICPConfigRequest, current_user: CurrentUser, db: Session = Depends(get_db)):
    """Create or update ICP configuration."""
    current_user.require_admin()

    icp = db.query(ICPConfig).filter_by(workspace_id=current_user.workspace_id).first()
    if icp is None:
        icp = ICPConfig(workspace_id=current_user.workspace_id)
        db.add(icp)

    for field, value in req.model_dump().items():
        setattr(icp, field, value)

    db.commit()
    db.refresh(icp)
    return {"success": True, "message": "ICP configuration saved", "id": str(icp.id)}
