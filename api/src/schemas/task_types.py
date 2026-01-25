"""Pydantic schemas for task type validation and responses."""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, field_validator


class TaskTypeCreateRequest(BaseModel):
    """Pydantic model for task type creation request validation."""

    name: str
    description: Optional[str] = None
    item_type_id: int

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

    @field_validator("item_type_id", mode="before")
    @classmethod
    def validate_item_type_id(cls, v) -> int:
        """Validate that item_type_id is a positive integer."""
        if not isinstance(v, int):
            raise ValueError("item_type_id must be an integer")
        if v <= 0:
            raise ValueError("item_type_id must be a positive integer")
        return v


class TaskTypeResponse(BaseModel):
    """Pydantic model for task type response."""

    id: int
    name: str
    description: Optional[str] = None
    item_type_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "frozen": True}


class TaskTypeListResponse(BaseModel):
    """Pydantic model for task type list response."""

    task_types: List[TaskTypeResponse]
    count: int

    model_config = {"frozen": True}
