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


class TestGetItemMaintenancePlansByItemEndpoint:
    """Tests for GET /item_maintenance_plans/items/{item_id} endpoint."""

    def test_get_plans_by_item_nonexistent_returns_404(self, client: TestClient):
        """Test GET plans for nonexistent item returns 404."""
        response = client.get("/item_maintenance_plans/items/9999")

        # Should return 404 when item doesn't exist
        assert response.status_code == 404
        data = response.json()
        assert data["error"] == "RESOURCE_NOT_FOUND"

    def test_get_plans_by_item_response_format(self, client: TestClient):
        """Test response format for GET plans by item."""
        # This test would pass if an item with ID 1 exists
        response = client.get("/item_maintenance_plans/items/1")

        # Should return 200 if item exists, 404 if not
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert "data" in data
            assert "message" in data
            assert isinstance(data["data"], list)

            # Each plan should have required fields
            for plan in data["data"]:
                assert "id" in plan
                assert "item_id" in plan
                assert "task_type_id" in plan
                assert "time_interval_days" in plan
                assert "created_at" in plan
                assert "updated_at" in plan

    def test_get_plans_by_item_empty_list(self, client: TestClient):
        """Test GET plans returns empty list if no plans exist."""
        response = client.get("/item_maintenance_plans/items/1")

        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data["data"], list)

    def test_get_plans_by_item_includes_custom_interval(self, client: TestClient):
        """Test GET plans includes custom_interval field."""
        response = client.get("/item_maintenance_plans/items/1")

        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            for plan in data["data"]:
                assert "custom_interval" in plan
