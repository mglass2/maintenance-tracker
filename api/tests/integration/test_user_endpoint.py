"""Integration tests for user API endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestCreateUserEndpoint:
    """Tests for POST /users endpoint."""

    def test_create_user_valid_request(self, client: TestClient):
        """Test successful user creation with valid data."""
        response = client.post(
            "/users",
            json={
                "name": "John Doe",
                "email": "john@example.com",
            },
        )

        assert response.status_code == 201
        data = response.json()

        assert "data" in data
        assert "message" in data
        assert data["message"] == "User created successfully"

        user = data["data"]
        assert user["id"] is not None
        assert user["name"] == "John Doe"
        assert user["email"] == "john@example.com"
        assert "created_at" in user
        assert "updated_at" in user
        assert "is_deleted" not in user

    def test_create_user_response_format(self, client: TestClient):
        """Test response format matches API specification."""
        response = client.post(
            "/users",
            json={
                "name": "Test User",
                "email": "test@example.com",
            },
        )

        assert response.status_code == 201
        data = response.json()

        # Check response structure
        assert isinstance(data, dict)
        assert "data" in data
        assert "message" in data

        user = data["data"]
        assert isinstance(user, dict)
        assert set(user.keys()) == {"id", "name", "email", "created_at", "updated_at"}

    def test_create_user_email_normalization(self, client: TestClient):
        """Test email is normalized to lowercase in response."""
        response = client.post(
            "/users",
            json={
                "name": "Test User",
                "email": "Test@EXAMPLE.COM",
            },
        )

        assert response.status_code == 201
        user = response.json()["data"]
        assert user["email"] == "test@example.com"

    def test_create_user_duplicate_email_returns_409(self, client: TestClient):
        """Test creating user with duplicate email returns 409 Conflict."""
        # Create first user
        client.post(
            "/users",
            json={
                "name": "John Doe",
                "email": "john@example.com",
            },
        )

        # Try to create second user with same email
        response = client.post(
            "/users",
            json={
                "name": "Jane Doe",
                "email": "john@example.com",
            },
        )

        assert response.status_code == 409
        data = response.json()

        assert data["error"] == "DUPLICATE_EMAIL"
        assert "already exists" in data["message"]

    def test_create_user_duplicate_email_case_insensitive(self, client: TestClient):
        """Test email duplicate check is case-insensitive."""
        # Create first user
        client.post(
            "/users",
            json={
                "name": "John Doe",
                "email": "john@example.com",
            },
        )

        # Try with uppercase variant
        response = client.post(
            "/users",
            json={
                "name": "Jane Doe",
                "email": "JOHN@EXAMPLE.COM",
            },
        )

        assert response.status_code == 409

    def test_create_user_invalid_email_format(self, client: TestClient):
        """Test invalid email format returns 400 Bad Request."""
        response = client.post(
            "/users",
            json={
                "name": "Test User",
                "email": "not-an-email",
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert "error" in data

    def test_create_user_empty_email(self, client: TestClient):
        """Test empty email returns 400 Bad Request."""
        response = client.post(
            "/users",
            json={
                "name": "Test User",
                "email": "",
            },
        )

        assert response.status_code == 400

    def test_create_user_empty_name(self, client: TestClient):
        """Test empty name returns 400 Bad Request."""
        response = client.post(
            "/users",
            json={
                "name": "",
                "email": "test@example.com",
            },
        )

        assert response.status_code == 400

    def test_create_user_name_too_long(self, client: TestClient):
        """Test name exceeding 255 characters returns 400 Bad Request."""
        response = client.post(
            "/users",
            json={
                "name": "a" * 256,
                "email": "test@example.com",
            },
        )

        assert response.status_code == 400

    def test_create_user_missing_name_field(self, client: TestClient):
        """Test missing name field returns 422 Unprocessable Entity."""
        response = client.post(
            "/users",
            json={
                "email": "test@example.com",
            },
        )

        assert response.status_code == 422

    def test_create_user_missing_email_field(self, client: TestClient):
        """Test missing email field returns 422 Unprocessable Entity."""
        response = client.post(
            "/users",
            json={
                "name": "Test User",
            },
        )

        assert response.status_code == 422

    def test_create_user_returns_user_id(self, client: TestClient):
        """Test that created user has an ID."""
        response = client.post(
            "/users",
            json={
                "name": "Test User",
                "email": "test@example.com",
            },
        )

        assert response.status_code == 201
        user = response.json()["data"]

        assert user["id"] is not None
        assert isinstance(user["id"], int)
        assert user["id"] > 0

    def test_create_user_name_whitespace_stripping(self, client: TestClient):
        """Test name whitespace is stripped."""
        response = client.post(
            "/users",
            json={
                "name": "  John Doe  ",
                "email": "john@example.com",
            },
        )

        assert response.status_code == 201
        user = response.json()["data"]
        assert user["name"] == "John Doe"

    def test_create_user_email_whitespace_stripping(self, client: TestClient):
        """Test email whitespace is stripped."""
        response = client.post(
            "/users",
            json={
                "name": "Test User",
                "email": "  test@example.com  ",
            },
        )

        assert response.status_code == 201
        user = response.json()["data"]
        assert user["email"] == "test@example.com"

    def test_create_user_returns_timestamps(self, client: TestClient):
        """Test that response includes created_at and updated_at."""
        response = client.post(
            "/users",
            json={
                "name": "Test User",
                "email": "test@example.com",
            },
        )

        assert response.status_code == 201
        user = response.json()["data"]

        assert "created_at" in user
        assert "updated_at" in user
        assert user["created_at"] is not None
        assert user["updated_at"] is not None

    def test_create_multiple_users(self, client: TestClient):
        """Test creating multiple users."""
        response1 = client.post(
            "/users",
            json={
                "name": "John Doe",
                "email": "john@example.com",
            },
        )
        response2 = client.post(
            "/users",
            json={
                "name": "Jane Doe",
                "email": "jane@example.com",
            },
        )

        assert response1.status_code == 201
        assert response2.status_code == 201

        user1 = response1.json()["data"]
        user2 = response2.json()["data"]

        assert user1["id"] != user2["id"]
        assert user1["email"] != user2["email"]
