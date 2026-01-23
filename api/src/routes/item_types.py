"""Item type routes for creating and managing item types."""

from fastapi import APIRouter, Depends, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

try:
    from ..database.connection import get_db
    from ..schemas.item_types import ItemTypeCreateRequest, ItemTypeResponse
    from ..services.item_type_service import create_item_type
    from ..services.exceptions import DuplicateNameError
    from ..utils.responses import success_response, error_response
except ImportError:
    from database.connection import get_db
    from schemas.item_types import ItemTypeCreateRequest, ItemTypeResponse
    from services.item_type_service import create_item_type
    from services.exceptions import DuplicateNameError
    from utils.responses import success_response, error_response

router = APIRouter(prefix="/item_types", tags=["item_types"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_item_type_endpoint(
    item_type_data: ItemTypeCreateRequest,
    db: Session = Depends(get_db),
):
    """
    Create a new item type.

    Args:
        item_type_data: Item type creation request with name and optional description
        db: Database session (dependency injected)

    Returns:
        201 Created with created item type data

    Error responses:
        - 400 Bad Request: Invalid input (e.g., empty name, name too long)
        - 409 Conflict: Item type name already exists
        - 422 Unprocessable Entity: Missing required fields
        - 500 Internal Server Error: Unexpected server error
    """
    try:
        # Create item type in database
        db_item_type = create_item_type(db, item_type_data)

        # Convert to response schema
        item_type_response = ItemTypeResponse.model_validate(db_item_type)

        return success_response(
            data=item_type_response.model_dump(mode="json"),
            message="Item type created successfully",
            status_code=status.HTTP_201_CREATED,
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
