# Makefile for IGDB Game Recommendation System
# Docker and development commands

.PHONY: help build up down logs clean test lint

# Default target
help:
	@echo "IGDB Game Recommendation System - Docker Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  build     - Build all Docker images"
	@echo "  up        - Start all services"
	@echo "  down      - Stop all services"
	@echo "  logs      - Show logs for all services"
	@echo "  clean     - Remove all containers and images"
	@echo "  test      - Run tests in containers"
	@echo "  lint      - Run linting in containers"
	@echo "  dev       - Start development environment"
	@echo "  prod      - Start production environment"

# Build all Docker images
build:
	@echo "Building all Docker images..."
	docker-compose build

# Start all services
up:
	@echo "Starting all services..."
	docker-compose up -d

# Stop all services
down:
	@echo "Stopping all services..."
	docker-compose down

# Show logs
logs:
	@echo "Showing logs for all services..."
	docker-compose logs -f

# Clean up
clean:
	@echo "Cleaning up containers and images..."
	docker-compose down --rmi all --volumes --remove-orphans

# Run tests
test:
	@echo "Running tests..."
	docker-compose run --rm data-ingestion python -m pytest tests/
	docker-compose run --rm data-processing python -m pytest tests/
	docker-compose run --rm ml-training python -m pytest tests/

# Run linting
lint:
	@echo "Running linting..."
	docker-compose run --rm data-ingestion python -m flake8 data_pipeline/
	docker-compose run --rm data-processing python -m flake8 data_pipeline/
	docker-compose run --rm ml-training python -m flake8 data_pipeline/

# Development environment
dev:
	@echo "Starting development environment..."
	docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d

# Production environment
prod:
	@echo "Starting production environment..."
	docker-compose up -d

# Individual service commands
ingestion:
	@echo "Running data ingestion..."
	docker-compose run --rm data-ingestion

processing:
	@echo "Running data processing..."
	docker-compose run --rm data-processing

training:
	@echo "Running ML training..."
	docker-compose run --rm ml-training

# Database commands
db-shell:
	@echo "Opening database shell..."
	docker-compose exec data-ingestion sqlite3 /app/data/games.db

# Status check
status:
	@echo "Service status:"
	docker-compose ps
