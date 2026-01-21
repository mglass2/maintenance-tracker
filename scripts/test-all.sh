#!/bin/bash

# Test script for Maintenance Tracker
# Runs tests in all services

set -e

echo "Maintenance Tracker - Test Suite"
echo "================================"

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: docker-compose is not installed"
    exit 1
fi

echo ""
echo "Running API tests..."
docker exec -it maintenance-tracker-api pytest -v

echo ""
echo "Running CLI tests..."
docker exec -it maintenance-tracker-cli pytest -v

echo ""
echo "All tests completed!"
