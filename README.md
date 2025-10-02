# 🧠 FileCraft – Professional Media Processing API

**FileCraft** is a modern, enterprise-grade FastAPI application designed for high-performance file and media processing with industry-standard architecture, dependency injection, and comprehensive error handling.

> 📚 **Documentation**: For detailed API reference, deployment guides, and examples, visit the [`docs/`](docs/) folder.

## 🏗️ Architecture Overview

This application follows **Clean Architecture** principles with:
- **Service Layer**: Business logic isolation with dependency injection
- **Middleware**: Global exception handling and request logging
- **Repository Pattern**: Clean data access abstractions
- **Factory Pattern**: Service instantiation and lifecycle management
- **Structured Logging**: Comprehensive monitoring and debugging
- **Stream-based Processing**: No file system dependency for optimal performance

---

## 🚀 Core Features

### 📄 Base64 & File Processing
✅ **Universal Base64 Conversion**: Convert any uploaded file to Base64 with optional compression  
✅ **Smart Compression**: Intelligent file and image compression with format-specific optimization  
✅ **Stream-based Processing**: Memory-efficient handling of large files  
✅ **Security**: Input validation, file size limits, and sanitization  

### 🖼️ Image Processing
✅ **20+ Formats**: JPEG, PNG, WebP, HEIC, AVIF, RAW (CR2, NEF, ARW, DNG), BMP, GIF, TIFF, ICO, and more  
✅ **Quality Control**: Adjustable compression and optimization (1-100 scale)  
✅ **Smart Resizing**: Size presets (thumbnail to 8K) with aspect ratio preservation  
✅ **Batch Processing**: Convert multiple images simultaneously  
✅ **Professional Tools**: Metadata removal, format recommendations, compression analysis  

### 🎵 Audio Processing
✅ **23+ Formats**: WAV, MP3, AAC, OGG, FLAC, AIFF, AU, M4A, WMA, AC3, OPUS, AMR, and more  
✅ **Quality & Encoding**: Bitrate options (32kbps-320kbps+), sample rates (8kHz-192kHz)  
✅ **Audio Effects**: Normalize, compress, EQ, noise reduction, fade effects  
✅ **Advanced Analysis**: Tempo, pitch, spectral features, waveform analysis  
✅ **Professional Processing**: Speed/pitch control, volume adjustment  

### 🎬 Video Processing
✅ **Universal Formats**: MP4, MKV, WebM, AVI, MOV, WMV, FLV, OGV, 3GP, MTS, and more  
✅ **Quality Presets**: Mobile to 8K resolution options  
✅ **Audio Extraction**: Extract audio tracks from videos  
✅ **Thumbnail Generation**: Create previews at any timestamp  
✅ **Modern Codecs**: H.264, H.265, VP9, AV1 support with hardware acceleration  

### 🔐 Encoder/Decoder System
✅ **Multiple Formats**: Base64, JWT, URL, Hex, Hash (MD5, SHA1, SHA256, SHA512)  
✅ **Streaming Support**: Handle large files efficiently  
✅ **JWT Processing**: Create, verify, and decode JSON Web Tokens  
✅ **Security Features**: Secure handling with proper validation  

### ⚡ Performance & Infrastructure
✅ **Background Processing**: Async tasks with Celery + Redis  
✅ **Memory Efficient**: Optimized for large files  
✅ **Docker Ready**: Production deployment support  
✅ **API Documentation**: Interactive Swagger/OpenAPI docs  
✅ **Error Handling**: Comprehensive exception hierarchy with structured responses  
✅ **Monitoring**: Request/response logging with performance metrics  

---

## 🛠️ Tech Stack

| Category | Tool | Purpose |
|----------|------|---------|
| **Core** | 🐍 Python 3.12+ | Core language |
| **Framework** | ⚡ FastAPI | High-performance web framework |
| **Image Processing** | 🖼️ Pillow | Image processing and conversion |
| **Audio Processing** | 🎵 Pydub + LibROSA + Essentia | Audio manipulation and analysis |
| **Video Processing** | 🎬 FFmpeg | Video processing and conversion |
| **Background Tasks** | 🔥 Celery | Async task processing |
| **Caching** | 📦 Redis | Task queue and caching |
| **Compression** | 🧪 Zlib | Binary file compression |
| **Deployment** | 🐳 Docker | Containerization |
| **Server** | 🔥 Uvicorn | ASGI server |

---

## 📂 Project Structure

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
│   │   ├── audio.py           # Audio processing service
│   │   ├── video.py           # Video processing service
│   │   ├── compression.py     # File compression service
│   │   └── factory.py         # Service factory for DI
│   │
│   ├── middleware/            # Application middleware
│   │   └── logging.py         # Request/response logging
│   │
│   ├── router/                # API endpoints
│   │   ├── encoder_decoder.py # Encoding/decoding endpoints
│   │   ├── converters/        # Format conversion endpoints
│   │   │   ├── base64.py      # Base64 conversion
│   │   │   ├── images.py      # Image processing
│   │   │   └── compression.py # File compression
│   │   └── auth/              # Authentication endpoints
│   │
│   ├── schemas/               # Pydantic models
│   │   ├── requests.py        # Request schemas
│   │   └── responses.py       # Response schemas
│   │
│   ├── tasks/                 # Celery background tasks
│   │   ├── audio_tasks.py     # Audio processing tasks
│   │   ├── image_tasks.py     # Image processing tasks
│   │   ├── video_tasks.py     # Video processing tasks
│   │   └── optimization_tasks.py # Optimization tasks
│   │
│   ├── helpers/               # Utility functions
│   │   ├── constants.py       # Application constants
│   │   ├── converter.py       # Conversion utilities
│   │   └── file_validator.py  # File validation utilities
│   │
│   ├── exceptions/            # Custom exceptions
│   ├── models/                # Database models (if needed)
│   ├── dependencies.py        # FastAPI dependencies
│   ├── celery_app.py         # Celery configuration
│   └── main.py               # FastAPI application entry point
│
├── config/                    # Configuration files
│   ├── database.py           # Database configuration
│   └── settings/             # Environment-specific settings
│
├── tests/                     # Test files
├── docker-compose.yml         # Docker composition
├── Dockerfile                # Docker image definition
├── requirements.txt          # Python dependencies
└── pyproject.toml           # Project configuration
```

---

## 📚 API Documentation

FileCraft provides comprehensive processing capabilities through organized API endpoints:

### 📄 Base64 & File Processing (`/base64`, `/compression`)
- **Universal Conversion**: Convert any file to Base64 with optional compression
- **Smart Compression**: Intelligent file optimization
- **Stream Processing**: Memory-efficient handling of large files

### 🔐 Encoder/Decoder System (`/codec`)
- **Base64**: Encode/decode text and files to/from Base64
- **JWT**: Create, verify, and decode JSON Web Tokens
- **URL Encoding**: URL encode/decode operations  
- **Hash Functions**: MD5, SHA1, SHA256, SHA512 hashing
- **Hex Encoding**: Hexadecimal encoding/decoding
- **Format Validation**: Validate data formats and integrity

### 🖼️ Image Processing (`/images`)
- **Format Conversion**: Convert between 20+ image formats
- **Quality Control**: Adjustable compression and optimization
- **Smart Resizing**: Size presets from thumbnail to 8K resolution
- **Batch Processing**: Convert multiple images simultaneously
- **Analysis**: Get detailed image information and metadata
- **Professional Tools**: Format recommendations, compression analysis

### 🎵 Audio Processing (`/audio`)
- **Format Conversion**: Support for 23+ audio formats
- **Quality & Encoding Control**: Bitrate, sample rate, channel configuration
- **Audio Effects**: Normalize, compress, EQ, noise reduction, fade effects
- **Advanced Processing**: Speed/pitch control, volume adjustment
- **Analysis**: Extract tempo, pitch, spectral features, waveform analysis
- **Professional Tools**: Multi-channel support, metadata extraction

### 🎬 Video Processing (`/video`)
- **Format Conversion**: Universal video format support (20+ input, 10+ output)
- **Audio Extraction**: Extract audio tracks from videos
- **Thumbnail Generation**: Create previews at any timestamp
- **Quality Presets**: Mobile to 8K resolution options
- **Modern Codecs**: H.264, H.265, VP9, AV1 with hardware acceleration
- **Batch Processing**: Process multiple videos simultaneously

### 🌐 Interactive API Documentation
Once running, access the interactive documentation:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/api/openapi.json`

📖 **Detailed API Reference**: [`docs/api-endpoints.md`](docs/api-endpoints.md)

---

## ⚙️ Getting Started

### 🧪 1. Prerequisites

**System Requirements:**
- Python 3.12+
- FFmpeg (for audio/video processing)
- Redis (for background processing)

**FFmpeg Installation** (Required for audio/video processing):

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

**Redis Installation** (Required for background processing):

```bash
# Ubuntu/Debian
sudo apt install redis-server

# macOS
brew install redis

# Windows
# Download from https://redis.io/download
```

### 🧪 2. Local Setup

```bash
git clone https://github.com/yourusername/filecraft.git
cd filecraft

python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**Verify Installation**:
```bash
ffmpeg -version  # Should show FFmpeg version
redis-cli ping   # Should return PONG
python -c "import ffmpeg; print('FFmpeg Python bindings OK')"
```

### ▶️ 3. Run Application

**Development Mode:**
```bash
uvicorn app.main:filecraft --reload --host 0.0.0.0 --port 8000
```

**With Background Processing:**
```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start Celery worker
celery -A app.celery_app worker --loglevel=info

# Terminal 3: Start FastAPI app
uvicorn app.main:filecraft --reload --host 0.0.0.0 --port 8000
```

### 🐳 4. Docker Deployment

**Simple Docker Run:**
```bash
docker build -t filecraft .
docker run -p 8000:8000 filecraft
```

**Docker Compose (Recommended):**
```bash
docker-compose up --build -d
```

This starts:
- FileCraft API server
- Redis for caching and task queues
- Celery workers for background processing

🚀 **Production Deployment**: See [`docs/deployment.md`](docs/deployment.md) for detailed deployment instructions.

---

## 🚀 Quick API Examples

### Base64 Conversion
```bash
# Convert file to Base64
curl -X POST "http://localhost:8000/base64/encode" \
  -F "file=@document.pdf"

# Decode Base64 to file
curl -X POST "http://localhost:8000/base64/decode" \
  -d '{"base64_data": "JVBERi0xLjQ...", "filename": "output.pdf"}'
```

### JWT Operations
```bash
# Create JWT token
curl -X POST "http://localhost:8000/codec/encode/jwt/payload" \
  -H "Content-Type: application/json" \
  -d '{"payload": {"user": "john", "role": "admin"}, "secret": "your-secret"}'

# Decode JWT token
curl -X POST "http://localhost:8000/codec/decode/jwt/token" \
  -H "Content-Type: application/json" \
  -d '{"token": "eyJ0eXAiOiJKV1Q...", "secret": "your-secret"}'
```

### Image Processing
```bash
# Convert image format
curl -X POST "http://localhost:8000/images/convert" \
  -F "image=@photo.jpg" \
  -F "target_format=webp" \
  -d "quality=85"

# Resize image
curl -X POST "http://localhost:8000/images/resize" \
  -F "image=@photo.jpg" \
  -d "size_preset=hd" \
  -d "maintain_aspect_ratio=true"

# Batch convert images
curl -X POST "http://localhost:8000/images/batch-convert" \
  -F "images=@photo1.jpg" \
  -F "images=@photo2.png" \
  -F "target_format=webp"
```

### Audio Processing
```bash
# Convert audio format
curl -X POST "http://localhost:8000/audio/convert" \
  -F "audio=@song.wav" \
  -F "target_format=mp3" \
  -d "bitrate=320"

# Apply audio effects
curl -X POST "http://localhost:8000/audio/effects" \
  -F "audio=@song.wav" \
  -d "normalize=true" \
  -d "noise_reduction=true"

# Extract audio analysis
curl -X POST "http://localhost:8000/audio/analyze" \
  -F "audio=@song.mp3"
```

### Video Processing
```bash
# Convert video format
curl -X POST "http://localhost:8000/video/convert" \
  -F "video=@movie.avi" \
  -F "target_format=mp4" \
  -d "quality_preset=hd"

# Extract audio from video
curl -X POST "http://localhost:8000/video/extract-audio" \
  -F "video=@movie.mp4" \
  -d "audio_format=mp3"

# Generate video thumbnail
curl -X POST "http://localhost:8000/video/thumbnail" \
  -F "video=@movie.mp4" \
  -d "timestamp=30" \
  -d "width=640" \
  -d "height=360"
```

---

## 🌟 Detailed Features

### 🖼️ Image Processing Capabilities

**Input Formats (20+):**
- **Modern**: JPEG, PNG, WebP, AVIF, HEIC, HEIF
- **Professional**: TIFF, RAW (CR2, NEF, ARW, DNG, RAF, ORF)
- **Legacy**: BMP, GIF, ICO, PCX, TGA, JP2
- **Specialized**: PDF (first page), SVG (rasterized)

**Output Formats (12+):**
- **Web Optimized**: WebP, AVIF, JPEG, PNG
- **Professional**: TIFF, HEIC, HEIF, JP2
- **Universal**: BMP, GIF, ICO, PDF

**Quality & Optimization:**
- Quality presets: Low (30-50), Medium (60-75), High (80-90), Maximum (95-100)
- Size presets: Thumbnail (150px), Small (300px), Medium (600px), Large (1200px), HD (1920px), Full HD (1920x1080), 2K (2560x1440), 4K (3840x2160), 8K (7680x4320)
- Smart algorithms with automatic format detection
- Target file size optimization

### 🎵 Audio Processing Capabilities

**Input Formats (23+):**
- **Lossless**: WAV, FLAC, AIFF, AU, APE, WV, TTA
- **Lossy**: MP3, AAC, OGG, OPUS, M4A, WMA, AC3
- **Professional**: BWF, RF64, CAF, AMR, 3GA
- **Streaming**: WebM Audio, Matroska Audio

**Output Formats (10+):**
- **Universal**: MP3, WAV, AAC, OGG, FLAC
- **Modern**: OPUS, WebM, M4A
- **Professional**: AIFF, AU

**Processing Features:**
- Bitrate options: 32kbps to 320kbps and beyond
- Sample rates: 8kHz to 192kHz
- Channel configurations: Mono, Stereo, 5.1, 7.1
- Audio effects: Normalization, compression, EQ, reverb, noise reduction
- Advanced analysis: Tempo detection, pitch analysis, spectral features

### 🎬 Video Processing Capabilities

**Input Formats (20+):**
- **Modern**: MP4, MKV, WebM, MOV, AVI, WMV
- **Streaming**: FLV, OGV, M4V, 3GP, ASF
- **Professional**: MXF, ProRes, DNxHD, MTS, M2TS
- **Legacy**: RM, VOB, DV, MPG, MPEG

**Output Formats (10+):**
- **Web Optimized**: MP4, WebM, OGV
- **Universal**: AVI, MOV, MKV
- **Mobile**: 3GP, M4V
- **Platform Specific**: WMV, FLV

**Quality Presets:**
- Mobile (480p), SD (720p), HD (1080p), Full HD (1920x1080)
- 2K (2560x1440), 4K (3840x2160), 8K (7680x4320)
- Custom resolution, bitrate, and frame rate options

### 🔐 Encoder/Decoder Features

**Supported Operations:**
- **Base64**: Text and file encoding/decoding with validation
- **JWT**: Token creation, verification, inspection, header decoding
- **URL**: Standard and component encoding/decoding  
- **Hash**: MD5, SHA1, SHA224, SHA256, SHA384, SHA512
- **Hex**: Hexadecimal encoding/decoding with validation

**Security Features:**
- JWT algorithm support: HS256, HS384, HS512, RS256, RS384, RS512
- Token expiration handling and validation
- Secure secret management
- Input sanitization and validation

---

## 🏗️ Advanced Architecture

### Service Layer Architecture
- **Dependency Injection**: Clean service instantiation and management
- **Interface Segregation**: Focused service contracts
- **Single Responsibility**: Each service handles one concern
- **Factory Pattern**: Centralized service creation and configuration

### Error Handling
- **Structured Exceptions**: Custom exception hierarchy
- **Global Error Handler**: Consistent error responses
- **Validation**: Comprehensive input validation with Pydantic
- **Logging**: Detailed error tracking and debugging

### Performance Optimization
- **Streaming Processing**: Memory-efficient file handling
- **Async Operations**: Non-blocking I/O for better throughput
- **Background Tasks**: Long-running operations with Celery
- **Caching**: Redis-based caching for improved response times

---

## 🧪 Environment Setup

### Development Environment
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run with auto-reload
uvicorn app.main:filecraft --reload

# Run tests
pytest tests/
```

### Production Environment
```bash
# Use Docker Compose for production
docker-compose -f docker-compose.prod.yml up -d

# Or build production image
docker build -f Dockerfile.prod -t filecraft:prod .
```

### Environment Variables
```bash
# Core Settings
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# File Processing Limits
MAX_FILE_SIZE=100MB
MAX_BATCH_SIZE=10
TEMP_DIR=/tmp/filecraft
```

---

## 🚀 Performance & Scalability

### Horizontal Scaling
- **Load Balancing**: Deploy multiple API instances behind a load balancer
- **Worker Scaling**: Scale Celery workers based on queue length
- **Redis Clustering**: Use Redis Cluster for high availability
- **Database Sharding**: Distribute data across multiple database instances

### Performance Monitoring
- **Metrics Collection**: Prometheus-compatible metrics endpoint
- **Health Checks**: Built-in health check endpoints
- **Request Tracing**: Distributed tracing with OpenTelemetry
- **Performance Profiling**: Built-in performance monitoring

### Optimization Tips
- **Memory Management**: Tune worker memory limits and restart policies
- **Disk I/O**: Use SSD storage for temporary file processing
- **Network**: Optimize network settings for high-throughput file transfers
- **Caching**: Implement result caching for frequently processed files

---

## 📝 API Reference

### Response Format
All API responses follow a consistent structure:

```json
{
    "success": true,
    "data": {
        // Response data
    },
    "message": "Operation completed successfully",
    "timestamp": "2024-01-01T12:00:00Z",
    "processing_time": 0.123
}
```

### Error Response Format
```json
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid file format",
        "details": {
            "field": "file",
            "reason": "Unsupported format"
        }
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

### Status Codes
- **200**: Success
- **201**: Created (for background tasks)
- **400**: Bad Request (validation errors)
- **413**: Payload Too Large (file size exceeded)
- **415**: Unsupported Media Type
- **429**: Too Many Requests (rate limiting)
- **500**: Internal Server Error

---

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Install development dependencies
4. Make your changes
5. Run tests and linting
6. Submit a pull request

### Code Standards
- **Type Hints**: Use Python type hints throughout
- **Docstrings**: Document all public methods and classes
- **Testing**: Write comprehensive tests for new features
- **Linting**: Follow PEP 8 and use Black for formatting

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

Built with ❤️ and performance in mind by **Shivam Pandey**.

Optimized for speed, low memory usage, and a seamless developer experience.

---

## 🔗 Links

- **Documentation**: [API Docs](http://localhost:8000/docs)
- **Repository**: [GitHub](https://github.com/yourusername/filecraft)
- **Issues**: [Bug Reports](https://github.com/yourusername/filecraft/issues)
- **Discussions**: [Community](https://github.com/yourusername/filecraft/discussions)

---

## 📊 Project Stats

- **Languages**: Python, Docker, Shell
- **Dependencies**: FastAPI, Pillow, FFmpeg, Celery, Redis
- **File Formats Supported**: 50+ input formats, 30+ output formats
- **API Endpoints**: 40+ comprehensive endpoints
- **Background Processing**: Full async task support
- **Documentation**: 100% API coverage with examples