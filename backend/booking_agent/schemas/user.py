import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class CreateUserRequest(BaseModel):
    """Request to create a new user."""

    username: str = Field(..., min_length=1)
    email: EmailStr
    role: Literal["ADMIN_USER", "APPLICATION_USER"] = "APPLICATION_USER"


class CreateUserResponse(BaseModel):
    """Response after creating a user, includes the one-time plaintext password."""

    id: uuid.UUID
    username: str
    email: str
    role: str
    password: str
    created_at: datetime


class UserResponse(BaseModel):
    """Public user representation (no password)."""

    id: uuid.UUID
    username: str
    email: str
    role: str
    created_at: datetime


class UserListResponse(BaseModel):
    """Paginated list of users."""

    items: list[UserResponse]
    total: int


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str
    id: uuid.UUID | None = None
