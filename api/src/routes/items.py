"""Item routes for creating and managing items."""

from fastapi import APIRouter, Depends, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

try:
    from ..database.connection import get_db
    from ..schemas.items import ItemCreateRequest, ItemResponse, ItemListResponse
    from ..services.item_service import create_item, get_items_by_user
    from ..services.exceptions import ResourceNotFoundError
    from ..utils.responses import success_response, error_response
except ImportError:
    from database.connection import get_db
    from schemas.items import ItemCreateRequest, ItemResponse, ItemListResponse
    from services.item_service import create_item, get_items_by_user
    from services.exceptions import ResourceNotFoundError
    from utils.responses import success_response, error_response

router = APIRouter(prefix="/items", tags=["items"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_item_endpoint(
    item_data: ItemCreateRequest,
    db: Session = Depends(get_db),
):
    """
    Create a new item.

    Args:
        item_data: Item creation request with user_id (optional), item_type_id, name, and acquired_at
        db: Database session (dependency injected)

    Returns:
        201 Created with created item data

    Error responses:
        - 400 Bad Request: Invalid input (e.g., invalid name, negative IDs)
        - 404 Not Found: Referenced user or item type doesn't exist
        - 422 Unprocessable Entity: Missing required fields
        - 500 Internal Server Error: Unexpected server error
    """
    try:
        # Create item in database
        db_item = create_item(db, item_data)

        # Convert to response schema
        item_response = ItemResponse.model_validate(db_item)

        return success_response(
            data=item_response.model_dump(mode="json"),
            message="Item created successfully",
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


@router.get("/users/{user_id}", status_code=status.HTTP_200_OK)
def get_user_items_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    Get all items belonging to a specific user.

    Args:
        user_id: ID of the user whose items to retrieve
        db: Database session (dependency injected)

    Returns:
        200 OK with list of items for the user (empty list if no items)

    Error responses:
        - 404 Not Found: User doesn't exist or is deleted
        - 500 Internal Server Error: Unexpected server error
    """
    try:
        # Get items for the user
        items = get_items_by_user(db, user_id)

        # Convert to response schema
        item_responses = [ItemResponse.model_validate(item) for item in items]
        list_response = ItemListResponse(items=item_responses, count=len(item_responses))

        return success_response(
            data=list_response.model_dump(mode="json"),
            message=f"Retrieved {len(item_responses)} items for user {user_id}",
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
