"""Maintenance template routes for creating and managing maintenance templates."""

from fastapi import APIRouter, Depends, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

try:
    from ..database.connection import get_db
    from ..schemas.maintenance_templates import (
        MaintenanceTemplateCreateRequest,
        MaintenanceTemplateResponse,
    )
    from ..services.maintenance_template_service import create_maintenance_template
    from ..services.exceptions import ResourceNotFoundError, DuplicateNameError
    from ..utils.responses import success_response, error_response
except ImportError:
    from database.connection import get_db
    from schemas.maintenance_templates import (
        MaintenanceTemplateCreateRequest,
        MaintenanceTemplateResponse,
    )
    from services.maintenance_template_service import create_maintenance_template
    from services.exceptions import ResourceNotFoundError, DuplicateNameError
    from utils.responses import success_response, error_response

router = APIRouter(prefix="/maintenance_templates", tags=["maintenance_templates"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_maintenance_template_endpoint(
    template_data: MaintenanceTemplateCreateRequest,
    db: Session = Depends(get_db),
):
    """
    Create a new maintenance template.

    Args:
        template_data: Maintenance template creation request with item_type_id, task_type_id, time_interval_days, and optional custom_interval
        db: Database session (dependency injected)

    Returns:
        201 Created with created maintenance template data

    Error responses:
        - 400 Bad Request: Invalid input (e.g., negative interval, invalid JSON)
        - 404 Not Found: Referenced item_type or task_type doesn't exist
        - 409 Conflict: Maintenance template for this item_type/task_type combination already exists
        - 422 Unprocessable Entity: Missing required fields
        - 500 Internal Server Error: Unexpected server error
    """
    try:
        # Create maintenance template in database
        db_template = create_maintenance_template(db, template_data)

        # Convert to response schema
        template_response = MaintenanceTemplateResponse.model_validate(db_template)

        return success_response(
            data=template_response.model_dump(mode="json"),
            message="Maintenance template created successfully",
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
            error="DUPLICATE_TEMPLATE",
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
