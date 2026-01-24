"""Item maintenance plan routes for creating and managing item maintenance plans."""

from fastapi import APIRouter, Depends, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

try:
    from ..database.connection import get_db
    from ..schemas.item_maintenance_plans import (
        ItemMaintenancePlanCreateRequest,
        ItemMaintenancePlanResponse,
    )
    from ..services.item_maintenance_plan_service import create_item_maintenance_plan, get_plans_by_item
    from ..services.exceptions import ResourceNotFoundError, DuplicateNameError
    from ..utils.responses import success_response, error_response
except ImportError:
    from database.connection import get_db
    from schemas.item_maintenance_plans import (
        ItemMaintenancePlanCreateRequest,
        ItemMaintenancePlanResponse,
    )
    from services.item_maintenance_plan_service import create_item_maintenance_plan, get_plans_by_item
    from services.exceptions import ResourceNotFoundError, DuplicateNameError
    from utils.responses import success_response, error_response

router = APIRouter(prefix="/item_maintenance_plans", tags=["item_maintenance_plans"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_item_maintenance_plan_endpoint(
    plan_data: ItemMaintenancePlanCreateRequest,
    db: Session = Depends(get_db),
):
    """
    Create a new item maintenance plan.

    Args:
        plan_data: Item maintenance plan creation request with item_id, task_type_id, time_interval_days, and optional custom_interval
        db: Database session (dependency injected)

    Returns:
        201 Created with created item maintenance plan data

    Error responses:
        - 400 Bad Request: Invalid input (e.g., negative interval, invalid JSON)
        - 404 Not Found: Referenced item or task_type doesn't exist
        - 409 Conflict: Item maintenance plan for this item/task_type combination already exists
        - 422 Unprocessable Entity: Missing required fields
        - 500 Internal Server Error: Unexpected server error
    """
    try:
        # Create item maintenance plan in database
        db_plan = create_item_maintenance_plan(db, plan_data)

        # Convert to response schema
        plan_response = ItemMaintenancePlanResponse.model_validate(db_plan)

        return success_response(
            data=plan_response.model_dump(mode="json"),
            message="Item maintenance plan created successfully",
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
            error="DUPLICATE_PLAN",
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


@router.get("/items/{item_id}", status_code=status.HTTP_200_OK)
def get_plans_by_item_endpoint(
    item_id: int,
    db: Session = Depends(get_db),
):
    """
    Get all maintenance plans for a specific item.

    Args:
        item_id: ID of the item whose plans to retrieve
        db: Database session (dependency injected)

    Returns:
        200 OK with list of plans

    Error responses:
        - 404 Not Found: Item doesn't exist or is deleted
        - 500 Internal Server Error: Unexpected server error
    """
    try:
        # Get plans for the item
        plans = get_plans_by_item(db, item_id)

        # Convert to response schema
        plan_responses = [ItemMaintenancePlanResponse.model_validate(plan) for plan in plans]

        return success_response(
            data=[plan.model_dump(mode="json") for plan in plan_responses],
            message=f"Retrieved {len(plan_responses)} plans for item {item_id}",
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
