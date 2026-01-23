"""Tests for session management module."""

import pytest

from src import session


class TestSessionState:
    """Test session state management."""

    def teardown_method(self):
        """Clear session after each test."""
        session.clear_session()

    def test_set_and_get_active_user(self):
        """Test setting and getting active user."""
        user_data = {"id": 1, "name": "John Doe", "email": "john@example.com"}
        session.set_active_user(1, user_data)

        assert session.get_active_user_id() == 1
        assert session.get_active_user_data() == user_data

    def test_get_active_user_id_when_not_authenticated(self):
        """Test getting user ID when no user is selected."""
        assert session.get_active_user_id() is None

    def test_get_active_user_data_when_not_authenticated(self):
        """Test getting user data when no user is selected."""
        assert session.get_active_user_data() is None

    def test_is_authenticated_true(self):
        """Test is_authenticated returns True when user is set."""
        user_data = {"id": 1, "name": "John Doe", "email": "john@example.com"}
        session.set_active_user(1, user_data)

        assert session.is_authenticated() is True

    def test_is_authenticated_false(self):
        """Test is_authenticated returns False when no user is set."""
        assert session.is_authenticated() is False

    def test_clear_session(self):
        """Test clearing session state."""
        user_data = {"id": 1, "name": "John Doe", "email": "john@example.com"}
        session.set_active_user(1, user_data)

        session.clear_session()

        assert session.get_active_user_id() is None
        assert session.get_active_user_data() is None
        assert session.is_authenticated() is False

    def test_overwrite_active_user(self):
        """Test overwriting active user."""
        user_data_1 = {"id": 1, "name": "John Doe", "email": "john@example.com"}
        session.set_active_user(1, user_data_1)

        user_data_2 = {"id": 2, "name": "Jane Doe", "email": "jane@example.com"}
        session.set_active_user(2, user_data_2)

        assert session.get_active_user_id() == 2
        assert session.get_active_user_data() == user_data_2

    def test_session_preserves_all_user_fields(self):
        """Test that session preserves all user data fields."""
        user_data = {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "created_at": "2026-01-23T10:00:00Z",
            "updated_at": "2026-01-23T10:00:00Z",
        }
        session.set_active_user(1, user_data)

        retrieved_data = session.get_active_user_data()
        assert retrieved_data == user_data
        assert retrieved_data["created_at"] == user_data["created_at"]
        assert retrieved_data["updated_at"] == user_data["updated_at"]
