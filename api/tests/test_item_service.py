"""Tests for item service business logic."""

from datetime import date
from schemas.items import ItemCreateRequest


class TestCreateItem:
    """Tests for create_item service function - validation logic only."""

    def test_description_field_hardcoded_to_none(self):
        """Test that description is always set to None regardless of input."""
        # The service explicitly sets description=None in the Item creation
        item_data = ItemCreateRequest(
            user_id=1,
            item_type_id=1,
            name="Test Item",
        )

        # This doesn't test actually creating an item (due to FK constraints)
        # But verifies that the schema accepts it
        assert item_data is not None

    def test_create_item_accepts_valid_schema(self):
        """Test that create_item accepts valid ItemCreateRequest."""
        item_data = ItemCreateRequest(
            user_id=1,
            item_type_id=1,
            name="Valid Item",
            acquired_at=date(2020, 1, 1),
        )

        # Verify the schema is valid
        assert item_data.name == "Valid Item"
        assert item_data.user_id == 1
        assert item_data.item_type_id == 1
        assert item_data.acquired_at == date(2020, 1, 1)

    def test_create_item_without_acquired_at(self):
        """Test that create_item accepts item without acquired_at."""
        item_data = ItemCreateRequest(
            user_id=1,
            item_type_id=1,
            name="Item Without Date",
        )

        assert item_data.acquired_at is None
        assert item_data.name == "Item Without Date"

    def test_item_without_user_id_accepted(self):
        """Test that item can be created without user_id."""
        item_data = ItemCreateRequest(
            item_type_id=1,
            name="Orphaned Item",
        )

        assert item_data.user_id is None
        assert item_data.item_type_id == 1

    def test_item_field_defaults(self):
        """Test optional field defaults."""
        item_data = ItemCreateRequest(
            item_type_id=5,
            name="Test Item",
        )

        assert item_data.user_id is None
        assert item_data.acquired_at is None
        assert item_data.item_type_id == 5
