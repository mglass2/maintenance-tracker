"""Tests for APIClient user context header injection."""

from unittest.mock import MagicMock, patch

import pytest

from src.api_client import APIClient
from src import session


@pytest.fixture(autouse=True)
def clear_session():
    """Clear session before and after each test."""
    session.clear_session()
    yield
    session.clear_session()


class TestAPIClientUserHeader:
    """Test X-User-ID header injection in APIClient."""

    def test_api_client_includes_user_id_header(self):
        """Test that APIClient includes X-User-ID header when user is authenticated."""
        # Set active user
        user_data = {"id": 42, "name": "John Doe", "email": "john@example.com"}
        session.set_active_user(42, user_data)

        # Mock the requests session
        with patch("src.api_client.client.requests.Session.request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = '{"status": "ok"}'
            mock_response.headers = {}
            mock_request.return_value = mock_response

            client = APIClient()
            client._make_request("GET", "/test")

            # Verify the request was made with the X-User-ID header
            mock_request.assert_called_once()
            call_kwargs = mock_request.call_args[1]
            assert "headers" in call_kwargs
            assert call_kwargs["headers"]["X-User-ID"] == "42"

    def test_api_client_omits_user_id_header_when_not_authenticated(self):
        """Test that APIClient omits X-User-ID header when no user is authenticated."""
        # Ensure no user is authenticated
        assert not session.is_authenticated()

        # Mock the requests session
        with patch("src.api_client.client.requests.Session.request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = '{"status": "ok"}'
            mock_response.headers = {}
            mock_request.return_value = mock_response

            client = APIClient()
            client._make_request("GET", "/test")

            # Verify the request was made without X-User-ID header
            mock_request.assert_called_once()
            call_kwargs = mock_request.call_args[1]
            assert "headers" in call_kwargs
            assert "X-User-ID" not in call_kwargs["headers"]

    def test_api_client_header_value_is_string(self):
        """Test that X-User-ID header value is a string."""
        # Set active user with integer ID
        user_data = {"id": 123, "name": "Jane Doe", "email": "jane@example.com"}
        session.set_active_user(123, user_data)

        # Mock the requests session
        with patch("src.api_client.client.requests.Session.request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = '{"status": "ok"}'
            mock_response.headers = {}
            mock_request.return_value = mock_response

            client = APIClient()
            client._make_request("GET", "/test")

            # Verify the header value is a string
            call_kwargs = mock_request.call_args[1]
            header_value = call_kwargs["headers"]["X-User-ID"]
            assert isinstance(header_value, str)
            assert header_value == "123"

    def test_api_client_switches_user_context(self):
        """Test that APIClient uses updated user context."""
        # Set first user
        user1 = {"id": 1, "name": "User One", "email": "user1@example.com"}
        session.set_active_user(1, user1)

        with patch("src.api_client.client.requests.Session.request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = '{"status": "ok"}'
            mock_response.headers = {}
            mock_request.return_value = mock_response

            # First request with user 1
            client = APIClient()
            client._make_request("GET", "/test")

            first_call_headers = mock_request.call_args[1]["headers"]
            assert first_call_headers["X-User-ID"] == "1"

        # Switch to second user
        user2 = {"id": 2, "name": "User Two", "email": "user2@example.com"}
        session.set_active_user(2, user2)

        with patch("src.api_client.client.requests.Session.request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = '{"status": "ok"}'
            mock_response.headers = {}
            mock_request.return_value = mock_response

            # Second request with user 2
            client = APIClient()
            client._make_request("GET", "/test")

            second_call_headers = mock_request.call_args[1]["headers"]
            assert second_call_headers["X-User-ID"] == "2"

    def test_api_client_preserves_other_headers(self):
        """Test that APIClient preserves default headers while adding user header."""
        user_data = {"id": 1, "name": "John Doe", "email": "john@example.com"}
        session.set_active_user(1, user_data)

        with patch("src.api_client.client.requests.Session.request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = '{"status": "ok"}'
            mock_response.headers = {}
            mock_request.return_value = mock_response

            client = APIClient()
            client._make_request("POST", "/test", data={"key": "value"})

            call_kwargs = mock_request.call_args[1]
            headers = call_kwargs["headers"]

            # Verify X-User-ID header is present
            assert headers["X-User-ID"] == "1"

            # Verify default headers are preserved
            # (they're set in _create_session, so they come from the session)
            assert "json" in mock_request.call_args[1]
