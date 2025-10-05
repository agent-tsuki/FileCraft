# FileCraft Railway Deployment Guide

This guide will help you deploy FileCraft to Railway with all necessary services and configurations.

## Prerequisites

1. A Railway account (https://railway.app)
2. Railway CLI installed (optional but recommended)
3. Your FileCraft project code

## Deployment Steps

### 1. Create a New Railway Project

1. Go to https://railway.app and create a new project
2. Connect your GitHub repository or deploy from template

### 2. Add Required Services

Your FileCraft application needs the following services:

#### PostgreSQL Database
1. In your Railway project dashboard, click "New Service"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically create the database and provide environment variables

#### Redis Service
1. Click "New Service" again
2. Select "Database" → "Redis"
3. Railway will automatically provide Redis connection variables

### 3. Configure Environment Variables

In your Railway project settings, add the following environment variables:

#### Critical Security Variables (MUST SET)
```
SECRET_KEY=your-super-secret-production-key-min-32-characters
JWT_SECRET_KEY=your-jwt-secret-production-key-min-32-characters
```

#### Application Configuration
```
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info

# CORS Configuration - Replace with your actual domains
CORS_ORIGINS=["https://your-app.railway.app", "https://your-custom-domain.com"]
ALLOWED_HOSTS=["your-app.railway.app", "your-custom-domain.com"]
```

#### Optional Services (if needed)
```
# AWS S3 for file storage (recommended for production)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
S3_BUCKET_NAME=your-bucket-name
ENABLE_S3_STORAGE=true

# Sentry for error tracking (recommended)
SENTRY_DSN=your-sentry-dsn

# Email notifications
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=noreply@your-domain.com
ENABLE_EMAIL_NOTIFICATIONS=true
```

### 4. Deploy the Application

#### Method 1: GitHub Integration (Recommended)
1. Connect your GitHub repository to Railway
2. Railway will automatically detect the Python application
3. The deployment will use the `Procfile` for the web service
4. Celery workers can be deployed as separate services

#### Method 2: Railway CLI
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Link to your project
railway link

# Deploy
railway up
```

### 5. Configure Multiple Services (Web + Worker)

For production, you'll want separate web and worker services:

#### Web Service (Main Application)
- Use the main repository deployment
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

#### Worker Service (Celery)
1. Create a new service in the same project
2. Use the same repository
3. Start command: `celery -A app.celery_app worker --loglevel=info --concurrency=2`

### 6. Domain Configuration

1. In Railway dashboard, go to your web service
2. Click on "Settings" → "Domains"
3. Add your custom domain or use the provided Railway domain
4. Update your CORS_ORIGINS and ALLOWED_HOSTS accordingly

### 7. Health Check Setup

Railway automatically monitors your application. The health check endpoint is available at:
```
GET https://your-app.railway.app/health
```

### 8. Monitoring and Logging

1. Railway provides automatic logging - view in the deployment logs
2. Set up Sentry for error tracking (recommended)
3. Monitor resource usage in Railway dashboard

## Production Checklist

- [ ] PostgreSQL database added and configured
- [ ] Redis service added and configured  
- [ ] SECRET_KEY and JWT_SECRET_KEY set to strong values
- [ ] CORS_ORIGINS configured with actual domains
- [ ] ALLOWED_HOSTS configured with actual domains
- [ ] Documentation endpoints disabled (ENABLE_DOCS=false)
- [ ] S3 storage configured for file persistence (recommended)
- [ ] Sentry configured for error tracking
- [ ] Email notifications configured (if needed)
- [ ] Custom domain configured
- [ ] SSL/HTTPS enabled (automatic with Railway)

## Environment Variables Reference

### Automatically Provided by Railway
```
PORT                    # Web service port
DATABASE_URL           # PostgreSQL connection string
PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD  # PostgreSQL details
REDIS_URL              # Redis connection string
REDIS_HOST, REDIS_PORT, REDIS_PASSWORD          # Redis details
```

### Must Be Set Manually
```
SECRET_KEY             # Application secret key
JWT_SECRET_KEY         # JWT signing key
ENVIRONMENT=production # Environment setting
CORS_ORIGINS          # Allowed CORS origins
ALLOWED_HOSTS         # Allowed host headers
```

## Common Issues and Solutions

### 1. Build Failures
- Ensure all dependencies are in `requirements.txt`
- Check Python version compatibility
- Review build logs for specific errors

### 2. Database Connection Issues
- Verify PostgreSQL service is running
- Check DATABASE_URL environment variable
- Ensure database migrations are run if needed

### 3. Redis Connection Issues
- Verify Redis service is running
- Check REDIS_URL environment variable
- Ensure SSL is properly configured for Redis

### 4. File Upload Issues
- Consider using S3 storage for file persistence
- Check upload size limits
- Ensure proper file permissions

### 5. CORS Issues
- Verify CORS_ORIGINS includes your frontend domain
- Check ALLOWED_HOSTS configuration
- Ensure protocol (https) matches

## Support

If you encounter issues:
1. Check Railway deployment logs
2. Review environment variable configuration
3. Test endpoints with the health check
4. Monitor Sentry for application errors (if configured)

## Scaling Considerations

For high traffic:
1. Increase web service resources in Railway
2. Add more Celery worker services
3. Consider Redis scaling options
4. Monitor database performance
5. Implement caching strategies