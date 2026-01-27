#!/bin/bash
# Initialize test database schema WITHOUT seed data
# This script applies all migrations to the test database while skipping 02-seed-data.sql
# It's idempotent and safe to run multiple times

set -e

echo "Initializing test database schema..."

# Wait for database to be ready
until pg_isready -h db -U ${POSTGRES_USER:-maintenance_user}; do
  echo "Waiting for database..."
  sleep 1
done

# Set password for psql if needed
export PGPASSWORD=${POSTGRES_PASSWORD}

# Apply schema creation (01-create-schema.sql)
if [ -f /docker-entrypoint-initdb.d/01-create-schema.sql ]; then
  echo "Applying schema..."
  psql -h db -U ${POSTGRES_USER:-maintenance_user} -d maintenance_tracker_test -f /docker-entrypoint-initdb.d/01-create-schema.sql
fi

# Apply all migrations (03-*.sql, 04-*.sql, 05-*.sql, 06-*.sql, 07-*.sql)
# Note: 02-seed-data.sql is intentionally skipped for test database
for migration in /docker-entrypoint-initdb.d/03-*.sql \
                 /docker-entrypoint-initdb.d/04-*.sql \
                 /docker-entrypoint-initdb.d/05-*.sql \
                 /docker-entrypoint-initdb.d/06-*.sql \
                 /docker-entrypoint-initdb.d/07-*.sql; do
  if [ -f "$migration" ]; then
    echo "Applying $(basename "$migration")..."
    psql -h db -U ${POSTGRES_USER:-maintenance_user} -d maintenance_tracker_test -f "$migration"
  fi
done

echo "Test database schema initialization complete!"
