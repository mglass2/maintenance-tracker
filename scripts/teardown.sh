#!/bin/bash

# Teardown script for Maintenance Tracker
# Stops and removes containers and optionally removes volumes

set -e

echo "Maintenance Tracker - Teardown Script"
echo "====================================="

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: docker-compose is not installed"
    exit 1
fi

echo "Stopping and removing containers..."
docker-compose down

read -p "Do you want to remove volumes (this will delete the database)? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Removing volumes..."
    docker-compose down -v
    echo "Volumes removed"
else
    echo "Volumes retained"
fi

echo ""
echo "Teardown complete!"
