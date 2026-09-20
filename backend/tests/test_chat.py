"""Tests for the POST /api/chat endpoint."""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

# Patch AgentService before importing app so the lifespan doesn't start a real agent.
_mock_agent_instance = MagicMock()
_mock_agent_instance.start = AsyncMock()
_mock_agent_instance.stop = AsyncMock()
_mock_agent_instance.invoke = AsyncMock(return_value="Here are flights from JFK to LAX.")

with patch("booking_agent.main.AgentService", return_value=_mock_agent_instance):
    from starlette.testclient import TestClient

    from booking_agent.dependencies import get_agent_service, get_current_user
    from booking_agent.main import app
    from booking_agent.models.user import User


def _make_user() -> User:
    """Build a test user."""
    user = User()
    user.id = uuid.uuid4()
    user.username = "testuser"
    user.email = "test@example.com"
    user.password_hash = "hashed"
    user.role = "APPLICATION_USER"
    user.created_at = datetime.now(timezone.utc)
    user.updated_at = datetime.now(timezone.utc)
    return user


class TestChatEndpoint:
    """Tests for POST /api/chat."""

    def setup_method(self):
        """Override dependencies for each test."""
        self.mock_agent = MagicMock()
        self.mock_agent.invoke = AsyncMock(return_value="Here are flights from JFK to LAX.")
        self.user = _make_user()

        app.dependency_overrides[get_current_user] = lambda: self.user
        app.dependency_overrides[get_agent_service] = lambda: self.mock_agent
        self.client = TestClient(app)

    def teardown_method(self):
        """Clear dependency overrides."""
        app.dependency_overrides.clear()

    def test_chat_success(self):
        """Authenticated user sends a message and receives an agent response."""
        res = self.client.post(
            "/api/chat",
            json={"message": "Any flights from JFK to LAX?", "thread_id": "test-thread-1"},
        )

        assert res.status_code == 200
        data = res.json()
        assert data["response"] == "Here are flights from JFK to LAX."
        assert data["thread_id"] == "test-thread-1"
        expected_scoped_id = f"{self.user.id}:test-thread-1"
        self.mock_agent.invoke.assert_called_once_with(
            "Any flights from JFK to LAX?", expected_scoped_id
        )

    def test_chat_thread_scoped_per_user(self):
        """Two users with the same thread_id get different scoped thread_ids."""
        user_a = _make_user()
        user_b = _make_user()
        user_b.id = uuid.uuid4()
        user_b.username = "otheruser"
        user_b.email = "other@example.com"

        # User A sends a message
        app.dependency_overrides[get_current_user] = lambda: user_a
        self.client.post("/api/chat", json={"message": "Hi", "thread_id": "shared-thread"})
        call_a = self.mock_agent.invoke.call_args_list[-1]

        # User B sends with the same thread_id
        app.dependency_overrides[get_current_user] = lambda: user_b
        self.client.post("/api/chat", json={"message": "Hi", "thread_id": "shared-thread"})
        call_b = self.mock_agent.invoke.call_args_list[-1]

        # The scoped thread_ids passed to the agent must differ
        assert call_a[0][1] != call_b[0][1]
        assert call_a[0][1] == f"{user_a.id}:shared-thread"
        assert call_b[0][1] == f"{user_b.id}:shared-thread"

    def test_chat_empty_message(self):
        """Empty message string returns 422 validation error."""
        res = self.client.post(
            "/api/chat",
            json={"message": "", "thread_id": "test-thread-1"},
        )

        assert res.status_code == 422

    def test_chat_missing_thread_id(self):
        """Missing thread_id returns 422 validation error."""
        res = self.client.post(
            "/api/chat",
            json={"message": "Hello"},
        )

        assert res.status_code == 422

    def test_chat_unauthenticated(self):
        """Request without valid auth returns 401 or 403."""
        # Remove the get_current_user override so the real guard runs
        app.dependency_overrides.pop(get_current_user, None)

        res = self.client.post(
            "/api/chat",
            json={"message": "Hello", "thread_id": "test-thread-1"},
        )

        assert res.status_code in (401, 403)
