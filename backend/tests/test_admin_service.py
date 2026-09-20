"""Tests for AdminService."""

import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from booking_agent.models.user import User
from booking_agent.schemas.user import CreateUserRequest
from booking_agent.services.admin_service import AdminService


def _make_user(
    user_id: uuid.UUID | None = None,
    username: str = "testuser",
    email: str = "test@example.com",
    role: str = "APPLICATION_USER",
) -> User:
    """Build a User for admin service tests."""
    user = User()
    user.id = user_id or uuid.uuid4()
    user.username = username
    user.email = email
    user.password_hash = "hashed"
    user.role = role
    user.created_at = datetime.now(timezone.utc)
    user.updated_at = datetime.now(timezone.utc)
    return user


def _simulate_create(user: User) -> User:
    """Simulate what the DB does on insert: fill in defaults for id and created_at."""
    if user.id is None:
        user.id = uuid.uuid4()
    if user.created_at is None:
        user.created_at = datetime.now(timezone.utc)
    if user.updated_at is None:
        user.updated_at = datetime.now(timezone.utc)
    return user


class TestCreateUser:
    """Tests for AdminService.create_user."""

    def test_create_user_success(self):
        """Creating a user returns the user details with a one-time password."""
        repo = MagicMock()
        repo.get_by_username_or_email.return_value = None
        repo.create.side_effect = _simulate_create

        service = AdminService(repo)
        result = service.create_user(
            CreateUserRequest(username="newuser", email="new@example.com", role="APPLICATION_USER")
        )

        assert result.username == "newuser"
        assert result.email == "new@example.com"
        assert result.role == "APPLICATION_USER"
        assert result.password  # one-time password returned
        assert len(result.password) == 16
        repo.create.assert_called_once()

    def test_create_admin_user(self):
        """Creating an admin user sets the correct role."""
        repo = MagicMock()
        repo.get_by_username_or_email.return_value = None
        repo.create.side_effect = _simulate_create

        service = AdminService(repo)
        result = service.create_user(
            CreateUserRequest(username="admin2", email="admin2@example.com", role="ADMIN_USER")
        )

        assert result.role == "ADMIN_USER"

    def test_create_user_duplicate(self):
        """Attempting to create a user with an existing username or email raises 409."""
        existing = _make_user()
        repo = MagicMock()
        repo.get_by_username_or_email.return_value = existing

        service = AdminService(repo)
        with pytest.raises(HTTPException) as exc_info:
            service.create_user(
                CreateUserRequest(username="testuser", email="test@example.com")
            )

        assert exc_info.value.status_code == 409

    def test_create_user_password_is_hashed(self):
        """The stored password_hash differs from the plaintext password."""
        repo = MagicMock()
        repo.get_by_username_or_email.return_value = None
        created_user = None

        def capture_create(user):
            nonlocal created_user
            _simulate_create(user)
            created_user = user
            return user

        repo.create.side_effect = capture_create

        service = AdminService(repo)
        result = service.create_user(
            CreateUserRequest(username="newuser", email="new@example.com")
        )

        assert created_user.password_hash != result.password


class TestListUsers:
    """Tests for AdminService.list_users."""

    def test_list_users_empty(self):
        """Returns empty list when no users exist."""
        repo = MagicMock()
        repo.get_all.return_value = []
        repo.count.return_value = 0

        service = AdminService(repo)
        result = service.list_users()

        assert result.items == []
        assert result.total == 0
        repo.get_all.assert_called_once_with(order_by="created_at")

    def test_list_users_with_data(self):
        """Returns all users with correct total."""
        users = [
            _make_user(username="alice", email="alice@example.com"),
            _make_user(username="bob", email="bob@example.com"),
        ]
        repo = MagicMock()
        repo.get_all.return_value = users
        repo.count.return_value = 2

        service = AdminService(repo)
        result = service.list_users()

        assert len(result.items) == 2
        assert result.total == 2
        assert result.items[0].username == "alice"
        assert result.items[1].username == "bob"

    def test_list_users_excludes_password(self):
        """User list items do not contain password fields."""
        users = [_make_user()]
        repo = MagicMock()
        repo.get_all.return_value = users
        repo.count.return_value = 1

        service = AdminService(repo)
        result = service.list_users()

        item_dict = result.items[0].model_dump()
        assert "password" not in item_dict
        assert "password_hash" not in item_dict


class TestDeleteUser:
    """Tests for AdminService.delete_user."""

    def test_delete_user_success(self):
        """Deleting an application user succeeds."""
        user = _make_user(role="APPLICATION_USER")
        repo = MagicMock()
        repo.get_by_id.return_value = user

        service = AdminService(repo)
        result = service.delete_user(str(user.id))

        assert result.message == "User deleted"
        assert result.id == user.id
        repo.delete.assert_called_once_with(user)

    def test_delete_user_not_found(self):
        """Deleting a non-existent user raises 404."""
        repo = MagicMock()
        repo.get_by_id.return_value = None

        service = AdminService(repo)
        with pytest.raises(HTTPException) as exc_info:
            service.delete_user(str(uuid.uuid4()))

        assert exc_info.value.status_code == 404

    def test_delete_admin_forbidden(self):
        """Deleting an admin user raises 403."""
        admin = _make_user(role="ADMIN_USER")
        repo = MagicMock()
        repo.get_by_id.return_value = admin

        service = AdminService(repo)
        with pytest.raises(HTTPException) as exc_info:
            service.delete_user(str(admin.id))

        assert exc_info.value.status_code == 403
        repo.delete.assert_not_called()
