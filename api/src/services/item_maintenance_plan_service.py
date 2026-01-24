"""Item maintenance plan service for business logic operations."""

from typing import List
from sqlalchemy.orm import Session

try:
    from ..models.item_maintenance_plan import ItemMaintenancePlan
    from ..models.item import Item
    from ..models.task_type import TaskType
    from ..schemas.item_maintenance_plans import ItemMaintenancePlanCreateRequest
except ImportError:
    from models.item_maintenance_plan import ItemMaintenancePlan
    from models.item import Item
    from models.task_type import TaskType
    from schemas.item_maintenance_plans import ItemMaintenancePlanCreateRequest

from .exceptions import ResourceNotFoundError, DuplicateNameError


class ItemMaintenancePlanServiceError(Exception):
    """Base exception for item maintenance plan service errors."""

    pass


def create_item_maintenance_plan(
    db: Session, plan_data: ItemMaintenancePlanCreateRequest
) -> ItemMaintenancePlan:
    """
    Create a new item maintenance plan with validation.

    Args:
        db: Database session
        plan_data: Validated item maintenance plan creation request

    Returns:
        Created ItemMaintenancePlan instance with database-generated fields (id, timestamps)

    Raises:
        ResourceNotFoundError: If item_id or task_type_id don't exist or are deleted
        DuplicateNameError: If item_id + task_type_id combination already exists
    """
    # Validate item_id exists and is not deleted
    item = db.query(Item).filter(
        Item.id == plan_data.item_id,
        Item.is_deleted == False,
    ).first()

    if not item:
        raise ResourceNotFoundError(
            f"Item with ID {plan_data.item_id} not found or is deleted"
        )

    # Validate task_type_id exists and is not deleted
    task_type = db.query(TaskType).filter(
        TaskType.id == plan_data.task_type_id,
        TaskType.is_deleted == False,
    ).first()

    if not task_type:
        raise ResourceNotFoundError(
            f"Task type with ID {plan_data.task_type_id} not found or is deleted"
        )

    # Check for duplicate (item_id, task_type_id) combination among non-deleted records
    existing = db.query(ItemMaintenancePlan).filter(
        ItemMaintenancePlan.item_id == plan_data.item_id,
        ItemMaintenancePlan.task_type_id == plan_data.task_type_id,
        ItemMaintenancePlan.is_deleted == False,
    ).first()

    if existing:
        raise DuplicateNameError(
            f"Item maintenance plan for item {plan_data.item_id} and task type {plan_data.task_type_id} already exists"
        )

    # Create new item maintenance plan instance
    db_plan = ItemMaintenancePlan(
        item_id=plan_data.item_id,
        task_type_id=plan_data.task_type_id,
        time_interval_days=plan_data.time_interval_days,
        custom_interval=plan_data.custom_interval,
    )

    try:
        db.add(db_plan)
        db.commit()
        # After commit, SQLAlchemy has the ID and server defaults
        # Return the object (attributes will be loaded on access via lazy loading)
        return db_plan
    except Exception as e:
        db.rollback()
        error_str = str(e).lower()
        error_type = type(e).__name__
        print(
            f"DEBUG: Exception during item maintenance plan creation: {error_type}: {error_str}"
        )

        # Check if it's a unique constraint error
        if "unique" in error_str or "integrity" in error_str:
            raise DuplicateNameError(
                f"Item maintenance plan for item {plan_data.item_id} and task type {plan_data.task_type_id} already exists"
            )
        raise


def get_plans_by_item(db: Session, item_id: int) -> List[ItemMaintenancePlan]:
    """
    Retrieve all maintenance plans for a specific item.

    Args:
        db: Database session
        item_id: ID of the item

    Returns:
        List of ItemMaintenancePlan instances (empty list if none exist)

    Raises:
        ResourceNotFoundError: If item doesn't exist or is deleted
    """
    # Validate item_id exists and is not deleted
    item = db.query(Item).filter(
        Item.id == item_id,
        Item.is_deleted == False,
    ).first()

    if not item:
        raise ResourceNotFoundError(
            f"Item with ID {item_id} not found or is deleted"
        )

    # Get all non-deleted plans for this item
    plans = db.query(ItemMaintenancePlan).filter(
        ItemMaintenancePlan.item_id == item_id,
        ItemMaintenancePlan.is_deleted == False,
    ).order_by(ItemMaintenancePlan.created_at.desc()).all()

    return plans
