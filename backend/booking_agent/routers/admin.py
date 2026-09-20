from fastapi import APIRouter, Depends, status

from booking_agent.dependencies import get_admin_service, require_admin
from booking_agent.schemas.user import (
    CreateUserRequest,
    CreateUserResponse,
    MessageResponse,
    UserListResponse,
)
from booking_agent.services.admin_service import AdminService

router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(require_admin)])


@router.post("/users", response_model=CreateUserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    body: CreateUserRequest,
    service: AdminService = Depends(get_admin_service),
) -> CreateUserResponse:
    """Create a new user. Returns the user details with a one-time plaintext password."""
    return service.create_user(body)


@router.get("/users", response_model=UserListResponse)
def list_users(
    service: AdminService = Depends(get_admin_service),
) -> UserListResponse:
    """List all users."""
    return service.list_users()


@router.delete("/users/{user_id}", response_model=MessageResponse)
def delete_user(
    user_id: str,
    service: AdminService = Depends(get_admin_service),
) -> MessageResponse:
    """Delete a user. Admin users cannot be deleted."""
    return service.delete_user(user_id)
