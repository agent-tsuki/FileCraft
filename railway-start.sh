#!/bin/bash

# Railway Production Start Script for FileCraft

echo "🚀 Starting FileCraft on Railway..."
echo "Environment: ${ENVIRONMENT:-development}"
echo "Port: ${PORT:-8000}"

# Check if we're in production
if [ "$ENVIRONMENT" = "production" ]; then
    echo "📊 Production environment detected"
    
    # Ensure PORT is set (Railway should provide this)
    if [ -z "$PORT" ]; then
        echo "⚠️  PORT not set, using default 8000"
        export PORT=8000
    fi
    
    # Run any database migrations if needed (uncomment if using Alembic)
    # echo "🗄️  Running database migrations..."
    # alembic upgrade head
    
    # Start the application with Railway's port
    echo "🌟 Starting FileCraft API server on port $PORT..."
    exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1 --access-log
else
    echo "🔧 Development environment detected"
    PORT=${PORT:-8000}
    exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --reload
fi