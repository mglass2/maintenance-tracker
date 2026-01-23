"""User routes for creating and managing users."""

from fastapi import APIRouter, Depends, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

try:
    from ..database.connection import get_db
    from ..models.user import User
    from ..schemas.users import UserCreateRequest, UserResponse
    from ..services.user_service import create_user
    from ..services.exceptions import DuplicateEmailError
    from ..utils.responses import success_response, error_response
except ImportError:
    from database.connection import get_db
    from models.user import User
    from schemas.users import UserCreateRequest, UserResponse
    from services.user_service import create_user
    from services.exceptions import DuplicateEmailError
    from utils.responses import success_response, error_response

router = APIRouter(prefix="/users", tags=["users"])


@router.get("")
def list_users_endpoint(db: Session = Depends(get_db)):
    """
    List all active (non-deleted) users in the system.

    Returns:
        200 OK with list of users
    """
    try:
        # Fetch all active users (not soft-deleted)
        users = db.query(User).filter(User.is_deleted == False).all()

        # Convert to response schema
        user_responses = [
            UserResponse.model_validate(user).model_dump()
            for user in users
        ]

        return success_response(
            data=user_responses,
            message="Users retrieved successfully",
            status_code=status.HTTP_200_OK,
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return error_response(
            error="INTERNAL_ERROR",
            message=f"An unexpected error occurred: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


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
