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
