"""Pydantic schemas for user validation and serialization."""

from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict


class UserCreateRequest(BaseModel):
    """Request schema for creating a new user."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "John Doe",
                "email": "john@example.com",
            }
        }
    )

    name: str
    email: EmailStr

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        """Normalize email to lowercase."""
        if isinstance(v, str):
            return v.lower().strip()
        return v

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


class UserResponse(BaseModel):
    """Response schema for user data."""

    model_config = ConfigDict(
        from_attributes=True,
        frozen=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "John Doe",
                "email": "john@example.com",
                "created_at": "2026-01-22T12:00:00",
                "updated_at": "2026-01-22T12:00:00",
            }
        },
    )

    id: int
    name: str
    email: str
    created_at: datetime
    updated_at: datetime


class ErrorResponse(BaseModel):
    """Standard error response schema."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": "DUPLICATE_EMAIL",
                "message": "Email already exists",
                "details": None,
            }
        }
    )

    error: str
    message: str
    details: dict | None = None
