# 🧠 FileCraft – Professional File & Image Processing API

**FileCraft** is a modern, enterprise-grade FastAPI application designed for high-performance file processing with industry-standard architecture, dependency injection, and comprehensive error handling.

## 🏗️ Architecture Overview

This application follows **Clean Architecture** principles with:
- **Service Layer**: Business logic isolation with dependency injection
- **Middleware**: Global exception handling and request logging
- **Repository Pattern**: Clean data access abstractions
- **Factory Pattern**: Service instantiation and lifecycle management
- **Structured Logging**: Comprehensive monitoring and debugging

---

## 🚀 Key Features

### File Processing
- 📄 **Base64 Conversion**: Stream-based file to Base64 encoding with optional compression
- 🖼️ **Image Format Conversion**: Professional image processing with quality control
- 📦 **Smart Compression**: Intelligent file and image compression with format-specific optimization
- 🔒 **Security**: Input validation, file size limits, and sanitization

### Technical Excellence
- ⚡ **High Performance**: Async processing with memory-efficient streaming
- 🛡️ **Error Handling**: Comprehensive exception hierarchy with structured responses
- 📊 **Monitoring**: Request/response logging with performance metrics
- 🔧 **Dependency Injection**: Modular, testable service architecture
- 📝 **API Documentation**: Auto-generated OpenAPI/Swagger documentation

---

## 📂 Restructured Architecture

```
FileCraft/
├── app/
│   ├── core/                    # Core application configuration
│   │   ├── config.py           # Application settings and DI
│   │   └── logging.py          # Logging configuration
│   │
│   ├── services/               # Business logic layer
│   │   ├── base.py            # Base service with common functionality
│   │   ├── file_validation.py # File validation service
│   │   ├── base64.py          # Base64 conversion service
│   │   ├── image.py           # Image processing service
│   │   ├── compression.py     # File compression service
│   │   └── factory.py         # Service factory for DI
│   │
│   ├── middleware/            # Application middleware
│   │   ├── __init__.py       # Exception handlers setup
│   │   └── logging.py        # Request/response logging
│   │
│   ├── exceptions/           # Custom exception classes
│   │   └── __init__.py      # Exception hierarchy
│   │
│   ├── schemas/             # Pydantic models
│   │   ├── requests.py     # Request models
│   │   └── responses.py    # Response models
│   │
│   ├── router/             # API endpoints
│   │   └── converters/    # Converter endpoints
│   │
│   ├── helpers/           # Legacy utilities (backward compatibility)
│   ├── dependencies.py   # Global dependencies
│   └── main.py          # Application factory and setup
│
├── config/              # Configuration management
├── tests/              # Test suite
├── requirements.txt    # Production dependencies
├── requirements-dev.txt # Development dependencies
└── docker-compose.yml  # Container orchestration
```

---

## 🛠️ Enhanced Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Framework** | FastAPI | High-performance async web framework |
| **Architecture** | Clean Architecture | Separation of concerns and maintainability |
| **DI Container** | Custom Factory | Service lifecycle management |
| **Validation** | Pydantic | Request/response validation |
| **Error Handling** | Custom Middleware | Structured error responses |
| **Logging** | Structured Logging | Monitoring and debugging |
| **Image Processing** | Pillow | Professional image manipulation |
| **Compression** | zlib | Binary file compression |
| **Testing** | pytest | Comprehensive test suite |
| **Documentation** | OpenAPI/Swagger | Auto-generated API docs |

---

## ⚙️ Getting Started

### 1. 🧪 Development Setup

```bash
# Clone repository
git clone https://github.com/agent-tsuki/FileCraft.git
cd FileCraft

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. ▶️ Run Application

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 3. 🐳 Docker Deployment

```bash
# Using Docker Compose (recommended)
docker-compose up -d

# Direct Docker build
docker build -t filecraft .
docker run -p 8000:8000 filecraft
```

### 4. 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_main.py -v
```

---

## 📚 API Endpoints

### Health Check
- `GET /health` - Application health and uptime
- `GET /system-check` - Legacy compatibility endpoint

### File Conversion
- `POST /base64/file` - Convert file to Base64 with optional compression
- `POST /images/convert` - Convert image formats with quality control
- `POST /compression/smart-compress` - Smart file and image compression

### Documentation
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /api/openapi.json` - OpenAPI specification

---

## 🔧 Configuration

The application uses environment-based configuration:

```bash
# .env file
PROJECT_NAME=FileCraft
DEBUG=true
DOCS=/docs

# Database (if using)
DB_PORT=5432
DB_HOSTNAME=localhost
DB_DATABASE=filecraft
DB_USER=user
DB_PASSWORD=password
```

---

## 🧪 Testing Strategy

- **Unit Tests**: Service layer testing with mocked dependencies
- **Integration Tests**: End-to-end API testing
- **Performance Tests**: Load testing for file processing
- **Security Tests**: Input validation and error handling

---

## 📊 Monitoring & Logging

- **Structured Logging**: JSON-formatted logs with correlation IDs
- **Performance Metrics**: Request processing time tracking  
- **Error Tracking**: Comprehensive exception logging with stack traces
- **Health Checks**: Application uptime and dependency status

---

## 🔒 Security Features

- **Input Validation**: File type and size restrictions
- **Error Sanitization**: No sensitive information in error responses
- **Memory Management**: Stream-based processing to prevent memory exhaustion
- **CORS Configuration**: Configurable cross-origin request handling

---

## 🚀 Production Deployment

### Environment Variables
Configure these for production:
```bash
DEBUG=false
DOCS=null  # Disable docs in production
# Add proper CORS origins
# Configure database connections
# Set up logging levels
```

### Performance Optimization
- Use multiple worker processes
- Configure proper logging levels
- Set up reverse proxy (nginx)
- Enable gzip compression
- Configure proper CORS policies

---

## 👨‍💻 Development

### Code Quality
- **Linting**: ruff for code formatting and style
- **Type Checking**: mypy for static type analysis
- **Testing**: pytest with coverage reporting
- **Documentation**: Comprehensive docstrings and OpenAPI specs

### Contributing
1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Shivam Pandey**
- Built with enterprise-grade architecture and performance optimization
- Designed for scalability, maintainability, and production readiness
- Optimized for high throughput and low latency file processing