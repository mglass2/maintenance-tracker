"""Tests for getting item tasks endpoint."""

import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from models.user import User
from models.item import Item
from models.task import Task


class TestGetItemTasks:
    """Tests for GET /tasks/items/{item_id} endpoint."""

    @pytest.fixture
    def setup_test_data(self, db: Session):
        """Create test item and tasks."""
        # Create test user
        user = User(
            name="Test User",
            email="test@example.com",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Create test item
        item = Item(
            user_id=user.id,
            item_type_id=1,
            name="Test Car",
        )
        db.add(item)
        db.commit()
        db.refresh(item)

        # Create test tasks
        task1 = Task(
            item_id=item.id,
            task_type_id=1,
            completed_at=date(2024, 1, 10),
            notes="Oil change",
        )
        task2 = Task(
            item_id=item.id,
            task_type_id=1,
            completed_at=date(2024, 1, 20),
            notes="Tire rotation",
        )
        db.add_all([task1, task2])
        db.commit()

        yield {"user": user, "item": item, "tasks": [task1, task2]}

    def test_get_item_tasks_success(self, client: TestClient, setup_test_data):
        """Test successfully getting tasks for an item."""
        item_id = setup_test_data["item"].id
        response = client.get(f"/tasks/items/{item_id}")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "tasks" in data["data"]
        assert data["data"]["count"] == 2

    def test_get_item_tasks_no_tasks(self, client: TestClient, db: Session):
        """Test getting tasks for item with no tasks returns empty list."""
        # Create user and item without tasks
        user = User(
            name="Empty User",
            email="empty@example.com",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        item = Item(
            user_id=user.id,
            item_type_id=1,
            name="Empty Item",
        )
        db.add(item)
        db.commit()
        db.refresh(item)

        response = client.get(f"/tasks/items/{item.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["count"] == 0
        assert len(data["data"]["tasks"]) == 0

    def test_get_item_tasks_response_format(self, client: TestClient, setup_test_data):
        """Test response format for item tasks."""
        item_id = setup_test_data["item"].id
        response = client.get(f"/tasks/items/{item_id}")

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "data" in data
        assert "message" in data

        # Check tasks structure
        tasks = data["data"]["tasks"]
        assert len(tasks) > 0

        for task in tasks:
            assert "id" in task
            assert "item_id" in task
            assert "task_type_id" in task
            assert "completed_at" in task
            assert "notes" in task
            assert "cost" in task
            assert "created_at" in task
            assert "updated_at" in task

    def test_get_item_tasks_excludes_deleted(self, client: TestClient, db: Session):
        """Test that deleted tasks are excluded from results."""
        # Create user and item
        user = User(
            name="User With Deleted Tasks",
            email="deleted@example.com",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        item = Item(
            user_id=user.id,
            item_type_id=1,
            name="Item With Deleted Tasks",
        )
        db.add(item)
        db.commit()
        db.refresh(item)

        # Create tasks
        task1 = Task(
            item_id=item.id,
            task_type_id=1,
            completed_at=date(2024, 1, 15),
            notes="Active Task",
        )
        task2 = Task(
            item_id=item.id,
            task_type_id=1,
            completed_at=date(2024, 1, 16),
            notes="Deleted Task",
            is_deleted=True,
        )
        db.add_all([task1, task2])
        db.commit()

        response = client.get(f"/tasks/items/{item.id}")

        assert response.status_code == 200
        data = response.json()
        # Should only have 1 task (the non-deleted one)
        assert data["data"]["count"] == 1
        assert data["data"]["tasks"][0]["notes"] == "Active Task"

    def test_get_item_tasks_response_includes_message(self, client: TestClient, setup_test_data):
        """Test that response includes appropriate message."""
        item_id = setup_test_data["item"].id
        response = client.get(f"/tasks/items/{item_id}")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Retrieved" in data["message"]
        assert str(item_id) in data["message"]
