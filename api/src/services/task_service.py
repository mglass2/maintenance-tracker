"""Task service for business logic operations."""

from typing import List
from sqlalchemy.orm import Session

try:
    from ..models.task import Task
    from ..models.item import Item
    from ..schemas.tasks import TaskCreateRequest
except ImportError:
    from models.task import Task
    from models.item import Item
    from schemas.tasks import TaskCreateRequest

from .exceptions import ResourceNotFoundError


class TaskServiceError(Exception):
    """Base exception for task service errors."""

    pass


def create_task(db: Session, task_data: TaskCreateRequest) -> Task:
    """
    Create a new task with validation and foreign key checking.

    Args:
        db: Database session
        task_data: Validated task creation request

    Returns:
        Created Task instance with database-generated fields (id, timestamps)

    Raises:
        ResourceNotFoundError: If item_id or task_type_id don't exist
    """
    # Validate item_id exists
    item = db.query(Item).filter(
        Item.id == task_data.item_id,
        Item.is_deleted == False,
    ).first()

    if not item:
        raise ResourceNotFoundError(
            f"Item with ID {task_data.item_id} not found or is deleted"
        )

    # Validate task_type_id exists
    # Note: We need to query task_types table, but we don't have an ORM model for it yet
    # For now, we'll attempt to create the task and let the database foreign key constraint handle it
    # In production, you'd want to create a TaskType ORM model and validate here

    # Create new task instance
    db_task = Task(
        item_id=task_data.item_id,
        task_type_id=task_data.task_type_id,
        completed_at=task_data.completed_at,
        notes=task_data.notes,
        cost=task_data.cost,
        details=task_data.details,
    )

    try:
        db.add(db_task)
        db.commit()
        # Refresh to get database-generated id and timestamps
        db.refresh(db_task)
        return db_task
    except Exception as e:
        db.rollback()
        error_str = str(e).lower()
        error_type = type(e).__name__
        print(f"DEBUG: Exception during task creation: {error_type}: {error_str}")

        # Check if it's a foreign key constraint error
        # PostgreSQL constraint violation errors usually contain "violates foreign key constraint"
        if "foreign key" in error_str or "integrity" in error_str:
            if "task_type" in error_str:
                raise ResourceNotFoundError(
                    f"Task type with ID {task_data.task_type_id} not found"
                )
            elif "item" in error_str:
                raise ResourceNotFoundError(
                    f"Item with ID {task_data.item_id} not found"
                )
        raise


def get_tasks_by_item(db: Session, item_id: int) -> List[Task]:
    """
    Retrieve all tasks belonging to a specific item.

    Args:
        db: Database session
        item_id: ID of the item whose tasks to retrieve

    Returns:
        List of Task instances (empty list if item has no tasks)

    Raises:
        ResourceNotFoundError: If item doesn't exist or is deleted
    """
    # Validate item exists and is not deleted
    item = db.query(Item).filter(
        Item.id == item_id,
        Item.is_deleted == False,
    ).first()

    if not item:
        raise ResourceNotFoundError(
            f"Item with ID {item_id} not found or is deleted"
        )

    # Get all non-deleted tasks for this item
    tasks = db.query(Task).filter(
        Task.item_id == item_id,
        Task.is_deleted == False,
    ).order_by(Task.completed_at.desc()).all()

    return tasks
