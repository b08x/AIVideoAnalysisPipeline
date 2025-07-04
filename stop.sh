#!/bin/bash
set -e

echo "Stopping production environment..."
make down-prod
echo "Production environment stopped."
