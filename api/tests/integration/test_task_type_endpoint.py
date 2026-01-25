"""Integration tests for task type API endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestCreateTaskTypeEndpoint:
    """Tests for POST /task_types endpoint."""

    def test_create_task_type_success_with_valid_item_type(self, client_with_item_types: TestClient):
        """Test successful task type creation with valid item_type_id."""
        response = client_with_item_types.post(
            "/task_types",
            json={
                "name": "New Task Type",
                "description": "A new task type for testing",
                "item_type_id": 1,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["data"]["name"] == "New Task Type"
        assert data["data"]["item_type_id"] == 1

    def test_create_task_type_missing_name(self, client: TestClient):
        """Test missing name returns 422."""
        response = client.post(
            "/task_types",
            json={
                "description": "Some description",
                "item_type_id": 1,
            },
        )

        assert response.status_code == 422

    def test_create_task_type_empty_name(self, client: TestClient):
        """Test empty name returns 422."""
        response = client.post(
            "/task_types",
            json={
                "name": "",
                "item_type_id": 1,
            },
        )

        assert response.status_code == 422

    def test_create_task_type_whitespace_only_name(self, client: TestClient):
        """Test whitespace-only name returns 422."""
        response = client.post(
            "/task_types",
            json={
                "name": "   ",
                "item_type_id": 1,
            },
        )

        assert response.status_code == 422

    def test_create_task_type_name_too_long(self, client: TestClient):
        """Test name exceeding 255 characters returns 422."""
        response = client.post(
            "/task_types",
            json={
                "name": "a" * 256,
                "item_type_id": 1,
            },
        )

        assert response.status_code == 422

    def test_create_task_type_non_string_name(self, client: TestClient):
        """Test non-string name returns 422."""
        response = client.post(
            "/task_types",
            json={
                "name": 123,
                "item_type_id": 1,
            },
        )

        assert response.status_code == 422

    def test_create_task_type_non_string_description(self, client: TestClient):
        """Test non-string description returns 422."""
        response = client.post(
            "/task_types",
            json={
                "name": "Valid Name",
                "description": 456,
                "item_type_id": 1,
            },
        )

        assert response.status_code == 422

    def test_create_task_type_missing_item_type_id(self, client: TestClient):
        """Test missing item_type_id returns 422."""
        response = client.post(
            "/task_types",
            json={
                "name": "Valid Name",
                "description": "A description",
            },
        )

        assert response.status_code == 422

    def test_create_task_type_invalid_item_type_id(self, client: TestClient):
        """Test invalid item_type_id returns 404."""
        response = client.post(
            "/task_types",
            json={
                "name": "Valid Name",
                "description": "A description",
                "item_type_id": 9999,
            },
        )

        assert response.status_code == 404

    def test_create_task_type_negative_item_type_id(self, client: TestClient):
        """Test negative item_type_id returns 422."""
        response = client.post(
            "/task_types",
            json={
                "name": "Valid Name",
                "item_type_id": -1,
            },
        )

        assert response.status_code == 422

    def test_create_task_type_zero_item_type_id(self, client: TestClient):
        """Test zero item_type_id returns 422."""
        response = client.post(
            "/task_types",
            json={
                "name": "Valid Name",
                "item_type_id": 0,
            },
        )

        assert response.status_code == 422

    def test_create_task_type_non_integer_item_type_id(self, client: TestClient):
        """Test non-integer item_type_id returns 422."""
        response = client.post(
            "/task_types",
            json={
                "name": "Valid Name",
                "item_type_id": "not_an_int",
            },
        )

        assert response.status_code == 422


class TestGetTaskTypesEndpoint:
    """Tests for GET /task_types endpoint."""

    def test_get_all_task_types_success(self, client_with_item_types: TestClient):
        """Test retrieving all task types."""
        response = client_with_item_types.get("/task_types")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "task_types" in data["data"]
        assert isinstance(data["data"]["task_types"], list)

    def test_get_task_types_with_item_type_id_filter(self, client_with_item_types: TestClient):
        """Test filtering task types by item_type_id."""
        # First create a task type for item_type_id 1
        client_with_item_types.post(
            "/task_types",
            json={
                "name": "Test Task Type 1",
                "item_type_id": 1,
            },
        )

        response = client_with_item_types.get("/task_types?item_type_id=1")

        assert response.status_code == 200
        data = response.json()
        task_types = data["data"]["task_types"]

        # All returned task types should have item_type_id = 1
        for task_type in task_types:
            assert task_type["item_type_id"] == 1

    def test_get_task_types_with_different_item_type_id_filter(self, client_with_item_types: TestClient):
        """Test filtering task types by different item_type_id."""
        # First create a task type for item_type_id 2
        client_with_item_types.post(
            "/task_types",
            json={
                "name": "Test Task Type 2",
                "item_type_id": 2,
            },
        )

        response = client_with_item_types.get("/task_types?item_type_id=2")

        assert response.status_code == 200
        data = response.json()
        task_types = data["data"]["task_types"]

        # All returned task types should have item_type_id = 2
        for task_type in task_types:
            assert task_type["item_type_id"] == 2

    def test_get_task_types_with_non_existent_item_type_id(self, client_with_item_types: TestClient):
        """Test filtering with non-existent item_type_id returns empty list."""
        response = client_with_item_types.get("/task_types?item_type_id=9999")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["count"] == 0
        assert data["data"]["task_types"] == []

    def test_get_task_types_includes_item_type_id_in_response(self, client_with_item_types: TestClient):
        """Test that response includes item_type_id field."""
        # First create a task type so we have something to retrieve
        client_with_item_types.post(
            "/task_types",
            json={
                "name": "Test Task Type",
                "item_type_id": 1,
            },
        )

        response = client_with_item_types.get("/task_types")

        assert response.status_code == 200
        data = response.json()
        task_types = data["data"]["task_types"]

        # All task types should have item_type_id
        for task_type in task_types:
            assert "item_type_id" in task_type
            assert isinstance(task_type["item_type_id"], int)


