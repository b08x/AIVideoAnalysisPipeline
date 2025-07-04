.PHONY: build up-dev down-dev up-prod down-prod logs-dev logs-prod clean

# Build all Docker images defined in both compose files
build:
	@echo "Building base image..."
	docker-compose -f docker-compose.dev.yml build base
	@echo "Building remaining services..."
	docker-compose -f docker-compose.dev.yml build
	docker-compose -f docker-compose.prod.yml build

# Development environment
up-dev:
	@echo "Starting development environment..."
	docker-compose -f docker-compose.dev.yml up -d
	@echo "Development environment is up."

down-dev:
	@echo "Stopping development environment..."
	docker-compose -f docker-compose.dev.yml down
	@echo "Development environment is down."

logs-dev:
	@echo "Tailing logs for development environment..."
	docker-compose -f docker-compose.dev.yml logs -f

# Production environment
up-prod:
	@echo "Starting production environment..."
	docker-compose -f docker-compose.prod.yml up -d
	@echo "Production environment is up."

down-prod:
	@echo "Stopping production environment..."
	docker-compose -f docker-compose.prod.yml down
	@echo "Production environment is down."

logs-prod:
	@echo "Tailing logs for production environment..."
	docker-compose -f docker-compose.prod.yml logs -f

# Clean up Docker environment
clean:
	@echo "Cleaning up Docker environment..."
	docker-compose -f docker-compose.dev.yml down -v --remove-orphans
	docker-compose -f docker-compose.prod.yml down -v --remove-orphans
	@echo "Cleanup complete."

help:
	@echo "Available commands:"
	@echo "  make build       - Build all Docker images"
	@echo "  make up-dev      - Start development environment"
	@echo "  make down-dev    - Stop development environment"
	@echo "  make logs-dev    - View development logs"
	@echo "  make up-prod     - Start production environment"
	@echo "  make down-prod   - Stop production environment"
	@echo "  make logs-prod   - View production logs"
	@echo "  make clean       - Stop and remove all containers, networks, and volumes"
