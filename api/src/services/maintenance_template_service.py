"""Maintenance template service for business logic operations."""

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
