#!/bin/bash

# Test script for Maintenance Tracker
# Runs tests in all services

echo "Maintenance Tracker - Test Suite"
echo "================================"

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: docker-compose is not installed"
    exit 1
fi

# Track test results
test_failed=0

echo ""
echo "Running API tests..."
docker exec -it maintenance-tracker-api pytest -v || test_failed=$((test_failed + 1))

echo ""
echo "Running CLI tests..."
docker exec -it maintenance-tracker-cli pytest -v || test_failed=$((test_failed + 1))

echo ""
if [ $test_failed -eq 0 ]; then
    echo "All tests completed successfully!"
    exit 0
else
    echo "Some tests failed ($test_failed test suite(s))"
    exit 1
fi
