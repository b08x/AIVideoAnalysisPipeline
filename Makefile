.PHONY: build build-dev build-prod build-optimized up-dev down-dev up-prod down-prod logs-dev logs-prod clean analyze-image

# Enable BuildKit for optimized builds
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Build all Docker images defined in both compose files
build:
	@echo "Building all services with BuildKit optimizations..."
	DOCKER_BUILDKIT=1 docker-compose -f docker-compose.dev.yml build
	DOCKER_BUILDKIT=1 docker-compose -f docker-compose.prod.yml build

# Build only development environment
build-dev:
	@echo "Building development services..."
	DOCKER_BUILDKIT=1 docker-compose -f docker-compose.dev.yml build

# Build only production environment with cache optimization
build-prod:
	@echo "Building production services with cache optimization..."
	DOCKER_BUILDKIT=1 docker-compose -f docker-compose.prod.yml build --build-arg BUILDKIT_INLINE_CACHE=1

# Build production with no cache (clean build)
build-optimized:
	@echo "Building production services without cache (clean build)..."
	DOCKER_BUILDKIT=1 docker-compose -f docker-compose.prod.yml build --no-cache --build-arg BUILDKIT_INLINE_CACHE=1

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

# Analyze image size and layers
analyze-image:
	@echo "Analyzing backend image size and layers..."
	@if docker images video-analysis-backend:latest >/dev/null 2>&1; then \
		echo "=== IMAGE INFORMATION ==="; \
		docker images video-analysis-backend:latest --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"; \
		echo ""; \
		echo "=== LAYER ANALYSIS ==="; \
		docker history video-analysis-backend:latest --format "table {{.CreatedBy}}\t{{.Size}}" --no-trunc | head -15; \
	else \
		echo "Backend image not found. Run 'make build-prod' first."; \
	fi

# Clean up Docker environment
clean:
	@echo "Cleaning up Docker environment..."
	docker-compose -f docker-compose.dev.yml down -v --remove-orphans
	docker-compose -f docker-compose.prod.yml down -v --remove-orphans
	docker system prune -f
	@echo "Cleanup complete."

# Clean up everything including images
clean-all:
	@echo "Cleaning up Docker environment and images..."
	docker-compose -f docker-compose.dev.yml down -v --remove-orphans
	docker-compose -f docker-compose.prod.yml down -v --remove-orphans
	docker system prune -af
	@echo "Complete cleanup finished."

help:
	@echo "Available commands:"
	@echo "  make build           - Build all Docker images with BuildKit"
	@echo "  make build-dev       - Build development environment only"
	@echo "  make build-prod      - Build production environment with cache"
	@echo "  make build-optimized - Build production environment without cache"
	@echo "  make up-dev          - Start development environment"
	@echo "  make down-dev        - Stop development environment"
	@echo "  make logs-dev        - View development logs"
	@echo "  make up-prod         - Start production environment"
	@echo "  make down-prod       - Stop production environment"
	@echo "  make logs-prod       - View production logs"
	@echo "  make analyze-image   - Analyze backend image size and layers"
	@echo "  make clean           - Stop and remove containers, networks, volumes"
	@echo "  make clean-all       - Complete cleanup including images"
