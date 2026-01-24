"""Pydantic schemas for maintenance template validation and responses."""

from datetime import datetime
from typing import Optional, Any, Dict
from pydantic import BaseModel, field_validator


class MaintenanceTemplateCreateRequest(BaseModel):
    """Pydantic model for maintenance template creation request validation."""

    item_type_id: int
    task_type_id: int
    time_interval_days: int
    custom_interval: Optional[Dict[str, Any]] = None

    @field_validator("item_type_id", mode="before")
    @classmethod
    def validate_item_type_id(cls, v):
        """Validate item_type_id is a positive integer."""
        if not isinstance(v, int):
            raise ValueError("item_type_id must be an integer")
        if v <= 0:
            raise ValueError("item_type_id must be a positive integer")
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

    @field_validator("time_interval_days", mode="before")
    @classmethod
    def validate_time_interval_days(cls, v):
        """Validate time_interval_days is a positive integer."""
        if not isinstance(v, int):
            raise ValueError("time_interval_days must be an integer")
        if v <= 0:
            raise ValueError("time_interval_days must be a positive integer")
        return v

    @field_validator("custom_interval", mode="before")
    @classmethod
    def validate_custom_interval(cls, v):
        """Validate custom_interval is a dictionary if provided."""
        if v is None:
            return None

        if not isinstance(v, dict):
            raise ValueError("custom_interval must be a dictionary (JSON object)")

        return v


class MaintenanceTemplateResponse(BaseModel):
    """Pydantic model for maintenance template response."""

    id: int
    item_type_id: int
    task_type_id: int
    time_interval_days: int
    custom_interval: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "frozen": True}


class MaintenanceTemplateWithTaskTypeResponse(BaseModel):
    """Pydantic model for maintenance template response with task type name."""

    id: int
    item_type_id: int
    task_type_id: int
    task_type_name: str
    time_interval_days: int
    custom_interval: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "frozen": True}
