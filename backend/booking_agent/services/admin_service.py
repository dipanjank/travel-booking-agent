from fastapi import HTTPException, status

from booking_agent.models.user import User
from booking_agent.repositories.user_repository import UserRepository
from booking_agent.schemas.user import (
    CreateUserRequest,
    CreateUserResponse,
    MessageResponse,
    UserListResponse,
    UserResponse,
)
from booking_agent.utils.auth import generate_password, hash_password


class AdminService:
    """Handles user management operations for admin users."""

    def __init__(self, user_repo: UserRepository) -> None:
        self._user_repo = user_repo

    def create_user(self, body: CreateUserRequest) -> CreateUserResponse:
        """Create a new user with a randomly generated password.

        Returns the user details including the one-time plaintext password.
        Raises HTTPException 409 if the username or email already exists.
        """
        existing = self._user_repo.get_by_username_or_email(body.username, body.email)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username or email already exists",
            )

        password = generate_password()
        user = self._user_repo.create(
            User(
                username=body.username,
                email=body.email,
                password_hash=hash_password(password),
                role=body.role,
            )
        )

        return CreateUserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            password=password,
            created_at=user.created_at,
        )

    def list_users(self) -> UserListResponse:
        """Return all users ordered by creation date."""
        users = self._user_repo.get_all(order_by="created_at")
        total = self._user_repo.count()
        return UserListResponse(
            items=[
                UserResponse(
                    id=u.id,
                    username=u.username,
                    email=u.email,
                    role=u.role,
                    created_at=u.created_at,
                )
                for u in users
            ],
            total=total,
        )

    def delete_user(self, user_id: str) -> MessageResponse:
        """Delete a user by ID. Admin users cannot be deleted.

        Raises HTTPException 404 if the user is not found.
        Raises HTTPException 403 if attempting to delete an admin user.
        """
        user = self._user_repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if user.role == "ADMIN_USER":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot delete admin users")

        self._user_repo.delete(user)
        return MessageResponse(message="User deleted", id=user.id)
