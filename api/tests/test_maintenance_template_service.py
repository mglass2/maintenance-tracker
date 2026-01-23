"""Unit tests for maintenance template service."""

import pytest
from sqlalchemy.orm import Session
from models.maintenance_template import MaintenanceTemplate
from models.item_type import ItemType
from models.task_type import TaskType
from schemas.maintenance_templates import MaintenanceTemplateCreateRequest
from services.maintenance_template_service import create_maintenance_template
from services.exceptions import ResourceNotFoundError, DuplicateNameError


class TestCreateMaintenanceTemplate:
    """Tests for create_maintenance_template service function."""

    def test_create_with_valid_ids(self, db: Session):
        """Test creating maintenance template with valid item and task types."""
        # Create item type
        item_type = ItemType(name="Test Car")
        db.add(item_type)
        db.commit()
        db.refresh(item_type)

        # Create task type
        task_type = TaskType(name="Oil Change")
        db.add(task_type)
        db.commit()
        db.refresh(task_type)

        # Create maintenance template
        template_data = MaintenanceTemplateCreateRequest(
            item_type_id=item_type.id,
            task_type_id=task_type.id,
            time_interval_days=30,
        )

        template = create_maintenance_template(db, template_data)

        assert template.id is not None
        assert template.item_type_id == item_type.id
        assert template.task_type_id == task_type.id
        assert template.time_interval_days == 30
        assert template.custom_interval is None
        assert template.is_deleted is False

    def test_create_with_custom_interval(self, db: Session):
        """Test creating maintenance template with custom_interval."""
        # Create item type
        item_type = ItemType(name="Test Vehicle")
        db.add(item_type)
        db.commit()
        db.refresh(item_type)

        # Create task type
        task_type = TaskType(name="Tire Rotation")
        db.add(task_type)
        db.commit()
        db.refresh(task_type)

        # Create maintenance template with custom interval
        custom_interval = {"type": "mileage", "value": 5000, "unit": "miles"}
        template_data = MaintenanceTemplateCreateRequest(
            item_type_id=item_type.id,
            task_type_id=task_type.id,
            time_interval_days=90,
            custom_interval=custom_interval,
        )

        template = create_maintenance_template(db, template_data)

        assert template.custom_interval == custom_interval

    def test_create_nonexistent_item_type_raises_error(self, db: Session):
        """Test creating with nonexistent item_type_id raises ResourceNotFoundError."""
        # Create task type
        task_type = TaskType(name="Test Task")
        db.add(task_type)
        db.commit()
        db.refresh(task_type)

        # Try to create template with nonexistent item_type_id
        template_data = MaintenanceTemplateCreateRequest(
            item_type_id=999999,
            task_type_id=task_type.id,
            time_interval_days=30,
        )

        with pytest.raises(ResourceNotFoundError) as exc_info:
            create_maintenance_template(db, template_data)
        assert "item type" in str(exc_info.value).lower()

    def test_create_nonexistent_task_type_raises_error(self, db: Session):
        """Test creating with nonexistent task_type_id raises ResourceNotFoundError."""
        # Create item type
        item_type = ItemType(name="Test Type")
        db.add(item_type)
        db.commit()
        db.refresh(item_type)

        # Try to create template with nonexistent task_type_id
        template_data = MaintenanceTemplateCreateRequest(
            item_type_id=item_type.id,
            task_type_id=999999,
            time_interval_days=30,
        )

        with pytest.raises(ResourceNotFoundError) as exc_info:
            create_maintenance_template(db, template_data)
        assert "task type" in str(exc_info.value).lower()

    def test_create_duplicate_combination_raises_error(self, db: Session):
        """Test creating duplicate item_type/task_type combination raises DuplicateNameError."""
        # Create item type
        item_type = ItemType(name="Duplicate Test Car")
        db.add(item_type)
        db.commit()
        db.refresh(item_type)

        # Create task type
        task_type = TaskType(name="Duplicate Test Task")
        db.add(task_type)
        db.commit()
        db.refresh(task_type)

        # Create first maintenance template
        template_data1 = MaintenanceTemplateCreateRequest(
            item_type_id=item_type.id,
            task_type_id=task_type.id,
            time_interval_days=30,
        )
        create_maintenance_template(db, template_data1)

        # Try to create duplicate
        template_data2 = MaintenanceTemplateCreateRequest(
            item_type_id=item_type.id,
            task_type_id=task_type.id,
            time_interval_days=60,
        )

        with pytest.raises(DuplicateNameError) as exc_info:
            create_maintenance_template(db, template_data2)
        assert "already exists" in str(exc_info.value).lower()

    def test_create_deleted_item_type_raises_error(self, db: Session):
        """Test creating with deleted item_type raises ResourceNotFoundError."""
        # Create and delete item type
        item_type = ItemType(name="Deleted Item Type", is_deleted=True)
        db.add(item_type)
        db.commit()
        db.refresh(item_type)

        # Create task type
        task_type = TaskType(name="Task for Deleted Item")
        db.add(task_type)
        db.commit()
        db.refresh(task_type)

        # Try to create template with deleted item_type
        template_data = MaintenanceTemplateCreateRequest(
            item_type_id=item_type.id,
            task_type_id=task_type.id,
            time_interval_days=30,
        )

        with pytest.raises(ResourceNotFoundError) as exc_info:
            create_maintenance_template(db, template_data)
        assert "not found or is deleted" in str(exc_info.value).lower()

    def test_create_deleted_task_type_raises_error(self, db: Session):
        """Test creating with deleted task_type raises ResourceNotFoundError."""
        # Create item type
        item_type = ItemType(name="Item for Deleted Task")
        db.add(item_type)
        db.commit()
        db.refresh(item_type)

        # Create and delete task type
        task_type = TaskType(name="Deleted Task Type", is_deleted=True)
        db.add(task_type)
        db.commit()
        db.refresh(task_type)

        # Try to create template with deleted task_type
        template_data = MaintenanceTemplateCreateRequest(
            item_type_id=item_type.id,
            task_type_id=task_type.id,
            time_interval_days=30,
        )

        with pytest.raises(ResourceNotFoundError) as exc_info:
            create_maintenance_template(db, template_data)
        assert "not found or is deleted" in str(exc_info.value).lower()

    def test_create_multiple_different_combinations(self, db: Session):
        """Test creating multiple templates with same item type but different task types."""
        # Create item type
        item_type = ItemType(name="Multi Task Item")
        db.add(item_type)
        db.commit()
        db.refresh(item_type)

        # Create two task types
        task_type1 = TaskType(name="Task Type 1")
        task_type2 = TaskType(name="Task Type 2")
        db.add_all([task_type1, task_type2])
        db.commit()
        db.refresh(task_type1)
        db.refresh(task_type2)

        # Create first template
        template_data1 = MaintenanceTemplateCreateRequest(
            item_type_id=item_type.id,
            task_type_id=task_type1.id,
            time_interval_days=30,
        )
        template1 = create_maintenance_template(db, template_data1)

        # Create second template (different task type, same item type)
        template_data2 = MaintenanceTemplateCreateRequest(
            item_type_id=item_type.id,
            task_type_id=task_type2.id,
            time_interval_days=60,
        )
        template2 = create_maintenance_template(db, template_data2)

        # Verify both were created successfully
        assert template1.id is not None
        assert template2.id is not None
        assert template1.id != template2.id
        assert template1.item_type_id == template2.item_type_id
        assert template1.task_type_id != template2.task_type_id
