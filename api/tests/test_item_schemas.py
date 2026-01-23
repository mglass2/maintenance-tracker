"""Tests for item Pydantic schemas and validation."""

import pytest
from datetime import date
from pydantic import ValidationError

from schemas.items import ItemCreateRequest, ItemResponse


class TestItemCreateRequest:
    """Tests for ItemCreateRequest validation schema."""

    def test_valid_item_creation_request(self):
        """Test creating a valid item request."""
        item_data = ItemCreateRequest(
            user_id=1,
            item_type_id=1,
            name="2015 Toyota Camry",
            acquired_at=date(2015, 6, 15),
        )
        assert item_data.user_id == 1
        assert item_data.item_type_id == 1
        assert item_data.name == "2015 Toyota Camry"
        assert item_data.acquired_at == date(2015, 6, 15)

    def test_item_without_user_id(self):
        """Test creating item without user_id (nullable field)."""
        item_data = ItemCreateRequest(
            item_type_id=1,
            name="Orphaned Item",
        )
        assert item_data.user_id is None
        assert item_data.item_type_id == 1
        assert item_data.acquired_at is None

    def test_item_without_acquired_at(self):
        """Test creating item without acquired_at (nullable field)."""
        item_data = ItemCreateRequest(
            user_id=1,
            item_type_id=1,
            name="Item Without Date",
        )
        assert item_data.acquired_at is None

    def test_name_whitespace_stripping(self):
        """Test name whitespace is stripped."""
        item_data = ItemCreateRequest(
            user_id=1,
            item_type_id=1,
            name="  My Item  ",
        )
        assert item_data.name == "My Item"

    def test_empty_name(self):
        """Test empty name raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ItemCreateRequest(
                user_id=1,
                item_type_id=1,
                name="",
            )
        assert "empty" in str(exc_info.value).lower()

    def test_whitespace_only_name(self):
        """Test name that is only whitespace raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ItemCreateRequest(
                user_id=1,
                item_type_id=1,
                name="   ",
            )
        assert "whitespace" in str(exc_info.value).lower()

    def test_name_too_long(self):
        """Test name exceeding 255 characters raises validation error."""
        long_name = "a" * 256
        with pytest.raises(ValidationError) as exc_info:
            ItemCreateRequest(
                user_id=1,
                item_type_id=1,
                name=long_name,
            )
        assert "255" in str(exc_info.value)

    def test_name_exactly_255_characters(self):
        """Test name with exactly 255 characters is valid."""
        name_255 = "a" * 255
        item_data = ItemCreateRequest(
            user_id=1,
            item_type_id=1,
            name=name_255,
        )
        assert len(item_data.name) == 255

    def test_negative_user_id(self):
        """Test negative user_id raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ItemCreateRequest(
                user_id=-1,
                item_type_id=1,
                name="Test Item",
            )
        assert "greater than 0" in str(exc_info.value).lower()

    def test_zero_user_id(self):
        """Test zero user_id raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ItemCreateRequest(
                user_id=0,
                item_type_id=1,
                name="Test Item",
            )
        assert "greater than 0" in str(exc_info.value).lower()

    def test_negative_item_type_id(self):
        """Test negative item_type_id raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ItemCreateRequest(
                user_id=1,
                item_type_id=-1,
                name="Test Item",
            )
        assert "greater than 0" in str(exc_info.value).lower()

    def test_zero_item_type_id(self):
        """Test zero item_type_id raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ItemCreateRequest(
                user_id=1,
                item_type_id=0,
                name="Test Item",
            )
        assert "greater than 0" in str(exc_info.value).lower()

    def test_missing_item_type_id(self):
        """Test missing item_type_id raises validation error."""
        with pytest.raises(ValidationError):
            ItemCreateRequest(
                user_id=1,
                name="Test Item",
            )

    def test_missing_name(self):
        """Test missing name raises validation error."""
        with pytest.raises(ValidationError):
            ItemCreateRequest(
                user_id=1,
                item_type_id=1,
            )

    def test_valid_request_with_details(self):
        """Test creating a valid item request with details field."""
        item_data = ItemCreateRequest(
            user_id=1,
            item_type_id=1,
            name="2015 Toyota Camry",
            acquired_at=date(2015, 6, 15),
            details={"current_miles": 45000, "vin": "JTDKBRFH5J5621359"},
        )
        assert item_data.details == {"current_miles": 45000, "vin": "JTDKBRFH5J5621359"}

    def test_valid_request_without_details(self):
        """Test creating a valid item request without details field."""
        item_data = ItemCreateRequest(
            user_id=1,
            item_type_id=1,
            name="2015 Toyota Camry",
            acquired_at=date(2015, 6, 15),
        )
        assert item_data.details is None

    def test_details_with_nested_objects(self):
        """Test details field with nested JSON objects."""
        item_data = ItemCreateRequest(
            user_id=1,
            item_type_id=1,
            name="Complex Item",
            details={
                "vehicle_info": {
                    "make": "Toyota",
                    "model": "Camry",
                    "year": 2015,
                },
                "current_miles": 45000,
                "features": ["heated_seats", "backup_camera"],
            },
        )
        assert item_data.details["vehicle_info"]["make"] == "Toyota"
        assert 45000 in item_data.details.values()

    def test_details_invalid_string_type(self):
        """Test that details as string raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ItemCreateRequest(
                user_id=1,
                item_type_id=1,
                name="Test Item",
                details="not_a_dict",
            )
        assert "dictionary" in str(exc_info.value).lower()

    def test_details_invalid_list_type(self):
        """Test that details as list raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ItemCreateRequest(
                user_id=1,
                item_type_id=1,
                name="Test Item",
                details=["item1", "item2"],
            )
        assert "dictionary" in str(exc_info.value).lower()

    def test_details_invalid_number_type(self):
        """Test that details as number raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ItemCreateRequest(
                user_id=1,
                item_type_id=1,
                name="Test Item",
                details=42,
            )
        assert "dictionary" in str(exc_info.value).lower()

    def test_details_empty_dict(self):
        """Test details field with empty dictionary."""
        item_data = ItemCreateRequest(
            user_id=1,
            item_type_id=1,
            name="Test Item",
            details={},
        )
        assert item_data.details == {}


class TestItemResponse:
    """Tests for ItemResponse validation schema."""

    def test_item_response_from_dict(self):
        """Test creating ItemResponse from dictionary."""
        from datetime import datetime

        item_dict = {
            "id": 1,
            "user_id": 1,
            "item_type_id": 1,
            "name": "2015 Toyota Camry",
            "description": None,
            "acquired_at": date(2015, 6, 15),
            "details": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        item_response = ItemResponse.model_validate(item_dict)
        assert item_response.id == 1
        assert item_response.user_id == 1
        assert item_response.item_type_id == 1
        assert item_response.name == "2015 Toyota Camry"

    def test_item_response_is_frozen(self):
        """Test that ItemResponse is immutable (frozen)."""
        from datetime import datetime

        item_dict = {
            "id": 1,
            "user_id": 1,
            "item_type_id": 1,
            "name": "Test Item",
            "description": None,
            "acquired_at": date(2015, 6, 15),
            "details": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        item_response = ItemResponse.model_validate(item_dict)

        # Attempting to modify should raise an error
        with pytest.raises(Exception):
            item_response.name = "Modified Name"

    def test_item_response_serialization(self):
        """Test ItemResponse serialization to JSON."""
        from datetime import datetime

        item_dict = {
            "id": 1,
            "user_id": 1,
            "item_type_id": 1,
            "name": "Test Item",
            "description": None,
            "acquired_at": date(2015, 6, 15),
            "details": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        item_response = ItemResponse.model_validate(item_dict)
        serialized = item_response.model_dump()

        assert serialized["id"] == 1
        assert serialized["user_id"] == 1
        assert serialized["item_type_id"] == 1
        assert serialized["name"] == "Test Item"
        assert serialized["acquired_at"] == date(2015, 6, 15)

    def test_item_response_with_details(self):
        """Test ItemResponse with details field."""
        from datetime import datetime

        item_dict = {
            "id": 1,
            "user_id": 1,
            "item_type_id": 1,
            "name": "2015 Toyota Camry",
            "description": None,
            "acquired_at": date(2015, 6, 15),
            "details": {"current_miles": 45000, "vin": "JTDKBRFH5J5621359"},
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        item_response = ItemResponse.model_validate(item_dict)
        assert item_response.details == {"current_miles": 45000, "vin": "JTDKBRFH5J5621359"}

    def test_item_response_without_details(self):
        """Test ItemResponse with null details field."""
        from datetime import datetime

        item_dict = {
            "id": 1,
            "user_id": 1,
            "item_type_id": 1,
            "name": "Test Item",
            "description": None,
            "acquired_at": date(2015, 6, 15),
            "details": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        item_response = ItemResponse.model_validate(item_dict)
        assert item_response.details is None

    def test_item_response_details_serialization(self):
        """Test ItemResponse serialization includes details field."""
        from datetime import datetime

        item_dict = {
            "id": 1,
            "user_id": 1,
            "item_type_id": 1,
            "name": "Test Item",
            "description": None,
            "acquired_at": date(2015, 6, 15),
            "details": {"engine_hours": 150, "model_year": 2020},
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        item_response = ItemResponse.model_validate(item_dict)
        serialized = item_response.model_dump()
        assert serialized["details"] == {"engine_hours": 150, "model_year": 2020}
