"""Tests for task type schema validation."""

from datetime import datetime
import pytest
from pydantic import ValidationError
from schemas.task_types import TaskTypeCreateRequest, TaskTypeResponse


class TestTaskTypeCreateRequest:
    """Tests for TaskTypeCreateRequest schema validation."""

    def test_create_task_type_valid_request(self):
        """Test valid task type creation request."""
        task_type_data = TaskTypeCreateRequest(
            name="Oil Change",
            description="Regular oil and filter replacement",
        )

        assert task_type_data.name == "Oil Change"
        assert task_type_data.description == "Regular oil and filter replacement"

    def test_create_task_type_minimal_required_fields(self):
        """Test task type creation with only required fields."""
        task_type_data = TaskTypeCreateRequest(
            name="Brake Inspection",
        )

        assert task_type_data.name == "Brake Inspection"
        assert task_type_data.description is None

    def test_create_task_type_name_whitespace_stripped(self):
        """Test name whitespace is stripped."""
        task_type_data = TaskTypeCreateRequest(
            name="  Tire Rotation  ",
        )
        assert task_type_data.name == "Tire Rotation"

    def test_create_task_type_empty_name_rejected(self):
        """Test empty name is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TaskTypeCreateRequest(
                name="",
            )
        assert "empty" in str(exc_info.value).lower()

    def test_create_task_type_whitespace_only_name_rejected(self):
        """Test whitespace-only name is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TaskTypeCreateRequest(
                name="   ",
            )
        assert "empty" in str(exc_info.value).lower()

    def test_create_task_type_name_too_long_rejected(self):
        """Test name exceeding 255 characters is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TaskTypeCreateRequest(
                name="a" * 256,
            )
        assert "255" in str(exc_info.value)

    def test_create_task_type_name_exactly_255_characters(self):
        """Test name with exactly 255 characters is accepted."""
        task_type_data = TaskTypeCreateRequest(
            name="a" * 255,
        )
        assert len(task_type_data.name) == 255

    def test_create_task_type_description_whitespace_stripped(self):
        """Test description whitespace is stripped."""
        task_type_data = TaskTypeCreateRequest(
            name="Inspection",
            description="  Visual inspection of components  ",
        )
        assert task_type_data.description == "Visual inspection of components"

    def test_create_task_type_description_whitespace_only_becomes_none(self):
        """Test description with only whitespace becomes None."""
        task_type_data = TaskTypeCreateRequest(
            name="Replacement",
            description="   ",
        )
        assert task_type_data.description is None

    def test_create_task_type_description_empty_string_becomes_none(self):
        """Test empty description becomes None."""
        task_type_data = TaskTypeCreateRequest(
            name="Service",
            description="",
        )
        assert task_type_data.description is None

    def test_create_task_type_missing_name(self):
        """Test missing name returns validation error."""
        with pytest.raises(ValidationError):
            TaskTypeCreateRequest(
                description="Some description",
            )

    def test_create_task_type_non_string_name_rejected(self):
        """Test non-string name is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TaskTypeCreateRequest(
                name=123,
            )
        assert "string" in str(exc_info.value).lower()

    def test_create_task_type_non_string_description_rejected(self):
        """Test non-string description is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TaskTypeCreateRequest(
                name="Valid Name",
                description=456,
            )
        assert "string" in str(exc_info.value).lower()


class TestTaskTypeResponse:
    """Tests for TaskTypeResponse schema."""

    def test_task_type_response_immutable(self):
        """Test that TaskTypeResponse is frozen (immutable)."""
        response = TaskTypeResponse(
            id=1,
            name="Oil Change",
            description="Service task",
            created_at=datetime(2024, 1, 15, 10, 0, 0),
            updated_at=datetime(2024, 1, 15, 10, 0, 0),
        )

        with pytest.raises(Exception):  # Should raise when trying to modify
            response.id = 999

    def test_task_type_response_serialization(self):
        """Test TaskTypeResponse serialization."""
        created = datetime(2024, 1, 15, 10, 30, 0)
        updated = datetime(2024, 1, 15, 10, 30, 0)
        response = TaskTypeResponse(
            id=5,
            name="Tire Rotation",
            description="Rotate tires for even wear",
            created_at=created,
            updated_at=updated,
        )

        data = response.model_dump()
        assert data["id"] == 5
        assert data["name"] == "Tire Rotation"
        assert data["description"] == "Rotate tires for even wear"
        assert data["created_at"] == created
        assert data["updated_at"] == updated
