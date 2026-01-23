"""Response formatting utilities for consistent API responses."""

from fastapi.responses import JSONResponse
from datetime import datetime
import json


def _serialize_datetime(obj):
    """Serialize datetime objects to ISO format strings."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def success_response(
    data: dict | list,
    message: str = "Success",
    status_code: int = 200,
) -> JSONResponse:
    """
    Format a successful response with data and message.

    Args:
        data: Response data (dictionary or list)
        message: Success message
        status_code: HTTP status code

    Returns:
        JSONResponse with formatted data and message
    """
    content = {
        "data": data,
        "message": message,
    }

    return JSONResponse(
        status_code=status_code,
        content=json.loads(json.dumps(content, default=_serialize_datetime)),
    )


def error_response(
    error: str,
    message: str,
    status_code: int = 400,
    details: dict | None = None,
) -> JSONResponse:
    """
    Format an error response with error code, message, and optional details.

    Args:
        error: Error code (e.g., "DUPLICATE_EMAIL")
        message: Human-readable error message
        status_code: HTTP status code
        details: Optional additional error details

    Returns:
        JSONResponse with formatted error information
    """
    content = {
        "error": error,
        "message": message,
    }

    if details:
        content["details"] = details

    return JSONResponse(
        status_code=status_code,
        content=json.loads(json.dumps(content, default=_serialize_datetime)),
    )
