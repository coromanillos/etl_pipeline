#!/bin/bash

set -e  # Exit immediately on error

echo "📦 Updating requirements.lock with latest compatible dependencies..."
pip-compile requirements.in --output-file=requirements.txt

echo "🐳 Building Docker services (including test_runner)..."
docker compose -f docker-compose.yml -f docker-compose.override.yml -f docker-compose.test.yml build test_runner

echo "✅ Running integration tests..."
docker compose -f docker-compose.yml -f docker-compose.override.yml -f docker-compose.test.yml up --abort-on-container-exit --exit-code-from test_runner

echo "🧹 Cleaning up containers and volumes..."
docker compose -f docker-compose.yml -f docker-compose.override.yml -f docker-compose.test.yml down -v
