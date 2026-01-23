"""Tests for user Pydantic schemas and validation."""

import pytest
from pydantic import ValidationError

from schemas.users import UserCreateRequest, UserResponse


class TestUserCreateRequest:
    """Tests for UserCreateRequest validation schema."""

    def test_valid_user_creation_request(self):
        """Test creating a valid user request."""
        user_data = UserCreateRequest(
            name="John Doe",
            email="john@example.com",
        )
        assert user_data.name == "John Doe"
        assert user_data.email == "john@example.com"

    def test_email_normalization_to_lowercase(self):
        """Test email is normalized to lowercase."""
        user_data = UserCreateRequest(
            name="Jane Doe",
            email="JANE@EXAMPLE.COM",
        )
        assert user_data.email == "jane@example.com"

    def test_email_normalization_with_mixed_case(self):
        """Test email with mixed case is normalized."""
        user_data = UserCreateRequest(
            name="Bob Smith",
            email="Bob.Smith@Example.COM",
        )
        assert user_data.email == "bob.smith@example.com"

    def test_email_whitespace_stripping(self):
        """Test email whitespace is stripped."""
        user_data = UserCreateRequest(
            name="Test User",
            email="  test@example.com  ",
        )
        assert user_data.email == "test@example.com"

    def test_name_whitespace_stripping(self):
        """Test name whitespace is stripped."""
        user_data = UserCreateRequest(
            name="  John Doe  ",
            email="john@example.com",
        )
        assert user_data.name == "John Doe"

    def test_invalid_email_format(self):
        """Test invalid email format raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreateRequest(
                name="John Doe",
                email="not-an-email",
            )
        assert "email" in str(exc_info.value).lower()

    def test_empty_email(self):
        """Test empty email raises validation error."""
        with pytest.raises(ValidationError):
            UserCreateRequest(
                name="John Doe",
                email="",
            )

    def test_empty_name(self):
        """Test empty name raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreateRequest(
                name="",
                email="john@example.com",
            )
        assert "empty" in str(exc_info.value).lower()

    def test_whitespace_only_name(self):
        """Test name that is only whitespace raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreateRequest(
                name="   ",
                email="john@example.com",
            )
        assert "whitespace" in str(exc_info.value).lower()

    def test_name_too_long(self):
        """Test name exceeding 255 characters raises validation error."""
        long_name = "a" * 256
        with pytest.raises(ValidationError) as exc_info:
            UserCreateRequest(
                name=long_name,
                email="john@example.com",
            )
        assert "255" in str(exc_info.value)

    def test_name_exactly_255_characters(self):
        """Test name with exactly 255 characters is valid."""
        name_255 = "a" * 255
        user_data = UserCreateRequest(
            name=name_255,
            email="john@example.com",
        )
        assert len(user_data.name) == 255

    def test_missing_name_field(self):
        """Test missing name field raises validation error."""
        with pytest.raises(ValidationError):
            UserCreateRequest(email="john@example.com")

    def test_missing_email_field(self):
        """Test missing email field raises validation error."""
        with pytest.raises(ValidationError):
            UserCreateRequest(name="John Doe")


class TestUserResponse:
    """Tests for UserResponse validation schema."""

    def test_user_response_from_dict(self):
        """Test creating UserResponse from dictionary."""
        from datetime import datetime

        user_dict = {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        user_response = UserResponse.model_validate(user_dict)
        assert user_response.id == 1
        assert user_response.name == "John Doe"
        assert user_response.email == "john@example.com"

    def test_user_response_is_frozen(self):
        """Test that UserResponse is immutable (frozen)."""
        from datetime import datetime

        user_dict = {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        user_response = UserResponse.model_validate(user_dict)

        # Attempting to modify should raise an error
        with pytest.raises(Exception):
            user_response.name = "Jane Doe"

    def test_user_response_excludes_is_deleted(self):
        """Test that is_deleted field is not included in response."""
        from datetime import datetime

        user_dict = {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "is_deleted": False,
        }
        user_response = UserResponse.model_validate(user_dict)

        # is_deleted should not be in the serialized output
        assert "is_deleted" not in user_response.model_dump()

    def test_user_response_serialization(self):
        """Test UserResponse serialization to JSON."""
        from datetime import datetime

        user_dict = {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        user_response = UserResponse.model_validate(user_dict)
        serialized = user_response.model_dump()

        assert serialized["id"] == 1
        assert serialized["name"] == "John Doe"
        assert serialized["email"] == "john@example.com"
        assert "created_at" in serialized
        assert "updated_at" in serialized
        assert "is_deleted" not in serialized
