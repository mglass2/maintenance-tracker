# Maintenance Tracker

A comprehensive application for tracking and forecasting maintenance tasks on items you own.

## Overview

The Maintenance Tracker allows you to:
- Record a history of maintenance tasks performed on your items
- Forecast when different types of maintenance need to be performed
- View maintenance history and future schedules

## Architecture

The application uses a 3-tier architecture:

- **CLI**: Command-line interface for user interaction (Python)
- **API**: RESTful API managing business logic (FastAPI/Python)
- **Database**: PostgreSQL for data persistence

All services are containerized using Docker and orchestrated with docker-compose.

## Prerequisites

- Docker (version 20.10 or higher)
- docker-compose (version 1.29 or higher)

## Quick Start

### 1. Setup Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Or use the setup script:

```bash
bash scripts/setup.sh
```

### 2. Start Services

```bash
docker-compose up --build
```

The application will:
- Initialize the PostgreSQL database
- Start the API server (available at http://localhost:8000)
- Start the CLI service

### 3. Verify Installation

In a new terminal, verify the API is running:

```bash
curl http://localhost:8000/health
```

Expected output:
```json
{"status": "healthy"}
```

Access interactive API documentation:

```
http://localhost:8000/docs
```

## Usage

### CLI Commands

To run CLI commands, use:

```bash
docker exec -it maintenance-tracker-cli python -m src.main [COMMAND]
```

Test the CLI:

```bash
docker exec -it maintenance-tracker-cli python -m src.main hello
```

Example output:
```
Hello from Maintenance Tracker CLI!
```

### Database Access

Connect directly to the database:

```bash
docker exec -it maintenance-tracker-db psql -U maintenance_user -d maintenance_tracker
```

### API Endpoints

#### Health Check

```bash
GET /health
```

#### Root

```bash
GET /
```

See `/docs` endpoint for complete API documentation once the application is running.

## Project Structure

```
maintenance-tracker/
├── cli/                           # CLI service
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py               # Entry point
│   │   ├── commands/             # Command modules
│   │   ├── api_client/           # HTTP client
│   │   └── utils/                # Helpers
│   └── tests/
│
├── api/                           # API service
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI app
│   │   ├── models/               # SQLAlchemy models
│   │   ├── routes/               # API endpoints
│   │   ├── services/             # Business logic
│   │   ├── database/             # DB connection
│   │   └── utils/                # Helpers
│   └── tests/
│
├── db/                            # Database
│   ├── init/                      # Initialization scripts
│   │   ├── 01-create-schema.sql  # Schema definition
│   │   └── 02-seed-data.sql      # Sample data
│   └── backups/                   # Backup directory
│
├── shared/                        # Shared code
├── docs/                          # Documentation
└── scripts/                       # Utility scripts
```

## Development

### Running Tests

API tests:

```bash
docker exec -it maintenance-tracker-api pytest
```

CLI tests:

```bash
docker exec -it maintenance-tracker-cli pytest
```

Run all tests:

```bash
bash scripts/test-all.sh
```

### Hot Reload

During development, code changes in `cli/src/`, `api/src/` automatically trigger reloads thanks to volume mounts in docker-compose.yml.

### Stopping Services

```bash
docker-compose down
```

To also remove volumes (clears database):

```bash
docker-compose down -v
```

## Configuration

Environment variables are defined in `.env`:

- `POSTGRES_DB`: Database name (default: `maintenance_tracker`)
- `POSTGRES_USER`: Database user (default: `maintenance_user`)
- `POSTGRES_PASSWORD`: Database password (default: `maintenance_pass`)
- `DATABASE_URL`: PostgreSQL connection string
- `API_HOST`: API server host (default: `0.0.0.0`)
- `API_PORT`: API server port (default: `8000`)
- `API_URL`: API URL for CLI (default: `http://api:8000`)

## Troubleshooting

### Services won't start

Check logs:

```bash
docker-compose logs [SERVICE]
```

Services: `db`, `api`, `cli`

### Database connection issues

Verify database health:

```bash
docker-compose ps
```

All services should show "Up" status.

### Port conflicts

If ports 5432 or 8000 are in use, modify `docker-compose.yml` to use different ports:

```yaml
ports:
  - "5433:5432"  # PostgreSQL
  - "8001:8000"  # API
```

## Technology Stack

- **Framework**: FastAPI (API), Click (CLI)
- **Database**: PostgreSQL 16 Alpine
- **ORM**: SQLAlchemy
- **Testing**: pytest
- **Containerization**: Docker

## License

Open source, permissively licensed.

## Documentation

For detailed documentation, see:

- [Architecture](docs/architecture.md)
- [API Specification](docs/api-spec.md)
- [Database Schema](docs/database-schema.md)
