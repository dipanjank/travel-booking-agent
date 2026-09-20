"""Tests for UserRepository and GenericRepository base methods."""

import uuid

import pytest

from booking_agent.models.user import User
from booking_agent.repositories.user_repository import UserRepository
from tests.conftest import make_user


class TestGenericRepository:
    """Tests for CRUD operations inherited from GenericRepository."""

    def test_create_and_get_by_id(self, user_repo: UserRepository):
        """Creating a user and fetching by ID returns the same entity."""
        user = make_user()
        created = user_repo.create(user)

        assert created.id == user.id
        fetched = user_repo.get_by_id(user.id)
        assert fetched is not None
        assert fetched.username == "testuser"

    def test_get_by_id_not_found(self, user_repo: UserRepository):
        """Fetching a non-existent ID returns None."""
        result = user_repo.get_by_id(uuid.uuid4())
        assert result is None

    def test_get_one_match(self, user_repo: UserRepository):
        """get_one returns the entity matching the given filter."""
        user_repo.create(make_user(username="alice", email="alice@example.com"))
        user_repo.create(make_user(username="bob", email="bob@example.com"))

        result = user_repo.get_one(username="bob")
        assert result is not None
        assert result.username == "bob"

    def test_get_one_no_match(self, user_repo: UserRepository):
        """get_one returns None when no entity matches."""
        result = user_repo.get_one(username="nonexistent")
        assert result is None

    def test_get_all(self, user_repo: UserRepository):
        """get_all returns all entities."""
        user_repo.create(make_user(username="alice", email="alice@example.com"))
        user_repo.create(make_user(username="bob", email="bob@example.com"))

        users = user_repo.get_all()
        assert len(users) == 2

    def test_get_all_with_order_by(self, user_repo: UserRepository):
        """get_all with order_by sorts results by the given column."""
        user_repo.create(make_user(username="zara", email="zara@example.com"))
        user_repo.create(make_user(username="alice", email="alice@example.com"))

        users = user_repo.get_all(order_by="username")
        assert users[0].username == "alice"
        assert users[1].username == "zara"

    def test_get_all_empty(self, user_repo: UserRepository):
        """get_all returns an empty list when no entities exist."""
        users = user_repo.get_all()
        assert users == []

    def test_count(self, user_repo: UserRepository):
        """count returns the total number of entities."""
        assert user_repo.count() == 0

        user_repo.create(make_user(username="alice", email="alice@example.com"))
        assert user_repo.count() == 1

        user_repo.create(make_user(username="bob", email="bob@example.com"))
        assert user_repo.count() == 2

    def test_delete(self, user_repo: UserRepository):
        """Deleting an entity removes it from the database."""
        user = user_repo.create(make_user())
        assert user_repo.count() == 1

        user_repo.delete(user)
        assert user_repo.count() == 0
        assert user_repo.get_by_id(user.id) is None


class TestUserRepository:
    """Tests for UserRepository domain-specific methods."""

    def test_get_by_username_or_email_matches_username(self, user_repo: UserRepository):
        """Finds a user when the username matches."""
        user_repo.create(make_user(username="alice", email="alice@example.com"))

        result = user_repo.get_by_username_or_email("alice", "other@example.com")
        assert result is not None
        assert result.username == "alice"

    def test_get_by_username_or_email_matches_email(self, user_repo: UserRepository):
        """Finds a user when the email matches."""
        user_repo.create(make_user(username="alice", email="alice@example.com"))

        result = user_repo.get_by_username_or_email("other", "alice@example.com")
        assert result is not None
        assert result.email == "alice@example.com"

    def test_get_by_username_or_email_no_match(self, user_repo: UserRepository):
        """Returns None when neither username nor email matches."""
        user_repo.create(make_user(username="alice", email="alice@example.com"))

        result = user_repo.get_by_username_or_email("bob", "bob@example.com")
        assert result is None
