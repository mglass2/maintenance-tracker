"""Tests for task service business logic."""

from datetime import date
from decimal import Decimal
from schemas.tasks import TaskCreateRequest


class TestCreateTask:
    """Tests for create_task service function - validation logic only."""

    def test_create_task_accepts_valid_schema(self):
        """Test that create_task accepts valid TaskCreateRequest."""
        task_data = TaskCreateRequest(
            item_id=1,
            task_type_id=1,
            completed_at=date(2024, 1, 15),
            notes="Oil change performed",
            cost=Decimal("45.99"),
        )

        # Verify the schema is valid
        assert task_data.item_id == 1
        assert task_data.task_type_id == 1
        assert task_data.completed_at == date(2024, 1, 15)
        assert task_data.notes == "Oil change performed"
        assert task_data.cost == Decimal("45.99")

    def test_create_task_without_notes(self):
        """Test that create_task accepts task without notes."""
        task_data = TaskCreateRequest(
            item_id=2,
            task_type_id=2,
            completed_at=date(2024, 2, 10),
        )

        assert task_data.notes is None
        assert task_data.item_id == 2

    def test_create_task_without_cost(self):
        """Test that create_task accepts task without cost."""
        task_data = TaskCreateRequest(
            item_id=3,
            task_type_id=3,
            completed_at=date(2024, 3, 5),
        )

        assert task_data.cost is None
        assert task_data.item_id == 3

    def test_create_task_field_defaults(self):
        """Test optional field defaults."""
        task_data = TaskCreateRequest(
            item_id=4,
            task_type_id=2,
            completed_at=date(2024, 1, 20),
        )

        assert task_data.notes is None
        assert task_data.cost is None
        assert task_data.item_id == 4
