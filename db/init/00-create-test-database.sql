-- Create test database (if not exists)
-- This file runs FIRST (00-* naming convention) when PostgreSQL container starts
-- The test database is separate and safe for destructive operations like DROP SCHEMA CASCADE

SELECT 'CREATE DATABASE maintenance_tracker_test'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'maintenance_tracker_test')\gexec

-- Grant permissions to maintenance_user (the app user)
GRANT ALL PRIVILEGES ON DATABASE maintenance_tracker_test TO maintenance_user;

-- Comment for clarity
COMMENT ON DATABASE maintenance_tracker_test IS 'Test database for running automated tests. Safe for destructive operations.';
