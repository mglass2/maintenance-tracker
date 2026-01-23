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

