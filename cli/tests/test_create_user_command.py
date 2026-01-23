"""Tests for the create-user command."""

import json
import sys
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from src.api_client import (
    APIClientError4xx,
    APIConnectionError,
    APIServerError5xx,
    APITimeoutError,
)
from src.commands.user import create_user


@pytest.fixture
def cli_runner():
    """Provide a Click CLI test runner."""
    return CliRunner()


class TestCreateUserSuccess:
    """Test successful user creation scenarios."""

    def test_create_user_success(self, cli_runner):
        """Test successful user creation with valid input."""
        with patch("src.commands.user.APIClient") as mock_api_client:
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.data = {
                "data": {
                    "id": 1,
                    "name": "John Doe",
                    "email": "john@example.com",
                    "created_at": "2026-01-23T10:00:00Z",
                    "updated_at": "2026-01-23T10:00:00Z",
                }
            }

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.return_value = mock_response
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(create_user, input="John Doe\njohn@example.com\n")

            assert result.exit_code == 0
            assert "Success: User created successfully!" in result.output
            assert "John Doe" in result.output
            assert "john@example.com" in result.output
            assert "ID:      1" in result.output

    def test_create_user_with_special_characters_in_name(self, cli_runner):
        """Test user creation with special characters in name."""
        with patch("src.commands.user.APIClient") as mock_api_client:
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.data = {
                "data": {
                    "id": 2,
                    "name": "María José García",
                    "email": "maria@example.com",
                    "created_at": "2026-01-23T10:00:00Z",
                    "updated_at": "2026-01-23T10:00:00Z",
                }
            }

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.return_value = mock_response
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(create_user, input="María José García\nmaria@example.com\n")

            assert result.exit_code == 0
            assert "Success: User created successfully!" in result.output


class TestCreateUserClientValidation:
    """Test client-side input validation."""

    def test_create_user_empty_name(self, cli_runner):
        """Test that empty name is rejected and user is re-prompted."""
        with patch("src.commands.user.APIClient") as mock_api_client:
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.data = {
                "data": {
                    "id": 1,
                    "name": "John Doe",
                    "email": "john@example.com",
                    "created_at": "2026-01-23T10:00:00Z",
                    "updated_at": "2026-01-23T10:00:00Z",
                }
            }

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.return_value = mock_response
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(create_user, input="\nJohn Doe\njohn@example.com\n")

            assert result.exit_code == 0
            assert "Error: Name cannot be empty" in result.output
            assert "Success: User created successfully!" in result.output

    def test_create_user_empty_email(self, cli_runner):
        """Test that empty email is rejected and user is re-prompted."""
        with patch("src.commands.user.APIClient") as mock_api_client:
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.data = {
                "data": {
                    "id": 1,
                    "name": "John Doe",
                    "email": "john@example.com",
                    "created_at": "2026-01-23T10:00:00Z",
                    "updated_at": "2026-01-23T10:00:00Z",
                }
            }

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.return_value = mock_response
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(create_user, input="John Doe\n\njohn@example.com\n")

            assert result.exit_code == 0
            assert "Error: Email cannot be empty" in result.output
            assert "Success: User created successfully!" in result.output

    def test_create_user_name_too_long(self, cli_runner):
        """Test that name exceeding 255 characters is rejected and user is re-prompted."""
        with patch("src.commands.user.APIClient") as mock_api_client:
            long_name = "a" * 256
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.data = {
                "data": {
                    "id": 1,
                    "name": "John Doe",
                    "email": "john@example.com",
                    "created_at": "2026-01-23T10:00:00Z",
                    "updated_at": "2026-01-23T10:00:00Z",
                }
            }

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.return_value = mock_response
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(create_user, input=f"{long_name}\nJohn Doe\njohn@example.com\n")

            assert result.exit_code == 0
            assert "Error: Name must be 255 characters or less" in result.output
            assert "Success: User created successfully!" in result.output

    def test_create_user_name_at_max_length(self, cli_runner):
        """Test that name of exactly 255 characters is accepted."""
        with patch("src.commands.user.APIClient") as mock_api_client:
            max_length_name = "a" * 255
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.data = {
                "data": {
                    "id": 3,
                    "name": max_length_name,
                    "email": "user@example.com",
                    "created_at": "2026-01-23T10:00:00Z",
                    "updated_at": "2026-01-23T10:00:00Z",
                }
            }

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.return_value = mock_response
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(create_user, input=f"{max_length_name}\nuser@example.com\n")

            assert result.exit_code == 0
            assert "Success: User created successfully!" in result.output

    def test_create_user_invalid_email_format_no_at(self, cli_runner):
        """Test that email without @ is rejected and user is re-prompted."""
        with patch("src.commands.user.APIClient") as mock_api_client:
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.data = {
                "data": {
                    "id": 1,
                    "name": "John Doe",
                    "email": "john@example.com",
                    "created_at": "2026-01-23T10:00:00Z",
                    "updated_at": "2026-01-23T10:00:00Z",
                }
            }

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.return_value = mock_response
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(create_user, input="John Doe\njohdomain.com\njohn@example.com\n")

            assert result.exit_code == 0
            assert "Error: Invalid email format" in result.output
            assert "Success: User created successfully!" in result.output

    def test_create_user_invalid_email_format_no_domain(self, cli_runner):
        """Test that email without domain is rejected and user is re-prompted."""
        with patch("src.commands.user.APIClient") as mock_api_client:
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.data = {
                "data": {
                    "id": 1,
                    "name": "John Doe",
                    "email": "john@example.com",
                    "created_at": "2026-01-23T10:00:00Z",
                    "updated_at": "2026-01-23T10:00:00Z",
                }
            }

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.return_value = mock_response
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(create_user, input="John Doe\njohn@\njohn@example.com\n")

            assert result.exit_code == 0
            assert "Error: Invalid email format" in result.output
            assert "Success: User created successfully!" in result.output

    def test_create_user_invalid_email_format_no_tld(self, cli_runner):
        """Test that email without TLD is rejected and user is re-prompted."""
        with patch("src.commands.user.APIClient") as mock_api_client:
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.data = {
                "data": {
                    "id": 1,
                    "name": "John Doe",
                    "email": "john@example.com",
                    "created_at": "2026-01-23T10:00:00Z",
                    "updated_at": "2026-01-23T10:00:00Z",
                }
            }

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.return_value = mock_response
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(create_user, input="John Doe\njohn@domain\njohn@example.com\n")

            assert result.exit_code == 0
            assert "Error: Invalid email format" in result.output
            assert "Success: User created successfully!" in result.output

    def test_create_user_valid_email_formats(self, cli_runner):
        """Test various valid email formats are accepted."""
        valid_emails = [
            "user@example.com",
            "user.name@example.com",
            "user+tag@example.co.uk",
            "user_name@example-domain.com",
            "123@example.com",
        ]

        with patch("src.commands.user.APIClient") as mock_api_client:
            for email in valid_emails:
                mock_response = MagicMock()
                mock_response.status_code = 201
                mock_response.data = {
                    "data": {
                        "id": 1,
                        "name": "Test User",
                        "email": email,
                        "created_at": "2026-01-23T10:00:00Z",
                        "updated_at": "2026-01-23T10:00:00Z",
                    }
                }

                mock_client_instance = MagicMock()
                mock_client_instance._make_request.return_value = mock_response
                mock_client_instance.__enter__.return_value = mock_client_instance
                mock_client_instance.__exit__.return_value = False

                mock_api_client.return_value = mock_client_instance

                result = cli_runner.invoke(create_user, input=f"Test User\n{email}\n")

                assert result.exit_code == 0
                assert "Success: User created successfully!" in result.output


class TestCreateUserDuplicate:
    """Test duplicate email error handling."""

    def test_create_user_duplicate_email_409(self, cli_runner):
        """Test handling of duplicate email (409 Conflict)."""
        with patch("src.commands.user.APIClient") as mock_api_client:
            error_response = json.dumps({"message": "Email already exists"})

            mock_client_instance = MagicMock()
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            error = APIClientError4xx(
                "Conflict",
                status_code=409,
                response_body=error_response,
            )
            mock_client_instance._make_request.side_effect = error

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(create_user, input="John Doe\njohn@example.com\n")

            assert result.exit_code == 0
            assert "Email already exists" in result.output
            assert "Please use a different email address" in result.output


class TestCreateUserValidationError:
    """Test validation error (400) handling."""

    def test_create_user_validation_error_400_with_details(self, cli_runner):
        """Test handling of validation error with field-specific details."""
        with patch("src.commands.user.APIClient") as mock_api_client:
            error_response = json.dumps({
                "message": "Validation failed",
                "details": {
                    "errors": [
                        {"loc": ["name"], "msg": "name must not be empty"},
                        {"loc": ["email"], "msg": "invalid email format"},
                    ]
                },
            })

            mock_client_instance = MagicMock()
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            error = APIClientError4xx(
                "Bad Request",
                status_code=400,
                response_body=error_response,
            )
            mock_client_instance._make_request.side_effect = error

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(create_user, input="John\ninvalid\njohn@example.com\n")

            assert result.exit_code == 0
            assert "Error: Invalid email format" in result.output
            assert "Invalid input provided" in result.output

    def test_create_user_validation_error_400_without_details(self, cli_runner):
        """Test handling of validation error without field details."""
        with patch("src.commands.user.APIClient") as mock_api_client:
            error_response = json.dumps({"message": "Validation failed"})

            mock_client_instance = MagicMock()
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            error = APIClientError4xx(
                "Bad Request",
                status_code=400,
                response_body=error_response,
            )
            mock_client_instance._make_request.side_effect = error

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(create_user, input="John\ntest@example.com\n")

            assert result.exit_code == 0
            assert "Invalid input provided" in result.output
            assert "Validation failed" in result.output


class TestCreateUserConnectionErrors:
    """Test network/connection error handling."""

    def test_create_user_connection_error(self, cli_runner):
        """Test handling of connection error."""
        with patch("src.commands.user.APIClient") as mock_api_client:
            mock_client_instance = MagicMock()
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            error = APIConnectionError("Failed to connect to API", url="http://api:8000")
            mock_client_instance._make_request.side_effect = error

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(create_user, input="John Doe\njohn@example.com\n")

            assert result.exit_code == 0
            assert "Unable to connect to API" in result.output
            assert "Please ensure the API service is running" in result.output

    def test_create_user_timeout_error(self, cli_runner):
        """Test handling of timeout error."""
        with patch("src.commands.user.APIClient") as mock_api_client:
            mock_client_instance = MagicMock()
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            error = APITimeoutError("Request timed out", url="http://api:8000")
            mock_client_instance._make_request.side_effect = error

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(create_user, input="John Doe\njohn@example.com\n")

            assert result.exit_code == 0
            assert "Unable to connect to API" in result.output
            assert "Please ensure the API service is running" in result.output


class TestCreateUserServerErrors:
    """Test server error (5xx) handling."""

    def test_create_user_server_error_500(self, cli_runner):
        """Test handling of internal server error."""
        with patch("src.commands.user.APIClient") as mock_api_client:
            mock_client_instance = MagicMock()
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            error = APIServerError5xx(
                "Internal Server Error",
                status_code=500,
                response_body="Internal error",
            )
            mock_client_instance._make_request.side_effect = error

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(create_user, input="John Doe\njohn@example.com\n")

            assert result.exit_code == 0
            assert "Server error occurred" in result.output
            assert "Please try again later" in result.output


class TestCreateUserUnexpectedErrors:
    """Test unexpected error handling."""

    def test_create_user_unexpected_error(self, cli_runner):
        """Test handling of unexpected exception."""
        with patch("src.commands.user.APIClient") as mock_api_client:
            mock_client_instance = MagicMock()
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            error = RuntimeError("Something went wrong")
            mock_client_instance._make_request.side_effect = error

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(create_user, input="John Doe\njohn@example.com\n")

            assert result.exit_code == 0
            assert "An unexpected error occurred" in result.output
            assert "Something went wrong" in result.output


class TestCreateUserCommandHelp:
    """Test command help and documentation."""

    def test_create_user_has_proper_docstring(self):
        """Test create-user command has proper docstring."""
        # Verify command has proper docstring
        assert create_user.__doc__
        assert "Create a new user in the system" in create_user.__doc__

    def test_create_user_is_click_command(self):
        """Test create-user is a Click command."""
        # Verify the function is a Click command with the right name
        assert hasattr(create_user, "callback")
        assert create_user.name == "create-user"


class TestCreateUserInputStripping:
    """Test that input is properly trimmed."""

    def test_create_user_trims_whitespace_from_name(self, cli_runner):
        """Test that leading/trailing whitespace is stripped from name."""
        with patch("src.commands.user.APIClient") as mock_api_client:
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.data = {
                "data": {
                    "id": 1,
                    "name": "John Doe",
                    "email": "john@example.com",
                    "created_at": "2026-01-23T10:00:00Z",
                    "updated_at": "2026-01-23T10:00:00Z",
                }
            }

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.return_value = mock_response
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(create_user, input="  John Doe  \njohn@example.com\n")

            assert result.exit_code == 0
            assert "Success: User created successfully!" in result.output

            # Verify the API was called with trimmed name
            call_args = mock_client_instance._make_request.call_args
            assert call_args[1]["data"]["name"] == "John Doe"

    def test_create_user_trims_whitespace_from_email(self, cli_runner):
        """Test that leading/trailing whitespace is stripped from email."""
        with patch("src.commands.user.APIClient") as mock_api_client:
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.data = {
                "data": {
                    "id": 1,
                    "name": "John Doe",
                    "email": "john@example.com",
                    "created_at": "2026-01-23T10:00:00Z",
                    "updated_at": "2026-01-23T10:00:00Z",
                }
            }

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.return_value = mock_response
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(create_user, input="John Doe\n  john@example.com  \n")

            assert result.exit_code == 0
            assert "Success: User created successfully!" in result.output

            # Verify the API was called with trimmed email
            call_args = mock_client_instance._make_request.call_args
            assert call_args[1]["data"]["email"] == "john@example.com"


class TestCreateUserAPICall:
    """Test that API is called correctly."""

    def test_create_user_api_endpoint(self, cli_runner):
        """Test that the correct API endpoint is called."""
        with patch("src.commands.user.APIClient") as mock_api_client:
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.data = {
                "data": {
                    "id": 1,
                    "name": "John Doe",
                    "email": "john@example.com",
                    "created_at": "2026-01-23T10:00:00Z",
                    "updated_at": "2026-01-23T10:00:00Z",
                }
            }

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.return_value = mock_response
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            cli_runner.invoke(create_user, input="John Doe\njohn@example.com\n")

            # Verify the API was called with correct endpoint and method
            mock_client_instance._make_request.assert_called_once()
            call_args = mock_client_instance._make_request.call_args
            assert call_args[0][0] == "POST"  # method
            assert call_args[0][1] == "/users"  # endpoint
            assert call_args[1]["data"]["name"] == "John Doe"
            assert call_args[1]["data"]["email"] == "john@example.com"

    def test_create_user_api_context_manager(self, cli_runner):
        """Test that APIClient is used as context manager."""
        with patch("src.commands.user.APIClient") as mock_api_client:
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.data = {
                "data": {
                    "id": 1,
                    "name": "John Doe",
                    "email": "john@example.com",
                    "created_at": "2026-01-23T10:00:00Z",
                    "updated_at": "2026-01-23T10:00:00Z",
                }
            }

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.return_value = mock_response
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            cli_runner.invoke(create_user, input="John Doe\njohn@example.com\n")

            # Verify context manager was used
            mock_client_instance.__enter__.assert_called_once()
            mock_client_instance.__exit__.assert_called_once()
