#!/bin/bash
set -e

echo "Building and starting production environment with optimizations..."
echo "Using BuildKit for faster, more efficient builds..."

# Enable BuildKit
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Build with production optimizations
make build-prod

# Start production environment
make up-prod

echo ""
echo "✅ Production environment is running with multistage optimizations!"
echo ""
echo "Available commands:"
echo "  make logs-prod      - View application logs"
echo "  make down-prod      - Stop the environment"
echo "  make analyze-image  - Analyze image size and layers"
echo "  make clean          - Clean up containers and volumes"
echo ""
echo "🔍 To analyze the optimized image: make analyze-image"
