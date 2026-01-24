"""Pydantic schemas for item maintenance plan validation and responses."""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, field_validator, ConfigDict


class ItemMaintenancePlanCreateRequest(BaseModel):
    """Request schema for creating a new item maintenance plan."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "item_id": 1,
                "task_type_id": 2,
                "time_interval_days": 90,
                "custom_interval": {"type": "mileage", "value": 5000, "unit": "miles"},
            }
        }
    )

    item_id: int
    task_type_id: int
    time_interval_days: int
    custom_interval: Optional[Dict[str, Any]] = None

    @field_validator("item_id", mode="before")
    @classmethod
    def validate_item_id(cls, v: int) -> int:
        """Validate item_id is positive."""
        if not isinstance(v, int):
            raise ValueError("item_id must be an integer")
        if v <= 0:
            raise ValueError("item_id must be greater than 0")
        return v

    @field_validator("task_type_id", mode="before")
    @classmethod
    def validate_task_type_id(cls, v: int) -> int:
        """Validate task_type_id is positive."""
        if not isinstance(v, int):
            raise ValueError("task_type_id must be an integer")
        if v <= 0:
            raise ValueError("task_type_id must be greater than 0")
        return v

    @field_validator("time_interval_days", mode="before")
    @classmethod
    def validate_time_interval_days(cls, v: int) -> int:
        """Validate time_interval_days is positive."""
        if not isinstance(v, int):
            raise ValueError("time_interval_days must be an integer")
        if v <= 0:
            raise ValueError("time_interval_days must be greater than 0")
        return v

    @field_validator("custom_interval", mode="before")
    @classmethod
    def validate_custom_interval(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Validate custom_interval is a dictionary if provided."""
        if v is None:
            return None
        if not isinstance(v, dict):
            raise ValueError("custom_interval must be a dictionary (JSON object)")
        return v


class ItemMaintenancePlanResponse(BaseModel):
    """Response schema for item maintenance plan data."""

    model_config = ConfigDict(
        from_attributes=True,
        frozen=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "item_id": 1,
                "task_type_id": 2,
                "time_interval_days": 90,
                "custom_interval": {"type": "mileage", "value": 5000, "unit": "miles"},
                "created_at": "2026-01-24T12:00:00",
                "updated_at": "2026-01-24T12:00:00",
            }
        },
    )

    id: int
    item_id: int
    task_type_id: int
    time_interval_days: int
    custom_interval: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
