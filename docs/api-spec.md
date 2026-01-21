# API Specification

## Base URL

Local development: `http://localhost:8000`

Docker compose: `http://api:8000`

## Authentication

Currently: None (local use only)

Future: JWT tokens (Bearer authentication)

## Response Format

All responses are JSON with the following structure:

### Success Response (200-299)
```json
{
  "data": { ... },
  "message": "Operation successful"
}
```

### Error Response (400-599)
```json
{
  "error": "Error code",
  "message": "Human readable error message",
  "details": { ... }
}
```

## Endpoints

### Health Check

#### GET /health
Check API and database connectivity.

**Response (200 OK)**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### Items

#### GET /api/items
List all items.

**Query Parameters**
- `skip`: Number of items to skip (default: 0)
- `limit`: Number of items to return (default: 100)
- `order_by`: Field to order by (default: created_at)

**Response (200 OK)**
```json
{
  "data": [
    {
      "id": 1,
      "name": "Car - Toyota Camry",
      "description": "Daily commute vehicle",
      "purchase_date": "2020-06-15",
      "created_at": "2025-01-15T10:00:00Z",
      "updated_at": "2025-01-15T10:00:00Z"
    }
  ],
  "total": 1
}
```

#### POST /api/items
Create a new item.

**Request Body**
```json
{
  "name": "Item name",
  "description": "Optional description",
  "purchase_date": "2025-01-15"
}
```

**Response (201 Created)**
```json
{
  "data": {
    "id": 1,
    "name": "Item name",
    "description": "Optional description",
    "purchase_date": "2025-01-15",
    "created_at": "2025-01-15T10:00:00Z",
    "updated_at": "2025-01-15T10:00:00Z"
  },
  "message": "Item created"
}
```

#### GET /api/items/{item_id}
Get a specific item.

**Response (200 OK)**
```json
{
  "data": {
    "id": 1,
    "name": "Car - Toyota Camry",
    "description": "Daily commute vehicle",
    "purchase_date": "2020-06-15",
    "created_at": "2025-01-15T10:00:00Z",
    "updated_at": "2025-01-15T10:00:00Z"
  }
}
```

#### PUT /api/items/{item_id}
Update an item.

**Request Body**
```json
{
  "name": "Updated name",
  "description": "Updated description",
  "purchase_date": "2025-01-15"
}
```

**Response (200 OK)**
```json
{
  "data": { ... },
  "message": "Item updated"
}
```

#### DELETE /api/items/{item_id}
Delete an item and all related data.

**Response (200 OK)**
```json
{
  "message": "Item deleted"
}
```

### Maintenance Task Types

#### GET /api/items/{item_id}/task-types
List maintenance task types for an item.

**Response (200 OK)**
```json
{
  "data": [
    {
      "id": 1,
      "item_id": 1,
      "name": "Oil Change",
      "description": "Change engine oil and filter",
      "frequency_days": 10000,
      "estimated_duration_minutes": 30,
      "created_at": "2025-01-15T10:00:00Z",
      "updated_at": "2025-01-15T10:00:00Z"
    }
  ]
}
```

#### POST /api/items/{item_id}/task-types
Create a new maintenance task type.

**Request Body**
```json
{
  "name": "Oil Change",
  "description": "Change engine oil and filter",
  "frequency_days": 10000,
  "estimated_duration_minutes": 30
}
```

**Response (201 Created)**
```json
{
  "data": { ... },
  "message": "Task type created"
}
```

#### PUT /api/task-types/{task_type_id}
Update a task type.

**Request Body**
```json
{
  "name": "Oil Change",
  "description": "Updated description",
  "frequency_days": 10000,
  "estimated_duration_minutes": 30
}
```

**Response (200 OK)**
```json
{
  "data": { ... },
  "message": "Task type updated"
}
```

#### DELETE /api/task-types/{task_type_id}
Delete a task type.

**Response (200 OK)**
```json
{
  "message": "Task type deleted"
}
```

### Task History

#### GET /api/items/{item_id}/task-history
Get maintenance history for an item.

**Query Parameters**
- `task_type_id`: Filter by task type (optional)
- `skip`: Number of records to skip (default: 0)
- `limit`: Number of records to return (default: 100)
- `order_by`: Field to order by (default: completed_date)

**Response (200 OK)**
```json
{
  "data": [
    {
      "id": 1,
      "item_id": 1,
      "task_type_id": 1,
      "completed_date": "2025-01-15",
      "notes": "Regular maintenance, all OK",
      "created_at": "2025-01-15T10:00:00Z",
      "updated_at": "2025-01-15T10:00:00Z"
    }
  ],
  "total": 1
}
```

#### POST /api/items/{item_id}/task-history
Record a completed maintenance task.

**Request Body**
```json
{
  "task_type_id": 1,
  "completed_date": "2025-01-15",
  "notes": "Optional notes about the task"
}
```

**Response (201 Created)**
```json
{
  "data": { ... },
  "message": "Task recorded"
}
```

#### PUT /api/task-history/{history_id}
Update a task history record.

**Request Body**
```json
{
  "completed_date": "2025-01-15",
  "notes": "Updated notes"
}
```

**Response (200 OK)**
```json
{
  "data": { ... },
  "message": "Task history updated"
}
```

#### DELETE /api/task-history/{history_id}
Delete a task history record.

**Response (200 OK)**
```json
{
  "message": "Task history deleted"
}
```

### Forecast

#### GET /api/items/{item_id}/forecast
Get forecasted maintenance schedule for an item.

**Query Parameters**
- `days_ahead`: Number of days to forecast (default: 365)
- `include_overdue`: Include overdue tasks (default: true)

**Response (200 OK)**
```json
{
  "data": [
    {
      "id": 1,
      "item_id": 1,
      "task_type_id": 1,
      "task_name": "Oil Change",
      "scheduled_date": "2025-02-15",
      "days_until": 31,
      "is_overdue": false,
      "is_completed": false
    }
  ],
  "total": 5
}
```

#### POST /api/items/{item_id}/forecast/regenerate
Recalculate forecast for an item.

**Response (200 OK)**
```json
{
  "data": {
    "item_id": 1,
    "forecast_count": 12,
    "regenerated_at": "2025-01-15T10:30:00Z"
  },
  "message": "Forecast regenerated"
}
```

## Error Codes

| Code | Meaning |
|------|---------|
| 400  | Bad Request - Invalid input |
| 404  | Not Found - Resource doesn't exist |
| 409  | Conflict - Item with name already exists |
| 500  | Internal Server Error |
| 503  | Service Unavailable - Database connection failed |

### Error Response Examples

```json
{
  "error": "validation_error",
  "message": "frequency_days must be positive",
  "details": {
    "field": "frequency_days",
    "value": -1
  }
}
```

## Interactive Documentation

Access the interactive API documentation at:

```
http://localhost:8000/docs
```

This provides:
- Full endpoint documentation
- Request/response examples
- Try It Out functionality
- Schema definitions

Alternative Swagger UI is available at:

```
http://localhost:8000/redoc
```
