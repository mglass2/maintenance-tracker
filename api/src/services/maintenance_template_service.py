"""Maintenance template service for business logic operations."""

from typing import List
from sqlalchemy.orm import Session

try:
    from ..models.maintenance_template import MaintenanceTemplate
    from ..models.item_type import ItemType
    from ..models.task_type import TaskType
    from ..schemas.maintenance_templates import MaintenanceTemplateCreateRequest
except ImportError:
    from models.maintenance_template import MaintenanceTemplate
    from models.item_type import ItemType
    from models.task_type import TaskType
    from schemas.maintenance_templates import MaintenanceTemplateCreateRequest

from .exceptions import ResourceNotFoundError, DuplicateNameError


class MaintenanceTemplateServiceError(Exception):
    """Base exception for maintenance template service errors."""

    pass


def create_maintenance_template(
    db: Session, template_data: MaintenanceTemplateCreateRequest
) -> MaintenanceTemplate:
    """
    Create a new maintenance template with validation.

    Args:
        db: Database session
        template_data: Validated maintenance template creation request

    Returns:
        Created MaintenanceTemplate instance with database-generated fields (id, timestamps)

    Raises:
        ResourceNotFoundError: If item_type_id or task_type_id don't exist or are deleted
        DuplicateNameError: If item_type_id + task_type_id combination already exists
    """
    # Validate item_type_id exists and is not deleted
    item_type = db.query(ItemType).filter(
        ItemType.id == template_data.item_type_id,
        ItemType.is_deleted == False,
    ).first()

    if not item_type:
        raise ResourceNotFoundError(
            f"Item type with ID {template_data.item_type_id} not found or is deleted"
        )

    # Validate task_type_id exists and is not deleted
    task_type = db.query(TaskType).filter(
        TaskType.id == template_data.task_type_id,
        TaskType.is_deleted == False,
    ).first()

    if not task_type:
        raise ResourceNotFoundError(
            f"Task type with ID {template_data.task_type_id} not found or is deleted"
        )

    # Check for duplicate (item_type_id, task_type_id) combination among non-deleted records
    existing = db.query(MaintenanceTemplate).filter(
        MaintenanceTemplate.item_type_id == template_data.item_type_id,
        MaintenanceTemplate.task_type_id == template_data.task_type_id,
        MaintenanceTemplate.is_deleted == False,
    ).first()

    if existing:
        raise DuplicateNameError(
            f"Maintenance template for item type {template_data.item_type_id} and task type {template_data.task_type_id} already exists"
        )

    # Create new maintenance template instance
    db_template = MaintenanceTemplate(
        item_type_id=template_data.item_type_id,
        task_type_id=template_data.task_type_id,
        time_interval_days=template_data.time_interval_days,
        custom_interval=template_data.custom_interval,
    )

    try:
        db.add(db_template)
        db.commit()
        # Refresh to get database-generated id and timestamps
        db.refresh(db_template)
        return db_template
    except Exception as e:
        db.rollback()
        error_str = str(e).lower()
        error_type = type(e).__name__
        print(
            f"DEBUG: Exception during maintenance template creation: {error_type}: {error_str}"
        )

        # Check if it's a unique constraint error
        if "unique" in error_str or "integrity" in error_str:
            raise DuplicateNameError(
                f"Maintenance template for item type {template_data.item_type_id} and task type {template_data.task_type_id} already exists"
            )
        raise


def get_templates_by_item_type(db: Session, item_type_id: int) -> List[MaintenanceTemplate]:
    """
    Retrieve all maintenance templates for a specific item type.

    Args:
        db: Database session
        item_type_id: ID of the item type

    Returns:
        List of MaintenanceTemplate instances (empty list if none exist)

    Raises:
        ResourceNotFoundError: If item_type doesn't exist or is deleted
    """
    # Validate item_type_id exists and is not deleted
    item_type = db.query(ItemType).filter(
        ItemType.id == item_type_id,
        ItemType.is_deleted == False,
    ).first()

    if not item_type:
        raise ResourceNotFoundError(
            f"Item type with ID {item_type_id} not found or is deleted"
        )

    # Get all non-deleted templates for this item type
    templates = db.query(MaintenanceTemplate).filter(
        MaintenanceTemplate.item_type_id == item_type_id,
        MaintenanceTemplate.is_deleted == False,
    ).order_by(MaintenanceTemplate.created_at.desc()).all()

    return templates


def get_all_templates_grouped_by_item_type(db: Session) -> dict:
    """
    Retrieve all maintenance templates grouped by item type.

    Groups all non-deleted templates by item type and includes task type names.
    Only returns item types that have at least one template and are not deleted.

    Args:
        db: Database session

    Returns:
        Dictionary with structure:
        {
            "item_types": [
                {
                    "item_type_id": int,
                    "item_type_name": str,
                    "templates": [
                        {
                            "task_type_id": int,
                            "task_type_name": str,
                            "time_interval_days": int,
                            "custom_interval": dict or None,
                        }
                    ]
                }
            ]
        }

    """
    # Get all non-deleted templates with their associated item types and task types
    templates = db.query(MaintenanceTemplate).filter(
        MaintenanceTemplate.is_deleted == False,
    ).all()

    if not templates:
        return {"item_types": []}

    # Get all non-deleted item types and task types
    item_types = {
        it.id: it.name
        for it in db.query(ItemType).filter(ItemType.is_deleted == False).all()
    }

    task_types = {
        tt.id: tt.name
        for tt in db.query(TaskType).filter(TaskType.is_deleted == False).all()
    }

    # Group templates by item type, only including those where item_type and task_type are not deleted
    grouped = {}
    for template in templates:
        # Skip templates where the item type is deleted
        if template.item_type_id not in item_types:
            continue

        # Skip templates where the task type is deleted
        if template.task_type_id not in task_types:
            continue

        if template.item_type_id not in grouped:
            grouped[template.item_type_id] = {
                "item_type_id": template.item_type_id,
                "item_type_name": item_types[template.item_type_id],
                "templates": [],
            }

        grouped[template.item_type_id]["templates"].append(
            {
                "task_type_id": template.task_type_id,
                "task_type_name": task_types[template.task_type_id],
                "time_interval_days": template.time_interval_days,
                "custom_interval": template.custom_interval,
            }
        )

    # Sort by item type name, then sort templates within each group by task type name
    for group in grouped.values():
        group["templates"].sort(
            key=lambda t: t["task_type_name"]
        )

    result = {
        "item_types": sorted(
            grouped.values(),
            key=lambda x: x["item_type_name"]
        )
    }

    return result
