#!/bin/bash

# FileCraft Local Development Startup Script

echo "🚀 Starting FileCraft locally..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📋 Installing dependencies..."
pip install -r requirements.txt

# Copy environment file
if [ ! -f ".env" ]; then
    echo "⚙️ Setting up environment configuration..."
    cp .env.local .env
fi

# Create uploads directory
mkdir -p uploads

# Start the application
echo "🎉 Starting FileCraft API server..."
echo "📍 API will be available at: http://127.0.0.1:8000"
echo "📚 API docs will be available at: http://127.0.0.1:8000/docs"
echo "🔍 Health check: http://127.0.0.1:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000