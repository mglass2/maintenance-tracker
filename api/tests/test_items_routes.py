"""Tests for item routes endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from models.user import User
from models.item import Item
from models.item_type import ItemType


class TestCreateItemWithXUserIdHeader:
    """Tests for POST /items with x-user-id header."""

    @pytest.fixture
    def setup_test_data(self, db: Session):
        """Create test user and item type."""
        # Create test user
        user = User(
            name="Test User",
            email="test@example.com",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Create test item type
        item_type = ItemType(
            name="Car",
            description="Automobile",
        )
        db.add(item_type)
        db.commit()
        db.refresh(item_type)

        yield {"user": user, "item_type": item_type}

    def test_create_item_with_x_user_id_header(self, client: TestClient, setup_test_data):
        """Test that x-user-id header populates user_id when not in body."""
        user_id = setup_test_data["user"].id
        item_type_id = setup_test_data["item_type"].id

        response = client.post(
            "/items",
            json={
                "item_type_id": item_type_id,
                "name": "My Car",
                "acquired_at": "2015-06-15",
            },
            headers={"x-user-id": str(user_id)},
        )

        assert response.status_code == 201
        data = response.json()
        assert "data" in data
        assert data["data"]["user_id"] == user_id
        assert data["data"]["name"] == "My Car"

    def test_create_item_body_user_id_takes_precedence(self, client: TestClient, db: Session, setup_test_data):
        """Test that user_id in body takes precedence over x-user-id header."""
        # Create second user
        user2 = User(
            name="Second User",
            email="second@example.com",
        )
        db.add(user2)
        db.commit()
        db.refresh(user2)

        item_type_id = setup_test_data["item_type"].id
        body_user_id = user2.id
        header_user_id = setup_test_data["user"].id

        response = client.post(
            "/items",
            json={
                "user_id": body_user_id,
                "item_type_id": item_type_id,
                "name": "My Car",
            },
            headers={"x-user-id": str(header_user_id)},
        )

        assert response.status_code == 201
        data = response.json()
        # Body user_id should be used, not header
        assert data["data"]["user_id"] == body_user_id

    def test_create_item_invalid_x_user_id_header_format(self, client: TestClient, setup_test_data):
        """Test handling of invalid x-user-id header format."""
        item_type_id = setup_test_data["item_type"].id

        response = client.post(
            "/items",
            json={
                "item_type_id": item_type_id,
                "name": "My Car",
            },
            headers={"x-user-id": "not-a-number"},
        )

        # Should fail validation since user_id is still None and required
        assert response.status_code in (400, 422)

    def test_create_item_without_x_user_id_header_requires_body(self, client: TestClient, setup_test_data):
        """Test that user_id must be provided in body if no x-user-id header."""
        item_type_id = setup_test_data["item_type"].id

        response = client.post(
            "/items",
            json={
                "item_type_id": item_type_id,
                "name": "My Car",
            },
        )

        # Should fail validation since user_id is missing
        assert response.status_code in (400, 422)

    def test_create_item_with_minimal_fields_and_header(self, client: TestClient, setup_test_data):
        """Test creating item with only required fields and x-user-id header."""
        user_id = setup_test_data["user"].id
        item_type_id = setup_test_data["item_type"].id

        response = client.post(
            "/items",
            json={
                "item_type_id": item_type_id,
                "name": "Minimal Item",
            },
            headers={"x-user-id": str(user_id)},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["data"]["user_id"] == user_id
        assert data["data"]["name"] == "Minimal Item"
        assert data["data"]["acquired_at"] is None
        assert data["data"]["details"] is None

    def test_create_item_with_details_and_header(self, client: TestClient, setup_test_data):
        """Test creating item with details and x-user-id header."""
        user_id = setup_test_data["user"].id
        item_type_id = setup_test_data["item_type"].id

        response = client.post(
            "/items",
            json={
                "item_type_id": item_type_id,
                "name": "2015 Toyota Camry",
                "acquired_at": "2015-06-15",
                "details": {"mileage": 45000, "vin": "JTDKBRFH5J5621359"},
            },
            headers={"x-user-id": str(user_id)},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["data"]["user_id"] == user_id
        assert data["data"]["details"]["mileage"] == 45000
        assert data["data"]["details"]["vin"] == "JTDKBRFH5J5621359"

    def test_create_item_nonexistent_user_in_header(self, client: TestClient, setup_test_data):
        """Test that nonexistent user_id in header still fails validation."""
        item_type_id = setup_test_data["item_type"].id
        nonexistent_user_id = 99999

        response = client.post(
            "/items",
            json={
                "item_type_id": item_type_id,
                "name": "My Car",
            },
            headers={"x-user-id": str(nonexistent_user_id)},
        )

        # Should fail because user doesn't exist
        assert response.status_code == 404

    def test_create_item_x_user_id_zero_invalid(self, client: TestClient, setup_test_data):
        """Test that zero user_id is rejected."""
        item_type_id = setup_test_data["item_type"].id

        response = client.post(
            "/items",
            json={
                "item_type_id": item_type_id,
                "name": "My Car",
            },
            headers={"x-user-id": "0"},
        )

        # Should fail validation
        assert response.status_code in (400, 422)


class TestGetItemTypesEndpoint:
    """Tests for GET /item_types endpoint."""

    @pytest.fixture
    def setup_item_types(self, db: Session):
        """Create test item types."""
        types = [
            ItemType(name="Car", description="Automobile"),
            ItemType(name="House", description="Residential property"),
            ItemType(name="Bicycle", description="Two-wheeled vehicle"),
            ItemType(name="Deleted", description="Should not appear", is_deleted=True),
        ]
        db.add_all(types)
        db.commit()
        yield types

    def test_get_item_types_success(self, client: TestClient, setup_item_types):
        """Test successfully getting all item types."""
        response = client.get("/item_types")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "item_types" in data["data"]
        assert data["data"]["count"] == 3

    def test_get_item_types_excludes_deleted(self, client: TestClient, setup_item_types):
        """Test that deleted item types are excluded."""
        response = client.get("/item_types")

        assert response.status_code == 200
        data = response.json()
        item_types = data["data"]["item_types"]

        names = [item_type["name"] for item_type in item_types]
        assert "Car" in names
        assert "House" in names
        assert "Bicycle" in names
        assert "Deleted" not in names

    def test_get_item_types_response_structure(self, client: TestClient, setup_item_types):
        """Test response structure for item types."""
        response = client.get("/item_types")

        assert response.status_code == 200
        data = response.json()

        # Check top-level structure
        assert "data" in data
        assert "message" in data

        # Check data structure
        assert "item_types" in data["data"]
        assert "count" in data["data"]

        # Check individual item structure
        item_types = data["data"]["item_types"]
        assert len(item_types) > 0

        for item_type in item_types:
            assert "id" in item_type
            assert "name" in item_type
            assert "description" in item_type
            assert "created_at" in item_type
            assert "updated_at" in item_type

    def test_get_item_types_ordered_by_name(self, client: TestClient, setup_item_types):
        """Test that item types are ordered by name."""
        response = client.get("/item_types")

        assert response.status_code == 200
        data = response.json()
        item_types = data["data"]["item_types"]

        names = [item_type["name"] for item_type in item_types]
        # Should be alphabetically ordered (excluding deleted)
        expected_order = ["Bicycle", "Car", "House"]
        assert names == expected_order

    def test_get_item_types_empty_response(self, client: TestClient, db: Session):
        """Test getting item types when none exist."""
        response = client.get("/item_types")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["count"] == 0
        assert len(data["data"]["item_types"]) == 0

    def test_get_item_types_only_deleted(self, client: TestClient, db: Session):
        """Test that only deleted types returns empty list."""
        db.add(ItemType(name="Deleted 1", is_deleted=True))
        db.add(ItemType(name="Deleted 2", is_deleted=True))
        db.commit()

        response = client.get("/item_types")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["count"] == 0
        assert len(data["data"]["item_types"]) == 0

    def test_get_item_types_count_accuracy(self, client: TestClient, setup_item_types):
        """Test that count matches actual number of items returned."""
        response = client.get("/item_types")

        assert response.status_code == 200
        data = response.json()
        count = data["data"]["count"]
        actual_count = len(data["data"]["item_types"])

        assert count == actual_count

    def test_get_item_types_includes_description(self, client: TestClient, db: Session):
        """Test that descriptions are included in response."""
        db.add(ItemType(name="Car", description="Four-wheeled vehicle"))
        db.commit()

        response = client.get("/item_types")

        assert response.status_code == 200
        data = response.json()
        item_types = data["data"]["item_types"]

        assert len(item_types) > 0
        car = next(it for it in item_types if it["name"] == "Car")
        assert car["description"] == "Four-wheeled vehicle"

    def test_get_item_types_without_description(self, client: TestClient, db: Session):
        """Test item types without description return None."""
        db.add(ItemType(name="No Description Type"))
        db.commit()

        response = client.get("/item_types")

        assert response.status_code == 200
        data = response.json()
        item_types = data["data"]["item_types"]

        item_without_desc = next(it for it in item_types if it["name"] == "No Description Type")
        assert item_without_desc["description"] is None
