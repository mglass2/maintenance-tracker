"""Task type routes for creating and managing task types."""

from typing import Optional
from fastapi import APIRouter, Depends, status, Query
from pydantic import ValidationError
from sqlalchemy.orm import Session

try:
    from ..database.connection import get_db
    from ..schemas.task_types import TaskTypeCreateRequest, TaskTypeResponse, TaskTypeListResponse
    from ..services.task_type_service import create_task_type, get_all_task_types
    from ..services.exceptions import DuplicateNameError, ResourceNotFoundError
    from ..utils.responses import success_response, error_response
except ImportError:
    from database.connection import get_db
    from schemas.task_types import TaskTypeCreateRequest, TaskTypeResponse, TaskTypeListResponse
    from services.task_type_service import create_task_type, get_all_task_types
    from services.exceptions import DuplicateNameError, ResourceNotFoundError
    from utils.responses import success_response, error_response

router = APIRouter(prefix="/task_types", tags=["task_types"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_task_type_endpoint(
    task_type_data: TaskTypeCreateRequest,
    db: Session = Depends(get_db),
):
    """
    Create a new task type.

    Args:
        task_type_data: Task type creation request with name, optional description, and item_type_id
        db: Database session (dependency injected)

    Returns:
        201 Created with created task type data

    Error responses:
        - 400 Bad Request: Invalid input (e.g., empty name, name too long)
        - 404 Not Found: Referenced item_type_id does not exist
        - 409 Conflict: Task type name already exists
        - 422 Unprocessable Entity: Missing required fields or invalid field values
        - 500 Internal Server Error: Unexpected server error
    """
    try:
        # Create task type in database
        db_task_type = create_task_type(db, task_type_data)

        # Convert to response schema
        task_type_response = TaskTypeResponse.model_validate(db_task_type)

        return success_response(
            data=task_type_response.model_dump(mode="json"),
            message="Task type created successfully",
            status_code=status.HTTP_201_CREATED,
        )

    except ResourceNotFoundError as e:
        return error_response(
            error="RESOURCE_NOT_FOUND",
            message=str(e),
            status_code=status.HTTP_404_NOT_FOUND,
        )

    except DuplicateNameError as e:
        return error_response(
            error="DUPLICATE_NAME",
            message=str(e),
            status_code=status.HTTP_409_CONFLICT,
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


@router.get("", status_code=status.HTTP_200_OK)
def get_task_types_endpoint(
    db: Session = Depends(get_db),
    item_type_id: Optional[int] = Query(None, description="Filter by item type ID"),
):
    """
    Get all available task types, optionally filtered by item type.

    Args:
        db: Database session (dependency injected)
        item_type_id: Optional item type ID to filter by

    Returns:
        200 OK with list of non-deleted task types (filtered if item_type_id provided)

    Error responses:
        - 500 Internal Server Error: Unexpected server error
    """
    try:
        # Get all task types, optionally filtered
        task_types = get_all_task_types(db, item_type_id=item_type_id)

        # Convert to response schema
        task_type_responses = [TaskTypeResponse.model_validate(task_type) for task_type in task_types]
        list_response = TaskTypeListResponse(task_types=task_type_responses, count=len(task_type_responses))

        return success_response(
            data=list_response.model_dump(mode="json"),
            message=f"Retrieved {len(task_type_responses)} task types",
            status_code=status.HTTP_200_OK,
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
