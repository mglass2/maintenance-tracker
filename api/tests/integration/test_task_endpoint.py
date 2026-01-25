"""Integration tests for task API endpoints."""

import pytest
from datetime import date
from decimal import Decimal
from fastapi.testclient import TestClient


class TestCreateTaskEndpoint:
    """Tests for POST /tasks endpoint."""

    def test_create_task_missing_item_id(self, client: TestClient):
        """Test missing item_id returns 422."""
        response = client.post(
            "/tasks",
            json={
                "task_type_id": 1,
                "completed_at": "2024-01-15",
            },
        )

        assert response.status_code == 422

    def test_create_task_missing_task_type_id(self, client: TestClient):
        """Test missing task_type_id returns 422."""
        response = client.post(
            "/tasks",
            json={
                "item_id": 1,
                "completed_at": "2024-01-15",
            },
        )

        assert response.status_code == 422

    def test_create_task_missing_completed_at(self, client: TestClient):
        """Test missing completed_at returns 422."""
        response = client.post(
            "/tasks",
            json={
                "item_id": 1,
                "task_type_id": 1,
            },
        )

        assert response.status_code == 422

    def test_create_task_negative_item_id(self, client: TestClient):
        """Test negative item_id returns 422."""
        response = client.post(
            "/tasks",
            json={
                "item_id": -1,
                "task_type_id": 1,
                "completed_at": "2024-01-15",
            },
        )

        assert response.status_code == 422

    def test_create_task_zero_item_id(self, client: TestClient):
        """Test zero item_id returns 422."""
        response = client.post(
            "/tasks",
            json={
                "item_id": 0,
                "task_type_id": 1,
                "completed_at": "2024-01-15",
            },
        )

        assert response.status_code == 422

    def test_create_task_negative_task_type_id(self, client: TestClient):
        """Test negative task_type_id returns 422."""
        response = client.post(
            "/tasks",
            json={
                "item_id": 1,
                "task_type_id": -1,
                "completed_at": "2024-01-15",
            },
        )

        assert response.status_code == 422

    def test_create_task_zero_task_type_id(self, client: TestClient):
        """Test zero task_type_id returns 422."""
        response = client.post(
            "/tasks",
            json={
                "item_id": 1,
                "task_type_id": 0,
                "completed_at": "2024-01-15",
            },
        )

        assert response.status_code == 422

    def test_create_task_negative_cost(self, client: TestClient):
        """Test negative cost returns 422."""
        response = client.post(
            "/tasks",
            json={
                "item_id": 1,
                "task_type_id": 1,
                "completed_at": "2024-01-15",
                "cost": "-10.00",
            },
        )

        assert response.status_code == 422

    def test_create_task_invalid_cost(self, client: TestClient):
        """Test invalid cost value returns 422."""
        response = client.post(
            "/tasks",
            json={
                "item_id": 1,
                "task_type_id": 1,
                "completed_at": "2024-01-15",
                "cost": "not a number",
            },
        )

        assert response.status_code == 422

    def test_create_task_invalid_date(self, client: TestClient):
        """Test invalid completed_at date returns 422."""
        response = client.post(
            "/tasks",
            json={
                "item_id": 1,
                "task_type_id": 1,
                "completed_at": "not a date",
            },
        )

        assert response.status_code == 422

    def test_create_task_with_details_dict(self, client: TestClient):
        """Test creating task with details field as dict."""
        response = client.post(
            "/tasks",
            json={
                "item_id": 1,
                "task_type_id": 1,
                "completed_at": "2024-01-15",
                "details": {"mileage": 75000, "oil_type": "5W-30"},
            },
        )

        # Will fail with 404 because item/task_type don't exist,
        # but validates details field is accepted
        assert response.status_code in [201, 404]

        if response.status_code == 201:
            data = response.json()
            assert data["data"]["details"] == {"mileage": 75000, "oil_type": "5W-30"}

    def test_create_task_with_details_nested_dict(self, client: TestClient):
        """Test creating task with nested details dictionary."""
        response = client.post(
            "/tasks",
            json={
                "item_id": 1,
                "task_type_id": 1,
                "completed_at": "2024-01-15",
                "details": {"maintenance": {"type": "oil change", "filters": 2}},
            },
        )

        assert response.status_code in [201, 404]

        if response.status_code == 201:
            data = response.json()
            assert data["data"]["details"] == {"maintenance": {"type": "oil change", "filters": 2}}

    def test_create_task_with_details_mixed_types(self, client: TestClient):
        """Test creating task with details containing mixed data types."""
        response = client.post(
            "/tasks",
            json={
                "item_id": 1,
                "task_type_id": 1,
                "completed_at": "2024-01-15",
                "details": {
                    "mileage": 75000,
                    "hours": 100.5,
                    "description": "Scheduled maintenance",
                    "completed": True,
                },
            },
        )

        assert response.status_code in [201, 404]

        if response.status_code == 201:
            data = response.json()
            assert data["data"]["details"]["mileage"] == 75000
            assert data["data"]["details"]["hours"] == 100.5
            assert data["data"]["details"]["description"] == "Scheduled maintenance"
            assert data["data"]["details"]["completed"] is True

    def test_create_task_with_empty_details_dict(self, client: TestClient):
        """Test creating task with empty details dict."""
        response = client.post(
            "/tasks",
            json={
                "item_id": 1,
                "task_type_id": 1,
                "completed_at": "2024-01-15",
                "details": {},
            },
        )

        assert response.status_code in [201, 404]

        if response.status_code == 201:
            data = response.json()
            assert data["data"]["details"] == {}

    def test_create_task_with_details_none(self, client: TestClient):
        """Test creating task with details explicitly None."""
        response = client.post(
            "/tasks",
            json={
                "item_id": 1,
                "task_type_id": 1,
                "completed_at": "2024-01-15",
                "details": None,
            },
        )

        assert response.status_code in [201, 404]

        if response.status_code == 201:
            data = response.json()
            assert data["data"]["details"] is None

    def test_create_task_without_details_field(self, client: TestClient):
        """Test creating task without details field uses None default."""
        response = client.post(
            "/tasks",
            json={
                "item_id": 1,
                "task_type_id": 1,
                "completed_at": "2024-01-15",
            },
        )

        assert response.status_code in [201, 404]

        if response.status_code == 201:
            data = response.json()
            assert data["data"]["details"] is None

    def test_create_task_details_invalid_type_string(self, client: TestClient):
        """Test details field with string value is rejected (422)."""
        response = client.post(
            "/tasks",
            json={
                "item_id": 1,
                "task_type_id": 1,
                "completed_at": "2024-01-15",
                "details": "invalid",
            },
        )

        assert response.status_code == 422

    def test_create_task_details_invalid_type_list(self, client: TestClient):
        """Test details field with list value is rejected (422)."""
        response = client.post(
            "/tasks",
            json={
                "item_id": 1,
                "task_type_id": 1,
                "completed_at": "2024-01-15",
                "details": ["invalid"],
            },
        )

        assert response.status_code == 422

    def test_create_task_details_invalid_type_number(self, client: TestClient):
        """Test details field with number value is rejected (422)."""
        response = client.post(
            "/tasks",
            json={
                "item_id": 1,
                "task_type_id": 1,
                "completed_at": "2024-01-15",
                "details": 123,
            },
        )

        assert response.status_code == 422

    def test_create_task_all_fields_with_details(self, client: TestClient):
        """Test creating task with all fields including details."""
        response = client.post(
            "/tasks",
            json={
                "item_id": 1,
                "task_type_id": 1,
                "completed_at": "2024-01-15",
                "notes": "Oil change at dealer",
                "cost": 75.50,
                "details": {"mileage": 85000, "filter_part": "OEM-12345"},
            },
        )

        assert response.status_code in [201, 404]

        if response.status_code == 201:
            data = response.json()
            assert data["data"]["notes"] == "Oil change at dealer"
            assert data["data"]["cost"] == "75.50"
            assert data["data"]["details"] == {"mileage": 85000, "filter_part": "OEM-12345"}

