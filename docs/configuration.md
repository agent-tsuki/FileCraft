# FastAPI Configuration Guide

This document provides a comprehensive overview of the FastAPI configuration system implemented in FileCraft.

## Overview

FileCraft uses a layered configuration system that provides extensive customization options for API behavior, security, processing, and documentation without implementing actual authentication functionality.

## Configuration Structure

### Core Configuration Files

1. **`config/settings/base.py`** - Main settings class with all configuration options
2. **`app/core/config.py`** - Application configuration class with methods for different config groups
3. **`app/core/security.py`** - Security configuration schemas (documentation only)
4. **`app/core/api_config.py`** - OpenAPI and documentation configuration
5. **`.env.example`** - Environment variable template

## Configuration Categories

### 1. API Configuration

Controls basic API settings and metadata:

```python
# API Information
PROJECT_NAME = "FileCraft"
PROJECT_DESCRIPTION = "Professional file conversion and processing API"
VERSION = "1.2.0"
API_V1_PREFIX = "/api/v1"
DEBUG = False

# Documentation URLs
DOCS = "/docs"
REDOC_URL = "/redoc"
OPENAPI_URL = "/api/openapi.json"
```

### 2. Server Configuration

Server runtime settings:

```python
HOST = "0.0.0.0"
PORT = 8000
WORKERS = 4
RELOAD = False
LOG_LEVEL = "info"
```

### 3. Security Configuration (Not Implemented)

Authentication and security settings for documentation:

```python
# JWT Settings (Documentation only)
JWT_SECRET_KEY = "jwt-secret-key"
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 15

# API Key Settings (Documentation only)
API_KEY_HEADER = "X-API-Key"
ENABLE_API_KEY_AUTH = False
```

**Important**: Authentication is NOT implemented. These settings are for documentation and future implementation only.

### 4. CORS Configuration

Cross-Origin Resource Sharing settings:

```python
CORS_ORIGINS = ["*"]  # Change to specific domains in production
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
CORS_ALLOW_HEADERS = ["*"]
```

### 5. Rate Limiting Configuration

API rate limiting settings:

```python
RATE_LIMIT_ENABLED = True
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW = 3600  # 1 hour
RATE_LIMIT_PER_IP = 1000
```

### 6. File Processing Configuration

File upload and processing limits:

```python
# Upload Limits
MAX_UPLOAD_SIZE = 500 * 1024 * 1024  # 500MB
MAX_IMAGE_SIZE_MB = 50
MAX_AUDIO_SIZE_MB = 200
MAX_VIDEO_SIZE_MB = 500

# Processing Settings
ENABLE_ASYNC_PROCESSING = True
MAX_CONCURRENT_TASKS = 10
TASK_TIMEOUT = 300  # 5 minutes
```

### 7. Database Configuration

Database connection settings:

```python
DB_HOSTNAME = "localhost"
DB_PORT = 5432
DB_DATABASE = "filecraft"
DB_USER = "postgres"
DB_PASSWORD = "password"
DATABASE_URL = "postgresql://user:pass@host:port/db"
```

### 8. Redis and Celery Configuration

Background task processing:

```python
# Redis
REDIS_URL = "redis://localhost:6379/0"
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

# Celery
CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
CELERY_TASK_TIME_LIMIT = 1800  # 30 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 1500  # 25 minutes
```

### 9. Feature Flags

Enable/disable specific features:

```python
ENABLE_SWAGGER_UI = True
ENABLE_REDOC = True
ENABLE_OPENAPI = True
ENABLE_ADMIN_PANEL = False  # Not implemented
ENABLE_WEBHOOKS = False  # Not implemented
ENABLE_BATCH_PROCESSING = True
ENABLE_REAL_TIME_PROCESSING = True
```

### 10. External Services Configuration

Third-party service integration:

```python
# AWS S3 (Optional)
AWS_ACCESS_KEY_ID = "your-access-key"
AWS_SECRET_ACCESS_KEY = "your-secret-key"
AWS_REGION = "us-east-1"
S3_BUCKET_NAME = "your-bucket"
ENABLE_S3_STORAGE = False

# Email (Optional)
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "your-email@gmail.com"
SMTP_PASSWORD = "your-password"
ENABLE_EMAIL_NOTIFICATIONS = False
```

## Configuration Usage

### Accessing Configuration

```python
from app.core.config import get_app_config

config = get_app_config()

# Access specific config groups
cors_config = config.get_cors_config()
security_config = config.get_security_config()
rate_limit_config = config.get_rate_limit_config()
celery_config = config.get_celery_config()
```

### Environment Detection

```python
config = get_app_config()

if config.is_production():
    # Production-specific logic
    pass

if config.is_development():
    # Development-specific logic
    pass
```

## OpenAPI Configuration

### Enhanced Documentation

The API includes comprehensive OpenAPI/Swagger documentation with:

- Custom security schemes (documentation only)
- Detailed endpoint tags and descriptions
- Example responses for common scenarios
- External documentation links
- Enhanced Swagger UI configuration
- ReDoc alternative documentation

### Security Schemes (Documentation Only)

```python
# JWT Bearer (not implemented)
"JWTBearer": {
    "type": "http",
    "scheme": "bearer",
    "bearerFormat": "JWT"
}

# API Key (not implemented)
"ApiKeyAuth": {
    "type": "apiKey",
    "in": "header", 
    "name": "X-API-Key"
}
```

## Environment Configuration

### Development Environment

```bash
# .env for development
ENVIRONMENT=development
DEBUG=true
RELOAD=true
LOG_LEVEL=debug
CORS_ORIGINS=["*"]
```

### Production Environment

```bash
# .env for production
ENVIRONMENT=production
DEBUG=false
RELOAD=false
LOG_LEVEL=info
CORS_ORIGINS=["https://yourdomain.com"]
ALLOWED_HOSTS=["yourdomain.com", "api.yourdomain.com"]
```

## API Endpoints for Configuration

### Get API Information

```
GET /api/info
```

Returns comprehensive API metadata, features, and capabilities.

### Get Public Configuration

```
GET /api/config
```

Returns public configuration settings (non-sensitive information only).

### Health Check with Configuration

```
GET /health/detailed
```

Returns health status with configuration summary.

## Security Headers

The application automatically adds security headers to all responses:

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
X-API-Version: v1.2.0
```

## Rate Limiting Headers

When rate limiting is enabled, responses include:

```
X-RateLimit-Limit: 100
X-RateLimit-Window: 3600
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1696248000
```

## Configuration Best Practices

### 1. Environment Variables

Always use environment variables for sensitive configuration:

```bash
# Good
SECRET_KEY=your-secret-key-from-env

# Bad (in code)
SECRET_KEY = "hardcoded-secret"
```

### 2. Production Settings

For production deployment:

1. Set `DEBUG=false`
2. Use specific CORS origins
3. Configure proper `ALLOWED_HOSTS`
4. Use strong secret keys
5. Enable HTTPS settings
6. Configure proper logging

### 3. Security Considerations

- Change default secret keys
- Use environment-specific database credentials
- Enable rate limiting
- Configure CORS properly
- Use HTTPS in production

## Configuration Validation

The configuration system uses Pydantic for validation:

- Type checking for all settings
- Default values for optional settings
- Automatic environment variable parsing
- Configuration validation on startup

## Extending Configuration

To add new configuration options:

1. Add the setting to `config/settings/base.py`
2. Update `app/core/config.py` to expose the setting
3. Add documentation and examples
4. Update `.env.example` with the new variable

Example:

```python
# In base.py
NEW_FEATURE_ENABLED: bool = False

# In config.py
self.new_feature_enabled = settings.NEW_FEATURE_ENABLED

# In .env.example
NEW_FEATURE_ENABLED=false
```

## Notes

- **Authentication is NOT implemented** - all authentication-related configuration is for documentation and future implementation only
- Rate limiting configuration is included but rate limiting implementation may need to be added
- All secret keys and passwords should be changed in production
- Configuration supports both development and production environments
- External service integrations are optional and disabled by default