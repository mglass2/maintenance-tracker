"""Task type service for business logic operations."""

from typing import List
from sqlalchemy.orm import Session

try:
    from ..models.task_type import TaskType
    from ..schemas.task_types import TaskTypeCreateRequest
except ImportError:
    from models.task_type import TaskType
    from schemas.task_types import TaskTypeCreateRequest

from .exceptions import DuplicateNameError


class TaskTypeServiceError(Exception):
    """Base exception for task type service errors."""

    pass


def create_task_type(db: Session, task_type_data: TaskTypeCreateRequest) -> TaskType:
    """
    Create a new task type with validation.

    Args:
        db: Database session
        task_type_data: Validated task type creation request

    Returns:
        Created TaskType instance with database-generated fields (id, timestamps)

    Raises:
        DuplicateNameError: If name is not unique
    """
    # Check for duplicate name (case-insensitive among non-deleted types)
    existing = db.query(TaskType).filter(
        TaskType.name.ilike(task_type_data.name),
        TaskType.is_deleted == False,
    ).first()

    if existing:
        raise DuplicateNameError(
            f"Task type with name '{task_type_data.name}' already exists"
        )

    # Create new task type instance
    db_task_type = TaskType(
        name=task_type_data.name,
        description=task_type_data.description,
    )

    try:
        db.add(db_task_type)
        db.commit()
        # Refresh to get database-generated id and timestamps
        db.refresh(db_task_type)
        return db_task_type
    except Exception as e:
        db.rollback()
        error_str = str(e).lower()
        error_type = type(e).__name__
        print(f"DEBUG: Exception during task type creation: {error_type}: {error_str}")

        # Check if it's a unique constraint error
        if "unique" in error_str or "integrity" in error_str:
            raise DuplicateNameError(
                f"Task type with name '{task_type_data.name}' already exists"
            )
        raise


def get_all_task_types(db: Session) -> List[TaskType]:
    """
    Retrieve all non-deleted task types.

    Args:
        db: Database session

    Returns:
        List of TaskType instances ordered by name
    """
    task_types = db.query(TaskType).filter(
        TaskType.is_deleted == False,
    ).order_by(TaskType.name).all()

    return task_types
