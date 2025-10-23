# 🐳 FileCraft Docker Deployment Guide

This guide shows how to run FileCraft using Docker, both locally and on Render, using a **single container** that runs both FastAPI and Celery.

## 🎯 Key Features

✅ **Single Container**: FastAPI + Celery in one container using Supervisor  
✅ **Local Development**: Docker Compose with PostgreSQL + Redis  
✅ **Production Ready**: Same container works on Render  
✅ **No Complexity**: One Dockerfile, one deployment method  

## 🚀 Quick Start (Local)

### Prerequisites
- Docker and Docker Compose installed

### Start Everything
```bash
# Clone the repository
git clone <repository-url>
cd FileCraft

# Start all services (app + database + redis)
docker-compose up -d

# Check logs
docker-compose logs -f app
```

🎉 **Access your API:**
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health

### Stop Everything
```bash
docker-compose down
```

## 🌐 Deploy to Render

### Step 1: Create Render Services

1. **Web Service**:
   - Connect your GitHub repository
   - **Build Command**: `docker build -t app .`
   - **Start Command**: *(leave blank - handled by Dockerfile)*

2. **PostgreSQL Database**:
   - Create a PostgreSQL service
   - Copy the `DATABASE_URL` 

3. **Redis**:
   - Create a Redis service
   - Copy the `REDIS_URL`

### Step 2: Environment Variables

Add these to your Render Web Service:

```bash
# Security (REQUIRED - change these!)
SECRET_KEY=your-super-secret-key-change-this
JWT_SECRET_KEY=your-jwt-secret-key-change-this

# Application
ENVIRONMENT=production
DEBUG=false

# CORS (update with your actual URL)
CORS_ORIGINS=["https://your-app-name.onrender.com"]
ALLOWED_HOSTS=["your-app-name.onrender.com"]

# File limits
MAX_UPLOAD_SIZE=104857600
MAX_IMAGE_SIZE_MB=20
MAX_AUDIO_SIZE_MB=50
MAX_VIDEO_SIZE_MB=100

# Processing
ENABLE_ASYNC_PROCESSING=true
MAX_CONCURRENT_TASKS=2

# API Docs (set to false for production security)
ENABLE_DOCS=false
ENABLE_SWAGGER_UI=false
ENABLE_REDOC=false
```

### Step 3: Deploy

1. **Push to GitHub**: Render will auto-deploy
2. **Check Logs**: Monitor the deployment
3. **Test**: Visit `https://your-app-name.onrender.com/health`

## 🔧 How It Works

### Single Container Architecture

```
┌─────────────────────────────────────┐
│            Docker Container         │
│  ┌─────────────┐  ┌─────────────┐  │
│  │   FastAPI   │  │   Celery    │  │
│  │   (API)     │  │  (Worker)   │  │
│  └─────────────┘  └─────────────┘  │
│           │              │         │
│           └──────────────┘         │
│              Supervisor             │
└─────────────────────────────────────┘
```

### Local Development
```
Docker Compose:
├── app (FastAPI + Celery)
├── db (PostgreSQL)
└── redis (Redis)
```

### Render Deployment
```
Render:
├── Web Service (FastAPI + Celery)
├── PostgreSQL Service
└── Redis Service
```

## 📁 File Structure

```
FileCraft/
├── Dockerfile              # Single container definition
├── docker-compose.yml      # Local development
├── supervisord.conf        # Process manager config
├── start_docker.sh        # Alternative startup script
├── .env.docker            # Local Docker environment
├── .env.render            # Render environment template
└── requirements.txt        # All dependencies
```

## 🛠 Development Commands

```bash
# Build the image
docker build -t filecraft .

# Run locally with compose
docker-compose up -d

# View logs
docker-compose logs -f app

# Execute commands in container
docker-compose exec app bash

# Stop services
docker-compose down

# Clean up
docker-compose down -v
docker system prune
```

## 🔍 Monitoring

### Health Checks
- **Local**: http://localhost:8000/health
- **Render**: https://your-app.onrender.com/health

### Logs
- **Local**: `docker-compose logs -f app`
- **Render**: Check Render dashboard logs

### Supervisor Status
```bash
# Inside container
supervisorctl status

# Restart services
supervisorctl restart fastapi
supervisorctl restart celery
```

## 🐛 Troubleshooting

### Local Issues

**Services won't start:**
```bash
docker-compose down -v
docker-compose up -d --build
```

**Database connection issues:**
```bash
# Check if database is running
docker-compose ps
docker-compose logs db
```

**Redis connection issues:**
```bash
# Check Redis
docker-compose logs redis
```

### Render Issues

**Build failures:**
- Check that all files are committed to Git
- Verify Dockerfile syntax
- Check build logs in Render dashboard

**Runtime errors:**
- Verify all environment variables are set
- Check that DATABASE_URL and REDIS_URL are configured
- Monitor application logs

**Celery not working:**
- Ensure Redis service is connected
- Check CELERY_BROKER_URL is set correctly
- Verify async processing is enabled

## 📝 Notes

- **Same Container**: FastAPI and Celery run in the same container using Supervisor
- **Resource Efficient**: Perfect for small to medium workloads
- **Render Friendly**: Optimized for Render's resource limits
- **Local Development**: Full feature development with Docker Compose
- **Production Ready**: Same container works in production

## 🎉 Success!

You now have a unified Docker setup that:
- ✅ Runs both FastAPI and Celery in one container
- ✅ Works locally with Docker Compose
- ✅ Deploys to Render without changes
- ✅ Includes database and Redis
- ✅ Supports async task processing

**Local**: http://localhost:8000/docs  
**Render**: https://your-app.onrender.com/health