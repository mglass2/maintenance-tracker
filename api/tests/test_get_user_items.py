"""Tests for getting user items endpoint."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from models.user import User
from models.item import Item


class TestGetUserItems:
    """Tests for GET /items/users/{user_id} endpoint."""

    @pytest.fixture
    def setup_test_data(self, db: Session):
        """Create test user and items."""
        # Create test user
        user = User(
            name="Test User",
            email="test@example.com",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Create test items
        item1 = Item(
            user_id=user.id,
            item_type_id=1,
            name="Car",
        )
        item2 = Item(
            user_id=user.id,
            item_type_id=1,
            name="Bicycle",
        )
        db.add_all([item1, item2])
        db.commit()

        yield {"user": user, "items": [item1, item2]}

    def test_get_user_items_success(self, client: TestClient, setup_test_data):
        """Test successfully getting items for a user."""
        user_id = setup_test_data["user"].id
        response = client.get(f"/items/users/{user_id}")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "items" in data["data"]
        assert data["data"]["count"] == 2


    def test_get_user_items_no_items(self, client: TestClient, db: Session):
        """Test getting items for user with no items returns empty list."""
        # Create user without items
        user = User(
            name="Empty User",
            email="empty@example.com",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        response = client.get(f"/items/users/{user.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["count"] == 0
        assert len(data["data"]["items"]) == 0

    def test_get_user_items_response_format(self, client: TestClient, setup_test_data):
        """Test response format for user items."""
        user_id = setup_test_data["user"].id
        response = client.get(f"/items/users/{user_id}")

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "data" in data
        assert "message" in data

        # Check items structure
        items = data["data"]["items"]
        assert len(items) > 0

        for item in items:
            assert "id" in item
            assert "user_id" in item
            assert "item_type_id" in item
            assert "name" in item
            assert "description" in item
            assert "acquired_at" in item
            assert "created_at" in item
            assert "updated_at" in item

    def test_get_user_items_excludes_deleted(self, client: TestClient, db: Session):
        """Test that deleted items are excluded from results."""
        # Create user
        user = User(
            name="User With Deleted Items",
            email="deleted@example.com",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Create items
        item1 = Item(
            user_id=user.id,
            item_type_id=1,
            name="Active Item",
        )
        item2 = Item(
            user_id=user.id,
            item_type_id=1,
            name="Deleted Item",
            is_deleted=True,
        )
        db.add_all([item1, item2])
        db.commit()

        response = client.get(f"/items/users/{user.id}")

        assert response.status_code == 200
        data = response.json()
        # Should only have 1 item (the non-deleted one)
        assert data["data"]["count"] == 1
        assert data["data"]["items"][0]["name"] == "Active Item"

    def test_get_user_items_response_includes_message(self, client: TestClient, setup_test_data):
        """Test that response includes appropriate message."""
        user_id = setup_test_data["user"].id
        response = client.get(f"/items/users/{user_id}")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Retrieved" in data["message"]
        assert str(user_id) in data["message"]
