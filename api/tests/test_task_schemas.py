"""Tests for task schema validation."""

from datetime import date
from decimal import Decimal
import pytest
from pydantic import ValidationError
from schemas.tasks import TaskCreateRequest, TaskResponse


class TestTaskCreateRequest:
    """Tests for TaskCreateRequest schema validation."""

    def test_create_task_valid_request(self):
        """Test valid task creation request."""
        task_data = TaskCreateRequest(
            item_id=1,
            task_type_id=1,
            completed_at=date(2024, 1, 15),
            notes="Oil change performed",
            cost=Decimal("45.99"),
        )

        assert task_data.item_id == 1
        assert task_data.task_type_id == 1
        assert task_data.completed_at == date(2024, 1, 15)
        assert task_data.notes == "Oil change performed"
        assert task_data.cost == Decimal("45.99")

    def test_create_task_minimal_required_fields(self):
        """Test task creation with only required fields."""
        task_data = TaskCreateRequest(
            item_id=5,
            task_type_id=3,
            completed_at=date(2024, 1, 20),
        )

        assert task_data.item_id == 5
        assert task_data.task_type_id == 3
        assert task_data.completed_at == date(2024, 1, 20)
        assert task_data.notes is None
        assert task_data.cost is None

    def test_create_task_negative_item_id_rejected(self):
        """Test negative item_id is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreateRequest(
                item_id=-1,
                task_type_id=1,
                completed_at=date(2024, 1, 15),
            )
        assert "positive integer" in str(exc_info.value).lower()

    def test_create_task_zero_item_id_rejected(self):
        """Test zero item_id is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreateRequest(
                item_id=0,
                task_type_id=1,
                completed_at=date(2024, 1, 15),
            )
        assert "positive integer" in str(exc_info.value).lower()

    def test_create_task_negative_task_type_id_rejected(self):
        """Test negative task_type_id is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreateRequest(
                item_id=1,
                task_type_id=-5,
                completed_at=date(2024, 1, 15),
            )
        assert "positive integer" in str(exc_info.value).lower()

    def test_create_task_zero_task_type_id_rejected(self):
        """Test zero task_type_id is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreateRequest(
                item_id=1,
                task_type_id=0,
                completed_at=date(2024, 1, 15),
            )
        assert "positive integer" in str(exc_info.value).lower()

    def test_create_task_negative_cost_rejected(self):
        """Test negative cost is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreateRequest(
                item_id=1,
                task_type_id=1,
                completed_at=date(2024, 1, 15),
                cost=Decimal("-10.00"),
            )
        assert "non-negative" in str(exc_info.value).lower()

    def test_create_task_zero_cost_accepted(self):
        """Test zero cost is accepted (valid value)."""
        task_data = TaskCreateRequest(
            item_id=1,
            task_type_id=1,
            completed_at=date(2024, 1, 15),
            cost=Decimal("0.00"),
        )
        assert task_data.cost == Decimal("0.00")

    def test_create_task_notes_whitespace_stripped(self):
        """Test notes whitespace is stripped."""
        task_data = TaskCreateRequest(
            item_id=1,
            task_type_id=1,
            completed_at=date(2024, 1, 15),
            notes="  Routine maintenance  ",
        )
        assert task_data.notes == "Routine maintenance"

    def test_create_task_notes_whitespace_only_becomes_none(self):
        """Test notes with only whitespace becomes None."""
        task_data = TaskCreateRequest(
            item_id=1,
            task_type_id=1,
            completed_at=date(2024, 1, 15),
            notes="   ",
        )
        assert task_data.notes is None

    def test_create_task_cost_as_string_converted(self):
        """Test cost as string is converted to Decimal."""
        task_data = TaskCreateRequest(
            item_id=1,
            task_type_id=1,
            completed_at=date(2024, 1, 15),
            cost="99.50",
        )
        assert task_data.cost == Decimal("99.50")

    def test_create_task_cost_as_int_converted(self):
        """Test cost as int is converted to Decimal."""
        task_data = TaskCreateRequest(
            item_id=1,
            task_type_id=1,
            completed_at=date(2024, 1, 15),
            cost=50,
        )
        assert task_data.cost == Decimal("50")

    def test_create_task_invalid_cost_rejected(self):
        """Test invalid cost value is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreateRequest(
                item_id=1,
                task_type_id=1,
                completed_at=date(2024, 1, 15),
                cost="not a number",
            )
        assert "decimal" in str(exc_info.value).lower()

    def test_create_task_missing_item_id(self):
        """Test missing item_id returns validation error."""
        with pytest.raises(ValidationError):
            TaskCreateRequest(
                task_type_id=1,
                completed_at=date(2024, 1, 15),
            )

    def test_create_task_missing_task_type_id(self):
        """Test missing task_type_id returns validation error."""
        with pytest.raises(ValidationError):
            TaskCreateRequest(
                item_id=1,
                completed_at=date(2024, 1, 15),
            )

    def test_create_task_missing_completed_at(self):
        """Test missing completed_at returns validation error."""
        with pytest.raises(ValidationError):
            TaskCreateRequest(
                item_id=1,
                task_type_id=1,
            )

    def test_create_task_with_details_dict(self):
        """Test task creation with details field as dict."""
        task_data = TaskCreateRequest(
            item_id=1,
            task_type_id=1,
            completed_at=date(2024, 1, 15),
            details={"mileage": 75000, "oil_type": "5W-30"},
        )

        assert task_data.details == {"mileage": 75000, "oil_type": "5W-30"}
        assert isinstance(task_data.details, dict)

    def test_create_task_with_details_nested_dict(self):
        """Test task creation with nested details dictionary."""
        task_data = TaskCreateRequest(
            item_id=1,
            task_type_id=1,
            completed_at=date(2024, 1, 15),
            details={"maintenance": {"type": "oil change", "filters": 2}},
        )

        assert task_data.details == {"maintenance": {"type": "oil change", "filters": 2}}

    def test_create_task_with_details_mixed_types(self):
        """Test task creation with details containing mixed data types."""
        task_data = TaskCreateRequest(
            item_id=1,
            task_type_id=1,
            completed_at=date(2024, 1, 15),
            details={
                "mileage": 75000,
                "hours": 100.5,
                "description": "Scheduled maintenance",
                "completed": True,
            },
        )

        assert task_data.details["mileage"] == 75000
        assert task_data.details["hours"] == 100.5
        assert task_data.details["description"] == "Scheduled maintenance"
        assert task_data.details["completed"] is True

    def test_create_task_with_empty_details_dict(self):
        """Test task creation with empty details dict."""
        task_data = TaskCreateRequest(
            item_id=1,
            task_type_id=1,
            completed_at=date(2024, 1, 15),
            details={},
        )

        assert task_data.details == {}

    def test_create_task_with_details_none(self):
        """Test task creation with details explicitly None."""
        task_data = TaskCreateRequest(
            item_id=1,
            task_type_id=1,
            completed_at=date(2024, 1, 15),
            details=None,
        )

        assert task_data.details is None

    def test_create_task_without_details_field(self):
        """Test task creation without details field uses None default."""
        task_data = TaskCreateRequest(
            item_id=1,
            task_type_id=1,
            completed_at=date(2024, 1, 15),
        )

        assert task_data.details is None

    def test_create_task_details_invalid_type_string(self):
        """Test details field with string value is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreateRequest(
                item_id=1,
                task_type_id=1,
                completed_at=date(2024, 1, 15),
                details="invalid",
            )
        assert "dict" in str(exc_info.value).lower() or "json object" in str(exc_info.value).lower()

    def test_create_task_details_invalid_type_list(self):
        """Test details field with list value is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreateRequest(
                item_id=1,
                task_type_id=1,
                completed_at=date(2024, 1, 15),
                details=["invalid"],
            )
        assert "dict" in str(exc_info.value).lower() or "json object" in str(exc_info.value).lower()

    def test_create_task_details_invalid_type_number(self):
        """Test details field with number value is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreateRequest(
                item_id=1,
                task_type_id=1,
                completed_at=date(2024, 1, 15),
                details=123,
            )
        assert "dict" in str(exc_info.value).lower() or "json object" in str(exc_info.value).lower()

    def test_create_task_all_fields_with_details(self):
        """Test task creation with all fields including details."""
        task_data = TaskCreateRequest(
            item_id=5,
            task_type_id=2,
            completed_at=date(2024, 1, 15),
            notes="Oil change at dealer",
            cost=Decimal("75.50"),
            details={"mileage": 85000, "filter_part": "OEM-12345"},
        )

        assert task_data.item_id == 5
        assert task_data.task_type_id == 2
        assert task_data.completed_at == date(2024, 1, 15)
        assert task_data.notes == "Oil change at dealer"
        assert task_data.cost == Decimal("75.50")
        assert task_data.details == {"mileage": 85000, "filter_part": "OEM-12345"}


class TestTaskResponse:
    """Tests for TaskResponse schema."""

    def test_task_response_immutable(self):
        """Test that TaskResponse is frozen (immutable)."""
        response = TaskResponse(
            id=1,
            item_id=1,
            task_type_id=1,
            completed_at=date(2024, 1, 15),
            notes="Test",
            cost=Decimal("45.99"),
            created_at="2024-01-15T10:00:00",
            updated_at="2024-01-15T10:00:00",
        )

        with pytest.raises(Exception):  # Should raise when trying to modify
            response.id = 999

    def test_task_response_serialization(self):
        """Test TaskResponse serialization."""
        response = TaskResponse(
            id=5,
            item_id=2,
            task_type_id=3,
            completed_at=date(2024, 1, 15),
            notes="Brake inspection",
            cost=Decimal("75.50"),
            created_at="2024-01-15T10:30:00",
            updated_at="2024-01-15T10:30:00",
        )

        data = response.model_dump()
        assert data["id"] == 5
        assert data["item_id"] == 2
        assert data["task_type_id"] == 3
        assert data["completed_at"] == date(2024, 1, 15)
        assert data["notes"] == "Brake inspection"
        assert str(data["cost"]) == "75.50"

    def test_task_response_with_details(self):
        """Test TaskResponse includes details field."""
        response = TaskResponse(
            id=1,
            item_id=1,
            task_type_id=1,
            completed_at=date(2024, 1, 15),
            details={"mileage": 75000, "oil_type": "5W-30"},
            created_at="2024-01-15T10:00:00",
            updated_at="2024-01-15T10:00:00",
        )

        data = response.model_dump()
        assert data["details"] == {"mileage": 75000, "oil_type": "5W-30"}

    def test_task_response_with_details_none(self):
        """Test TaskResponse with details as None."""
        response = TaskResponse(
            id=1,
            item_id=1,
            task_type_id=1,
            completed_at=date(2024, 1, 15),
            details=None,
            created_at="2024-01-15T10:00:00",
            updated_at="2024-01-15T10:00:00",
        )

        data = response.model_dump()
        assert data["details"] is None

    def test_task_response_without_details_field(self):
        """Test TaskResponse defaults details to None if not provided."""
        response = TaskResponse(
            id=1,
            item_id=1,
            task_type_id=1,
            completed_at=date(2024, 1, 15),
            created_at="2024-01-15T10:00:00",
            updated_at="2024-01-15T10:00:00",
        )

        data = response.model_dump()
        assert data["details"] is None
