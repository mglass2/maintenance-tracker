"""Pydantic schemas for item type validation and responses."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class ItemTypeCreateRequest(BaseModel):
    """Pydantic model for item type creation request validation."""

    name: str
    description: Optional[str] = None

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and normalize name field."""
        if not isinstance(v, str):
            raise ValueError("name must be a string")

        v = v.strip()
        if not v:
            raise ValueError("name cannot be empty or whitespace-only")
        if len(v) > 255:
            raise ValueError("name must be 255 characters or less")

        return v

    @field_validator("description", mode="before")
    @classmethod
    def validate_description(cls, v):
        """Validate and normalize description field."""
        if v is None:
            return None

        if not isinstance(v, str):
            raise ValueError("description must be a string")

        # Strip whitespace but allow empty strings to become None
        v = v.strip()
        return v if v else None


class ItemTypeResponse(BaseModel):
    """Pydantic model for item type response."""

    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "frozen": True}
