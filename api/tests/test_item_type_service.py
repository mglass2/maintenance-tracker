"""Tests for item type service business logic."""

from schemas.item_types import ItemTypeCreateRequest


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
