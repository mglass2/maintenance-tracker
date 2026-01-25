"""Tests for the show-task-types command."""

from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from src.api_client import (
    APIConnectionError,
    APIServerError5xx,
    APITimeoutError,
)
from src.commands.show_task_types import show_task_types


@pytest.fixture
def cli_runner():
    """Provide a Click CLI test runner."""
    return CliRunner()


class TestShowTaskTypesCommand:
    """Tests for show-task-types command."""

    def test_show_task_types_empty_database(self, cli_runner):
        """Test displaying when no templates exist."""
        with patch("src.commands.show_task_types.APIClient") as mock_api_client:
            response = MagicMock()
            response.status_code = 200
            response.data = {
                "data": {
                    "item_types": [],
                },
                "message": "Retrieved all maintenance templates",
            }

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.return_value = response
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(show_task_types)

            assert result.exit_code == 0
            assert "No maintenance templates configured yet" in result.output

    def test_show_task_types_single_item_type(self, cli_runner):
        """Test displaying a single item type with templates."""
        with patch("src.commands.show_task_types.APIClient") as mock_api_client:
            response = MagicMock()
            response.status_code = 200
            response.data = {
                "data": {
                    "item_types": [
                        {
                            "item_type_id": 1,
                            "item_type_name": "Car",
                            "templates": [
                                {
                                    "task_type_id": 1,
                                    "task_type_name": "Oil Change",
                                    "time_interval_days": 30,
                                    "custom_interval": None,
                                }
                            ],
                        }
                    ],
                },
                "message": "Retrieved all maintenance templates",
            }

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.return_value = response
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(show_task_types)

            assert result.exit_code == 0
            assert "Car:" in result.output
            assert "Oil Change - 30 days" in result.output
            assert "Maintenance Task Types by Item Type:" in result.output

    def test_show_task_types_multiple_item_types(self, cli_runner):
        """Test displaying multiple item types."""
        with patch("src.commands.show_task_types.APIClient") as mock_api_client:
            response = MagicMock()
            response.status_code = 200
            response.data = {
                "data": {
                    "item_types": [
                        {
                            "item_type_id": 1,
                            "item_type_name": "Car",
                            "templates": [
                                {
                                    "task_type_id": 1,
                                    "task_type_name": "Oil Change",
                                    "time_interval_days": 30,
                                    "custom_interval": None,
                                }
                            ],
                        },
                        {
                            "item_type_id": 2,
                            "item_type_name": "House",
                            "templates": [
                                {
                                    "task_type_id": 2,
                                    "task_type_name": "Roof Inspection",
                                    "time_interval_days": 365,
                                    "custom_interval": None,
                                }
                            ],
                        },
                    ],
                },
                "message": "Retrieved all maintenance templates",
            }

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.return_value = response
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(show_task_types)

            assert result.exit_code == 0
            assert "Car:" in result.output
            assert "House:" in result.output
            assert "Oil Change - 30 days" in result.output
            assert "Roof Inspection - 365 days" in result.output

    def test_show_task_types_multiple_templates_per_item_type(self, cli_runner):
        """Test displaying item type with multiple templates."""
        with patch("src.commands.show_task_types.APIClient") as mock_api_client:
            response = MagicMock()
            response.status_code = 200
            response.data = {
                "data": {
                    "item_types": [
                        {
                            "item_type_id": 1,
                            "item_type_name": "Car",
                            "templates": [
                                {
                                    "task_type_id": 1,
                                    "task_type_name": "Oil Change",
                                    "time_interval_days": 30,
                                    "custom_interval": None,
                                },
                                {
                                    "task_type_id": 2,
                                    "task_type_name": "Tire Rotation",
                                    "time_interval_days": 90,
                                    "custom_interval": None,
                                },
                                {
                                    "task_type_id": 3,
                                    "task_type_name": "Brake Inspection",
                                    "time_interval_days": 180,
                                    "custom_interval": None,
                                },
                            ],
                        }
                    ],
                },
                "message": "Retrieved all maintenance templates",
            }

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.return_value = response
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(show_task_types)

            assert result.exit_code == 0
            assert "Car:" in result.output
            assert "Oil Change - 30 days" in result.output
            assert "Tire Rotation - 90 days" in result.output
            assert "Brake Inspection - 180 days" in result.output

    def test_show_task_types_with_custom_interval(self, cli_runner):
        """Test displaying custom_interval in output."""
        with patch("src.commands.show_task_types.APIClient") as mock_api_client:
            response = MagicMock()
            response.status_code = 200
            response.data = {
                "data": {
                    "item_types": [
                        {
                            "item_type_id": 1,
                            "item_type_name": "Car",
                            "templates": [
                                {
                                    "task_type_id": 1,
                                    "task_type_name": "Tire Rotation",
                                    "time_interval_days": 90,
                                    "custom_interval": {"type": "mileage", "value": 5000},
                                }
                            ],
                        }
                    ],
                },
                "message": "Retrieved all maintenance templates",
            }

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.return_value = response
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(show_task_types)

            assert result.exit_code == 0
            assert "Tire Rotation - 90 days" in result.output
            assert "{'type': 'mileage', 'value': 5000}" in result.output

    def test_show_task_types_api_connection_error(self, cli_runner):
        """Test handling of API connection error."""
        with patch("src.commands.show_task_types.APIClient") as mock_api_client:
            mock_client_instance = MagicMock()
            mock_client_instance.__enter__.side_effect = APIConnectionError(
                "Connection failed"
            )

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(show_task_types)

            assert result.exit_code == 0
            assert "Unable to connect to API" in result.output
            assert "API service is running" in result.output

    def test_show_task_types_api_timeout_error(self, cli_runner):
        """Test handling of API timeout error."""
        with patch("src.commands.show_task_types.APIClient") as mock_api_client:
            mock_client_instance = MagicMock()
            mock_client_instance.__enter__.side_effect = APITimeoutError(
                "Request timed out"
            )

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(show_task_types)

            assert result.exit_code == 0
            assert "Unable to connect to API" in result.output

    def test_show_task_types_server_error_5xx(self, cli_runner):
        """Test handling of server error."""
        with patch("src.commands.show_task_types.APIClient") as mock_api_client:
            mock_client_instance = MagicMock()
            mock_client_instance.__enter__.side_effect = APIServerError5xx(
                "Server error", 500, ""
            )

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(show_task_types)

            assert result.exit_code == 0
            assert "Server error occurred" in result.output
            assert "try again later" in result.output

    def test_show_task_types_unexpected_error(self, cli_runner):
        """Test handling of unexpected error."""
        with patch("src.commands.show_task_types.APIClient") as mock_api_client:
            mock_client_instance = MagicMock()
            mock_client_instance.__enter__.side_effect = Exception("Unexpected error")

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(show_task_types)

            assert result.exit_code == 0
            assert "unexpected error occurred" in result.output

    def test_show_task_types_bad_status_code(self, cli_runner):
        """Test handling of bad status code."""
        with patch("src.commands.show_task_types.APIClient") as mock_api_client:
            response = MagicMock()
            response.status_code = 500

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.return_value = response
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(show_task_types)

            assert result.exit_code == 0
            assert "Unable to fetch maintenance templates" in result.output
