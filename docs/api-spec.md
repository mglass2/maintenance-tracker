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

## Error Codes

| Code | Meaning |
|------|---------|
| 400  | Bad Request - Invalid input |
| 404  | Not Found - Resource doesn't exist |
| 409  | Conflict - Item with name already exists |
| 500  | Internal Server Error |
| 503  | Service Unavailable - Database connection failed |


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
