"""Database session management and connection pooling."""

import os
import warnings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Safety check: Warn if application connects to test database
if "maintenance_tracker_test" in DATABASE_URL:
    warnings.warn(
        "WARNING: Application is connecting to TEST database. "
        f"DATABASE_URL: {DATABASE_URL}",
        RuntimeWarning,
        stacklevel=2
    )

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Session:
    """Dependency injection for database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
