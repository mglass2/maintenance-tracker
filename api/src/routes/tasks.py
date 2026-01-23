"""Task routes for creating and managing tasks."""

from fastapi import APIRouter, Depends, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

try:
    from ..database.connection import get_db
    from ..schemas.tasks import TaskCreateRequest, TaskResponse, TaskListResponse
    from ..services.task_service import create_task, get_tasks_by_item
    from ..services.exceptions import ResourceNotFoundError
    from ..utils.responses import success_response, error_response
except ImportError:
    from database.connection import get_db
    from schemas.tasks import TaskCreateRequest, TaskResponse, TaskListResponse
    from services.task_service import create_task, get_tasks_by_item
    from services.exceptions import ResourceNotFoundError
    from utils.responses import success_response, error_response

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_task_endpoint(
    task_data: TaskCreateRequest,
    db: Session = Depends(get_db),
):
    """
    Create a new task.

    Args:
        task_data: Task creation request with item_id, task_type_id, completed_at, and optional notes/cost
        db: Database session (dependency injected)

    Returns:
        201 Created with created task data

    Error responses:
        - 400 Bad Request: Invalid input (e.g., negative IDs, invalid dates)
        - 404 Not Found: Referenced item or task type doesn't exist
        - 422 Unprocessable Entity: Missing required fields
        - 500 Internal Server Error: Unexpected server error
    """
    try:
        # Create task in database
        db_task = create_task(db, task_data)

        # Convert to response schema
        task_response = TaskResponse.model_validate(db_task)

        return success_response(
            data=task_response.model_dump(mode="json"),
            message="Task created successfully",
            status_code=status.HTTP_201_CREATED,
        )

    except ResourceNotFoundError as e:
        return error_response(
            error="RESOURCE_NOT_FOUND",
            message=str(e),
            status_code=status.HTTP_404_NOT_FOUND,
        )

    except ValidationError as e:
        return error_response(
            error="VALIDATION_ERROR",
            message="Invalid input provided",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"errors": e.errors()},
        )

    except Exception as e:
        import traceback
        print(f"DEBUG: Unexpected error: {type(e).__name__}: {str(e)}")
        traceback.print_exc()
        return error_response(
            error="INTERNAL_ERROR",
            message=f"An unexpected error occurred: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.get("/items/{item_id}", status_code=status.HTTP_200_OK)
def get_item_tasks_endpoint(
    item_id: int,
    db: Session = Depends(get_db),
):
    """
    Get all tasks belonging to a specific item.

    Args:
        item_id: ID of the item whose tasks to retrieve
        db: Database session (dependency injected)

    Returns:
        200 OK with list of tasks for the item (empty list if no tasks)

    Error responses:
        - 404 Not Found: Item doesn't exist or is deleted
        - 500 Internal Server Error: Unexpected server error
    """
    try:
        # Get tasks for the item
        tasks = get_tasks_by_item(db, item_id)

        # Convert to response schema
        task_responses = [TaskResponse.model_validate(task) for task in tasks]
        list_response = TaskListResponse(tasks=task_responses, count=len(task_responses))

        return success_response(
            data=list_response.model_dump(mode="json"),
            message=f"Retrieved {len(task_responses)} tasks for item {item_id}",
            status_code=status.HTTP_200_OK,
        )

    except ResourceNotFoundError as e:
        return error_response(
            error="RESOURCE_NOT_FOUND",
            message=str(e),
            status_code=status.HTTP_404_NOT_FOUND,
        )

    except Exception as e:
        import traceback
        print(f"DEBUG: Unexpected error: {type(e).__name__}: {str(e)}")
        traceback.print_exc()
        return error_response(
            error="INTERNAL_ERROR",
            message=f"An unexpected error occurred: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
