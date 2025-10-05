#!/bin/bash

# Railway Debug Script
echo "🔍 Railway Environment Debug"
echo "=========================="
echo "PORT: ${PORT:-NOT_SET}"
echo "ENVIRONMENT: ${ENVIRONMENT:-NOT_SET}"
echo "DATABASE_URL: ${DATABASE_URL:-NOT_SET}"
echo "REDIS_URL: ${REDIS_URL:-NOT_SET}"
echo ""
echo "🌐 Network Test:"
echo "==============="
echo "Testing port binding on 0.0.0.0:${PORT:-8000}..."

# Simple Python server test
python3 -c "
import socket
import sys

port = int('${PORT:-8000}')
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', port))
    s.close()
    print(f'✅ Port {port} is available')
except Exception as e:
    print(f'❌ Port {port} error: {e}')
    sys.exit(1)
"

echo ""
echo "🚀 Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --log-level debug