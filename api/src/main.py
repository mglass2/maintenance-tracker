"""Main FastAPI application entry point."""

from fastapi import FastAPI

try:
    # Try relative imports first (when run as a package)
    from .routes import users, items, tasks, item_types, task_types
except ImportError:
    # Fall back to absolute imports (when run with modified sys.path)
    from routes import users, items, tasks, item_types, task_types

app = FastAPI(
    title="Maintenance Tracker API",
    description="API for managing and forecasting maintenance tasks",
    version="0.1.0",
)

# Include routers
app.include_router(users.router)
app.include_router(items.router)
app.include_router(tasks.router)
app.include_router(item_types.router)
app.include_router(task_types.router)


@app.get("/")
def read_root():
    """Health check endpoint."""
    return {"message": "Maintenance Tracker API is running"}


@app.get("/health")
def health_check():
    """Detailed health check endpoint."""
    return {"status": "healthy"}
