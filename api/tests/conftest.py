"""Pytest configuration and fixtures for testing."""

import os
import sys
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

# Add src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

# Use PostgreSQL for testing (to support JSONB and other PG-specific types)
# Database URL from environment or default for local development
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@db:5432/maintenance_tracker_test"
)

test_engine = create_engine(
    DATABASE_URL,
    echo=False,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Import modules after creating test engine
from database.base import Base
from database.connection import get_db
from main import app

# Import models to register them with Base
from models.user import User
from models.item import Item
from models.task import Task
from models.item_type import ItemType
from models.task_type import TaskType
from models.maintenance_template import MaintenanceTemplate
from models.item_maintenance_plan import ItemMaintenancePlan


@pytest.fixture(scope="function")
def db():
    """Create a test database and session."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Drop all tables with CASCADE to handle foreign key constraints
        with test_engine.begin() as connection:
            connection.exec_driver_sql("DROP SCHEMA public CASCADE")
            connection.exec_driver_sql("CREATE SCHEMA public")


@pytest.fixture(scope="function")
def client(db: Session):
    """Create a test client with overridden database dependency."""

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def db_with_item_types(db: Session):
    """Create a test database with pre-populated item types."""
    # Insert test item types
    item_type_automobile = ItemType(
        name="Automobile",
        description="Motor vehicles including cars, trucks, and motorcycles"
    )
    item_type_house = ItemType(
        name="House",
        description="Residential buildings and properties"
    )
    db.add(item_type_automobile)
    db.add(item_type_house)
    db.commit()
    db.refresh(item_type_automobile)
    db.refresh(item_type_house)

    return db


@pytest.fixture(scope="function")
def client_with_item_types(db_with_item_types: Session):
    """Create a test client with overridden database dependency and pre-populated item types."""

    def override_get_db():
        try:
            yield db_with_item_types
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
