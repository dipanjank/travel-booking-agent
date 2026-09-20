import uuid

from fastapi import HTTPException, status

from booking_agent.config import settings
from booking_agent.repositories.user_repository import UserRepository
from booking_agent.schemas.auth import LoginRequest, TokenResponse
from booking_agent.utils.auth import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)


class AuthService:
    """Handles login and token refresh logic against the users database."""

    def __init__(self, user_repo: UserRepository) -> None:
        self._user_repo = user_repo

    def login(self, body: LoginRequest) -> tuple[TokenResponse, str]:
        """Validate credentials and return an access/refresh token pair.

        Raises HTTPException 401 if credentials are invalid.
        """
        user = self._user_repo.get_one(username=body.username)
        if user is None or not verify_password(body.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        access_token = create_access_token(str(user.id), user.role)
        refresh_token = create_refresh_token(str(user.id))

        token_response = TokenResponse(
            access_token=access_token,
            expires_in=settings.jwt_access_token_expire_minutes * 60,
        )
        return token_response, refresh_token

    def refresh(self, token: str) -> tuple[TokenResponse, str]:
        """Validate a refresh token and issue a new token pair.

        Raises HTTPException 401 if the refresh token is invalid or the user is not found.
        """
        payload = decode_token(token)
        if payload is None or payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        user = self._user_repo.get_by_id(uuid.UUID(payload["sub"]))
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        access_token = create_access_token(str(user.id), user.role)
        new_refresh_token = create_refresh_token(str(user.id))

        token_response = TokenResponse(
            access_token=access_token,
            expires_in=settings.jwt_access_token_expire_minutes * 60,
        )
        return token_response, new_refresh_token
