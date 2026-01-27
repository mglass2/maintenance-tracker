#!/bin/bash

# Test script for Maintenance Tracker
# Runs tests in all services with a separate test database to protect application data

set -e

# Load environment variables from .env file
set -a
source "$(dirname "$0")/../.env"
set +a

echo "Maintenance Tracker - Test Suite"
echo "================================"

# Initialize test database schema (idempotent)
echo ""
echo "Initializing test database schema..."
docker exec \
  -e POSTGRES_USER=${POSTGRES_USER} \
  -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
  maintenance-tracker-db /db-init-test/apply-schema.sh

# Track test results
test_failed=0

echo ""
echo "Running API tests..."
docker exec \
  -e TEST_DATABASE_URL="postgresql://postgres:postgres@db:5432/maintenance_tracker_test" \
  maintenance-tracker-api \
  pytest -v || test_failed=$((test_failed + 1))

echo ""
echo "Running CLI tests..."
docker exec \
  -e TEST_DATABASE_URL="postgresql://postgres:postgres@db:5432/maintenance_tracker_test" \
  maintenance-tracker-cli \
  pytest -v || test_failed=$((test_failed + 1))

echo ""
if [ $test_failed -eq 0 ]; then
    echo "All tests completed successfully!"
    echo "Application database was NOT modified."
    exit 0
else
    echo "Some tests failed ($test_failed test suite(s))"
    exit 1
fi
