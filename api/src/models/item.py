"""SQLAlchemy Item ORM model."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, Date, DateTime, Index, func, ForeignKey
from sqlalchemy.sql import expression

try:
    from ..database.base import Base
except ImportError:
    from database.base import Base


class Item(Base):
    """SQLAlchemy Item model mapping to the items table."""

    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)  # ForeignKey to users - validated in service
    item_type_id = Column(Integer, nullable=False)  # ForeignKey to item_types - validated in service
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    acquired_at = Column(Date, nullable=True)
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
        Index("idx_items_user_id", "user_id"),
        Index("idx_items_item_type_id", "item_type_id"),
        Index("idx_items_is_deleted", "is_deleted"),
    )

    def __repr__(self) -> str:
        return f"<Item(id={self.id}, name={self.name}, user_id={self.user_id}, item_type_id={self.item_type_id})>"
