"""User routes for creating and managing users."""

from fastapi import APIRouter, Depends, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

try:
    from ..database.connection import get_db
    from ..schemas.users import UserCreateRequest, UserResponse
    from ..services.user_service import create_user
    from ..services.exceptions import DuplicateEmailError
    from ..utils.responses import success_response, error_response
except ImportError:
    from database.connection import get_db
    from schemas.users import UserCreateRequest, UserResponse
    from services.user_service import create_user
    from services.exceptions import DuplicateEmailError
    from utils.responses import success_response, error_response

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_user_endpoint(
    user_data: UserCreateRequest,
    db: Session = Depends(get_db),
):
    """
    Create a new user.

    Args:
        user_data: User creation request with name and email
        db: Database session (dependency injected)

    Returns:
        201 Created with created user data

    Error responses:
        - 400 Bad Request: Invalid input (e.g., invalid email format)
        - 409 Conflict: Email already exists
        - 500 Internal Server Error: Unexpected server error
    """
    try:
        # Create user in database
        db_user = create_user(db, user_data)

        # Convert to response schema
        user_response = UserResponse.model_validate(db_user)

        return success_response(
            data=user_response.model_dump(),
            message="User created successfully",
            status_code=status.HTTP_201_CREATED,
        )

    except DuplicateEmailError as e:
        return error_response(
            error="DUPLICATE_EMAIL",
            message=f"Email '{user_data.email}' already exists",
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
        traceback.print_exc()
        return error_response(
            error="INTERNAL_ERROR",
            message=f"An unexpected error occurred: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
