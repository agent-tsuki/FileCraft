#!/bin/bash

# FileCraft Docker Startup Script
# Runs both FastAPI and Celery in a single container

set -e

echo "🚀 Starting FileCraft (Docker)..."

# Set default port if not provided
export PORT=${PORT:-8000}

echo "📍 Port: $PORT"
echo "🌍 Environment: ${ENVIRONMENT:-development}"

# Create necessary directories
mkdir -p uploads logs

# Wait for Redis and Database to be ready (if they exist)
if [ -n "$REDIS_URL" ]; then
    echo "⏳ Waiting for Redis..."
    while ! nc -z ${REDIS_HOST:-redis} ${REDIS_PORT:-6379}; do
        sleep 1
    done
    echo "✅ Redis is ready"
fi

if [ -n "$DATABASE_URL" ]; then
    echo "⏳ Waiting for Database..."
    while ! nc -z ${DB_HOSTNAME:-db} ${DB_PORT:-5432}; do
        sleep 1
    done
    echo "✅ Database is ready"
fi

# Start Celery worker in background
echo "🔄 Starting Celery worker..."
celery -A app.celery_app worker --loglevel=info --concurrency=2 &
CELERY_PID=$!

# Start FastAPI server
echo "🌐 Starting FastAPI server on port $PORT..."
exec gunicorn app.main:app \
    -w 2 \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:$PORT \
    --access-logfile - \
    --error-logfile - \
    --log-level info