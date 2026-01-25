"""Unit tests for item maintenance plan service."""

import pytest
from sqlalchemy.orm import Session
from models.item_maintenance_plan import ItemMaintenancePlan
from models.item import Item
from models.item_type import ItemType
from models.task_type import TaskType
from models.user import User
from schemas.item_maintenance_plans import ItemMaintenancePlanCreateRequest
from services.item_maintenance_plan_service import create_item_maintenance_plan
from services.exceptions import ResourceNotFoundError, DuplicateNameError


class TestCreateItemMaintenancePlan:
    """Tests for create_item_maintenance_plan service function."""

    def test_create_with_valid_ids(self, db: Session):
        """Test creating item maintenance plan with valid item and task types."""
        # Create user
        user = User(name="testuser", email="testuser@example.com")
        db.add(user)
        db.commit()
        db.refresh(user)

        # Create item type
        item_type = ItemType(name="Test Car")
        db.add(item_type)
        db.commit()
        db.refresh(item_type)

        # Create item
        item = Item(user_id=user.id, item_type_id=item_type.id, name="My Car")
        db.add(item)
        db.commit()
        db.refresh(item)

        # Create task type
        task_type = TaskType(name="Oil Change", item_type_id=item_type.id)
        db.add(task_type)
        db.commit()
        db.refresh(task_type)

        # Create item maintenance plan
        plan_data = ItemMaintenancePlanCreateRequest(
            item_id=item.id,
            task_type_id=task_type.id,
            time_interval_days=30,
        )

        plan = create_item_maintenance_plan(db, plan_data)

        assert plan.id is not None
        assert plan.item_id == item.id
        assert plan.task_type_id == task_type.id
        assert plan.time_interval_days == 30
        assert plan.custom_interval is None
        assert plan.is_deleted is False

    def test_create_with_custom_interval(self, db: Session):
        """Test creating item maintenance plan with custom_interval."""
        # Create user
        user = User(name="testuser2", email="testuser2@example.com")
        db.add(user)
        db.commit()
        db.refresh(user)

        # Create item type
        item_type = ItemType(name="Test Vehicle")
        db.add(item_type)
        db.commit()
        db.refresh(item_type)

        # Create item
        item = Item(user_id=user.id, item_type_id=item_type.id, name="My Vehicle")
        db.add(item)
        db.commit()
        db.refresh(item)

        # Create task type
        task_type = TaskType(name="Tire Rotation", item_type_id=item_type.id)
        db.add(task_type)
        db.commit()
        db.refresh(task_type)

        # Create item maintenance plan with custom interval
        custom_interval = {"type": "mileage", "value": 5000, "unit": "miles"}
        plan_data = ItemMaintenancePlanCreateRequest(
            item_id=item.id,
            task_type_id=task_type.id,
            time_interval_days=90,
            custom_interval=custom_interval,
        )

        plan = create_item_maintenance_plan(db, plan_data)

        assert plan.custom_interval == custom_interval

    def test_create_nonexistent_item_raises_error(self, db: Session):
        """Test creating with nonexistent item_id raises ResourceNotFoundError."""
        # Create a dummy item type for the task type (since task_type.item_type_id is required)
        item_type_dummy = ItemType(name="Dummy Item Type")
        db.add(item_type_dummy)
        db.commit()
        db.refresh(item_type_dummy)

        # Create task type
        task_type = TaskType(name="Test Task", item_type_id=item_type_dummy.id)
        db.add(task_type)
        db.commit()
        db.refresh(task_type)

        # Try to create plan with nonexistent item_id
        plan_data = ItemMaintenancePlanCreateRequest(
            item_id=999999,
            task_type_id=task_type.id,
            time_interval_days=30,
        )

        with pytest.raises(ResourceNotFoundError) as exc_info:
            create_item_maintenance_plan(db, plan_data)
        assert "item" in str(exc_info.value).lower()

    def test_create_nonexistent_task_type_raises_error(self, db: Session):
        """Test creating with nonexistent task_type_id raises ResourceNotFoundError."""
        # Create user
        user = User(name="testuser3", email="testuser3@example.com")
        db.add(user)
        db.commit()
        db.refresh(user)

        # Create item type
        item_type = ItemType(name="Test Type")
        db.add(item_type)
        db.commit()
        db.refresh(item_type)

        # Create item
        item = Item(user_id=user.id, item_type_id=item_type.id, name="Test Item")
        db.add(item)
        db.commit()
        db.refresh(item)

        # Try to create plan with nonexistent task_type_id
        plan_data = ItemMaintenancePlanCreateRequest(
            item_id=item.id,
            task_type_id=999999,
            time_interval_days=30,
        )

        with pytest.raises(ResourceNotFoundError) as exc_info:
            create_item_maintenance_plan(db, plan_data)
        assert "task type" in str(exc_info.value).lower()

    def test_create_duplicate_combination_raises_error(self, db: Session):
        """Test creating duplicate item/task_type combination raises DuplicateNameError."""
        # Create user
        user = User(name="testuser4", email="testuser4@example.com")
        db.add(user)
        db.commit()
        db.refresh(user)

        # Create item type
        item_type = ItemType(name="Duplicate Test Car")
        db.add(item_type)
        db.commit()
        db.refresh(item_type)

        # Create item
        item = Item(user_id=user.id, item_type_id=item_type.id, name="Duplicate Item")
        db.add(item)
        db.commit()
        db.refresh(item)

        # Create task type
        task_type = TaskType(name="Duplicate Test Task", item_type_id=item_type.id)
        db.add(task_type)
        db.commit()
        db.refresh(task_type)

        # Create first item maintenance plan
        plan_data1 = ItemMaintenancePlanCreateRequest(
            item_id=item.id,
            task_type_id=task_type.id,
            time_interval_days=30,
        )
        create_item_maintenance_plan(db, plan_data1)

        # Try to create duplicate
        plan_data2 = ItemMaintenancePlanCreateRequest(
            item_id=item.id,
            task_type_id=task_type.id,
            time_interval_days=60,
        )

        with pytest.raises(DuplicateNameError) as exc_info:
            create_item_maintenance_plan(db, plan_data2)
        assert "already exists" in str(exc_info.value).lower()

    def test_create_deleted_item_raises_error(self, db: Session):
        """Test creating with deleted item raises ResourceNotFoundError."""
        # Create user
        user = User(name="testuser5", email="testuser5@example.com")
        db.add(user)
        db.commit()
        db.refresh(user)

        # Create item type
        item_type = ItemType(name="Item Type for Deleted")
        db.add(item_type)
        db.commit()
        db.refresh(item_type)

        # Create and delete item
        item = Item(user_id=user.id, item_type_id=item_type.id, name="Deleted Item", is_deleted=True)
        db.add(item)
        db.commit()
        db.refresh(item)

        # Create task type
        task_type = TaskType(name="Task for Deleted Item", item_type_id=item_type.id)
        db.add(task_type)
        db.commit()
        db.refresh(task_type)

        # Try to create plan with deleted item
        plan_data = ItemMaintenancePlanCreateRequest(
            item_id=item.id,
            task_type_id=task_type.id,
            time_interval_days=30,
        )

        with pytest.raises(ResourceNotFoundError) as exc_info:
            create_item_maintenance_plan(db, plan_data)
        assert "not found or is deleted" in str(exc_info.value).lower()

    def test_create_deleted_task_type_raises_error(self, db: Session):
        """Test creating with deleted task_type raises ResourceNotFoundError."""
        # Create user
        user = User(name="testuser6", email="testuser6@example.com")
        db.add(user)
        db.commit()
        db.refresh(user)

        # Create item type
        item_type = ItemType(name="Item Type for Task")
        db.add(item_type)
        db.commit()
        db.refresh(item_type)

        # Create item
        item = Item(user_id=user.id, item_type_id=item_type.id, name="Item for Task")
        db.add(item)
        db.commit()
        db.refresh(item)

        # Create and delete task type
        task_type = TaskType(name="Deleted Task Type", item_type_id=item_type.id, is_deleted=True)
        db.add(task_type)
        db.commit()
        db.refresh(task_type)

        # Try to create plan with deleted task_type
        plan_data = ItemMaintenancePlanCreateRequest(
            item_id=item.id,
            task_type_id=task_type.id,
            time_interval_days=30,
        )

        with pytest.raises(ResourceNotFoundError) as exc_info:
            create_item_maintenance_plan(db, plan_data)
        assert "not found or is deleted" in str(exc_info.value).lower()

    def test_create_multiple_different_combinations(self, db: Session):
        """Test creating multiple plans with same item but different task types."""
        # Create user
        user = User(name="testuser7", email="testuser7@example.com")
        db.add(user)
        db.commit()
        db.refresh(user)

        # Create item type
        item_type = ItemType(name="Multi Task Item Type")
        db.add(item_type)
        db.commit()
        db.refresh(item_type)

        # Create item
        item = Item(user_id=user.id, item_type_id=item_type.id, name="Multi Task Item")
        db.add(item)
        db.commit()
        db.refresh(item)

        # Create two task types
        task_type1 = TaskType(name="Task Type 1", item_type_id=item_type.id)
        task_type2 = TaskType(name="Task Type 2", item_type_id=item_type.id)
        db.add_all([task_type1, task_type2])
        db.commit()
        db.refresh(task_type1)
        db.refresh(task_type2)

        # Create first plan
        plan_data1 = ItemMaintenancePlanCreateRequest(
            item_id=item.id,
            task_type_id=task_type1.id,
            time_interval_days=30,
        )
        plan1 = create_item_maintenance_plan(db, plan_data1)

        # Create second plan (different task type, same item)
        plan_data2 = ItemMaintenancePlanCreateRequest(
            item_id=item.id,
            task_type_id=task_type2.id,
            time_interval_days=60,
        )
        plan2 = create_item_maintenance_plan(db, plan_data2)

        # Verify both were created successfully
        assert plan1.id is not None
        assert plan2.id is not None
        assert plan1.id != plan2.id
        assert plan1.item_id == plan2.item_id
        assert plan1.task_type_id != plan2.task_type_id
