"""Tests for item type service business logic."""

import pytest
from sqlalchemy.orm import Session
from schemas.item_types import ItemTypeCreateRequest
from models.item_type import ItemType
from services.item_type_service import get_all_item_types


class TestCreateItemType:
    """Tests for create_item_type service function - validation logic only."""

    def test_create_item_type_accepts_valid_schema(self):
        """Test that create_item_type accepts valid ItemTypeCreateRequest."""
        item_type_data = ItemTypeCreateRequest(
            name="Automobile",
            description="Vehicles for personal transportation",
        )

        # Verify the schema is valid
        assert item_type_data.name == "Automobile"
        assert item_type_data.description == "Vehicles for personal transportation"

    def test_create_item_type_without_description(self):
        """Test that create_item_type accepts item type without description."""
        item_type_data = ItemTypeCreateRequest(
            name="Snowblower",
        )

        assert item_type_data.description is None
        assert item_type_data.name == "Snowblower"

    def test_create_item_type_field_defaults(self):
        """Test optional field defaults."""
        item_type_data = ItemTypeCreateRequest(
            name="Bicycle",
        )

        assert item_type_data.description is None
        assert item_type_data.name == "Bicycle"


class TestGetAllItemTypes:
    """Tests for get_all_item_types service function."""

    def test_get_all_item_types_returns_all_non_deleted(self, db: Session):
        """Test that get_all_item_types returns all non-deleted item types."""
        # Create test item types
        car_type = ItemType(name="Car", description="Automobile")
        house_type = ItemType(name="House", description="Residential property")
        deleted_type = ItemType(name="Deleted Type", description="Should not appear", is_deleted=True)

        db.add_all([car_type, house_type, deleted_type])
        db.commit()

        result = get_all_item_types(db)

        assert len(result) == 2
        names = [item_type.name for item_type in result]
        assert "Car" in names
        assert "House" in names
        assert "Deleted Type" not in names

    def test_get_all_item_types_ordered_by_name(self, db: Session):
        """Test that item types are ordered by name."""
        # Create test item types
        db.add(ItemType(name="Zebra", description="Animal"))
        db.add(ItemType(name="Apple", description="Fruit"))
        db.add(ItemType(name="Monkey", description="Animal"))
        db.commit()

        result = get_all_item_types(db)

        assert len(result) == 3
        names = [item_type.name for item_type in result]
        assert names == ["Apple", "Monkey", "Zebra"]

    def test_get_all_item_types_empty_when_none_exist(self, db: Session):
        """Test that get_all_item_types returns empty list when no types exist."""
        result = get_all_item_types(db)

        assert result == []
        assert len(result) == 0

    def test_get_all_item_types_excludes_all_deleted(self, db: Session):
        """Test that all deleted item types are excluded."""
        # Create only deleted item types
        db.add(ItemType(name="Type 1", is_deleted=True))
        db.add(ItemType(name="Type 2", is_deleted=True))
        db.commit()

        result = get_all_item_types(db)

        assert result == []

    def test_get_all_item_types_partial_deletion(self, db: Session):
        """Test with mix of deleted and non-deleted types."""
        db.add(ItemType(name="Active 1", description="First active"))
        db.add(ItemType(name="Deleted 1", is_deleted=True))
        db.add(ItemType(name="Active 2", description="Second active"))
        db.add(ItemType(name="Deleted 2", is_deleted=True))
        db.commit()

        result = get_all_item_types(db)

        assert len(result) == 2
        names = sorted([item_type.name for item_type in result])
        assert names == ["Active 1", "Active 2"]
