"""Tests for AuthService."""

import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from booking_agent.models.user import User
from booking_agent.schemas.auth import LoginRequest
from booking_agent.services.auth_service import AuthService
from booking_agent.utils.auth import create_refresh_token, hash_password


def _make_user(
    user_id: uuid.UUID | None = None,
    username: str = "testuser",
    role: str = "APPLICATION_USER",
    password: str = "password123",
) -> User:
    """Build a User with a hashed password for auth tests."""
    user = User()
    user.id = user_id or uuid.uuid4()
    user.username = username
    user.email = f"{username}@example.com"
    user.password_hash = hash_password(password)
    user.role = role
    user.created_at = datetime.now(timezone.utc)
    user.updated_at = datetime.now(timezone.utc)
    return user


class TestLogin:
    """Tests for AuthService.login."""

    def test_login_success(self):
        """Valid credentials return an access token and a refresh token."""
        user = _make_user()
        repo = MagicMock()
        repo.get_one.return_value = user

        service = AuthService(repo)
        token_resp, refresh_token = service.login(LoginRequest(username="testuser", password="password123"))

        assert token_resp.access_token
        assert token_resp.token_type == "bearer"
        assert token_resp.expires_in > 0
        assert refresh_token
        repo.get_one.assert_called_once_with(username="testuser")

    def test_login_user_not_found(self):
        """Non-existent username raises 401."""
        repo = MagicMock()
        repo.get_one.return_value = None

        service = AuthService(repo)
        with pytest.raises(HTTPException) as exc_info:
            service.login(LoginRequest(username="ghost", password="password123"))

        assert exc_info.value.status_code == 401

    def test_login_wrong_password(self):
        """Correct username but wrong password raises 401."""
        user = _make_user(password="correct-password")
        repo = MagicMock()
        repo.get_one.return_value = user

        service = AuthService(repo)
        with pytest.raises(HTTPException) as exc_info:
            service.login(LoginRequest(username="testuser", password="wrong-password"))

        assert exc_info.value.status_code == 401


class TestRefresh:
    """Tests for AuthService.refresh."""

    def test_refresh_success(self):
        """A valid refresh token issues a new token pair."""
        user = _make_user()
        repo = MagicMock()
        repo.get_by_id.return_value = user

        token = create_refresh_token(str(user.id))

        service = AuthService(repo)
        token_resp, new_refresh = service.refresh(token)

        assert token_resp.access_token
        assert token_resp.expires_in > 0
        assert new_refresh
        repo.get_by_id.assert_called_once_with(user.id)

    def test_refresh_invalid_token(self):
        """A garbage token raises 401."""
        repo = MagicMock()
        service = AuthService(repo)

        with pytest.raises(HTTPException) as exc_info:
            service.refresh("not-a-real-token")

        assert exc_info.value.status_code == 401

    def test_refresh_with_access_token(self):
        """Using an access token (type != refresh) raises 401."""
        from booking_agent.utils.auth import create_access_token

        token = create_access_token(str(uuid.uuid4()), "APPLICATION_USER")
        repo = MagicMock()
        service = AuthService(repo)

        with pytest.raises(HTTPException) as exc_info:
            service.refresh(token)

        assert exc_info.value.status_code == 401

    def test_refresh_user_not_found(self):
        """A valid refresh token for a deleted user raises 401."""
        user_id = uuid.uuid4()
        repo = MagicMock()
        repo.get_by_id.return_value = None

        token = create_refresh_token(str(user_id))

        service = AuthService(repo)
        with pytest.raises(HTTPException) as exc_info:
            service.refresh(token)

        assert exc_info.value.status_code == 401
