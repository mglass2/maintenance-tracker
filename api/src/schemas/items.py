"""Pydantic schemas for item validation and serialization."""

from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, field_validator, ConfigDict


class ItemCreateRequest(BaseModel):
    """Request schema for creating a new item."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": 1,
                "item_type_id": 1,
                "name": "2015 Toyota Camry",
                "acquired_at": "2015-06-15",
                "details": {"current_miles": 45000, "vin": "JTDKBRFH5J5621359"},
            }
        }
    )

    user_id: Optional[int] = None
    item_type_id: int
    name: str
    acquired_at: Optional[date] = None
    details: Optional[Dict[str, Any]] = None

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and normalize name."""
        if not isinstance(v, str):
            raise ValueError("Name must be a string")

        # Strip whitespace
        v = v.strip()

        # Check if it's whitespace-only
        if not v:
            raise ValueError("Name cannot be empty or whitespace-only")

        # Check length constraints
        if len(v) > 255:
            raise ValueError("Name must be 255 characters or less")

        return v

    @field_validator("user_id", mode="before")
    @classmethod
    def validate_user_id(cls, v: Optional[int]) -> Optional[int]:
        """Validate user_id is positive if provided."""
        if v is not None and v <= 0:
            raise ValueError("User ID must be greater than 0")
        return v

    @field_validator("item_type_id", mode="before")
    @classmethod
    def validate_item_type_id(cls, v: int) -> int:
        """Validate item_type_id is positive."""
        if not isinstance(v, int):
            raise ValueError("Item type ID must be an integer")
        if v <= 0:
            raise ValueError("Item type ID must be greater than 0")
        return v

    @field_validator("details", mode="before")
    @classmethod
    def validate_details(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Validate details is a dictionary if provided."""
        if v is None:
            return None

        if not isinstance(v, dict):
            raise ValueError("details must be a dictionary (JSON object)")

        return v


class ItemResponse(BaseModel):
    """Response schema for item data."""

    model_config = ConfigDict(
        from_attributes=True,
        frozen=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "user_id": 1,
                "item_type_id": 1,
                "name": "2015 Toyota Camry",
                "description": None,
                "acquired_at": "2015-06-15",
                "details": {"current_miles": 45000, "vin": "JTDKBRFH5J5621359"},
                "created_at": "2026-01-23T12:00:00",
                "updated_at": "2026-01-23T12:00:00",
            }
        },
    )

    id: int
    user_id: Optional[int]
    item_type_id: int
    name: str
    description: Optional[str]
    acquired_at: Optional[date]
    details: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime


class ItemListResponse(BaseModel):
    """Response schema for a list of items."""

    model_config = ConfigDict(frozen=True)

    items: List[ItemResponse]
    count: int
