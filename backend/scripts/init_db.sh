#!/bin/bash
set -e

echo "🚀 Initializing NeuroPlan AI Database..."

# Wait for DB to be ready
echo "⏳ Waiting for PostgreSQL..."
until pg_isready -h db -U postgres; do
  sleep 1
done

echo "✅ Database is online."

# Run migrations
echo "🔄 Running Alembic migrations..."
alembic upgrade head

echo "✨ Database initialized successfully."
