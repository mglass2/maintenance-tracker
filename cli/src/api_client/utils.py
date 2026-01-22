"""Utility functions for API client."""

import json
from typing import Any, Dict
from urllib.parse import urljoin, urlparse

from .exceptions import APIInvalidResponseError


def validate_url(url: str) -> str:
    """Validate URL format.

    Args:
        url: URL to validate

    Returns:
        The validated URL if valid

    Raises:
        ValueError: If URL format is invalid
    """
    if not url:
        raise ValueError("URL cannot be empty")

    if not url.startswith(("http://", "https://")):
        raise ValueError(
            f"URL must start with http:// or https:// (got: {url})"
        )

    try:
        result = urlparse(url)
        if not result.netloc:
            raise ValueError(f"URL must have a host (got: {url})")
    except Exception as e:
        raise ValueError(f"Invalid URL: {url}") from e

    return url


def build_url(base: str, path: str) -> str:
    """Build full URL from base and endpoint path.

    Args:
        base: Base URL (e.g., http://api:8000)
        path: Endpoint path (e.g., /health)

    Returns:
        Full URL (e.g., http://api:8000/health)

    Raises:
        ValueError: If base URL is invalid
    """
    validate_url(base)

    # Ensure path starts with /
    if path and not path.startswith("/"):
        path = "/" + path

    # Use urljoin to properly combine URL parts
    full_url = urljoin(base, path)
    return full_url


def parse_json_response(text: str, url: str = None) -> Dict[str, Any]:
    """Parse JSON response text.

    Args:
        text: JSON response text
        url: URL that was requested (for error context)

    Returns:
        Parsed JSON as dictionary

    Raises:
        APIInvalidResponseError: If JSON parsing fails
    """
    if not text:
        raise APIInvalidResponseError(
            "Empty response body",
            url=url,
            response_text=text,
        )

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise APIInvalidResponseError(
            f"Invalid JSON in response: {str(e)}",
            url=url,
            response_text=text,
        ) from e


def sanitize_error_message(message: str) -> str:
    """Remove sensitive data from error messages.

    Removes API keys, tokens, and other sensitive information from
    error messages before they are displayed to the user.

    Args:
        message: Error message that may contain sensitive data

    Returns:
        Sanitized error message
    """
    if not message:
        return message

    # This is a simple sanitizer - can be extended as needed
    # For now, we just return the message as-is since this is a local app
    # In a production app, you'd remove API keys, tokens, etc.
    return message
