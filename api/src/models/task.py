"""SQLAlchemy Task ORM model."""

from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, Text, Boolean, Date, DateTime, Index, func, Numeric
from sqlalchemy.sql import expression

try:
    from ..database.base import Base
except ImportError:
    from database.base import Base


class Task(Base):
    """SQLAlchemy Task model mapping to the tasks table."""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, nullable=False)  # ForeignKey to items - validated in service
    task_type_id = Column(Integer, nullable=False)  # ForeignKey to task_types - validated in service
    completed_at = Column(Date, nullable=False)
    notes = Column(Text, nullable=True)
    cost = Column(Numeric(10, 2), nullable=True)
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
        Index("idx_tasks_item_id", "item_id"),
        Index("idx_tasks_task_type_id", "task_type_id"),
        Index("idx_tasks_completed_at", "completed_at"),
        Index("idx_tasks_is_deleted", "is_deleted"),
    )

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, item_id={self.item_id}, task_type_id={self.task_type_id}, completed_at={self.completed_at})>"
