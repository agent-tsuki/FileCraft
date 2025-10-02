# Deployment Guide

## Docker Deployment (Recommended)

### Using Docker Compose

1. **Clone and setup:**
```bash
git clone <repository-url>
cd FileCraft
```

2. **Start services:**
```bash
docker-compose up --build -d
```

This starts:
- FileCraft API server (port 8000)
- Redis server (for caching and task queues)
- Celery workers (for background processing)

### Manual Docker Build

```bash
# Build image
docker build -t filecraft:latest .

# Run with Redis
docker run -d --name redis redis:alpine
docker run -d --name filecraft \
  --link redis:redis \
  -p 8000:8000 \
  -e REDIS_HOST=redis \
  filecraft:latest
```

## Local Development

### Prerequisites
- Python 3.12+
- FFmpeg
- Redis

### Setup
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install FFmpeg (Ubuntu/Debian)
sudo apt update && sudo apt install ffmpeg

# Install Redis
sudo apt install redis-server
```

### Run Services
```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start Celery worker
celery -A app.celery_app worker --loglevel=info

# Terminal 3: Start API server
uvicorn app.main:filecraft --reload --host 0.0.0.0 --port 8000
```

## Production Deployment

### Environment Variables
```bash
# Production settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Redis configuration
REDIS_HOST=your-redis-host
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password

# Celery configuration
CELERY_BROKER_URL=redis://user:pass@host:port/db
CELERY_RESULT_BACKEND=redis://user:pass@host:port/db

# File processing limits
MAX_FILE_SIZE=100MB
MAX_BATCH_SIZE=10
TEMP_DIR=/tmp/filecraft

# Security
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=your-domain.com,api.your-domain.com
```

### Docker Compose Production
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - REDIS_HOST=redis
    depends_on:
      - redis
    restart: unless-stopped

  redis:
    image: redis:alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data

  worker:
    build: .
    command: celery -A app.celery_app worker --loglevel=info
    environment:
      - REDIS_HOST=redis
    depends_on:
      - redis
    restart: unless-stopped

volumes:
  redis_data:
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: filecraft-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: filecraft-api
  template:
    metadata:
      labels:
        app: filecraft-api
    spec:
      containers:
      - name: api
        image: filecraft:latest
        ports:
        - containerPort: 8000
        env:
        - name: REDIS_HOST
          value: "redis-service"
---
apiVersion: v1
kind: Service
metadata:
  name: filecraft-service
spec:
  selector:
    app: filecraft-api
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

## Performance Tuning

### Redis Configuration
```bash
# Redis performance settings
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
```

### Uvicorn Configuration
```bash
# Production server command
uvicorn app.main:filecraft \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --access-log \
  --log-level info
```

### Nginx Proxy Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        client_max_body_size 100M;
    }
}
```

## Monitoring & Logging

### Health Checks
```bash
# Basic health check
curl http://localhost:8000/health

# Detailed status
curl http://localhost:8000/status
```

### Log Configuration
```python
# Configure structured logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'filecraft.log',
            'maxBytes': 10*1024*1024,  # 10MB
            'backupCount': 5,
            'formatter': 'detailed',
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['file'],
    },
}
```

## Scaling Considerations

### Horizontal Scaling
- Deploy multiple API instances behind a load balancer
- Scale Celery workers based on queue length
- Use Redis Cluster for high availability

### Vertical Scaling
- Increase worker processes per instance
- Allocate more memory for large file processing
- Use SSD storage for temporary files

### Performance Monitoring
- Monitor Redis memory usage and queue lengths
- Track API response times and error rates
- Monitor disk space for temporary file processing