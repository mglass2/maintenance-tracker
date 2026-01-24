"""Request logging middleware for API."""

from fastapi import Request


async def request_logging_middleware(request: Request, call_next):
    """
    Middleware to log incoming requests.

    Extracts user ID from X-User-ID header and logs the request method and path.

    Args:
        request: The incoming HTTP request
        call_next: The next middleware or handler in the chain

    Returns:
        The response from the next middleware or handler
    """
    # Extract user ID from header
    user_id = request.headers.get("x-user-id")

    # Extract path from request URL (bug fix: was incorrectly reading from headers)
    path = request.url.path

    # Log the request
    print(f"Request - User: {user_id}, {path}")

    # Call next middleware/handler
    response = await call_next(request)

    return response
