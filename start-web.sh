#!/bin/bash
set -e

echo "🚀 Starting FileCraft on Railway..."
echo "Port: ${PORT:-8000}"

# Ensure PORT is set
if [ -z "$PORT" ]; then
    echo "❌ PORT environment variable not set by Railway"
    export PORT=8000
    echo "🔧 Using default port: $PORT"
else
    echo "✅ Using Railway port: $PORT"
fi

# Start the application
echo "🌟 Starting uvicorn server..."
exec python -m uvicorn app.main:app --host 0.0.0.0 --port "$PORT"