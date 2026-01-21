# Architecture Overview

## System Design

The Maintenance Tracker uses a 3-tier architecture pattern with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                     User Environment                         │
├─────────────────────────────────────────────────────────────┤
│  Presentation Layer (CLI)                                   │
│  ├─ User Commands (items, tasks, forecast)                 │
│  ├─ Output Formatting & Display                            │
│  └─ API Client (HTTP calls to API)                         │
├─────────────────────────────────────────────────────────────┤
│  Application Layer (API)                                    │
│  ├─ Request Handling & Routing                             │
│  ├─ Business Logic & Forecast Calculations                 │
│  ├─ Data Validation & Error Handling                       │
│  └─ Database Abstraction (SQLAlchemy ORM)                  │
├─────────────────────────────────────────────────────────────┤
│  Data Layer (PostgreSQL)                                    │
│  ├─ Items (things to maintain)                             │
│  ├─ Task Types (types of maintenance)                      │
│  ├─ Task History (completed maintenance)                   │
│  └─ Forecasted Schedule (predicted future maintenance)     │
└─────────────────────────────────────────────────────────────┘
```

## Service Architecture

All services run in Docker containers and are orchestrated via docker-compose:

### Database Service (db)
- **Image**: PostgreSQL 16 Alpine
- **Role**: Persistent data storage
- **Health Check**: pg_isready command
- **Volume**: Named volume for data persistence across container restarts

### API Service (api)
- **Framework**: FastAPI (Python)
- **Role**: Business logic and data management
- **Dependencies**: Depends on database health check
- **Hot Reload**: Source code mounted as volume for development

### CLI Service (cli)
- **Framework**: Click (Python)
- **Role**: User interface
- **Dependencies**: Depends on API availability
- **Communication**: HTTP requests to API service

## Technology Choices

### FastAPI (API Framework)
**Why**: Modern, fast, auto-generated API documentation, type hints, easy testing

- Built on Starlette (high performance)
- Automatic OpenAPI/Swagger docs at `/docs`
- Strong type validation with Pydantic
- Excellent async/await support
- Simple dependency injection

### SQLAlchemy (ORM)
**Why**: Industry standard, database-agnostic, type-safe

- Declarative model definitions
- Automatic schema generation
- Query builder with intuitive syntax
- Transaction support
- Supports PostgreSQL features

### Click (CLI Framework)
**Why**: Simple, elegant, organized command structure

- Decorator-based command definition
- Automatic help text generation
- Type validation
- Easy testing with CliRunner

### PostgreSQL (Database)
**Why**: Powerful, reliable, open-source, excellent for local use

- ACID compliance
- Advanced data types and indexing
- Full-text search capability
- JSON support
- Proven stability

## Communication Flow

### User Creates a Maintenance Task Record

```
1. User → CLI: `maintenance-tracker add-task --item Car --type "Oil Change" --date 2025-01-15`
2. CLI → API: POST /api/tasks
   {
     "item_id": 1,
     "task_type_id": 1,
     "completed_date": "2025-01-15"
   }
3. API → Database: INSERT INTO task_history (...)
4. Database → API: Confirm insertion
5. API → CLI: 201 Created with task details
6. CLI → User: "Task recorded successfully"
```

### User Views Forecast

```
1. User → CLI: `maintenance-tracker forecast --item Car`
2. CLI → API: GET /api/items/1/forecast
3. API → Database: SELECT from forecasted_schedule WHERE item_id = 1
4. Database → API: Return forecast results
5. API → CLI: JSON response with upcoming maintenance dates
6. CLI → User: Formatted table of upcoming maintenance
```

## Data Model

### Items
- Represents items that require maintenance
- Has one-to-many relationship with task types and history

### Maintenance Task Types
- Defines categories of maintenance for an item
- Specifies frequency and duration estimates
- Used to forecast schedules

### Task History
- Records completed maintenance tasks
- Links items to task types
- Provides basis for forecasting

### Forecasted Schedule
- Calculates and stores predicted maintenance dates
- Generated based on task type frequency and history
- Tracks completion status

## API Design Principles

1. **RESTful**: Resources and standard HTTP methods
2. **Stateless**: Each request is independent
3. **JSON**: All request/response bodies
4. **Error Handling**: Consistent error response format
5. **Versioning**: Ready for future API versions
6. **Documentation**: Self-documenting via OpenAPI

## Security Considerations

### Current Implementation
- No authentication (local use only)
- No encryption (local environment)
- Standard SQL injection prevention via ORM

### Production Recommendations
- Add JWT authentication
- Use HTTPS/TLS
- Implement rate limiting
- Add request logging and audit trails
- Use secrets management for credentials
- Implement RBAC (Role-Based Access Control)

## Deployment Architecture

### Local Development
```
User's Computer
├── Docker Engine
└── docker-compose orchestration
    ├── PostgreSQL container
    ├── API container
    └── CLI container
```

### Future Multi-Machine Deployment
```
Kubernetes Cluster
├── PostgreSQL Pod (with PersistentVolume)
├── API Pods (replicated)
├── CLI Jobs/Pods
└── ConfigMaps/Secrets for configuration
```

## Scaling Considerations

### Current Limitations
- Single database instance (no replication)
- Single API instance
- CLI is ephemeral, interactive only

### Scaling Path
1. **Horizontal API scaling**: Multiple API replicas
2. **Database clustering**: PostgreSQL streaming replication
3. **Load balancing**: Nginx or similar reverse proxy
4. **Caching**: Redis for frequently accessed data
5. **Async jobs**: Background task processing for forecasts

## Development Workflow

### Adding a New Feature

1. **Database**: Update schema in `db/init/01-create-schema.sql`
2. **API Model**: Create SQLAlchemy model in `api/src/models/`
3. **API Route**: Add endpoint in `api/src/routes/`
4. **API Service**: Add business logic in `api/src/services/`
5. **CLI Command**: Add command in `cli/src/commands/`
6. **Tests**: Add tests in respective `tests/` directories
7. **Documentation**: Update API docs and README

### Testing Strategy

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test API endpoints with real database
- **CLI Tests**: Test command parsing and output

Run with: `bash scripts/test-all.sh`
