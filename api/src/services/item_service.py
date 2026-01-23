"""Item service for business logic operations."""

from typing import List
from sqlalchemy.orm import Session

try:
    from ..models.item import Item
    from ..models.user import User
    from ..schemas.items import ItemCreateRequest
except ImportError:
    from models.item import Item
    from models.user import User
    from schemas.items import ItemCreateRequest

from .exceptions import ResourceNotFoundError


class ItemServiceError(Exception):
    """Base exception for item service errors."""

    pass


def create_item(db: Session, item_data: ItemCreateRequest) -> Item:
    """
    Create a new item with validation and foreign key checking.

    Args:
        db: Database session
        item_data: Validated item creation request

    Returns:
        Created Item instance with database-generated fields (id, timestamps)

    Raises:
        ResourceNotFoundError: If user_id or item_type_id don't exist
    """
    # Validate user_id exists if provided
    if item_data.user_id is not None:
        user = db.query(User).filter(
            User.id == item_data.user_id,
            User.is_deleted == False,
        ).first()

        if not user:
            raise ResourceNotFoundError(
                f"User with ID {item_data.user_id} not found or is deleted"
            )

    # Validate item_type_id exists
    # Note: We need to query item_types table, but we don't have an ORM model for it yet
    # For now, we'll attempt to create the item and let the database foreign key constraint handle it
    # In production, you'd want to create an ItemType ORM model and validate here

    # Create new item instance
    db_item = Item(
        user_id=item_data.user_id,
        item_type_id=item_data.item_type_id,
        name=item_data.name,
        description=None,  # Always leave description empty per requirements
        acquired_at=item_data.acquired_at,
        details=item_data.details,
    )

    try:
        db.add(db_item)
        db.commit()
        # Refresh to get database-generated id and timestamps
        db.refresh(db_item)
        return db_item
    except Exception as e:
        db.rollback()
        error_str = str(e).lower()
        error_type = type(e).__name__
        print(f"DEBUG: Exception during item creation: {error_type}: {error_str}")

        # Check if it's a foreign key constraint error
        # PostgreSQL constraint violation errors usually contain "violates foreign key constraint"
        if "foreign key" in error_str or "integrity" in error_str:
            if "item_type" in error_str:
                raise ResourceNotFoundError(
                    f"Item type with ID {item_data.item_type_id} not found"
                )
            elif "user" in error_str:
                raise ResourceNotFoundError(
                    f"User with ID {item_data.user_id} not found"
                )
        raise


def get_items_by_user(db: Session, user_id: int) -> List[Item]:
    """
    Retrieve all items belonging to a specific user.

    Args:
        db: Database session
        user_id: ID of the user whose items to retrieve

    Returns:
        List of Item instances (empty list if user has no items)

    Raises:
        ResourceNotFoundError: If user doesn't exist or is deleted
    """
    # Validate user exists and is not deleted
    user = db.query(User).filter(
        User.id == user_id,
        User.is_deleted == False,
    ).first()

    if not user:
        raise ResourceNotFoundError(
            f"User with ID {user_id} not found or is deleted"
        )

    # Get all non-deleted items for this user
    items = db.query(Item).filter(
        Item.user_id == user_id,
        Item.is_deleted == False,
    ).order_by(Item.created_at.desc()).all()

    return items
