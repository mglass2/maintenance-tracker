"""Integration tests for task type API endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestCreateTaskTypeEndpoint:
    """Tests for POST /task_types endpoint."""

    def test_create_task_type_missing_name(self, client: TestClient):
        """Test missing name returns 422."""
        response = client.post(
            "/task_types",
            json={
                "description": "Some description",
            },
        )

        assert response.status_code == 422

    def test_create_task_type_empty_name(self, client: TestClient):
        """Test empty name returns 422."""
        response = client.post(
            "/task_types",
            json={
                "name": "",
            },
        )

        assert response.status_code == 422

    def test_create_task_type_whitespace_only_name(self, client: TestClient):
        """Test whitespace-only name returns 422."""
        response = client.post(
            "/task_types",
            json={
                "name": "   ",
            },
        )

        assert response.status_code == 422

    def test_create_task_type_name_too_long(self, client: TestClient):
        """Test name exceeding 255 characters returns 422."""
        response = client.post(
            "/task_types",
            json={
                "name": "a" * 256,
            },
        )

        assert response.status_code == 422

    def test_create_task_type_non_string_name(self, client: TestClient):
        """Test non-string name returns 422."""
        response = client.post(
            "/task_types",
            json={
                "name": 123,
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
            },
        )

        assert response.status_code == 422
