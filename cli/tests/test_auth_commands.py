"""Tests for authentication and user selection commands."""

import json
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from src.commands.auth import select_user, whoami, switch_user, logout
from src import session


@pytest.fixture
def cli_runner():
    """Provide a Click CLI test runner."""
    return CliRunner()


@pytest.fixture(autouse=True)
def clear_session():
    """Clear session before and after each test."""
    session.clear_session()
    yield
    session.clear_session()


class TestSelectUser:
    """Test select-user command."""

    def test_select_user_success(self, cli_runner):
        """Test successful user selection."""
        with patch("src.commands.auth.APIClient") as mock_api_client:
            mock_response = MagicMock()
            mock_response.data = {
                "data": [
                    {"id": 1, "name": "John Doe", "email": "john@example.com"},
                    {"id": 2, "name": "Jane Smith", "email": "jane@example.com"},
                ]
            }

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.return_value = mock_response
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(select_user, input="1\n")

            assert result.exit_code == 0
            assert "Available users:" in result.output
            assert "John Doe" in result.output
            assert "✓ Active user: John Doe" in result.output
            assert session.get_active_user_id() == 1

    def test_select_user_multiple_users(self, cli_runner):
        """Test selecting from multiple users."""
        with patch("src.commands.auth.APIClient") as mock_api_client:
            mock_response = MagicMock()
            mock_response.data = {
                "data": [
                    {"id": 1, "name": "John Doe", "email": "john@example.com"},
                    {"id": 2, "name": "Jane Smith", "email": "jane@example.com"},
                    {"id": 3, "name": "Bob Johnson", "email": "bob@example.com"},
                ]
            }

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.return_value = mock_response
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(select_user, input="3\n")

            assert result.exit_code == 0
            assert session.get_active_user_id() == 3
            assert session.get_active_user_data()["name"] == "Bob Johnson"

    def test_select_user_no_users(self, cli_runner):
        """Test select-user when no users exist."""
        with patch("src.commands.auth.APIClient") as mock_api_client:
            mock_response = MagicMock()
            mock_response.data = {"data": []}

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.return_value = mock_response
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(select_user)

            assert result.exit_code == 0
            assert "Error: No users found in the system." in result.output
            assert "create-user" in result.output
            assert not session.is_authenticated()

    def test_select_user_invalid_selection(self, cli_runner):
        """Test invalid user selection (out of range)."""
        with patch("src.commands.auth.APIClient") as mock_api_client:
            mock_response = MagicMock()
            mock_response.data = {
                "data": [
                    {"id": 1, "name": "John Doe", "email": "john@example.com"},
                    {"id": 2, "name": "Jane Smith", "email": "jane@example.com"},
                ]
            }

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.return_value = mock_response
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(select_user, input="5\n1\n")

            assert result.exit_code == 0
            assert "Error: Please enter a number between 1 and 2" in result.output
            assert session.get_active_user_id() == 1

    def test_select_user_api_error(self, cli_runner):
        """Test select-user when API call fails."""
        with patch("src.commands.auth.APIClient") as mock_api_client:
            mock_client_instance = MagicMock()
            mock_client_instance._make_request.side_effect = Exception("Connection failed")
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(select_user)

            assert result.exit_code == 0
            assert "Error selecting user" in result.output
            assert not session.is_authenticated()


class TestWhoami:
    """Test whoami command."""

    def test_whoami_with_active_user(self, cli_runner):
        """Test whoami when user is authenticated."""
        user_data = {"id": 1, "name": "John Doe", "email": "john@example.com"}
        session.set_active_user(1, user_data)

        result = cli_runner.invoke(whoami)

        assert result.exit_code == 0
        assert "Active User:" in result.output
        assert "ID:    1" in result.output
        assert "Name:  John Doe" in result.output
        assert "Email: john@example.com" in result.output

    def test_whoami_without_active_user(self, cli_runner):
        """Test whoami when no user is authenticated."""
        result = cli_runner.invoke(whoami)

        assert result.exit_code == 0
        assert "No active user" in result.output


class TestSwitchUser:
    """Test switch-user command."""

    def test_switch_user_success(self, cli_runner):
        """Test switching to a different user."""
        # First, set an initial user
        initial_user = {"id": 1, "name": "John Doe", "email": "john@example.com"}
        session.set_active_user(1, initial_user)

        with patch("src.commands.auth.APIClient") as mock_api_client:
            mock_response = MagicMock()
            mock_response.data = {
                "data": [
                    {"id": 1, "name": "John Doe", "email": "john@example.com"},
                    {"id": 2, "name": "Jane Smith", "email": "jane@example.com"},
                ]
            }

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.return_value = mock_response
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(switch_user, input="2\n")

            assert result.exit_code == 0
            assert "Switching user..." in result.output
            assert session.get_active_user_id() == 2
            assert session.get_active_user_data()["name"] == "Jane Smith"


class TestLogout:
    """Test logout command."""

    def test_logout_with_active_user(self, cli_runner):
        """Test logout when user is authenticated."""
        user_data = {"id": 1, "name": "John Doe", "email": "john@example.com"}
        session.set_active_user(1, user_data)

        result = cli_runner.invoke(logout, catch_exceptions=False)

        # CliRunner catches sys.exit() as an Exit exception
        assert "✓ Logged out: John Doe" in result.output
        assert "Exiting..." in result.output

    def test_logout_without_active_user(self, cli_runner):
        """Test logout when no user is authenticated."""
        result = cli_runner.invoke(logout, catch_exceptions=False)

        # CliRunner catches sys.exit() as an Exit exception
        assert "No active session." in result.output
        assert "Exiting..." in result.output
