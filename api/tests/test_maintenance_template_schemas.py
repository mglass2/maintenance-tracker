"""Unit tests for maintenance template Pydantic schemas."""

import pytest
from pydantic import ValidationError
from schemas.maintenance_templates import (
    MaintenanceTemplateCreateRequest,
    MaintenanceTemplateResponse,
)
from datetime import datetime


class TestMaintenanceTemplateCreateRequest:
    """Tests for MaintenanceTemplateCreateRequest schema."""

    def test_valid_request_minimal(self):
        """Test valid request with only required fields."""
        data = {
            "item_type_id": 1,
            "task_type_id": 1,
            "time_interval_days": 30,
        }
        request = MaintenanceTemplateCreateRequest(**data)
        assert request.item_type_id == 1
        assert request.task_type_id == 1
        assert request.time_interval_days == 30
        assert request.custom_interval is None

    def test_valid_request_with_custom_interval(self):
        """Test valid request with custom_interval."""
        data = {
            "item_type_id": 1,
            "task_type_id": 1,
            "time_interval_days": 30,
            "custom_interval": {"type": "mileage", "value": 5000},
        }
        request = MaintenanceTemplateCreateRequest(**data)
        assert request.custom_interval == {"type": "mileage", "value": 5000}

    def test_missing_item_type_id(self):
        """Test missing item_type_id raises ValidationError."""
        data = {
            "task_type_id": 1,
            "time_interval_days": 30,
        }
        with pytest.raises(ValidationError) as exc_info:
            MaintenanceTemplateCreateRequest(**data)
        assert "item_type_id" in str(exc_info.value)

    def test_missing_task_type_id(self):
        """Test missing task_type_id raises ValidationError."""
        data = {
            "item_type_id": 1,
            "time_interval_days": 30,
        }
        with pytest.raises(ValidationError) as exc_info:
            MaintenanceTemplateCreateRequest(**data)
        assert "task_type_id" in str(exc_info.value)

    def test_missing_time_interval_days(self):
        """Test missing time_interval_days raises ValidationError."""
        data = {
            "item_type_id": 1,
            "task_type_id": 1,
        }
        with pytest.raises(ValidationError) as exc_info:
            MaintenanceTemplateCreateRequest(**data)
        assert "time_interval_days" in str(exc_info.value)

    def test_negative_item_type_id(self):
        """Test negative item_type_id raises ValidationError."""
        data = {
            "item_type_id": -1,
            "task_type_id": 1,
            "time_interval_days": 30,
        }
        with pytest.raises(ValidationError) as exc_info:
            MaintenanceTemplateCreateRequest(**data)
        assert "positive" in str(exc_info.value).lower()

    def test_zero_item_type_id(self):
        """Test zero item_type_id raises ValidationError."""
        data = {
            "item_type_id": 0,
            "task_type_id": 1,
            "time_interval_days": 30,
        }
        with pytest.raises(ValidationError) as exc_info:
            MaintenanceTemplateCreateRequest(**data)
        assert "positive" in str(exc_info.value).lower()

    def test_negative_task_type_id(self):
        """Test negative task_type_id raises ValidationError."""
        data = {
            "item_type_id": 1,
            "task_type_id": -1,
            "time_interval_days": 30,
        }
        with pytest.raises(ValidationError) as exc_info:
            MaintenanceTemplateCreateRequest(**data)
        assert "positive" in str(exc_info.value).lower()

    def test_zero_task_type_id(self):
        """Test zero task_type_id raises ValidationError."""
        data = {
            "item_type_id": 1,
            "task_type_id": 0,
            "time_interval_days": 30,
        }
        with pytest.raises(ValidationError) as exc_info:
            MaintenanceTemplateCreateRequest(**data)
        assert "positive" in str(exc_info.value).lower()

    def test_negative_time_interval_days(self):
        """Test negative time_interval_days raises ValidationError."""
        data = {
            "item_type_id": 1,
            "task_type_id": 1,
            "time_interval_days": -30,
        }
        with pytest.raises(ValidationError) as exc_info:
            MaintenanceTemplateCreateRequest(**data)
        assert "positive" in str(exc_info.value).lower()

    def test_zero_time_interval_days(self):
        """Test zero time_interval_days raises ValidationError."""
        data = {
            "item_type_id": 1,
            "task_type_id": 1,
            "time_interval_days": 0,
        }
        with pytest.raises(ValidationError) as exc_info:
            MaintenanceTemplateCreateRequest(**data)
        assert "positive" in str(exc_info.value).lower()

    def test_non_integer_item_type_id(self):
        """Test non-integer item_type_id raises ValidationError."""
        data = {
            "item_type_id": "not_an_int",
            "task_type_id": 1,
            "time_interval_days": 30,
        }
        with pytest.raises(ValidationError) as exc_info:
            MaintenanceTemplateCreateRequest(**data)
        assert "integer" in str(exc_info.value).lower()

    def test_non_integer_task_type_id(self):
        """Test non-integer task_type_id raises ValidationError."""
        data = {
            "item_type_id": 1,
            "task_type_id": "not_an_int",
            "time_interval_days": 30,
        }
        with pytest.raises(ValidationError) as exc_info:
            MaintenanceTemplateCreateRequest(**data)
        assert "integer" in str(exc_info.value).lower()

    def test_non_integer_time_interval_days(self):
        """Test non-integer time_interval_days raises ValidationError."""
        data = {
            "item_type_id": 1,
            "task_type_id": 1,
            "time_interval_days": "thirty",
        }
        with pytest.raises(ValidationError) as exc_info:
            MaintenanceTemplateCreateRequest(**data)
        assert "integer" in str(exc_info.value).lower()

    def test_custom_interval_not_dict(self):
        """Test custom_interval that is not a dict raises ValidationError."""
        data = {
            "item_type_id": 1,
            "task_type_id": 1,
            "time_interval_days": 30,
            "custom_interval": "not_a_dict",
        }
        with pytest.raises(ValidationError) as exc_info:
            MaintenanceTemplateCreateRequest(**data)
        assert "dictionary" in str(exc_info.value).lower()

    def test_custom_interval_as_list(self):
        """Test custom_interval as a list raises ValidationError."""
        data = {
            "item_type_id": 1,
            "task_type_id": 1,
            "time_interval_days": 30,
            "custom_interval": ["type", "mileage"],
        }
        with pytest.raises(ValidationError) as exc_info:
            MaintenanceTemplateCreateRequest(**data)
        assert "dictionary" in str(exc_info.value).lower()

    def test_custom_interval_null_is_valid(self):
        """Test custom_interval set to None is valid."""
        data = {
            "item_type_id": 1,
            "task_type_id": 1,
            "time_interval_days": 30,
            "custom_interval": None,
        }
        request = MaintenanceTemplateCreateRequest(**data)
        assert request.custom_interval is None


class TestMaintenanceTemplateResponse:
    """Tests for MaintenanceTemplateResponse schema."""

    def test_response_from_dict(self):
        """Test creating response from dictionary."""
        data = {
            "id": 1,
            "item_type_id": 1,
            "task_type_id": 1,
            "time_interval_days": 30,
            "custom_interval": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        response = MaintenanceTemplateResponse(**data)
        assert response.id == 1
        assert response.item_type_id == 1
        assert response.task_type_id == 1

    def test_response_is_frozen(self):
        """Test that response object is frozen (immutable)."""
        data = {
            "id": 1,
            "item_type_id": 1,
            "task_type_id": 1,
            "time_interval_days": 30,
            "custom_interval": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        response = MaintenanceTemplateResponse(**data)

        with pytest.raises(Exception):  # FrozenInstanceError
            response.id = 999
