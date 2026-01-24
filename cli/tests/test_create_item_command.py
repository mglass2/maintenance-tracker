"""Tests for the create-item command."""

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
from src.commands.item import create_item, _translate_field_name, _convert_value_type


@pytest.fixture
def cli_runner():
    """Provide a Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_item_types():
    """Provide mock item types data."""
    return [
        {
            "id": 1,
            "name": "Car",
            "description": "Automobile",
            "created_at": "2026-01-23T10:00:00Z",
            "updated_at": "2026-01-23T10:00:00Z",
        },
        {
            "id": 2,
            "name": "House",
            "description": "Residential property",
            "created_at": "2026-01-23T10:00:00Z",
            "updated_at": "2026-01-23T10:00:00Z",
        },
    ]


@pytest.fixture
def successful_item_response():
    """Provide a successful item creation response."""
    return {
        "id": 1,
        "user_id": 1,
        "item_type_id": 1,
        "name": "2015 Toyota Camry",
        "description": None,
        "acquired_at": "2015-06-15",
        "details": {"mileage": 45000},
        "created_at": "2026-01-23T12:00:00Z",
        "updated_at": "2026-01-23T12:00:00Z",
    }


class TestCreateItemSuccess:
    """Test successful item creation scenarios."""

    def test_create_item_minimal_required_fields(self, cli_runner, mock_item_types, successful_item_response):
        """Test creating item with minimal required fields."""
        with patch("src.commands.item.APIClient") as mock_api_client:
            # Mock GET /item_types
            types_response = MagicMock()
            types_response.status_code = 200
            types_response.data = {"data": {"item_types": mock_item_types, "count": 2}}

            # Mock POST /items
            create_response = MagicMock()
            create_response.status_code = 201
            create_response.data = {"data": successful_item_response}

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.side_effect = [types_response, create_response]
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            # Invoke: select first item type, enter name, skip date, skip details
            result = cli_runner.invoke(create_item, input="1\n2015 Toyota Camry\n\nno\n")

            assert result.exit_code == 0
            assert "Success: Item created successfully!" in result.output
            assert "2015 Toyota Camry" in result.output

    def test_create_item_with_all_fields(self, cli_runner, mock_item_types, successful_item_response):
        """Test creating item with all fields including details."""
        with patch("src.commands.item.APIClient") as mock_api_client:
            # Mock GET /item_types
            types_response = MagicMock()
            types_response.status_code = 200
            types_response.data = {"data": {"item_types": mock_item_types, "count": 2}}

            # Mock POST /items
            create_response = MagicMock()
            create_response.status_code = 201
            create_response.data = {"data": successful_item_response}

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.side_effect = [types_response, create_response]
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            # Invoke: select first item type, enter name, enter date, add details
            result = cli_runner.invoke(
                create_item,
                input="1\n2015 Toyota Camry\n2015-06-15\nyes\nmileage\n45000\nno\n"
            )

            assert result.exit_code == 0
            assert "Success: Item created successfully!" in result.output
            assert "2015 Toyota Camry" in result.output

    def test_create_item_with_multiple_custom_details(self, cli_runner, mock_item_types):
        """Test creating item with multiple custom detail fields."""
        item_response = {
            "id": 1,
            "user_id": 1,
            "item_type_id": 1,
            "name": "2015 Toyota Camry",
            "description": None,
            "acquired_at": "2015-06-15",
            "details": {"mileage": 45000, "vin": "JTDKBRFH5J5621359"},
            "created_at": "2026-01-23T12:00:00Z",
            "updated_at": "2026-01-23T12:00:00Z",
        }

        with patch("src.commands.item.APIClient") as mock_api_client:
            types_response = MagicMock()
            types_response.status_code = 200
            types_response.data = {"data": {"item_types": mock_item_types, "count": 2}}

            create_response = MagicMock()
            create_response.status_code = 201
            create_response.data = {"data": item_response}

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.side_effect = [types_response, create_response]
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            # Add two custom details
            result = cli_runner.invoke(
                create_item,
                input="1\n2015 Toyota Camry\n2015-06-15\nyes\nmileage\n45000\nyes\nvin\nJTDKBRFH5J5621359\nno\n"
            )

            assert result.exit_code == 0
            assert "Success: Item created successfully!" in result.output


class TestCreateItemFieldTranslation:
    """Test field name translation functionality."""

    def test_translate_mileage_variations(self):
        """Test that mileage variations are translated correctly."""
        assert _translate_field_name("miles") == "mileage"
        assert _translate_field_name("mile") == "mileage"
        assert _translate_field_name("milage") == "mileage"
        assert _translate_field_name("mileage") == "mileage"

    def test_translate_vin_variations(self):
        """Test that VIN variations are translated correctly."""
        assert _translate_field_name("vin") == "vin"
        assert _translate_field_name("vehicle_id") == "vin"
        assert _translate_field_name("vehicle_identification") == "vin"

    def test_translate_serial_number_variations(self):
        """Test that serial number variations are translated correctly."""
        assert _translate_field_name("serial_number") == "serial_number"
        assert _translate_field_name("serial") == "serial_number"
        assert _translate_field_name("serial_no") == "serial_number"
        assert _translate_field_name("sn") == "serial_number"

    def test_translate_purchase_price_variations(self):
        """Test that purchase price variations are translated correctly."""
        assert _translate_field_name("purchase_price") == "purchase_price"
        assert _translate_field_name("price") == "purchase_price"
        assert _translate_field_name("cost") == "purchase_price"
        assert _translate_field_name("purchase_cost") == "purchase_price"

    def test_translate_unknown_field(self):
        """Test that unknown fields are normalized but not translated."""
        assert _translate_field_name("unknown_field") == "unknown_field"
        assert _translate_field_name("custom field") == "custom_field"

    def test_translate_case_insensitive(self):
        """Test that translation is case-insensitive."""
        assert _translate_field_name("MILEAGE") == "mileage"
        assert _translate_field_name("Miles") == "mileage"
        assert _translate_field_name("VIN") == "vin"


class TestCreateItemValueConversion:
    """Test value type conversion functionality."""

    def test_convert_value_to_int(self):
        """Test converting string to integer."""
        assert _convert_value_type("42") == 42
        assert _convert_value_type("0") == 0
        assert isinstance(_convert_value_type("100"), int)

    def test_convert_value_to_float(self):
        """Test converting string to float."""
        assert _convert_value_type("3.14") == 3.14
        assert _convert_value_type("0.5") == 0.5
        assert isinstance(_convert_value_type("99.99"), float)

    def test_convert_value_to_string(self):
        """Test that non-numeric strings remain strings."""
        assert _convert_value_type("hello") == "hello"
        assert _convert_value_type("abc123") == "abc123"
        assert isinstance(_convert_value_type("mixed"), str)

    def test_convert_int_vs_float_priority(self):
        """Test that integers are tried before floats."""
        assert isinstance(_convert_value_type("42"), int)
        assert isinstance(_convert_value_type("42.5"), float)


class TestCreateItemValidation:
    """Test input validation."""

    def test_create_item_empty_name_repromt(self, cli_runner, mock_item_types, successful_item_response):
        """Test that empty name is rejected and user is re-prompted."""
        with patch("src.commands.item.APIClient") as mock_api_client:
            types_response = MagicMock()
            types_response.status_code = 200
            types_response.data = {"data": {"item_types": mock_item_types, "count": 2}}

            create_response = MagicMock()
            create_response.status_code = 201
            create_response.data = {"data": successful_item_response}

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.side_effect = [types_response, create_response]
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            # Try empty name, then provide valid name
            result = cli_runner.invoke(create_item, input="1\n\n2015 Toyota Camry\n\nno\n")

            assert result.exit_code == 0
            assert "Error: Name cannot be empty" in result.output
            assert "Success: Item created successfully!" in result.output

    def test_create_item_name_too_long(self, cli_runner, mock_item_types, successful_item_response):
        """Test that name exceeding 255 characters is rejected and user is re-prompted."""
        with patch("src.commands.item.APIClient") as mock_api_client:
            long_name = "a" * 256
            types_response = MagicMock()
            types_response.status_code = 200
            types_response.data = {"data": {"item_types": mock_item_types, "count": 2}}

            create_response = MagicMock()
            create_response.status_code = 201
            create_response.data = {"data": successful_item_response}

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.side_effect = [types_response, create_response]
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(create_item, input=f"1\n{long_name}\n2015 Toyota Camry\n\nno\n")

            assert result.exit_code == 0
            assert "Error: Name must be 255 characters or less" in result.output
            assert "Success: Item created successfully!" in result.output

    def test_create_item_invalid_item_type_selection(self, cli_runner, mock_item_types):
        """Test that invalid item type selection is rejected."""
        with patch("src.commands.item.APIClient") as mock_api_client:
            types_response = MagicMock()
            types_response.status_code = 200
            types_response.data = {"data": {"item_types": mock_item_types, "count": 2}}

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.return_value = types_response
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            # Try invalid selection, then valid
            result = cli_runner.invoke(create_item, input="99\n1\nTest Item\n\nno\n")

            assert "Error: Please enter a number between 1 and 2" in result.output

    def test_create_item_invalid_date_format(self, cli_runner, mock_item_types, successful_item_response):
        """Test that invalid date format is rejected and user is re-prompted."""
        with patch("src.commands.item.APIClient") as mock_api_client:
            types_response = MagicMock()
            types_response.status_code = 200
            types_response.data = {"data": {"item_types": mock_item_types, "count": 2}}

            create_response = MagicMock()
            create_response.status_code = 201
            create_response.data = {"data": successful_item_response}

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.side_effect = [types_response, create_response]
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            # Try invalid date, then valid date
            result = cli_runner.invoke(
                create_item,
                input="1\n2015 Toyota Camry\n06/15/2015\n2015-06-15\nno\n"
            )

            assert result.exit_code == 0
            assert "Error: Invalid date format" in result.output
            assert "Success: Item created successfully!" in result.output


class TestCreateItemAPIErrors:
    """Test API error handling."""

    def test_create_item_not_found_error(self, cli_runner, mock_item_types):
        """Test handling of 404 Not Found error."""
        with patch("src.commands.item.APIClient") as mock_api_client:
            types_response = MagicMock()
            types_response.status_code = 200
            types_response.data = {"data": {"item_types": mock_item_types, "count": 2}}

            error_response = json.dumps({"message": "Item type not found"})

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.side_effect = [
                types_response,
                APIClientError4xx("Not Found", status_code=404, response_body=error_response),
            ]
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(create_item, input="1\nTest Item\n\nno\n")

            assert result.exit_code == 0
            assert "Item type not found" in result.output

    def test_create_item_validation_error_400(self, cli_runner, mock_item_types):
        """Test handling of 400 Bad Request error."""
        with patch("src.commands.item.APIClient") as mock_api_client:
            types_response = MagicMock()
            types_response.status_code = 200
            types_response.data = {"data": {"item_types": mock_item_types, "count": 2}}

            error_response = json.dumps({
                "message": "Validation failed",
                "details": {
                    "errors": [
                        {"loc": ["name"], "msg": "name must not be empty"},
                    ]
                },
            })

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.side_effect = [
                types_response,
                APIClientError4xx("Bad Request", status_code=400, response_body=error_response),
            ]
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(create_item, input="1\nTest Item\n\nno\n")

            assert result.exit_code == 0
            assert "Invalid input provided" in result.output
            assert "name" in result.output.lower()

    def test_create_item_connection_error(self, cli_runner):
        """Test handling of connection error."""
        with patch("src.commands.item.APIClient") as mock_api_client:
            mock_client_instance = MagicMock()
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            error = APIConnectionError("Failed to connect", url="http://api:8000")
            mock_client_instance._make_request.side_effect = error

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(create_item, input="")

            assert result.exit_code == 0
            assert "Unable to connect to API" in result.output

    def test_create_item_timeout_error(self, cli_runner):
        """Test handling of timeout error."""
        with patch("src.commands.item.APIClient") as mock_api_client:
            mock_client_instance = MagicMock()
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            error = APITimeoutError("Request timed out", url="http://api:8000")
            mock_client_instance._make_request.side_effect = error

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(create_item, input="")

            assert result.exit_code == 0
            assert "Unable to connect to API" in result.output

    def test_create_item_server_error_500(self, cli_runner):
        """Test handling of 500 Internal Server Error."""
        with patch("src.commands.item.APIClient") as mock_api_client:
            mock_client_instance = MagicMock()
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            error = APIServerError5xx("Internal Server Error", status_code=500, response_body="Error")
            mock_client_instance._make_request.side_effect = error

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(create_item, input="")

            assert result.exit_code == 0
            assert "Server error occurred" in result.output

    def test_create_item_no_item_types_available(self, cli_runner):
        """Test handling when no item types are available."""
        with patch("src.commands.item.APIClient") as mock_api_client:
            types_response = MagicMock()
            types_response.status_code = 200
            types_response.data = {"data": {"item_types": [], "count": 0}}

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.return_value = types_response
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(create_item, input="")

            assert result.exit_code == 0
            assert "No item types available" in result.output

    def test_create_item_fetch_types_error(self, cli_runner):
        """Test error when fetching item types."""
        with patch("src.commands.item.APIClient") as mock_api_client:
            mock_client_instance = MagicMock()
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            error = APIConnectionError("Failed to connect", url="http://api:8000")
            mock_client_instance._make_request.side_effect = error

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(create_item, input="")

            assert result.exit_code == 0
            assert "Unable to connect to API" in result.output


class TestCreateItemCommandMetadata:
    """Test command metadata and help."""

    def test_create_item_has_proper_docstring(self):
        """Test create-item command has proper docstring."""
        assert create_item.__doc__
        assert "Create a new item in the system" in create_item.__doc__

    def test_create_item_is_click_command(self):
        """Test create-item is a Click command with proper name."""
        assert hasattr(create_item, "callback")
        assert create_item.name == "create-item"


class TestCreateItemFieldDisplay:
    """Test that field details are properly displayed."""

    def test_create_item_displays_item_type_with_description(self, cli_runner, mock_item_types):
        """Test that item types are displayed with descriptions."""
        with patch("src.commands.item.APIClient") as mock_api_client:
            types_response = MagicMock()
            types_response.status_code = 200
            types_response.data = {"data": {"item_types": mock_item_types, "count": 2}}

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.return_value = types_response
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(create_item, input="")

            assert "Available Item Types:" in result.output
            assert "Car" in result.output
            assert "Automobile" in result.output

    def test_create_item_displays_success_with_all_fields(self, cli_runner, mock_item_types):
        """Test success message displays all item fields."""
        full_response = {
            "id": 42,
            "user_id": 1,
            "item_type_id": 1,
            "name": "2015 Toyota Camry",
            "description": None,
            "acquired_at": "2015-06-15",
            "details": {"mileage": 45000, "vin": "JTDKBRFH5J5621359"},
            "created_at": "2026-01-23T12:00:00Z",
            "updated_at": "2026-01-23T12:00:00Z",
        }

        with patch("src.commands.item.APIClient") as mock_api_client:
            types_response = MagicMock()
            types_response.status_code = 200
            types_response.data = {"data": {"item_types": mock_item_types, "count": 2}}

            create_response = MagicMock()
            create_response.status_code = 201
            create_response.data = {"data": full_response}

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.side_effect = [types_response, create_response]
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(create_item, input="1\n2015 Toyota Camry\n2015-06-15\nyes\nmileage\n45000\nno\n")

            assert "ID:          42" in result.output
            assert "Name:        2015 Toyota Camry" in result.output
            assert "Item Type:   1" in result.output
            assert "Acquired:    2015-06-15" in result.output
