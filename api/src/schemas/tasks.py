"""Pydantic schemas for task validation and responses."""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, field_validator


class TaskCreateRequest(BaseModel):
    """Pydantic model for task creation request validation."""

    item_id: int
    task_type_id: int
    completed_at: date
    notes: Optional[str] = None
    cost: Optional[Decimal] = None
    details: Optional[Dict[str, Any]] = None

    @field_validator("item_id", mode="before")
    @classmethod
    def validate_item_id(cls, v):
        """Validate item_id is a positive integer."""
        if not isinstance(v, int):
            raise ValueError("item_id must be an integer")
        if v <= 0:
            raise ValueError("item_id must be a positive integer")
        return v

    @field_validator("task_type_id", mode="before")
    @classmethod
    def validate_task_type_id(cls, v):
        """Validate task_type_id is a positive integer."""
        if not isinstance(v, int):
            raise ValueError("task_type_id must be an integer")
        if v <= 0:
            raise ValueError("task_type_id must be a positive integer")
        return v

    @field_validator("cost", mode="before")
    @classmethod
    def validate_cost(cls, v):
        """Validate cost is non-negative if provided."""
        if v is None:
            return None

        # Convert to Decimal for precision
        try:
            cost_decimal = Decimal(str(v))
        except (TypeError, ValueError, Exception):
            raise ValueError("cost must be a valid decimal number")

        if cost_decimal < 0:
            raise ValueError("cost must be non-negative")

        return cost_decimal

    @field_validator("notes", mode="before")
    @classmethod
    def validate_notes(cls, v):
        """Validate and normalize notes field."""
        if v is None:
            return None

        if not isinstance(v, str):
            raise ValueError("notes must be a string")

        # Strip whitespace but allow empty strings to become None
        v = v.strip()
        return v if v else None

    @field_validator("details", mode="before")
    @classmethod
    def validate_details(cls, v):
        """Validate details is a dict if provided."""
        if v is None:
            return None

        if not isinstance(v, dict):
            raise ValueError("details must be a JSON object (dict)")

        return v


class TaskResponse(BaseModel):
    """Pydantic model for task response."""

    id: int
    item_id: int
    task_type_id: int
    completed_at: date
    notes: Optional[str] = None
    cost: Optional[Decimal] = None
    details: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "frozen": True}


class TaskListResponse(BaseModel):
    """Response schema for a list of tasks."""

    model_config = {"frozen": True}

    tasks: List[TaskResponse]
    count: int
