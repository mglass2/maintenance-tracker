# APIClient Documentation

The `APIClient` class is the core HTTP client for communicating with the Maintenance Tracker API from the CLI service. It handles all request/response communication, error handling, and retry logic.

## Table of Contents

- [Overview](#overview)
- [Installation & Import](#installation--import)
- [Configuration](#configuration)
- [Basic Usage](#basic-usage)
- [Making Requests](#making-requests)
- [Error Handling](#error-handling)
- [Response Models](#response-models)
- [Context Manager](#context-manager)
- [Complete Examples](#complete-examples)

## Overview

The `APIClient` provides:

- **HTTP Communication**: GET, POST, PUT, DELETE, and other HTTP methods
- **Error Handling**: Comprehensive exception handling for network, timeout, and HTTP errors
- **Automatic Retries**: Exponential backoff retry logic for server errors (5xx)
- **Session Management**: Persistent HTTP session with proper headers
- **Response Parsing**: Automatic JSON parsing and validation

## Installation & Import

The `APIClient` is part of the `api_client` package in the CLI service:

```python
from src.api_client import APIClient
```

You can also import related classes:

```python
from src.api_client import (
    APIClient,
    APIConfig,
    APIResponse,
    HealthResponse,
    APIClientError,
    APIConnectionError,
    APITimeoutError,
    APIClientError4xx,
    APIServerError5xx,
)
```

## Configuration

The `APIClient` requires configuration to know where to send requests. Configuration is provided via the `APIConfig` class.

### Using Environment Variables (Recommended)

```python
from src.api_client import APIClient

# Loads API_URL from environment variable
client = APIClient()
```

**Required Environment Variables:**
- `API_URL`: Base URL of the API (e.g., `http://api:8000`)

### Using Explicit Configuration

```python
from src.api_client import APIClient, APIConfig

config = APIConfig(
    base_url="http://api:8000",
    timeout=30,           # Request timeout in seconds (default: 30)
    max_retries=3,        # Max retries for 5xx errors (default: 3)
    retry_backoff=0.5,    # Backoff multiplier for exponential backoff (default: 0.5)
)

client = APIClient(config=config)
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `base_url` | str | (required) | Base URL of the API (must start with http:// or https://) |
| `timeout` | int | 30 | Request timeout in seconds (must be > 0) |
| `max_retries` | int | 3 | Maximum retries for server errors (must be >= 0) |
| `retry_backoff` | float | 0.5 | Initial backoff multiplier for exponential backoff (must be >= 0) |

## Basic Usage

### Simple GET Request

```python
from src.api_client import APIClient

client = APIClient()
response = client._make_request("GET", "/health")

print(response.status_code)  # 200
print(response.data)         # {'status': 'healthy'}
print(response.headers)      # {'content-type': 'application/json', ...}

client.close()
```

### POST Request with Data

```python
from src.api_client import APIClient

client = APIClient()

data = {
    "name": "Oil Change",
    "interval_days": 180,
    "description": "Change engine oil"
}

response = client._make_request("POST", "/maintenance-types", data=data)

print(response.status_code)  # 201
print(response.data)         # {'id': 1, 'name': 'Oil Change', ...}

client.close()
```

## Making Requests

The `_make_request()` method is the primary way to communicate with the API.

### Method Signature

```python
def _make_request(
    method: str,
    endpoint: str,
    data: Optional[dict] = None,
) -> APIResponse:
    """
    Make HTTP request to API with error handling and retries.

    Args:
        method: HTTP method (GET, POST, PUT, DELETE, PATCH, etc.)
        endpoint: API endpoint path (e.g., /health, /items/123)
        data: Request body data (optional, for POST/PUT/PATCH)

    Returns:
        APIResponse with status code, data, and headers

    Raises:
        APIConnectionError: On network/connection failures
        APITimeoutError: On request timeout
        APIClientError4xx: On 4xx HTTP response (no retry)
        APIServerError5xx: On 5xx HTTP response (with retry)
        APIInvalidResponseError: On malformed response
    """
```

### Request Examples

```python
# GET request
response = client._make_request("GET", "/items")

# GET request with path parameters
response = client._make_request("GET", "/items/123")

# POST request
response = client._make_request("POST", "/items", data={"name": "Item 1"})

# PUT request (update)
response = client._make_request("PUT", "/items/123", data={"name": "Updated Name"})

# DELETE request
response = client._make_request("DELETE", "/items/123")
```

## Error Handling

The `APIClient` raises specific exceptions for different error scenarios. Always handle these exceptions in your code.

### Exception Hierarchy

```
APIClientError (base)
├── APIConnectionError
├── APITimeoutError
├── APIInvalidResponseError
├── APIConfigurationError
└── APIResponseError
    ├── APIClientError4xx
    └── APIServerError5xx
```

### Handling Specific Errors

```python
from src.api_client import (
    APIClient,
    APIConnectionError,
    APITimeoutError,
    APIClientError4xx,
    APIServerError5xx,
)

client = APIClient()

try:
    response = client._make_request("GET", "/items/123")
except APIConnectionError as e:
    print(f"Connection failed: {e.message}")
    print(f"URL: {e.url}")
except APITimeoutError as e:
    print(f"Request timed out: {e.message}")
except APIClientError4xx as e:
    print(f"Client error: {e.status_code}")
    print(f"Response: {e.response_body}")
except APIServerError5xx as e:
    print(f"Server error (after retries): {e.status_code}")
finally:
    client.close()
```

### Exception Details

**APIConnectionError**
- Raised when connection to API fails
- Attributes: `message`, `url`

**APITimeoutError**
- Raised when API request exceeds the timeout
- Attributes: `message`, `url`

**APIClientError4xx**
- Raised for 4xx HTTP responses (e.g., 400, 404)
- No automatic retries
- Attributes: `message`, `url`, `status_code`, `response_body`

**APIServerError5xx**
- Raised for 5xx HTTP responses after max retries exceeded
- Automatically retried with exponential backoff
- Attributes: `message`, `url`, `status_code`, `response_body`

**APIInvalidResponseError**
- Raised when API response is malformed or cannot be parsed
- Attributes: `message`, `url`, `response_text`

### Retry Behavior

The client automatically retries requests that fail with 5xx errors using exponential backoff:

```
Retry 1: wait 0.5 seconds (0.5 * 2^0)
Retry 2: wait 1.0 seconds (0.5 * 2^1)
Retry 3: wait 2.0 seconds (0.5 * 2^2)
```

This is configurable via `APIConfig.max_retries` and `APIConfig.retry_backoff`.

## Response Models

### APIResponse

Generic response model for all API requests.

```python
from src.api_client import APIResponse

response = client._make_request("GET", "/items")

# Attributes
response.status_code  # int: HTTP status code (e.g., 200, 404)
response.data         # dict: Parsed JSON response body
response.headers      # dict: HTTP response headers

# Methods
response.is_success()      # bool: True if 2xx status
response.is_client_error() # bool: True if 4xx status
response.is_server_error() # bool: True if 5xx status
```

### HealthResponse

Specialized response model for health check endpoint.

```python
from src.api_client import APIClient, HealthResponse

client = APIClient()
response = client._make_request("GET", "/health")

# Parse as HealthResponse
health = HealthResponse.from_dict(response.data)

# Attributes
health.status  # str: Health status (typically "healthy" or "unhealthy")

# Methods
health.is_healthy()  # bool: True if status is "healthy"
```

## Context Manager

The `APIClient` supports the context manager protocol for automatic resource cleanup.

### Using with Statement

```python
from src.api_client import APIClient

# Session is automatically closed
with APIClient() as client:
    response = client._make_request("GET", "/health")
    print(response.data)
# Session is automatically closed here
```

### Without Context Manager (Manual Cleanup)

```python
from src.api_client import APIClient

client = APIClient()
try:
    response = client._make_request("GET", "/health")
    print(response.data)
finally:
    client.close()  # Must call close() manually
```

## Complete Examples

### Example 1: Health Check

```python
from src.api_client import APIClient, HealthResponse, APITimeoutError

with APIClient() as client:
    try:
        response = client._make_request("GET", "/health")
        health = HealthResponse.from_dict(response.data)

        if health.is_healthy():
            print("API is healthy")
        else:
            print(f"API is unhealthy: {health.status}")
    except APITimeoutError:
        print("API is not responding")
```

### Example 2: Create and Retrieve Item

```python
from src.api_client import APIClient, APIClientError4xx

with APIClient() as client:
    # Create an item
    create_data = {
        "name": "Car",
        "make": "Toyota",
        "model": "Camry",
    }

    try:
        create_response = client._make_request("POST", "/items", data=create_data)
        item_id = create_response.data.get("id")
        print(f"Created item with ID: {item_id}")

        # Retrieve the item
        get_response = client._make_request("GET", f"/items/{item_id}")
        item = get_response.data
        print(f"Item: {item}")
    except APIClientError4xx as e:
        print(f"Error: {e.message}")
        print(f"Response: {e.response_body}")
```

### Example 3: List Items with Error Handling

```python
from src.api_client import (
    APIClient,
    APIConnectionError,
    APITimeoutError,
    APIServerError5xx,
)

with APIClient() as client:
    try:
        response = client._make_request("GET", "/items")

        if response.is_success():
            items = response.data.get("items", [])
            print(f"Found {len(items)} items")
            for item in items:
                print(f"  - {item['name']}")
        else:
            print(f"Unexpected status: {response.status_code}")

    except APIConnectionError as e:
        print(f"Cannot connect to API: {e.url}")
    except APITimeoutError as e:
        print(f"API request timed out")
    except APIServerError5xx as e:
        print(f"API server error (after retries): {e.status_code}")
```

### Example 4: Update and Delete

```python
from src.api_client import APIClient, APIClientError4xx

with APIClient() as client:
    item_id = 123

    # Update item
    update_data = {
        "name": "Car - Updated",
        "notes": "Regular maintenance performed"
    }

    try:
        update_response = client._make_request(
            "PUT",
            f"/items/{item_id}",
            data=update_data
        )
        print(f"Updated item: {update_response.data}")

        # Delete item
        delete_response = client._make_request("DELETE", f"/items/{item_id}")

        if delete_response.is_success():
            print(f"Item {item_id} deleted successfully")

    except APIClientError4xx as e:
        print(f"Error: {e.message}")
        print(f"Status: {e.status_code}")
```

### Example 5: Batch Operations with Error Recovery

```python
from src.api_client import (
    APIClient,
    APIClientError4xx,
    APIConnectionError,
)

def create_items(items_data):
    """Create multiple items, handling errors gracefully."""
    created_items = []
    failed_items = []

    with APIClient() as client:
        for item_data in items_data:
            try:
                response = client._make_request("POST", "/items", data=item_data)
                created_items.append(response.data)
            except APIClientError4xx as e:
                failed_items.append({
                    "data": item_data,
                    "error": e.message,
                    "status": e.status_code
                })
            except APIConnectionError:
                # Stop on connection errors
                print("Connection lost, stopping batch operation")
                break

    return created_items, failed_items

# Usage
items = [
    {"name": "Car", "make": "Toyota"},
    {"name": "Bike", "make": "Honda"},
    {"name": "Truck", "make": "Ford"},
]

created, failed = create_items(items)
print(f"Created: {len(created)}, Failed: {len(failed)}")
```

## Best Practices

1. **Always use context manager**: Ensures the session is properly closed
   ```python
   with APIClient() as client:
       response = client._make_request("GET", "/endpoint")
   ```

2. **Handle specific exceptions**: Catch specific exception types, not generic `Exception`
   ```python
   except APIClientError4xx as e:
       # Handle 4xx errors
   except APIServerError5xx as e:
       # Handle 5xx errors (after retries)
   ```

3. **Check response status**: Use helper methods to check response status
   ```python
   if response.is_success():
       data = response.data
   ```

4. **Set environment variables**: Configure the API URL via environment variables
   ```bash
   export API_URL=http://api:8000
   ```

5. **Validate response data**: Verify required fields exist before accessing
   ```python
   item_id = response.data.get("id")  # Safe access
   item_name = response.data["name"]  # Risky - may KeyError
   ```

6. **Log errors**: Log errors for debugging
   ```python
   except APIClientError4xx as e:
       print(f"API error: {e.message} (Status: {e.status_code})")
       print(f"Response: {e.response_body}")
   ```
