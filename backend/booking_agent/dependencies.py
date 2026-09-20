import uuid

from fastapi import Cookie, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from booking_agent.database import get_db
from booking_agent.models.user import User
from booking_agent.repositories.user_repository import UserRepository
from booking_agent.services.admin_service import AdminService
from booking_agent.services.agent_service import AgentService
from booking_agent.services.auth_service import AuthService
from booking_agent.utils.auth import decode_token

bearer_scheme = HTTPBearer()

_agent_service: AgentService | None = None


def set_agent_service(service: AgentService | None) -> None:
    """Set the singleton AgentService instance (called from lifespan)."""
    global _agent_service
    _agent_service = service


def get_agent_service() -> AgentService:
    """Return the singleton AgentService. Raises 503 if not started."""
    if _agent_service is None:
        raise HTTPException(status_code=503, detail="Agent service not available")
    return _agent_service


# --- Repository factories ---


def get_user_repo(db: Session = Depends(get_db)) -> UserRepository:
    """Create a UserRepository bound to the current DB session."""
    return UserRepository(db)


# --- Service factories ---


def get_auth_service(repo: UserRepository = Depends(get_user_repo)) -> AuthService:
    """Create an AuthService wired to a UserRepository."""
    return AuthService(repo)


def get_admin_service(repo: UserRepository = Depends(get_user_repo)) -> AdminService:
    """Create an AdminService wired to a UserRepository."""
    return AdminService(repo)


# --- Auth guards ---


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    repo: UserRepository = Depends(get_user_repo),
) -> User:
    """Decode a Bearer access token and return the corresponding User.

    Raises HTTPException 401 if the token is invalid or the user is not found.
    """
    payload = decode_token(credentials.credentials)
    if payload is None or payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = repo.get_by_id(uuid.UUID(payload["sub"]))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    """Ensure the current user has the ADMIN_USER role.

    Raises HTTPException 403 if the user is not an admin.
    """
    if user.role != "ADMIN_USER":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user


def get_refresh_token(refresh_token: str | None = Cookie(default=None)) -> str:
    """Extract the refresh token from the HttpOnly cookie.

    Raises HTTPException 401 if the cookie is missing.
    """
    if refresh_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token")
    return refresh_token
