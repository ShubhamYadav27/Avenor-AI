"""Auth routes — register, login, get current user."""
import uuid
from pydantic import BaseModel, EmailStr
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth import (
    CurrentUser, hash_password, verify_password, create_access_token
)
from app.db.session import get_db
from app.models import Workspace, WorkspaceUser, WorkspaceUserRole
from app.modules.scoring.engine import initialize_workspace_weights

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str
    workspace_name: str


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    workspace_id: str
    user_id: str


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user and create their workspace."""
    existing = db.query(WorkspaceUser).filter_by(email=req.email.lower()).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    # Create workspace
    slug = req.workspace_name.lower().replace(" ", "-")[:50] + "-" + str(uuid.uuid4())[:8]
    workspace = Workspace(
        name=req.workspace_name,
        slug=slug,
    )
    db.add(workspace)
    db.flush()

    # Create admin user
    user = WorkspaceUser(
        workspace_id=workspace.id,
        email=req.email.lower(),
        full_name=req.full_name,
        hashed_password=hash_password(req.password),
        role=WorkspaceUserRole.ADMIN,
    )
    db.add(user)
    db.flush()

    # Initialize default signal weights
    initialize_workspace_weights(db, str(workspace.id))

    db.commit()

    token = create_access_token(
        user_id=str(user.id),
        workspace_id=str(workspace.id),
        role=user.role,
    )
    return TokenResponse(
        access_token=token,
        workspace_id=str(workspace.id),
        user_id=str(user.id),
    )


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Login with email and password."""
    user = db.query(WorkspaceUser).filter_by(email=req.email.lower(), is_active=True).first()
    if not user or not user.hashed_password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(
        user_id=str(user.id),
        workspace_id=str(user.workspace_id),
        role=user.role,
    )
    return TokenResponse(
        access_token=token,
        workspace_id=str(user.workspace_id),
        user_id=str(user.id),
    )


@router.get("/me")
def get_me(current_user: CurrentUser):
    """Return current user and workspace info."""
    return {
        "user_id": str(current_user.user_id),
        "email": current_user.user.email,
        "full_name": current_user.user.full_name,
        "role": current_user.role,
        "workspace_id": str(current_user.workspace_id),
        "workspace_name": current_user.workspace.name,
        "subscription_tier": current_user.workspace.subscription_tier,
    }
