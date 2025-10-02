#!/bin/bash
"""
FileCraft Image Processing API - Development Startup Script
"""

echo "🚀 Starting FileCraft Image Processing API..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if Redis is available
echo "📡 Checking Redis availability..."
if ! nc -z localhost 6379 > /dev/null 2>&1; then
    echo "⚠️  Redis not available on localhost:6379, will use Docker Redis"
fi

# Start the services
echo "🏗️  Building and starting services..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service status
echo "📊 Service Status:"
docker-compose ps

# Show useful URLs
echo ""
echo "🌐 Service URLs:"
echo "   📱 FastAPI Application: http://localhost:8080"
echo "   📚 API Documentation: http://localhost:8080/docs"
echo "   🌸 Flower (Celery Monitor): http://localhost:5555"
echo "   🔍 Database (PostgreSQL): localhost:5432"
echo "   💾 Redis: localhost:6379"
echo ""
echo "🎯 Available Image Formats:"
echo "   Input: JPEG, PNG, WebP, BMP, GIF, TIFF, HEIC, HEIF, AVIF, RAW, etc."
echo "   Output: JPEG, PNG, WebP, BMP, GIF, TIFF, HEIC, HEIF, AVIF, ICO, JP2, PDF"
echo ""
echo "🔧 Features:"
echo "   ✨ 20+ image format support"
echo "   🎚️  Quality presets and custom settings"
echo "   📏 Smart resizing with aspect ratio preservation"
echo "   🚀 Background processing with Celery"
echo "   📊 Real-time progress tracking"
echo "   🛠️  Advanced optimization algorithms"
echo "   📦 Batch processing"
echo ""
echo "📖 Example API calls:"
echo "   curl -X POST http://localhost:8080/images/formats"
echo "   curl -X POST -F 'image=@photo.jpg' -F 'target_format=webp' http://localhost:8080/images/convert"
echo ""
echo "✅ FileCraft is ready! Happy image processing! 🎨"