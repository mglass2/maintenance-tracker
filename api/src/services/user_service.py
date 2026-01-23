"""User service for business logic operations."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

try:
    from ..models.user import User
    from ..schemas.users import UserCreateRequest
except ImportError:
    from models.user import User
    from schemas.users import UserCreateRequest

from .exceptions import DuplicateEmailError


def create_user(db: Session, user_data: UserCreateRequest) -> User:
    """
    Create a new user with validation and duplicate checking.

    Args:
        db: Database session
        user_data: Validated user creation request

    Returns:
        Created User instance with database-generated fields (id, timestamps)

    Raises:
        DuplicateEmailError: If email already exists for active (non-deleted) user
    """
    # Check for existing email among non-deleted users
    existing_user = db.query(User).filter(
        User.email == user_data.email,
        User.is_deleted == False,
    ).first()

    if existing_user:
        raise DuplicateEmailError(user_data.email)

    # Create new user instance
    db_user = User(
        name=user_data.name,
        email=user_data.email,
    )

    try:
        db.add(db_user)
        db.commit()
        # Refresh to get database-generated id and timestamps
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        db.rollback()
        # Handle race condition where email was inserted between check and insert
        if "email" in str(e).lower():
            raise DuplicateEmailError(user_data.email)
        raise
