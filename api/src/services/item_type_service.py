"""Item type service for business logic operations."""

from sqlalchemy.orm import Session

try:
    from ..models.item_type import ItemType
    from ..schemas.item_types import ItemTypeCreateRequest
except ImportError:
    from models.item_type import ItemType
    from schemas.item_types import ItemTypeCreateRequest

from .exceptions import DuplicateNameError


class ItemTypeServiceError(Exception):
    """Base exception for item type service errors."""

    pass


def create_item_type(db: Session, item_type_data: ItemTypeCreateRequest) -> ItemType:
    """
    Create a new item type with validation.

    Args:
        db: Database session
        item_type_data: Validated item type creation request

    Returns:
        Created ItemType instance with database-generated fields (id, timestamps)

    Raises:
        DuplicateNameError: If name is not unique
    """
    # Check for duplicate name (case-insensitive among non-deleted types)
    existing = db.query(ItemType).filter(
        ItemType.name.ilike(item_type_data.name),
        ItemType.is_deleted == False,
    ).first()

    if existing:
        raise DuplicateNameError(
            f"Item type with name '{item_type_data.name}' already exists"
        )

    # Create new item type instance
    db_item_type = ItemType(
        name=item_type_data.name,
        description=item_type_data.description,
    )

    try:
        db.add(db_item_type)
        db.commit()
        # Refresh to get database-generated id and timestamps
        db.refresh(db_item_type)
        return db_item_type
    except Exception as e:
        db.rollback()
        error_str = str(e).lower()
        error_type = type(e).__name__
        print(f"DEBUG: Exception during item type creation: {error_type}: {error_str}")

        # Check if it's a unique constraint error
        if "unique" in error_str or "integrity" in error_str:
            raise DuplicateNameError(
                f"Item type with name '{item_type_data.name}' already exists"
            )
        raise
