# Multi-stage Dockerfile for FileCraft
# Runs both FastAPI and Celery in a single container

FROM python:3.12-slim AS base

# Set working directory
WORKDIR /app

# Prevent interactive prompts during package install
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    gcc \
    netcat-traditional \
    # Image processing dependencies
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libwebp-dev \
    libopenjp2-7-dev \
    libheif-dev \
    libavif-dev \
    # Audio/Video processing dependencies
    ffmpeg \
    libavcodec-dev \
    libavformat-dev \
    libavutil-dev \
    libswscale-dev \
    libswresample-dev \
    # Essential libraries
    pkg-config \
    libfreetype6-dev \
    liblcms2-dev \
    # Supervisor for process management
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads logs /var/log/supervisor

# Create supervisor configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose port (will be set by Render automatically)
EXPOSE $PORT

# Set environment variables for production
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Use supervisor to run both FastAPI and Celery
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]