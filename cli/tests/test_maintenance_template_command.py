"""Tests for the create-maintenance-template command."""

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
from src.commands.maintenance_template import create_maintenance_template


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
            "name": "Automobile",
            "description": "Car",
        },
        {
            "id": 2,
            "name": "House",
            "description": "Residential property",
        },
    ]


@pytest.fixture
def mock_task_types():
    """Provide mock task types data."""
    return [
        {
            "id": 1,
            "name": "Oil Change",
            "description": "Replace engine oil and filter",
        },
        {
            "id": 2,
            "name": "Tire Rotation",
            "description": "Rotate tires",
        },
        {
            "id": 3,
            "name": "Air Filter Replacement",
            "description": "Replace air filter",
        },
    ]


@pytest.fixture
def mock_existing_templates():
    """Provide mock existing maintenance templates."""
    return [
        {
            "id": 1,
            "item_type_id": 1,
            "task_type_id": 1,
            "task_type_name": "Oil Change",
            "time_interval_days": 365,
            "custom_interval": None,
        },
        {
            "id": 2,
            "item_type_id": 1,
            "task_type_id": 2,
            "task_type_name": "Tire Rotation",
            "time_interval_days": 180,
            "custom_interval": None,
        },
    ]


@pytest.fixture
def successful_template_response():
    """Provide a successful template creation response."""
    return {
        "id": 3,
        "item_type_id": 1,
        "task_type_id": 3,
        "time_interval_days": 365,
        "custom_interval": None,
        "created_at": "2026-01-24T15:30:00Z",
        "updated_at": "2026-01-24T15:30:00Z",
    }


class TestCreateMaintenanceTemplateFiltering:
    """Test task type filtering in create-maintenance-template."""

    def test_filter_task_types_with_existing_templates(
        self, cli_runner, mock_item_types, mock_task_types, mock_existing_templates, successful_template_response
    ):
        """Test that task types with existing templates are filtered out."""
        with patch("src.commands.maintenance_template.APIClient") as mock_api_client:
            # Mock item types response
            item_types_response = MagicMock()
            item_types_response.status_code = 200
            item_types_response.data = {"data": {"item_types": mock_item_types}}

            # Mock existing templates response (2 templates exist)
            templates_response = MagicMock()
            templates_response.status_code = 200
            templates_response.data = {"data": mock_existing_templates}

            # Mock task types response (3 task types available)
            task_types_response = MagicMock()
            task_types_response.status_code = 200
            task_types_response.data = {"data": {"task_types": mock_task_types}}

            # Mock template creation response
            create_response = MagicMock()
            create_response.status_code = 201
            create_response.data = {"data": successful_template_response}

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.side_effect = [
                item_types_response,
                templates_response,
                task_types_response,
                create_response,
            ]
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            # Select item type 1 and task type 3 (which should be the only available one)
            # Since task types 1 and 2 have templates, only task type 3 should be shown
            result = cli_runner.invoke(
                create_maintenance_template,
                input="1\n1\n365\nno\nno\n"
            )

            # Verify the command output
            assert result.exit_code == 0
            assert "Available Task Types:" in result.output
            # Only task type 3 should be shown (not 1 and 2 which have templates)
            assert "Air Filter Replacement" in result.output
            assert "Success: Maintenance template created successfully!" in result.output

    def test_no_existing_templates_shows_all_task_types(
        self, cli_runner, mock_item_types, mock_task_types, successful_template_response
    ):
        """Test that all task types are shown when no templates exist."""
        with patch("src.commands.maintenance_template.APIClient") as mock_api_client:
            # Mock item types response
            item_types_response = MagicMock()
            item_types_response.status_code = 200
            item_types_response.data = {"data": {"item_types": mock_item_types}}

            # Mock existing templates response (no templates)
            templates_response = MagicMock()
            templates_response.status_code = 200
            templates_response.data = {"data": []}

            # Mock task types response
            task_types_response = MagicMock()
            task_types_response.status_code = 200
            task_types_response.data = {"data": {"task_types": mock_task_types}}

            # Mock template creation response
            create_response = MagicMock()
            create_response.status_code = 201
            create_response.data = {"data": successful_template_response}

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.side_effect = [
                item_types_response,
                templates_response,
                task_types_response,
                create_response,
            ]
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(
                create_maintenance_template,
                input="1\n1\n365\nno\nno\n"
            )

            assert result.exit_code == 0
            # All three task types should be shown
            assert "Oil Change" in result.output
            assert "Tire Rotation" in result.output
            assert "Air Filter Replacement" in result.output
            assert "Success: Maintenance template created successfully!" in result.output

    def test_all_task_types_have_templates_shows_error(
        self, cli_runner, mock_item_types, mock_task_types
    ):
        """Test error message when all task types already have templates."""
        with patch("src.commands.maintenance_template.APIClient") as mock_api_client:
            # Mock item types response
            item_types_response = MagicMock()
            item_types_response.status_code = 200
            item_types_response.data = {"data": {"item_types": mock_item_types}}

            # Mock existing templates response (all 3 task types have templates)
            all_templates = [
                {
                    "id": 1,
                    "item_type_id": 1,
                    "task_type_id": 1,
                    "task_type_name": "Oil Change",
                    "time_interval_days": 365,
                },
                {
                    "id": 2,
                    "item_type_id": 1,
                    "task_type_id": 2,
                    "task_type_name": "Tire Rotation",
                    "time_interval_days": 180,
                },
                {
                    "id": 3,
                    "item_type_id": 1,
                    "task_type_id": 3,
                    "task_type_name": "Air Filter Replacement",
                    "time_interval_days": 365,
                },
            ]
            templates_response = MagicMock()
            templates_response.status_code = 200
            templates_response.data = {"data": all_templates}

            # Mock task types response
            task_types_response = MagicMock()
            task_types_response.status_code = 200
            task_types_response.data = {"data": {"task_types": mock_task_types}}

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.side_effect = [
                item_types_response,
                templates_response,
                task_types_response,
            ]
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(
                create_maintenance_template,
                input="1\n"
            )

            # Should display error message when all task types have templates
            assert "No eligible task types available" in result.output
            assert "All task types for this item type already have maintenance templates" in result.output

    def test_filtering_preserves_correct_task_types(
        self, cli_runner, mock_item_types, mock_task_types
    ):
        """Test that filtering logic correctly preserves only eligible task types."""
        with patch("src.commands.maintenance_template.APIClient") as mock_api_client:
            # Mock item types response
            item_types_response = MagicMock()
            item_types_response.status_code = 200
            item_types_response.data = {"data": {"item_types": mock_item_types}}

            # Mock existing templates response (only task type 2 has a template)
            one_template = [
                {
                    "id": 1,
                    "item_type_id": 1,
                    "task_type_id": 2,  # Only task type 2 has a template
                    "task_type_name": "Tire Rotation",
                    "time_interval_days": 180,
                },
            ]
            templates_response = MagicMock()
            templates_response.status_code = 200
            templates_response.data = {"data": one_template}

            # Mock task types response
            task_types_response = MagicMock()
            task_types_response.status_code = 200
            task_types_response.data = {"data": {"task_types": mock_task_types}}

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.side_effect = [
                item_types_response,
                templates_response,
                task_types_response,
            ]
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(
                create_maintenance_template,
                input="1\n"
            )

            # Should show task types 1 and 3, but not task type 2
            assert "Oil Change" in result.output
            assert "Air Filter Replacement" in result.output
            assert "Tire Rotation" not in result.output


class TestCreateMaintenanceTemplateErrors:
    """Test error handling in create-maintenance-template."""

    def test_no_item_types_available(self, cli_runner):
        """Test error when no item types are available."""
        with patch("src.commands.maintenance_template.APIClient") as mock_api_client:
            # Mock empty item types response
            item_types_response = MagicMock()
            item_types_response.status_code = 200
            item_types_response.data = {"data": {"item_types": []}}

            mock_client_instance = MagicMock()
            mock_client_instance._make_request.return_value = item_types_response
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(create_maintenance_template)

            # Command exits gracefully with no item types
            assert "No item types available" in result.output

    def test_task_type_filtering_on_second_iteration(
        self, cli_runner, mock_item_types, mock_task_types, successful_template_response
    ):
        """Test that existing templates are refetched when user creates multiple templates."""
        with patch("src.commands.maintenance_template.APIClient") as mock_api_client:
            # Mock item types response
            item_types_response = MagicMock()
            item_types_response.status_code = 200
            item_types_response.data = {"data": {"item_types": mock_item_types}}

            # Mock existing templates response (empty initially)
            templates_response_empty = MagicMock()
            templates_response_empty.status_code = 200
            templates_response_empty.data = {"data": []}

            # Mock task types response (called multiple times)
            task_types_response = MagicMock()
            task_types_response.status_code = 200
            task_types_response.data = {"data": {"task_types": mock_task_types}}

            # Mock successful creation responses
            create_response = MagicMock()
            create_response.status_code = 201
            create_response.data = {"data": successful_template_response}

            mock_client_instance = MagicMock()
            # Initial: item types, templates, task types
            mock_client_instance._make_request.side_effect = [
                item_types_response,
                templates_response_empty,
                task_types_response,
                create_response,
            ]
            mock_client_instance.__enter__.return_value = mock_client_instance
            mock_client_instance.__exit__.return_value = False

            mock_api_client.return_value = mock_client_instance

            result = cli_runner.invoke(
                create_maintenance_template,
                input="1\n1\n365\nno\nno\n"
            )

            assert "Success: Maintenance template created successfully!" in result.output
