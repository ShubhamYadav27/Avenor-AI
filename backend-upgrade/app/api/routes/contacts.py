"""
GET /api/v1/contacts
 
Returns workspace-scoped contacts with their associated company info.
Supports: search (name/email/company), pagination, sort.
Used by the HubSpot CRM page expandable contacts panel.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
 
from app.api.auth import CurrentUser
from app.db.session import get_db
from app.models import Contact, Company
 
router = APIRouter(prefix="/contacts", tags=["contacts"])
 
SORT_FIELDS = {"full_name", "email", "title", "created_at"}
 
 
@router.get("")
def list_contacts(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Filter by name, email, or company name"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort_by: str = Query("full_name", description="Sort field"),
    sort_dir: str = Query("asc", pattern="^(asc|desc)$"),
):
    """
    List all contacts in the workspace.
    Joins to companies to return company_name and company_domain.
    Workspace-scoped: only returns contacts belonging to companies
    in the authenticated workspace.
    """
    # Base query — join Contact → Company, filter to workspace
    query = (
        db.query(Contact, Company)
        .join(Company, Contact.company_id == Company.id)
        .filter(Company.workspace_id == current_user.workspace_id)
    )
 
    # Search across name, email, and company name
    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Contact.full_name.ilike(term),
                Contact.email.ilike(term),
                Company.name.ilike(term),
            )
        )
 
    total = query.count()
 
    # Sorting — whitelist to prevent injection
    sort_col_map = {
        "full_name": Contact.full_name,
        "email": Contact.email,
        "title": Contact.title,
        "created_at": Contact.created_at,
        "company_name": Company.name,
    }
    sort_col = sort_col_map.get(sort_by, Contact.full_name)
    if sort_dir == "desc":
        sort_col = sort_col.desc()
    else:
        sort_col = sort_col.asc()
 
    rows = (
        query
        .order_by(sort_col)
        .offset(offset)
        .limit(limit)
        .all()
    )
 
    contacts = [
    {
        "id": str(contact.id),
        "full_name": contact.full_name,
        "email": contact.email,
        "job_title": contact.title,
        "phone": contact.phone,
        "seniority": contact.seniority,
        "department": contact.department,
        "linkedin_url": contact.linkedin_url,
        "is_primary": contact.is_primary,
        # Apollo IDs starting with "hs_" came from HubSpot sync
        "hubspot_contact_id": (
            contact.apollo_id.replace("hs_", "")
            if contact.apollo_id and contact.apollo_id.startswith("hs_")
            else None
        ),
        "company_id": str(contact.company_id),
        "company_name": company.name,
        "company_domain": company.domain,
        "created_at": contact.created_at.isoformat() if contact.created_at else None,
        "updated_at": contact.updated_at.isoformat() if contact.updated_at else None,
    }
    for contact, company in rows
]
 
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "contacts": contacts,
    }