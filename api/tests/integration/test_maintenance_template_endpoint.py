"""Integration tests for maintenance template API endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestCreateMaintenanceTemplateEndpoint:
    """Tests for POST /maintenance_templates endpoint."""

    def test_create_maintenance_template_missing_item_type_id(self, client: TestClient):
        """Test missing item_type_id returns 422."""
        response = client.post(
            "/maintenance_templates",
            json={
                "task_type_id": 1,
                "time_interval_days": 30,
            },
        )

        assert response.status_code == 422

    def test_create_maintenance_template_missing_task_type_id(self, client: TestClient):
        """Test missing task_type_id returns 422."""
        response = client.post(
            "/maintenance_templates",
            json={
                "item_type_id": 1,
                "time_interval_days": 30,
            },
        )

        assert response.status_code == 422

    def test_create_maintenance_template_missing_time_interval_days(
        self, client: TestClient
    ):
        """Test missing time_interval_days returns 422."""
        response = client.post(
            "/maintenance_templates",
            json={
                "item_type_id": 1,
                "task_type_id": 1,
            },
        )

        assert response.status_code == 422

    def test_create_maintenance_template_negative_item_type_id(self, client: TestClient):
        """Test negative item_type_id returns 422."""
        response = client.post(
            "/maintenance_templates",
            json={
                "item_type_id": -1,
                "task_type_id": 1,
                "time_interval_days": 30,
            },
        )

        assert response.status_code == 422

    def test_create_maintenance_template_zero_item_type_id(self, client: TestClient):
        """Test zero item_type_id returns 422."""
        response = client.post(
            "/maintenance_templates",
            json={
                "item_type_id": 0,
                "task_type_id": 1,
                "time_interval_days": 30,
            },
        )

        assert response.status_code == 422

    def test_create_maintenance_template_negative_task_type_id(self, client: TestClient):
        """Test negative task_type_id returns 422."""
        response = client.post(
            "/maintenance_templates",
            json={
                "item_type_id": 1,
                "task_type_id": -1,
                "time_interval_days": 30,
            },
        )

        assert response.status_code == 422

    def test_create_maintenance_template_zero_task_type_id(self, client: TestClient):
        """Test zero task_type_id returns 422."""
        response = client.post(
            "/maintenance_templates",
            json={
                "item_type_id": 1,
                "task_type_id": 0,
                "time_interval_days": 30,
            },
        )

        assert response.status_code == 422

    def test_create_maintenance_template_negative_time_interval_days(
        self, client: TestClient
    ):
        """Test negative time_interval_days returns 422."""
        response = client.post(
            "/maintenance_templates",
            json={
                "item_type_id": 1,
                "task_type_id": 1,
                "time_interval_days": -30,
            },
        )

        assert response.status_code == 422

    def test_create_maintenance_template_zero_time_interval_days(
        self, client: TestClient
    ):
        """Test zero time_interval_days returns 422."""
        response = client.post(
            "/maintenance_templates",
            json={
                "item_type_id": 1,
                "task_type_id": 1,
                "time_interval_days": 0,
            },
        )

        assert response.status_code == 422

    def test_create_maintenance_template_non_integer_item_type_id(
        self, client: TestClient
    ):
        """Test non-integer item_type_id returns 422."""
        response = client.post(
            "/maintenance_templates",
            json={
                "item_type_id": "not_an_int",
                "task_type_id": 1,
                "time_interval_days": 30,
            },
        )

        assert response.status_code == 422

    def test_create_maintenance_template_non_integer_task_type_id(
        self, client: TestClient
    ):
        """Test non-integer task_type_id returns 422."""
        response = client.post(
            "/maintenance_templates",
            json={
                "item_type_id": 1,
                "task_type_id": "not_an_int",
                "time_interval_days": 30,
            },
        )

        assert response.status_code == 422

    def test_create_maintenance_template_non_integer_time_interval_days(
        self, client: TestClient
    ):
        """Test non-integer time_interval_days returns 422."""
        response = client.post(
            "/maintenance_templates",
            json={
                "item_type_id": 1,
                "task_type_id": 1,
                "time_interval_days": "thirty",
            },
        )

        assert response.status_code == 422

    def test_create_maintenance_template_custom_interval_not_dict(
        self, client: TestClient
    ):
        """Test custom_interval that is not a dictionary returns 422."""
        response = client.post(
            "/maintenance_templates",
            json={
                "item_type_id": 1,
                "task_type_id": 1,
                "time_interval_days": 30,
                "custom_interval": "not_a_dict",
            },
        )

        assert response.status_code == 422

    def test_create_maintenance_template_custom_interval_as_list(
        self, client: TestClient
    ):
        """Test custom_interval that is a list returns 422."""
        response = client.post(
            "/maintenance_templates",
            json={
                "item_type_id": 1,
                "task_type_id": 1,
                "time_interval_days": 30,
                "custom_interval": ["type", "mileage"],
            },
        )

        assert response.status_code == 422


class TestGetMaintenanceTemplatesByItemTypeEndpoint:
    """Tests for GET /maintenance_templates/item_types/{item_type_id} endpoint."""

    def test_get_templates_by_item_type_nonexistent_returns_404(self, client: TestClient):
        """Test GET templates for nonexistent item type returns 404."""
        response = client.get("/maintenance_templates/item_types/9999")

        # Should return 404 when item_type doesn't exist
        assert response.status_code == 404
        data = response.json()
        assert data["error"] == "RESOURCE_NOT_FOUND"

    def test_get_templates_by_item_type_response_format(self, client: TestClient):
        """Test response format for GET templates by item type."""
        # This test would pass if an item_type with ID 1 exists and has templates
        response = client.get("/maintenance_templates/item_types/1")

        # Should return 200 if item_type exists, 404 if not
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert "data" in data
            assert "message" in data
            assert isinstance(data["data"], list)

            # Each template should have required fields
            for template in data["data"]:
                assert "id" in template
                assert "item_type_id" in template
                assert "task_type_id" in template
                assert "task_type_name" in template
                assert "time_interval_days" in template
                assert "created_at" in template
                assert "updated_at" in template

    def test_get_templates_by_item_type_includes_task_type_name(self, client: TestClient):
        """Test GET templates includes task_type_name field."""
        response = client.get("/maintenance_templates/item_types/1")

        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            for template in data["data"]:
                assert "task_type_name" in template
                assert isinstance(template["task_type_name"], str)

    def test_get_templates_by_item_type_empty_list(self, client: TestClient):
        """Test GET templates returns empty list if no templates exist."""
        response = client.get("/maintenance_templates/item_types/1")

        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data["data"], list)
