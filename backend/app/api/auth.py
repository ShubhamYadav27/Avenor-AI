"""
Authentication middleware.
For MVP: simple email/password with JWT tokens.
Designed for easy Clerk replacement: swap _verify_token() only.
"""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.db.session import get_db
from app.models import Workspace, WorkspaceUser, WorkspaceUserRole

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=False)


# ── Token helpers ─────────────────────────────────────────────

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: str, workspace_id: str, role: str) -> str:
    payload = {
        "sub": user_id,
        "workspace_id": workspace_id,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.APP_SECRET_KEY, algorithm=ALGORITHM)


def _verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.APP_SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.InvalidTokenError:
        raise AuthenticationError("Invalid token")


# ── FastAPI dependencies ───────────────────────────────────────

class AuthenticatedUser:
    """Represents the authenticated user + workspace context."""

    def __init__(self, user: WorkspaceUser, workspace: Workspace):
        self.user = user
        self.workspace = workspace
        self.workspace_id = workspace.id
        self.user_id = user.id
        self.role = user.role

    def require_admin(self):
        if self.role != WorkspaceUserRole.ADMIN:
            raise AuthorizationError("Admin access required")


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Session = Depends(get_db),
) -> AuthenticatedUser:
    """FastAPI dependency: validate JWT and return user + workspace."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = _verify_token(credentials.credentials)
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    workspace_id = payload.get("workspace_id")

    if not user_id or not workspace_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    user = db.get(WorkspaceUser, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    workspace = db.get(Workspace, workspace_id)
    if not workspace or not workspace.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Workspace not found or inactive")

    # Update last seen
    user.last_seen_at = datetime.now(timezone.utc)
    db.flush()

    return AuthenticatedUser(user=user, workspace=workspace)


# Type alias for routes
CurrentUser = Annotated[AuthenticatedUser, Depends(get_current_user)]
