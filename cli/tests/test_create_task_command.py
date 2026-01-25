"""Tests for the create-task command."""

import json
from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from src.api_client import (
    APIClientError4xx,
    APIConnectionError,
    APIServerError5xx,
    APITimeoutError,
)
from src.commands.task import create_task, _convert_value_type


@pytest.fixture
def cli_runner():
    """Provide a Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_items():
    """Provide mock items data."""
    return [
        {
            "id": 1,
            "name": "2015 Honda Accord",
            "item_type_name": "Automobile",
        },
        {
            "id": 2,
            "name": "Main Residence",
            "item_type_name": "House",
        },
    ]


@pytest.fixture
def mock_task_types():
    """Provide mock task types data."""
    return [
        {
            "id": 1,
            "name": "Oil Change",
            "description": "Replace engine oil and oil filter",
        },
        {
            "id": 2,
            "name": "Air Filter Replacement",
            "description": "Replace air filter element",
        },
    ]


@pytest.fixture
def mock_maintenance_plans():
    """Provide mock maintenance plans data."""
    return [
        {
            "id": 1,
            "task_type_id": 1,
            "item_id": 1,
            "custom_interval": {"mileage": 0, "oil_type": ""},
        },
        {
            "id": 2,
            "task_type_id": 2,
            "item_id": 1,
            "custom_interval": None,
        },
    ]


@pytest.fixture
def successful_task_response():
    """Provide a successful task creation response."""
    return {
        "id": 23,
        "item_id": 1,
        "task_type_id": 1,
        "completed_at": "2026-01-24",
        "notes": "Changed oil at 75,000 miles",
        "cost": "45.00",
        "details": {"mileage": 75000, "oil_type": "5W-30 Synthetic"},
        "created_at": "2026-01-24T15:30:00Z",
        "updated_at": "2026-01-24T15:30:00Z",
    }


class TestConvertValueType:
    """Tests for _convert_value_type helper function."""

    def test_convert_string_to_int(self):
        """Test converting string to int."""
        result = _convert_value_type("123")
        assert result == 123
        assert isinstance(result, int)

    def test_convert_string_to_float(self):
        """Test converting string to float."""
        result = _convert_value_type("123.45")
        assert result == 123.45
        assert isinstance(result, float)

    def test_convert_string_to_string(self):
        """Test string that can't be converted stays string."""
        result = _convert_value_type("hello")
        assert result == "hello"
        assert isinstance(result, str)

    def test_convert_negative_int(self):
        """Test converting negative integer string."""
        result = _convert_value_type("-123")
        assert result == -123
        assert isinstance(result, int)

    def test_convert_negative_float(self):
        """Test converting negative float string."""
        result = _convert_value_type("-123.45")
        assert result == -123.45
        assert isinstance(result, float)

    def test_convert_zero(self):
        """Test converting zero."""
        result = _convert_value_type("0")
        assert result == 0
        assert isinstance(result, int)

    def test_convert_leading_zeros(self):
        """Test converting string with leading zeros."""
        result = _convert_value_type("00123")
        assert result == 123
        assert isinstance(result, int)


class TestCreateTaskSuccess:
    """Test successful task creation scenarios."""

    def test_create_task_from_existing_plan_with_custom_interval(
        self, cli_runner, mock_items, mock_task_types, mock_maintenance_plans, successful_task_response
    ):
        """Test creating task from existing plan with custom interval fields."""
        with patch("src.commands.task.APIClient") as mock_api_client:
            # Mock responses
            items_response = MagicMock()
            items_response.status_code = 200
            items_response.data = {"data": {"items": mock_items}}

            plans_response = MagicMock()
            plans_response.status_code = 200
            plans_response.data = {"data": mock_maintenance_plans}

            types_response = MagicMock()
            types_response.status_code = 200
            types_response.data = {"data": {"task_types": mock_task_types}}

            create_response = MagicMock()
            create_response.status_code = 201
            create_response.data = {"data": successful_task_response}

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.side_effect = [
                items_response,
                plans_response,
                types_response,
                create_response,
            ]
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            # Mock authenticated user
            with patch("src.commands.task.get_active_user_id", return_value=1):
                result = cli_runner.invoke(
                    create_task,
                    input="1\n1\n\n\n\n75000\n5W-30 Synthetic\n"
                )

            assert result.exit_code == 0
            assert "Success: Task created successfully!" in result.output
            assert "ID:           23" in result.output
            assert "Item:         2015 Honda Accord" in result.output
            assert "Task Type:    Oil Change" in result.output

    def test_create_task_with_all_fields(
        self, cli_runner, mock_items, mock_task_types, mock_maintenance_plans, successful_task_response
    ):
        """Test creating task with all optional fields."""
        with patch("src.commands.task.APIClient") as mock_api_client:
            items_response = MagicMock()
            items_response.status_code = 200
            items_response.data = {"data": {"items": mock_items}}

            plans_response = MagicMock()
            plans_response.status_code = 200
            plans_response.data = {"data": mock_maintenance_plans}

            types_response = MagicMock()
            types_response.status_code = 200
            types_response.data = {"data": {"task_types": mock_task_types}}

            create_response = MagicMock()
            create_response.status_code = 201
            create_response.data = {"data": successful_task_response}

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.side_effect = [
                items_response,
                plans_response,
                types_response,
                create_response,
            ]
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            with patch("src.commands.task.get_active_user_id", return_value=1):
                result = cli_runner.invoke(
                    create_task,
                    input="1\n1\n2026-01-24\nChanged oil\n45.00\n75000\n5W-30 Synthetic\n"
                )

            assert result.exit_code == 0
            assert "Success: Task created successfully!" in result.output
            assert "Notes:        Changed oil" in result.output
            assert "Cost:         $45.00" in result.output

    def test_create_task_without_optional_fields(
        self, cli_runner, mock_items, mock_task_types, successful_task_response
    ):
        """Test creating task with minimal fields."""
        minimal_response = {
            "id": 24,
            "item_id": 1,
            "task_type_id": 2,
            "completed_at": "2026-01-24",
            "notes": None,
            "cost": None,
            "details": None,
            "created_at": "2026-01-24T15:35:00Z",
            "updated_at": "2026-01-24T15:35:00Z",
        }

        with patch("src.commands.task.APIClient") as mock_api_client:
            items_response = MagicMock()
            items_response.status_code = 200
            items_response.data = {"data": {"items": mock_items}}

            plans_response = MagicMock()
            plans_response.status_code = 200
            plans_response.data = {"data": []}  # No plans

            types_response = MagicMock()
            types_response.status_code = 200
            types_response.data = {"data": {"task_types": mock_task_types}}

            create_response = MagicMock()
            create_response.status_code = 201
            create_response.data = {"data": minimal_response}

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.side_effect = [
                items_response,
                plans_response,
                types_response,
                create_response,
            ]
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            with patch("src.commands.task.get_active_user_id", return_value=1):
                result = cli_runner.invoke(
                    create_task,
                    input="1\n2\n\n\n\n"
                )

            assert result.exit_code == 0
            assert "Success: Task created successfully!" in result.output
            assert "Task Type:    Air Filter Replacement" in result.output

    def test_create_task_with_new_task_type(
        self, cli_runner, mock_items, successful_task_response
    ):
        """Test creating task with 'Other' option (new task type)."""
        new_task_type_response = {
            "id": 99,
            "name": "Tire Rotation",
            "description": "Rotate tires to ensure even wear",
            "created_at": "2026-01-24T15:20:00Z",
            "updated_at": "2026-01-24T15:20:00Z",
        }

        task_with_new_type = {
            "id": 25,
            "item_id": 1,
            "task_type_id": 99,
            "completed_at": "2026-01-24",
            "notes": None,
            "cost": None,
            "details": None,
            "created_at": "2026-01-24T15:22:00Z",
            "updated_at": "2026-01-24T15:22:00Z",
        }

        with patch("src.commands.task.APIClient") as mock_api_client:
            items_response = MagicMock()
            items_response.status_code = 200
            items_response.data = {"data": {"items": mock_items}}

            plans_response = MagicMock()
            plans_response.status_code = 200
            plans_response.data = {"data": []}  # No plans

            types_response = MagicMock()
            types_response.status_code = 200
            types_response.data = {"data": {"task_types": []}}  # No existing types

            create_type_response = MagicMock()
            create_type_response.status_code = 201
            create_type_response.data = {"data": new_task_type_response}

            create_response = MagicMock()
            create_response.status_code = 201
            create_response.data = {"data": task_with_new_type}

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.side_effect = [
                items_response,
                plans_response,
                types_response,
                create_type_response,
                create_response,
            ]
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            with patch("src.commands.task.get_active_user_id", return_value=1):
                result = cli_runner.invoke(
                    create_task,
                    input="1\n1\nTire Rotation\nRotate tires\n\n\n\n"
                )

            assert result.exit_code == 0
            assert "Task type 'Tire Rotation' created successfully" in result.output
            assert "Success: Task created successfully!" in result.output


class TestCreateTaskErrors:
    """Test error scenarios in task creation."""

    def test_create_task_no_authenticated_user(self, cli_runner):
        """Test error when no user is authenticated."""
        with patch("src.commands.task.get_active_user_id", return_value=None):
            result = cli_runner.invoke(create_task)

        assert result.exit_code == 0  # CLI handles gracefully
        assert "No user is currently selected" in result.output
        assert "select-user" in result.output

    def test_create_task_no_items_available(self, cli_runner):
        """Test error when user has no items."""
        with patch("src.commands.task.APIClient") as mock_api_client:
            items_response = MagicMock()
            items_response.status_code = 200
            items_response.data = {"data": {"items": []}}

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.return_value = items_response
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            with patch("src.commands.task.get_active_user_id", return_value=1):
                result = cli_runner.invoke(create_task)

        assert result.exit_code == 0
        assert "don't have any items yet" in result.output
        assert "create-item" in result.output

    def test_create_task_connection_error(self, cli_runner):
        """Test error handling for connection failure."""
        with patch("src.commands.task.APIClient") as mock_api_client:
            mock_client_instance = MagicMock()
            mock_client_instance._make_request.side_effect = APIConnectionError(
                "Failed to connect"
            )
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            with patch("src.commands.task.get_active_user_id", return_value=1):
                result = cli_runner.invoke(create_task)

        assert result.exit_code == 0
        assert "Unable to connect to API" in result.output

    def test_create_task_invalid_item_selection(self, cli_runner, mock_items):
        """Test error handling for invalid item selection."""
        with patch("src.commands.task.APIClient") as mock_api_client:
            items_response = MagicMock()
            items_response.status_code = 200
            items_response.data = {"data": {"items": mock_items}}

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.return_value = items_response
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            with patch("src.commands.task.get_active_user_id", return_value=1):
                result = cli_runner.invoke(
                    create_task,
                    input="invalid\n1\n"  # Invalid input, then valid
                )

        # Should reprompt and handle gracefully
        assert "Error: Please enter a valid number" in result.output or "Error" in result.output

    def test_create_task_invalid_date_format(
        self, cli_runner, mock_items, mock_task_types, mock_maintenance_plans
    ):
        """Test error handling for invalid date format."""
        with patch("src.commands.task.APIClient") as mock_api_client:
            items_response = MagicMock()
            items_response.status_code = 200
            items_response.data = {"data": {"items": mock_items}}

            plans_response = MagicMock()
            plans_response.status_code = 200
            plans_response.data = {"data": mock_maintenance_plans}

            types_response = MagicMock()
            types_response.status_code = 200
            types_response.data = {"data": {"task_types": mock_task_types}}

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.side_effect = [
                items_response,
                plans_response,
                types_response,
            ]
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            with patch("src.commands.task.get_active_user_id", return_value=1):
                result = cli_runner.invoke(
                    create_task,
                    input="1\n1\n01/24/2026\n2026-01-24\n\n\n\n75000\n5W-30\n"
                )

        assert "Invalid date format" in result.output
        assert "yyyy-mm-dd" in result.output

    def test_create_task_invalid_cost(
        self, cli_runner, mock_items, mock_task_types, mock_maintenance_plans
    ):
        """Test error handling for invalid cost value."""
        with patch("src.commands.task.APIClient") as mock_api_client:
            items_response = MagicMock()
            items_response.status_code = 200
            items_response.data = {"data": {"items": mock_items}}

            plans_response = MagicMock()
            plans_response.status_code = 200
            plans_response.data = {"data": mock_maintenance_plans}

            types_response = MagicMock()
            types_response.status_code = 200
            types_response.data = {"data": {"task_types": mock_task_types}}

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.side_effect = [
                items_response,
                plans_response,
                types_response,
            ]
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            with patch("src.commands.task.get_active_user_id", return_value=1):
                result = cli_runner.invoke(
                    create_task,
                    input="1\n1\n\n\nnotanumber\n45.00\n\n75000\n5W-30\n"
                )

        assert "Please enter a valid number" in result.output

    def test_create_task_negative_cost(
        self, cli_runner, mock_items, mock_task_types, mock_maintenance_plans
    ):
        """Test error handling for negative cost."""
        with patch("src.commands.task.APIClient") as mock_api_client:
            items_response = MagicMock()
            items_response.status_code = 200
            items_response.data = {"data": {"items": mock_items}}

            plans_response = MagicMock()
            plans_response.status_code = 200
            plans_response.data = {"data": mock_maintenance_plans}

            types_response = MagicMock()
            types_response.status_code = 200
            types_response.data = {"data": {"task_types": mock_task_types}}

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.side_effect = [
                items_response,
                plans_response,
                types_response,
            ]
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            with patch("src.commands.task.get_active_user_id", return_value=1):
                result = cli_runner.invoke(
                    create_task,
                    input="1\n1\n\n\n-10\n45.00\n\n75000\n5W-30\n"
                )

        assert "Cost cannot be negative" in result.output

    def test_create_task_api_error_response(
        self, cli_runner, mock_items, mock_task_types, mock_maintenance_plans
    ):
        """Test error handling for API error response."""
        with patch("src.commands.task.APIClient") as mock_api_client:
            items_response = MagicMock()
            items_response.status_code = 200
            items_response.data = {"data": {"items": mock_items}}

            plans_response = MagicMock()
            plans_response.status_code = 200
            plans_response.data = {"data": mock_maintenance_plans}

            types_response = MagicMock()
            types_response.status_code = 200
            types_response.data = {"data": {"task_types": mock_task_types}}

            error_response = APIClientError4xx(
                "Invalid request",
                status_code=400,
                response_body='{"message": "Invalid input"}',
            )

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.side_effect = [
                items_response,
                plans_response,
                types_response,
                error_response,
            ]
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            with patch("src.commands.task.get_active_user_id", return_value=1):
                result = cli_runner.invoke(
                    create_task,
                    input="1\n1\n\n\n\n\n75000\n5W-30\n"
                )

        # Should handle error gracefully
        assert "Error" in result.output or "error" in result.output.lower()

    def test_create_task_timeout_error(self, cli_runner):
        """Test error handling for API timeout."""
        with patch("src.commands.task.APIClient") as mock_api_client:
            mock_client_instance = MagicMock()
            mock_client_instance._make_request.side_effect = APITimeoutError(
                "Request timed out"
            )
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            with patch("src.commands.task.get_active_user_id", return_value=1):
                result = cli_runner.invoke(create_task)

        assert result.exit_code == 0
        assert "Unable to connect to API" in result.output

    def test_create_task_server_error(self, cli_runner):
        """Test error handling for server error."""
        with patch("src.commands.task.APIClient") as mock_api_client:
            mock_client_instance = MagicMock()
            mock_client_instance._make_request.side_effect = APIServerError5xx(
                "Server error",
                status_code=500,
                response_body="Internal server error",
            )
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            with patch("src.commands.task.get_active_user_id", return_value=1):
                result = cli_runner.invoke(create_task)

        assert result.exit_code == 0
        assert "Server error" in result.output

    def test_create_task_missing_custom_interval_field(
        self, cli_runner, mock_items, mock_task_types, mock_maintenance_plans
    ):
        """Test error when required custom interval field is missing."""
        with patch("src.commands.task.APIClient") as mock_api_client:
            items_response = MagicMock()
            items_response.status_code = 200
            items_response.data = {"data": {"items": mock_items}}

            plans_response = MagicMock()
            plans_response.status_code = 200
            plans_response.data = {"data": mock_maintenance_plans}

            types_response = MagicMock()
            types_response.status_code = 200
            types_response.data = {"data": {"task_types": mock_task_types}}

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.side_effect = [
                items_response,
                plans_response,
                types_response,
            ]
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            with patch("src.commands.task.get_active_user_id", return_value=1):
                result = cli_runner.invoke(
                    create_task,
                    input="1\n1\n\n\n\n\n5W-30\n"  # Missing mileage
                )

        # Should reprompt for mileage
        assert "Error" in result.output or "required" in result.output.lower()


class TestCreateNewTaskTypeHelper:
    """Tests for _create_new_task_type helper function (called from create_task)."""

    def test_new_task_type_created_successfully_in_task_flow(
        self, cli_runner, mock_items
    ):
        """Test that new task type is created successfully within task creation flow."""
        new_task_type_response = {
            "id": 99,
            "name": "Tire Rotation",
            "description": "Rotate tires",
            "created_at": "2026-01-24T10:00:00Z",
            "updated_at": "2026-01-24T10:00:00Z",
        }

        task_response = {
            "id": 25,
            "item_id": 1,
            "task_type_id": 99,
            "completed_at": "2026-01-24",
            "notes": None,
            "cost": None,
            "details": None,
            "created_at": "2026-01-24T15:22:00Z",
            "updated_at": "2026-01-24T15:22:00Z",
        }

        with patch("src.commands.task.APIClient") as mock_api_client:
            items_response = MagicMock()
            items_response.status_code = 200
            items_response.data = {"data": {"items": mock_items}}

            plans_response = MagicMock()
            plans_response.status_code = 200
            plans_response.data = {"data": []}

            types_response = MagicMock()
            types_response.status_code = 200
            types_response.data = {"data": {"task_types": []}}

            create_type_response = MagicMock()
            create_type_response.status_code = 201
            create_type_response.data = {"data": new_task_type_response}

            create_response = MagicMock()
            create_response.status_code = 201
            create_response.data = {"data": task_response}

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.side_effect = [
                items_response,
                plans_response,
                types_response,
                create_type_response,
                create_response,
            ]
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            with patch("src.commands.task.get_active_user_id", return_value=1):
                result = cli_runner.invoke(
                    create_task,
                    input="1\n1\nTire Rotation\nRotate tires\n\n\n\n"
                )

        assert "Task type 'Tire Rotation' created successfully" in result.output
        assert "Success: Task created successfully!" in result.output

    def test_new_task_type_without_description_in_task_flow(self, cli_runner, mock_items):
        """Test creating task type without description within task creation flow."""
        new_task_type_response = {
            "id": 100,
            "name": "Inspection",
            "description": None,
            "created_at": "2026-01-24T10:00:00Z",
            "updated_at": "2026-01-24T10:00:00Z",
        }

        task_response = {
            "id": 26,
            "item_id": 1,
            "task_type_id": 100,
            "completed_at": "2026-01-24",
            "notes": None,
            "cost": None,
            "details": None,
            "created_at": "2026-01-24T15:22:00Z",
            "updated_at": "2026-01-24T15:22:00Z",
        }

        with patch("src.commands.task.APIClient") as mock_api_client:
            items_response = MagicMock()
            items_response.status_code = 200
            items_response.data = {"data": {"items": mock_items}}

            plans_response = MagicMock()
            plans_response.status_code = 200
            plans_response.data = {"data": []}

            types_response = MagicMock()
            types_response.status_code = 200
            types_response.data = {"data": {"task_types": []}}

            create_type_response = MagicMock()
            create_type_response.status_code = 201
            create_type_response.data = {"data": new_task_type_response}

            create_response = MagicMock()
            create_response.status_code = 201
            create_response.data = {"data": task_response}

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.side_effect = [
                items_response,
                plans_response,
                types_response,
                create_type_response,
                create_response,
            ]
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            with patch("src.commands.task.get_active_user_id", return_value=1):
                result = cli_runner.invoke(
                    create_task,
                    input="1\n1\nInspection\n\n\n\n\n"
                )

        assert "Task type 'Inspection' created successfully" in result.output

    def test_new_task_type_empty_name_error_in_task_flow(self, cli_runner, mock_items):
        """Test error handling for empty task type name within task creation."""
        with patch("src.commands.task.APIClient") as mock_api_client:
            items_response = MagicMock()
            items_response.status_code = 200
            items_response.data = {"data": {"items": mock_items}}

            plans_response = MagicMock()
            plans_response.status_code = 200
            plans_response.data = {"data": []}

            types_response = MagicMock()
            types_response.status_code = 200
            types_response.data = {"data": {"task_types": []}}

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.side_effect = [
                items_response,
                plans_response,
                types_response,
            ]
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            with patch("src.commands.task.get_active_user_id", return_value=1):
                result = cli_runner.invoke(
                    create_task,
                    input="1\n1\n\nValid Name\n\n\n\n"
                )

        assert "Name cannot be empty" in result.output

    def test_new_task_type_name_too_long_error_in_task_flow(self, cli_runner, mock_items):
        """Test error handling for task type name that's too long."""
        with patch("src.commands.task.APIClient") as mock_api_client:
            items_response = MagicMock()
            items_response.status_code = 200
            items_response.data = {"data": {"items": mock_items}}

            plans_response = MagicMock()
            plans_response.status_code = 200
            plans_response.data = {"data": []}

            types_response = MagicMock()
            types_response.status_code = 200
            types_response.data = {"data": {"task_types": []}}

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.side_effect = [
                items_response,
                plans_response,
                types_response,
            ]
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            long_name = "a" * 256
            with patch("src.commands.task.get_active_user_id", return_value=1):
                result = cli_runner.invoke(
                    create_task,
                    input=f"1\n1\n{long_name}\nValid Name\n\n\n\n"
                )

        assert "must be 255 characters or less" in result.output

    def test_new_task_type_duplicate_error_in_task_flow(self, cli_runner, mock_items):
        """Test error handling for duplicate task type name."""
        with patch("src.commands.task.APIClient") as mock_api_client:
            items_response = MagicMock()
            items_response.status_code = 200
            items_response.data = {"data": {"items": mock_items}}

            plans_response = MagicMock()
            plans_response.status_code = 200
            plans_response.data = {"data": []}

            types_response = MagicMock()
            types_response.status_code = 200
            types_response.data = {"data": {"task_types": []}}

            error = APIClientError4xx(
                "Conflict",
                status_code=409,
                response_body='{"message": "Task type already exists"}',
            )

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.side_effect = [
                items_response,
                plans_response,
                types_response,
                error,
            ]
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            with patch("src.commands.task.get_active_user_id", return_value=1):
                result = cli_runner.invoke(
                    create_task,
                    input="1\n1\nOil Change\n\n\n\n\n"
                )

        assert "already exists" in result.output.lower()
