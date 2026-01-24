"""Integration tests for item maintenance plan API endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestCreateItemMaintenancePlanEndpoint:
    """Tests for POST /item_maintenance_plans endpoint."""

    @pytest.mark.xfail(reason="Database session isolation between test setup and API calls")
    def test_create_item_maintenance_plan_nonexistent_item(
        self, db, client: TestClient
    ):
        """Test creating with nonexistent item_id returns 404."""
        response = client.post(
            "/item_maintenance_plans",
            json={
                "item_id": 999999,
                "task_type_id": 1,
                "time_interval_days": 30,
            },
        )

        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert "RESOURCE_NOT_FOUND" in data["error"]

    @pytest.mark.xfail(reason="Database session isolation between test setup and API calls")
    def test_create_item_maintenance_plan_nonexistent_task_type(
        self, db, client: TestClient
    ):
        """Test creating with nonexistent task_type_id returns 404."""
        response = client.post(
            "/item_maintenance_plans",
            json={
                "item_id": 1,
                "task_type_id": 999999,
                "time_interval_days": 30,
            },
        )

        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert "RESOURCE_NOT_FOUND" in data["error"]

    def test_create_item_maintenance_plan_missing_item_id(self, client: TestClient):
        """Test missing item_id returns 422."""
        response = client.post(
            "/item_maintenance_plans",
            json={
                "task_type_id": 1,
                "time_interval_days": 30,
            },
        )

        assert response.status_code == 422

    def test_create_item_maintenance_plan_missing_task_type_id(self, client: TestClient):
        """Test missing task_type_id returns 422."""
        response = client.post(
            "/item_maintenance_plans",
            json={
                "item_id": 1,
                "time_interval_days": 30,
            },
        )

        assert response.status_code == 422

    def test_create_item_maintenance_plan_missing_time_interval_days(
        self, client: TestClient
    ):
        """Test missing time_interval_days returns 422."""
        response = client.post(
            "/item_maintenance_plans",
            json={
                "item_id": 1,
                "task_type_id": 1,
            },
        )

        assert response.status_code == 422

    def test_create_item_maintenance_plan_negative_item_id(self, client: TestClient):
        """Test negative item_id returns 422."""
        response = client.post(
            "/item_maintenance_plans",
            json={
                "item_id": -1,
                "task_type_id": 1,
                "time_interval_days": 30,
            },
        )

        assert response.status_code == 422

    def test_create_item_maintenance_plan_zero_item_id(self, client: TestClient):
        """Test zero item_id returns 422."""
        response = client.post(
            "/item_maintenance_plans",
            json={
                "item_id": 0,
                "task_type_id": 1,
                "time_interval_days": 30,
            },
        )

        assert response.status_code == 422

    def test_create_item_maintenance_plan_negative_task_type_id(self, client: TestClient):
        """Test negative task_type_id returns 422."""
        response = client.post(
            "/item_maintenance_plans",
            json={
                "item_id": 1,
                "task_type_id": -1,
                "time_interval_days": 30,
            },
        )

        assert response.status_code == 422

    def test_create_item_maintenance_plan_zero_task_type_id(self, client: TestClient):
        """Test zero task_type_id returns 422."""
        response = client.post(
            "/item_maintenance_plans",
            json={
                "item_id": 1,
                "task_type_id": 0,
                "time_interval_days": 30,
            },
        )

        assert response.status_code == 422

    def test_create_item_maintenance_plan_negative_time_interval_days(
        self, client: TestClient
    ):
        """Test negative time_interval_days returns 422."""
        response = client.post(
            "/item_maintenance_plans",
            json={
                "item_id": 1,
                "task_type_id": 1,
                "time_interval_days": -30,
            },
        )

        assert response.status_code == 422

    def test_create_item_maintenance_plan_zero_time_interval_days(
        self, client: TestClient
    ):
        """Test zero time_interval_days returns 422."""
        response = client.post(
            "/item_maintenance_plans",
            json={
                "item_id": 1,
                "task_type_id": 1,
                "time_interval_days": 0,
            },
        )

        assert response.status_code == 422

    def test_create_item_maintenance_plan_non_integer_item_id(self, client: TestClient):
        """Test non-integer item_id returns 422."""
        response = client.post(
            "/item_maintenance_plans",
            json={
                "item_id": "not_an_int",
                "task_type_id": 1,
                "time_interval_days": 30,
            },
        )

        assert response.status_code == 422

    def test_create_item_maintenance_plan_non_integer_task_type_id(
        self, client: TestClient
    ):
        """Test non-integer task_type_id returns 422."""
        response = client.post(
            "/item_maintenance_plans",
            json={
                "item_id": 1,
                "task_type_id": "not_an_int",
                "time_interval_days": 30,
            },
        )

        assert response.status_code == 422

    def test_create_item_maintenance_plan_non_integer_time_interval_days(
        self, client: TestClient
    ):
        """Test non-integer time_interval_days returns 422."""
        response = client.post(
            "/item_maintenance_plans",
            json={
                "item_id": 1,
                "task_type_id": 1,
                "time_interval_days": "thirty",
            },
        )

        assert response.status_code == 422

    def test_create_item_maintenance_plan_custom_interval_not_dict(
        self, client: TestClient
    ):
        """Test custom_interval that is not a dictionary returns 422."""
        response = client.post(
            "/item_maintenance_plans",
            json={
                "item_id": 1,
                "task_type_id": 1,
                "time_interval_days": 30,
                "custom_interval": "not_a_dict",
            },
        )

        assert response.status_code == 422

    def test_create_item_maintenance_plan_custom_interval_as_list(
        self, client: TestClient
    ):
        """Test custom_interval that is a list returns 422."""
        response = client.post(
            "/item_maintenance_plans",
            json={
                "item_id": 1,
                "task_type_id": 1,
                "time_interval_days": 30,
                "custom_interval": ["type", "mileage"],
            },
        )

        assert response.status_code == 422

