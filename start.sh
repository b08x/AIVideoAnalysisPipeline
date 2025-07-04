#!/bin/bash
set -e

echo "Building and starting production environment..."
make build
make up-prod
echo "Production environment is running."
echo "Use 'make logs-prod' to view logs."
echo "Use 'make down-prod' to stop the environment."
