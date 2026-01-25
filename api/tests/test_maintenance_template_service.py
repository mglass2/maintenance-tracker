"""Unit tests for maintenance template service."""

import pytest
from sqlalchemy.orm import Session
from models.maintenance_template import MaintenanceTemplate
from models.item_type import ItemType
from models.task_type import TaskType
from schemas.maintenance_templates import MaintenanceTemplateCreateRequest
from services.maintenance_template_service import (
    create_maintenance_template,
    get_all_templates_grouped_by_item_type,
)
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


class TestGetAllTemplatesGroupedByItemType:
    """Tests for get_all_templates_grouped_by_item_type service function."""

    def test_empty_database(self, db: Session):
        """Test retrieving from empty database returns empty item_types list."""
        result = get_all_templates_grouped_by_item_type(db)

        assert result == {"item_types": []}

    def test_single_item_type_single_template(self, db: Session):
        """Test retrieving single item type with single template."""
        # Create item type
        item_type = ItemType(name="Car")
        db.add(item_type)
        db.commit()
        db.refresh(item_type)

        # Create task type
        task_type = TaskType(name="Oil Change")
        db.add(task_type)
        db.commit()
        db.refresh(task_type)

        # Create template
        template = MaintenanceTemplate(
            item_type_id=item_type.id,
            task_type_id=task_type.id,
            time_interval_days=30,
        )
        db.add(template)
        db.commit()

        result = get_all_templates_grouped_by_item_type(db)

        assert len(result["item_types"]) == 1
        assert result["item_types"][0]["item_type_name"] == "Car"
        assert result["item_types"][0]["item_type_id"] == item_type.id
        assert len(result["item_types"][0]["templates"]) == 1
        assert result["item_types"][0]["templates"][0]["task_type_name"] == "Oil Change"
        assert result["item_types"][0]["templates"][0]["time_interval_days"] == 30

    def test_multiple_item_types(self, db: Session):
        """Test retrieving multiple item types with templates."""
        # Create item types
        item_type1 = ItemType(name="Car")
        item_type2 = ItemType(name="House")
        db.add_all([item_type1, item_type2])
        db.commit()
        db.refresh(item_type1)
        db.refresh(item_type2)

        # Create task types
        task_type1 = TaskType(name="Oil Change")
        task_type2 = TaskType(name="Roof Inspection")
        db.add_all([task_type1, task_type2])
        db.commit()
        db.refresh(task_type1)
        db.refresh(task_type2)

        # Create templates
        template1 = MaintenanceTemplate(
            item_type_id=item_type1.id,
            task_type_id=task_type1.id,
            time_interval_days=30,
        )
        template2 = MaintenanceTemplate(
            item_type_id=item_type2.id,
            task_type_id=task_type2.id,
            time_interval_days=365,
        )
        db.add_all([template1, template2])
        db.commit()

        result = get_all_templates_grouped_by_item_type(db)

        assert len(result["item_types"]) == 2
        # Should be sorted by item_type_name
        names = [it["item_type_name"] for it in result["item_types"]]
        assert names == ["Car", "House"]

    def test_single_item_type_multiple_templates(self, db: Session):
        """Test retrieving single item type with multiple templates."""
        # Create item type
        item_type = ItemType(name="Car")
        db.add(item_type)
        db.commit()
        db.refresh(item_type)

        # Create task types
        task_type1 = TaskType(name="Oil Change")
        task_type2 = TaskType(name="Tire Rotation")
        task_type3 = TaskType(name="Brake Inspection")
        db.add_all([task_type1, task_type2, task_type3])
        db.commit()
        db.refresh(task_type1)
        db.refresh(task_type2)
        db.refresh(task_type3)

        # Create templates
        template1 = MaintenanceTemplate(
            item_type_id=item_type.id,
            task_type_id=task_type1.id,
            time_interval_days=30,
        )
        template2 = MaintenanceTemplate(
            item_type_id=item_type.id,
            task_type_id=task_type2.id,
            time_interval_days=90,
        )
        template3 = MaintenanceTemplate(
            item_type_id=item_type.id,
            task_type_id=task_type3.id,
            time_interval_days=180,
        )
        db.add_all([template1, template2, template3])
        db.commit()

        result = get_all_templates_grouped_by_item_type(db)

        assert len(result["item_types"]) == 1
        assert len(result["item_types"][0]["templates"]) == 3
        # Templates should be sorted by task_type_name
        task_names = [t["task_type_name"] for t in result["item_types"][0]["templates"]]
        assert task_names == ["Brake Inspection", "Oil Change", "Tire Rotation"]

    def test_filters_soft_deleted_templates(self, db: Session):
        """Test that soft-deleted templates are not included."""
        # Create item type
        item_type = ItemType(name="Car")
        db.add(item_type)
        db.commit()
        db.refresh(item_type)

        # Create task types
        task_type1 = TaskType(name="Oil Change")
        task_type2 = TaskType(name="Tire Rotation")
        db.add_all([task_type1, task_type2])
        db.commit()
        db.refresh(task_type1)
        db.refresh(task_type2)

        # Create templates, one of which is deleted
        template1 = MaintenanceTemplate(
            item_type_id=item_type.id,
            task_type_id=task_type1.id,
            time_interval_days=30,
        )
        template2 = MaintenanceTemplate(
            item_type_id=item_type.id,
            task_type_id=task_type2.id,
            time_interval_days=90,
            is_deleted=True,
        )
        db.add_all([template1, template2])
        db.commit()

        result = get_all_templates_grouped_by_item_type(db)

        assert len(result["item_types"]) == 1
        assert len(result["item_types"][0]["templates"]) == 1
        assert result["item_types"][0]["templates"][0]["task_type_name"] == "Oil Change"

    def test_filters_soft_deleted_item_types(self, db: Session):
        """Test that item types with only deleted templates are not included."""
        # Create item types
        item_type1 = ItemType(name="Car")
        item_type2 = ItemType(name="House", is_deleted=True)
        db.add_all([item_type1, item_type2])
        db.commit()
        db.refresh(item_type1)
        db.refresh(item_type2)

        # Create task types
        task_type1 = TaskType(name="Oil Change")
        task_type2 = TaskType(name="Roof Inspection")
        db.add_all([task_type1, task_type2])
        db.commit()
        db.refresh(task_type1)
        db.refresh(task_type2)

        # Create templates
        template1 = MaintenanceTemplate(
            item_type_id=item_type1.id,
            task_type_id=task_type1.id,
            time_interval_days=30,
        )
        template2 = MaintenanceTemplate(
            item_type_id=item_type2.id,
            task_type_id=task_type2.id,
            time_interval_days=365,
        )
        db.add_all([template1, template2])
        db.commit()

        result = get_all_templates_grouped_by_item_type(db)

        # Should only return Car, not deleted House
        assert len(result["item_types"]) == 1
        assert result["item_types"][0]["item_type_name"] == "Car"

    def test_custom_interval_included(self, db: Session):
        """Test that custom_interval is properly included in response."""
        # Create item type
        item_type = ItemType(name="Car")
        db.add(item_type)
        db.commit()
        db.refresh(item_type)

        # Create task type
        task_type = TaskType(name="Tire Rotation")
        db.add(task_type)
        db.commit()
        db.refresh(task_type)

        # Create template with custom_interval
        custom_interval = {"type": "mileage", "value": 5000}
        template = MaintenanceTemplate(
            item_type_id=item_type.id,
            task_type_id=task_type.id,
            time_interval_days=90,
            custom_interval=custom_interval,
        )
        db.add(template)
        db.commit()

        result = get_all_templates_grouped_by_item_type(db)

        assert result["item_types"][0]["templates"][0]["custom_interval"] == custom_interval

    def test_null_custom_interval(self, db: Session):
        """Test that null custom_interval is properly handled."""
        # Create item type
        item_type = ItemType(name="Car")
        db.add(item_type)
        db.commit()
        db.refresh(item_type)

        # Create task type
        task_type = TaskType(name="Oil Change")
        db.add(task_type)
        db.commit()
        db.refresh(task_type)

        # Create template without custom_interval
        template = MaintenanceTemplate(
            item_type_id=item_type.id,
            task_type_id=task_type.id,
            time_interval_days=30,
            custom_interval=None,
        )
        db.add(template)
        db.commit()

        result = get_all_templates_grouped_by_item_type(db)

        assert result["item_types"][0]["templates"][0]["custom_interval"] is None
