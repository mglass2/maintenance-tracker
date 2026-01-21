#!/bin/bash

# Setup script for Maintenance Tracker
# Creates .env file and starts Docker services

set -e

echo "Maintenance Tracker - Setup Script"
echo "=================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo ".env file created successfully"
else
    echo ".env file already exists, skipping..."
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: docker-compose is not installed"
    exit 1
fi

echo ""
echo "Building and starting services..."
docker-compose up --build -d

echo ""
echo "Waiting for services to be ready..."
sleep 5

echo ""
echo "Setup complete!"
echo ""
echo "Services:"
docker-compose ps
echo ""
echo "API Documentation: http://localhost:8000/docs"
echo "API Health Check: http://localhost:8000/health"
echo ""
echo "To interact with CLI:"
echo "  docker exec -it maintenance-tracker-cli python -m src.main --help"
echo ""
echo "To access database:"
echo "  docker exec -it maintenance-tracker-db psql -U maintenance_user -d maintenance_tracker"
echo ""
echo "To view logs:"
echo "  docker-compose logs [SERVICE]"
