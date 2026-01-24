"""SQLAlchemy ItemMaintenancePlan ORM model."""

from datetime import datetime
from sqlalchemy import Column, Integer, Boolean, DateTime, Index, func, JSON, ForeignKey
from sqlalchemy.sql import expression

try:
    from ..database.base import Base
except ImportError:
    from database.base import Base


class ItemMaintenancePlan(Base):
    """SQLAlchemy ItemMaintenancePlan model mapping to the item_maintenance_plan table."""

    __tablename__ = "item_maintenance_plan"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    task_type_id = Column(Integer, ForeignKey("task_types.id"), nullable=False)
    time_interval_days = Column(Integer, nullable=False)
    custom_interval = Column(JSON, nullable=True)
    is_deleted = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default=expression.false(),
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default=func.current_timestamp(),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default=func.current_timestamp(),
        onupdate=datetime.utcnow,
    )

    __table_args__ = (
        Index("idx_item_maintenance_plan_item_id", "item_id"),
        Index("idx_item_maintenance_plan_task_type_id", "task_type_id"),
        Index("idx_item_maintenance_plan_is_deleted", "is_deleted"),
    )

    def __repr__(self) -> str:
        return f"<ItemMaintenancePlan(id={self.id}, item_id={self.item_id}, task_type_id={self.task_type_id})>"
