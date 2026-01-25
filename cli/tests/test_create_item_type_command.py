"""Tests for the create-item-type command with item type display feature."""

import json
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from src.api_client import (
    APIClientError4xx,
    APIConnectionError,
    APIServerError5xx,
    APITimeoutError,
)
from src.commands.item_type import create_item_type


@pytest.fixture
def cli_runner():
    """Provide a Click CLI test runner."""
    return CliRunner()


class TestDisplayExistingItemTypes:
    """Test that existing item types are displayed correctly."""

    def test_display_single_item_type_with_description(self, cli_runner):
        """Test displaying a single item type with description."""
        with patch("src.commands.item_type.APIClient") as mock_api_client:
            # Mock the GET request to fetch item types
            get_response = MagicMock()
            get_response.status_code = 200
            get_response.data = {
                "data": {
                    "item_types": [
                        {
                            "id": 1,
                            "name": "Car",
                            "description": "Automobiles and vehicles",
                            "created_at": "2026-01-20T10:00:00Z",
                            "updated_at": "2026-01-20T10:00:00Z",
                        }
                    ],
                    "count": 1,
                },
                "message": "Retrieved 1 item types",
            }

            # Mock the POST request for creating new item type
            post_response = MagicMock()
            post_response.status_code = 201
            post_response.data = {
                "data": {
                    "id": 2,
                    "name": "House",
                    "description": "Residential properties",
                    "created_at": "2026-01-24T10:00:00Z",
                    "updated_at": "2026-01-24T10:00:00Z",
                }
            }

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.side_effect = [get_response, post_response]
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(
                create_item_type,
                input="House\nResidential properties\nno\n",
            )

            assert result.exit_code == 0
            assert "Existing Item Types:" in result.output
            assert "1. Car - Automobiles and vehicles" in result.output
            assert "Success: Item type created successfully!" in result.output

    def test_display_multiple_item_types_with_descriptions(self, cli_runner):
        """Test displaying multiple item types with descriptions."""
        with patch("src.commands.item_type.APIClient") as mock_api_client:
            get_response = MagicMock()
            get_response.status_code = 200
            get_response.data = {
                "data": {
                    "item_types": [
                        {
                            "id": 1,
                            "name": "Car",
                            "description": "Automobiles and vehicles",
                            "created_at": "2026-01-20T10:00:00Z",
                            "updated_at": "2026-01-20T10:00:00Z",
                        },
                        {
                            "id": 2,
                            "name": "House",
                            "description": "Residential properties",
                            "created_at": "2026-01-21T10:00:00Z",
                            "updated_at": "2026-01-21T10:00:00Z",
                        },
                        {
                            "id": 3,
                            "name": "Snowblower",
                            "description": None,
                            "created_at": "2026-01-22T10:00:00Z",
                            "updated_at": "2026-01-22T10:00:00Z",
                        },
                    ],
                    "count": 3,
                },
                "message": "Retrieved 3 item types",
            }

            post_response = MagicMock()
            post_response.status_code = 201
            post_response.data = {
                "data": {
                    "id": 4,
                    "name": "Lawn Mower",
                    "description": "Garden equipment",
                    "created_at": "2026-01-24T10:00:00Z",
                    "updated_at": "2026-01-24T10:00:00Z",
                }
            }

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.side_effect = [get_response, post_response]
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(
                create_item_type,
                input="Lawn Mower\nGarden equipment\nno\n",
            )

            assert result.exit_code == 0
            assert "Existing Item Types:" in result.output
            assert "1. Car - Automobiles and vehicles" in result.output
            assert "2. House - Residential properties" in result.output
            assert "3. Snowblower" in result.output  # No description, should not have dash
            assert "Success: Item type created successfully!" in result.output

    def test_display_item_type_without_description(self, cli_runner):
        """Test displaying item types without descriptions."""
        with patch("src.commands.item_type.APIClient") as mock_api_client:
            get_response = MagicMock()
            get_response.status_code = 200
            get_response.data = {
                "data": {
                    "item_types": [
                        {
                            "id": 1,
                            "name": "Car",
                            "description": None,
                            "created_at": "2026-01-20T10:00:00Z",
                            "updated_at": "2026-01-20T10:00:00Z",
                        }
                    ],
                    "count": 1,
                },
                "message": "Retrieved 1 item types",
            }

            post_response = MagicMock()
            post_response.status_code = 201
            post_response.data = {
                "data": {
                    "id": 2,
                    "name": "House",
                    "description": None,
                    "created_at": "2026-01-24T10:00:00Z",
                    "updated_at": "2026-01-24T10:00:00Z",
                }
            }

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.side_effect = [get_response, post_response]
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(
                create_item_type,
                input="House\n\nno\n",
            )

            assert result.exit_code == 0
            assert "Existing Item Types:" in result.output
            assert "1. Car" in result.output
            assert "Success: Item type created successfully!" in result.output


class TestEmptyItemTypeList:
    """Test behavior when no item types exist yet."""

    def test_create_first_item_type_empty_list(self, cli_runner):
        """Test creating the first item type when list is empty."""
        with patch("src.commands.item_type.APIClient") as mock_api_client:
            get_response = MagicMock()
            get_response.status_code = 200
            get_response.data = {
                "data": {
                    "item_types": [],
                    "count": 0,
                },
                "message": "Retrieved 0 item types",
            }

            post_response = MagicMock()
            post_response.status_code = 201
            post_response.data = {
                "data": {
                    "id": 1,
                    "name": "Car",
                    "description": "First item type",
                    "created_at": "2026-01-24T10:00:00Z",
                    "updated_at": "2026-01-24T10:00:00Z",
                }
            }

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.side_effect = [get_response, post_response]
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(
                create_item_type,
                input="Car\nFirst item type\nno\n",
            )

            assert result.exit_code == 0
            assert "Success: Item type created successfully!" in result.output
            assert "Car" in result.output


class TestFetchItemTypesErrors:
    """Test error handling when fetching existing item types."""

    def test_connection_error_fetching_item_types(self, cli_runner):
        """Test handling of connection error when fetching item types."""
        with patch("src.commands.item_type.APIClient") as mock_api_client:
            mock_client_instance = MagicMock()
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            error = APIConnectionError(
                "Failed to connect to API", url="http://api:8000"
            )
            mock_client_instance._make_request.side_effect = error

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(create_item_type)

            assert result.exit_code == 0
            assert "Unable to connect to API" in result.output
            assert "Please ensure the API service is running" in result.output

    def test_timeout_error_fetching_item_types(self, cli_runner):
        """Test handling of timeout error when fetching item types."""
        with patch("src.commands.item_type.APIClient") as mock_api_client:
            mock_client_instance = MagicMock()
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            error = APITimeoutError("Request timed out", url="http://api:8000")
            mock_client_instance._make_request.side_effect = error

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(create_item_type)

            assert result.exit_code == 0
            assert "Unable to connect to API" in result.output

    def test_server_error_fetching_item_types(self, cli_runner):
        """Test handling of server error when fetching item types."""
        with patch("src.commands.item_type.APIClient") as mock_api_client:
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

            result = cli_runner.invoke(create_item_type)

            assert result.exit_code == 0
            assert "Server error occurred" in result.output
            assert "Please try again later" in result.output

    def test_unexpected_error_fetching_item_types(self, cli_runner):
        """Test handling of unexpected exception when fetching item types."""
        with patch("src.commands.item_type.APIClient") as mock_api_client:
            mock_client_instance = MagicMock()
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            error = RuntimeError("Unexpected error")
            mock_client_instance._make_request.side_effect = error

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(create_item_type)

            assert result.exit_code == 0
            assert "An unexpected error occurred" in result.output
            assert "Unexpected error" in result.output


class TestCreateItemTypeAfterDisplay:
    """Test that item type creation works after displaying the list."""

    def test_create_item_type_with_description_after_display(self, cli_runner):
        """Test creating item type with description after displaying list."""
        with patch("src.commands.item_type.APIClient") as mock_api_client:
            get_response = MagicMock()
            get_response.status_code = 200
            get_response.data = {
                "data": {
                    "item_types": [
                        {
                            "id": 1,
                            "name": "Car",
                            "description": "Automobiles",
                            "created_at": "2026-01-20T10:00:00Z",
                            "updated_at": "2026-01-20T10:00:00Z",
                        }
                    ],
                    "count": 1,
                },
                "message": "Retrieved 1 item types",
            }

            post_response = MagicMock()
            post_response.status_code = 201
            post_response.data = {
                "data": {
                    "id": 2,
                    "name": "House",
                    "description": "Residential property",
                    "created_at": "2026-01-24T10:00:00Z",
                    "updated_at": "2026-01-24T10:00:00Z",
                }
            }

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.side_effect = [get_response, post_response]
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(
                create_item_type,
                input="House\nResidential property\nno\n",
            )

            assert result.exit_code == 0
            assert "1. Car - Automobiles" in result.output
            assert "Success: Item type created successfully!" in result.output
            assert "ID:          2" in result.output
            assert "House" in result.output

    def test_create_item_type_without_description_after_display(self, cli_runner):
        """Test creating item type without description after displaying list."""
        with patch("src.commands.item_type.APIClient") as mock_api_client:
            get_response = MagicMock()
            get_response.status_code = 200
            get_response.data = {
                "data": {
                    "item_types": [
                        {
                            "id": 1,
                            "name": "Car",
                            "description": "Automobiles",
                            "created_at": "2026-01-20T10:00:00Z",
                            "updated_at": "2026-01-20T10:00:00Z",
                        }
                    ],
                    "count": 1,
                },
                "message": "Retrieved 1 item types",
            }

            post_response = MagicMock()
            post_response.status_code = 201
            post_response.data = {
                "data": {
                    "id": 2,
                    "name": "Snowblower",
                    "description": None,
                    "created_at": "2026-01-24T10:00:00Z",
                    "updated_at": "2026-01-24T10:00:00Z",
                }
            }

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.side_effect = [get_response, post_response]
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(
                create_item_type,
                input="Snowblower\n\nno\n",
            )

            assert result.exit_code == 0
            assert "Success: Item type created successfully!" in result.output
            assert "Snowblower" in result.output

    def test_create_duplicate_item_type_after_display(self, cli_runner):
        """Test that duplicate name is rejected even after displaying existing types."""
        with patch("src.commands.item_type.APIClient") as mock_api_client:
            get_response = MagicMock()
            get_response.status_code = 200
            get_response.data = {
                "data": {
                    "item_types": [
                        {
                            "id": 1,
                            "name": "Car",
                            "description": "Automobiles",
                            "created_at": "2026-01-20T10:00:00Z",
                            "updated_at": "2026-01-20T10:00:00Z",
                        }
                    ],
                    "count": 1,
                },
                "message": "Retrieved 1 item types",
            }

            error_response = json.dumps(
                {"message": "Item type with this name already exists"}
            )

            mock_client_instance = MagicMock()
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            error = APIClientError4xx(
                "Conflict",
                status_code=409,
                response_body=error_response,
            )
            mock_client_instance._make_request.side_effect = [get_response, error]

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(
                create_item_type,
                input="Car\nDuplicate\n",
            )

            assert result.exit_code == 0
            assert "Existing Item Types:" in result.output
            assert "1. Car - Automobiles" in result.output
            assert "An item type with this name already exists" in result.output


class TestItemTypeDisplayFormatting:
    """Test the formatting of the item type display."""

    def test_item_types_numbered_correctly(self, cli_runner):
        """Test that item types are numbered starting from 1."""
        with patch("src.commands.item_type.APIClient") as mock_api_client:
            get_response = MagicMock()
            get_response.status_code = 200
            get_response.data = {
                "data": {
                    "item_types": [
                        {
                            "id": 10,
                            "name": "First Type",
                            "description": "Description 1",
                            "created_at": "2026-01-20T10:00:00Z",
                            "updated_at": "2026-01-20T10:00:00Z",
                        },
                        {
                            "id": 20,
                            "name": "Second Type",
                            "description": "Description 2",
                            "created_at": "2026-01-21T10:00:00Z",
                            "updated_at": "2026-01-21T10:00:00Z",
                        },
                        {
                            "id": 30,
                            "name": "Third Type",
                            "description": "Description 3",
                            "created_at": "2026-01-22T10:00:00Z",
                            "updated_at": "2026-01-22T10:00:00Z",
                        },
                    ],
                    "count": 3,
                },
                "message": "Retrieved 3 item types",
            }

            post_response = MagicMock()
            post_response.status_code = 201
            post_response.data = {
                "data": {
                    "id": 40,
                    "name": "New Type",
                    "description": "New description",
                    "created_at": "2026-01-24T10:00:00Z",
                    "updated_at": "2026-01-24T10:00:00Z",
                }
            }

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.side_effect = [get_response, post_response]
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(
                create_item_type,
                input="New Type\nNew description\nno\n",
            )

            assert result.exit_code == 0
            assert "1. First Type - Description 1" in result.output
            assert "2. Second Type - Description 2" in result.output
            assert "3. Third Type - Description 3" in result.output

    def test_missing_description_field_handled(self, cli_runner):
        """Test handling of missing description field in API response."""
        with patch("src.commands.item_type.APIClient") as mock_api_client:
            get_response = MagicMock()
            get_response.status_code = 200
            get_response.data = {
                "data": {
                    "item_types": [
                        {
                            "id": 1,
                            "name": "Car",
                            # description field missing
                            "created_at": "2026-01-20T10:00:00Z",
                            "updated_at": "2026-01-20T10:00:00Z",
                        }
                    ],
                    "count": 1,
                },
                "message": "Retrieved 1 item types",
            }

            post_response = MagicMock()
            post_response.status_code = 201
            post_response.data = {
                "data": {
                    "id": 2,
                    "name": "House",
                    "description": None,
                    "created_at": "2026-01-24T10:00:00Z",
                    "updated_at": "2026-01-24T10:00:00Z",
                }
            }

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.side_effect = [get_response, post_response]
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(
                create_item_type,
                input="House\n\nno\n",
            )

            assert result.exit_code == 0
            assert "1. Car" in result.output


class TestAPICallSequence:
    """Test the sequence of API calls."""

    def test_get_item_types_called_first(self, cli_runner):
        """Test that GET /item_types is called before POST."""
        with patch("src.commands.item_type.APIClient") as mock_api_client:
            get_response = MagicMock()
            get_response.status_code = 200
            get_response.data = {
                "data": {
                    "item_types": [
                        {
                            "id": 1,
                            "name": "Car",
                            "description": "Automobiles",
                            "created_at": "2026-01-20T10:00:00Z",
                            "updated_at": "2026-01-20T10:00:00Z",
                        }
                    ],
                    "count": 1,
                },
                "message": "Retrieved 1 item types",
            }

            post_response = MagicMock()
            post_response.status_code = 201
            post_response.data = {
                "data": {
                    "id": 2,
                    "name": "House",
                    "description": None,
                    "created_at": "2026-01-24T10:00:00Z",
                    "updated_at": "2026-01-24T10:00:00Z",
                }
            }

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.side_effect = [get_response, post_response]
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            cli_runner.invoke(
                create_item_type,
                input="House\n\nno\n",
            )

            # Verify the sequence of API calls
            calls = mock_client_instance._make_request.call_args_list
            assert len(calls) >= 2
            assert calls[0][0][0] == "GET"  # First call is GET
            assert calls[0][0][1] == "/item_types"
            assert calls[1][0][0] == "POST"  # Second call is POST
            assert calls[1][0][1] == "/item_types"
