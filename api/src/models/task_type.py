"""SQLAlchemy TaskType ORM model."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Index, func
from sqlalchemy.sql import expression

try:
    from ..database.base import Base
except ImportError:
    from database.base import Base


class TaskType(Base):
    """SQLAlchemy TaskType model mapping to the task_types table."""

    __tablename__ = "task_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
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
        Index("idx_task_types_is_deleted", "is_deleted"),
    )

    def __repr__(self) -> str:
        return f"<TaskType(id={self.id}, name={self.name})>"
