"""Tests for task type service business logic."""

from schemas.task_types import TaskTypeCreateRequest


class TestCreateTaskType:
    """Tests for create_task_type service function - validation logic only."""

    def test_create_task_type_accepts_valid_schema(self):
        """Test that create_task_type accepts valid TaskTypeCreateRequest."""
        task_type_data = TaskTypeCreateRequest(
            name="Oil Change",
            description="Regular oil and filter replacement",
            item_type_id=1,
        )

        # Verify the schema is valid
        assert task_type_data.name == "Oil Change"
        assert task_type_data.description == "Regular oil and filter replacement"
        assert task_type_data.item_type_id == 1

    def test_create_task_type_without_description(self):
        """Test that create_task_type accepts task type without description."""
        task_type_data = TaskTypeCreateRequest(
            name="Inspection",
            item_type_id=1,
        )

        assert task_type_data.description is None
        assert task_type_data.name == "Inspection"
        assert task_type_data.item_type_id == 1

    def test_create_task_type_field_defaults(self):
        """Test optional field defaults."""
        task_type_data = TaskTypeCreateRequest(
            name="Service",
            item_type_id=1,
        )

        assert task_type_data.description is None
        assert task_type_data.name == "Service"
        assert task_type_data.item_type_id == 1
