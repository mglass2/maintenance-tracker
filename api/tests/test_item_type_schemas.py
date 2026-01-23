"""Tests for item type schema validation."""

from datetime import datetime
import pytest
from pydantic import ValidationError
from schemas.item_types import ItemTypeCreateRequest, ItemTypeResponse


class TestItemTypeCreateRequest:
    """Tests for ItemTypeCreateRequest schema validation."""

    def test_create_item_type_valid_request(self):
        """Test valid item type creation request."""
        item_type_data = ItemTypeCreateRequest(
            name="Automobile",
            description="Vehicles for personal transportation",
        )

        assert item_type_data.name == "Automobile"
        assert item_type_data.description == "Vehicles for personal transportation"

    def test_create_item_type_minimal_required_fields(self):
        """Test item type creation with only required fields."""
        item_type_data = ItemTypeCreateRequest(
            name="House",
        )

        assert item_type_data.name == "House"
        assert item_type_data.description is None

    def test_create_item_type_name_whitespace_stripped(self):
        """Test name whitespace is stripped."""
        item_type_data = ItemTypeCreateRequest(
            name="  Motorcycle  ",
        )
        assert item_type_data.name == "Motorcycle"

    def test_create_item_type_empty_name_rejected(self):
        """Test empty name is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ItemTypeCreateRequest(
                name="",
            )
        assert "empty" in str(exc_info.value).lower()

    def test_create_item_type_whitespace_only_name_rejected(self):
        """Test whitespace-only name is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ItemTypeCreateRequest(
                name="   ",
            )
        assert "empty" in str(exc_info.value).lower()

    def test_create_item_type_name_too_long_rejected(self):
        """Test name exceeding 255 characters is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ItemTypeCreateRequest(
                name="a" * 256,
            )
        assert "255" in str(exc_info.value)

    def test_create_item_type_name_exactly_255_characters(self):
        """Test name with exactly 255 characters is accepted."""
        item_type_data = ItemTypeCreateRequest(
            name="a" * 255,
        )
        assert len(item_type_data.name) == 255

    def test_create_item_type_description_whitespace_stripped(self):
        """Test description whitespace is stripped."""
        item_type_data = ItemTypeCreateRequest(
            name="Boat",
            description="  Watercraft for recreation  ",
        )
        assert item_type_data.description == "Watercraft for recreation"

    def test_create_item_type_description_whitespace_only_becomes_none(self):
        """Test description with only whitespace becomes None."""
        item_type_data = ItemTypeCreateRequest(
            name="Bike",
            description="   ",
        )
        assert item_type_data.description is None

    def test_create_item_type_description_empty_string_becomes_none(self):
        """Test empty description becomes None."""
        item_type_data = ItemTypeCreateRequest(
            name="Tool",
            description="",
        )
        assert item_type_data.description is None

    def test_create_item_type_missing_name(self):
        """Test missing name returns validation error."""
        with pytest.raises(ValidationError):
            ItemTypeCreateRequest(
                description="Some description",
            )

    def test_create_item_type_non_string_name_rejected(self):
        """Test non-string name is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ItemTypeCreateRequest(
                name=123,
            )
        assert "string" in str(exc_info.value).lower()

    def test_create_item_type_non_string_description_rejected(self):
        """Test non-string description is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ItemTypeCreateRequest(
                name="Valid Name",
                description=456,
            )
        assert "string" in str(exc_info.value).lower()


class TestItemTypeResponse:
    """Tests for ItemTypeResponse schema."""

    def test_item_type_response_immutable(self):
        """Test that ItemTypeResponse is frozen (immutable)."""
        response = ItemTypeResponse(
            id=1,
            name="Automobile",
            description="Vehicles",
            created_at=datetime(2024, 1, 15, 10, 0, 0),
            updated_at=datetime(2024, 1, 15, 10, 0, 0),
        )

        with pytest.raises(Exception):  # Should raise when trying to modify
            response.id = 999

    def test_item_type_response_serialization(self):
        """Test ItemTypeResponse serialization."""
        created = datetime(2024, 1, 15, 10, 30, 0)
        updated = datetime(2024, 1, 15, 10, 30, 0)
        response = ItemTypeResponse(
            id=5,
            name="House",
            description="Residential properties",
            created_at=created,
            updated_at=updated,
        )

        data = response.model_dump()
        assert data["id"] == 5
        assert data["name"] == "House"
        assert data["description"] == "Residential properties"
        assert data["created_at"] == created
        assert data["updated_at"] == updated
