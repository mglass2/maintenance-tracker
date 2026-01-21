"""Main FastAPI application entry point."""

from fastapi import FastAPI

app = FastAPI(
    title="Maintenance Tracker API",
    description="API for managing and forecasting maintenance tasks",
    version="0.1.0",
)


@app.get("/")
def read_root():
    """Health check endpoint."""
    return {"message": "Maintenance Tracker API is running"}


@app.get("/health")
def health_check():
    """Detailed health check endpoint."""
    return {"status": "healthy"}
