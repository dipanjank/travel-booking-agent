"""Shared fixtures for backend tests."""

import os
from unittest.mock import patch

# Set environment variables before any booking_agent imports so that
# ``Settings()`` (evaluated at module level in config.py) can be satisfied.
os.environ.setdefault("JWT_SECRET", "test-secret-key")
os.environ.setdefault("ADMIN_PASSWORD", "test-admin-password")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("MCP_SERVER_URL", "http://localhost:8001/mcp")

# Patch create_engine before importing database.py so the module-level engine
# creation uses SQLite without unsupported pool arguments.
from sqlalchemy import create_engine as _real_create_engine
from sqlalchemy.orm import sessionmaker as _real_sessionmaker


def _sqlite_create_engine(url, **kwargs):
    """Drop pool_size/max_overflow for SQLite."""
    kwargs.pop("pool_size", None)
    kwargs.pop("max_overflow", None)
    return _real_create_engine(url, **kwargs)


patch("sqlalchemy.create_engine", _sqlite_create_engine).start()

import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from booking_agent.database import Base
from booking_agent.models.user import User
from booking_agent.repositories.user_repository import UserRepository
from booking_agent.utils.auth import hash_password


@pytest.fixture()
def db_session():
    """Create an in-memory SQLite database and yield a session.

    Tables are created fresh for each test and torn down afterwards.
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(engine, expire_on_commit=False)
    session = TestSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture()
def user_repo(db_session: Session) -> UserRepository:
    """Return a UserRepository bound to the test session."""
    return UserRepository(db_session)


def make_user(
    *,
    username: str = "testuser",
    email: str = "test@example.com",
    password: str = "password123",
    role: str = "APPLICATION_USER",
) -> User:
    """Helper to build a User instance with a hashed password."""
    return User(
        id=uuid.uuid4(),
        username=username,
        email=email,
        password_hash=hash_password(password),
        role=role,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
