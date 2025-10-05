#!/bin/bash

# Railway Production Start Script for FileCraft

echo "🚀 Starting FileCraft on Railway..."

# Check if we're in production
if [ "$ENVIRONMENT" = "production" ]; then
    echo "📊 Production environment detected"
    
    # Install any additional production dependencies if needed
    echo "📦 Installing production dependencies..."
    
    # Run any database migrations if needed (uncomment if using Alembic)
    # echo "🗄️  Running database migrations..."
    # alembic upgrade head
    
    # Start the application
    echo "🌟 Starting FileCraft API server..."
    exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 4 --access-log
else
    echo "🔧 Development environment detected"
    exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --reload
fi