"""SQLAlchemy MaintenanceTemplate ORM model."""

from datetime import datetime
from sqlalchemy import Column, Integer, Boolean, DateTime, Index, func, JSON, ForeignKey
from sqlalchemy.sql import expression

try:
    from ..database.base import Base
except ImportError:
    from database.base import Base


class MaintenanceTemplate(Base):
    """SQLAlchemy MaintenanceTemplate model mapping to the maintenance_template table."""

    __tablename__ = "maintenance_template"

    id = Column(Integer, primary_key=True, index=True)
    item_type_id = Column(Integer, ForeignKey("item_types.id"), nullable=False)
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
        Index("idx_maintenance_template_item_type_id", "item_type_id"),
        Index("idx_maintenance_template_task_type_id", "task_type_id"),
        Index("idx_maintenance_template_is_deleted", "is_deleted"),
    )

    def __repr__(self) -> str:
        return f"<MaintenanceTemplate(id={self.id}, item_type_id={self.item_type_id}, task_type_id={self.task_type_id})>"
