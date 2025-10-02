# 🧠 FileCraft – Professional Media Processing API

**FileCraft** is a modern, comprehensive API built with **FastAPI** that provides professional-grade media processing capabilities:

- 📄 Convert any uploaded file to **Base64** (with optional compression)
- 🖼️ **Image Processing**: Convert between 15+ formats with advanced features
- 🎵 **Audio Processing**: Convert, enhance, and analyze audio files
- 🎬 **Video Processing**: Convert videos, extract audio, generate thumbnails
- � **Smart Compression**: Optimize files and media with intelligent algorithms
- ⚡ **Background Processing**: Handle large files asynchronously with Celery

---

## 🚀 Core Features

### 🖼️ Image Processing
✅ **15+ Formats**: JPEG, PNG, WebP, HEIC, AVIF, RAW, and more  
✅ **Quality Control**: Adjustable compression and optimization  
✅ **Smart Resizing**: Maintain aspect ratios, size presets  
✅ **Batch Processing**: Convert multiple images simultaneously  
✅ **Metadata Removal**: Clean EXIF, ICC profiles  

### 🎵 Audio Processing
✅ **10+ Formats**: MP3, WAV, AAC, OGG, FLAC, Opus, and more  
✅ **Audio Effects**: Normalize, compress, EQ, noise reduction  
✅ **Quality Presets**: From phone to studio quality  
✅ **Advanced Analysis**: Tempo, pitch, spectral features  
✅ **Format Conversion**: Lossless and lossy options  

### 🎬 Video Processing
✅ **Universal Formats**: MP4, MKV, WebM, AVI, MOV, and more  
✅ **Quality Presets**: Mobile to 8K resolution options  
✅ **Audio Extraction**: Extract audio tracks from videos  
✅ **Thumbnail Generation**: Create previews at any timestamp  
✅ **Modern Codecs**: H.264, H.265, VP9, AV1 support  

### ⚡ Performance & Infrastructure
✅ **Stream-based Processing**: No file system dependency  
✅ **Background Processing**: Async tasks with Celery + Redis  
✅ **Memory Efficient**: Optimized for large files  
✅ **Docker Ready**: Production deployment support  
✅ **API Documentation**: Interactive Swagger/OpenAPI docs

---

## 🛠️ Tech Stack

| Category | Tool | Purpose |
|----------|------|---------|
| **Core** | 🐍 Python 3.12+ | Core language |
| **Framework** | ⚡ FastAPI | High-performance web framework |
| **Media Processing** | 🖼️ Pillow | Image processing and conversion |
| **Media Processing** | 🎵 Pydub + FFmpeg | Audio processing |
| **Media Processing** | 🎬 FFmpeg | Video processing and conversion |
| **Background Tasks** | 🔥 Celery | Async task processing |
| **Caching** | 📦 Redis | Task queue and caching |
| **Compression** | 🧪 Zlib | Binary file compression |
| **Deployment** | 🐳 Docker | Containerization |
| **Server** | 🔥 Uvicorn | ASGI server |

---

## 📂 Project Structure

├── app
│   ├── dependencies.py
│   ├── helpers
│   │   ├── constants.py
│   │   ├── converter.py
│   │   ├── file_validator.py
│   │   ├── __init__.py
|   |
│   ├── __init__.py
│   ├── main.py
│   ├── models
│   │   └── __init__.py
|   |
│   └── router
│       ├── auth
│       │   └── __init__.py
|       |
│       ├── converters
│       │   ├── base64.py
│       │   ├── compression.py
│       │   ├── images.py
│       │   ├── __init__.py
|       |
│       ├── decoder
│       │   └── __init__.py
│       ├── __init__.py
|
├── config
│   ├── database.py
│   ├── __init__.py
│   └── settings
│       ├── base.py
│       ├── config.py
│       ├── __init__.py
|
├── docker-compose.yml
├── Dockerfile
├── LICENSE
├── pyproject.toml
├── README.md
└── requirements.txt

---

## 📚 API Documentation

FileCraft provides comprehensive processing capabilities through organized API endpoints:

### 🖼️ Image Processing (`/images`)
- **Format Conversion**: Convert between 15+ image formats
- **Quality Control**: Adjustable compression and optimization
- **Batch Processing**: Convert multiple images simultaneously
- **Analysis**: Get detailed image information and metadata

**Detailed Guide**: [📖 Image Processing README](README_IMAGE_PROCESSING.md)

### 🎵 Audio Processing (`/audio`)
- **Format Conversion**: Support for 10+ audio formats
- **Audio Effects**: Normalize, compress, EQ, noise reduction
- **Analysis**: Extract tempo, pitch, and spectral features
- **Quality Presets**: From phone to studio quality

**Detailed Guide**: [📖 Audio Processing README](README_AUDIO_PROCESSING.md)

### 🎬 Video Processing (`/video`)
- **Format Conversion**: Universal video format support
- **Audio Extraction**: Extract audio tracks from videos
- **Thumbnail Generation**: Create previews at any timestamp
- **Quality Presets**: Mobile to 8K resolution options

**Detailed Guide**: [📖 Video Processing README](README_VIDEO_PROCESSING.md)

### 📦 Additional Services
- **Base64 Conversion** (`/base64`): Convert any file to Base64
- **Smart Compression** (`/compression`): Optimize files intelligently

### 🌐 Interactive API Documentation
Once running, access the interactive documentation:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/api/openapi.json`

---

## ⚙️ Getting Started

### 🧪 1. Prerequisites

**FFmpeg Installation** (Required for audio/video processing):

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

### 🧪 2. Local Setup

```bash
git clone https://github.com/yourusername/filecraft.git
cd filecraft

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Verify Installation**:
```bash
ffmpeg -version  # Should show FFmpeg version
python -c "import ffmpeg; print('FFmpeg Python bindings OK')"
```

### ▶️ 3. Run App (Dev Mode)

```bash
uvicorn app.main:filecraft --reload --host 0.0.0.0 --port 8000
```
## or you can chose docker file
### 🐳 4. Run with Docker
```bash
docker build -t filecraft .
docker run -p 8000:8000 filecraft
```

### ▶️ 5. Optional: Background Processing Setup

For handling large files asynchronously, set up Redis and Celery:

```bash
# Install Redis
sudo apt install redis-server  # Ubuntu/Debian
brew install redis              # macOS

# Start Redis
redis-server

# In another terminal, start Celery worker
celery -A app.celery_app worker --loglevel=info
```

---

## 🚀 Quick API Examples

### Convert Image Format
```bash
curl -X POST "http://localhost:8000/images/convert" \
  -F "image=@photo.jpg" \
  -F "target_format=webp" \
  -d "quality=85"
```

### Convert Audio Format
```bash
curl -X POST "http://localhost:8000/audio/convert" \
  -F "audio=@song.wav" \
  -F "target_format=mp3" \
  -d "bitrate=320"
```

### Convert Video Format
```bash
curl -X POST "http://localhost:8000/video/convert" \
  -F "video=@movie.avi" \
  -F "target_format=mp4" \
  -d "quality_preset=hd"
```

### Extract Audio from Video
```bash
curl -X POST "http://localhost:8000/video/extract-audio" \
  -F "video=@movie.mp4" \
  -d "audio_format=mp3"
```

### Generate Video Thumbnail
```bash
curl -X POST "http://localhost:8000/video/thumbnail" \
  -F "video=@movie.mp4" \
  -d "timestamp=30" \
  -d "width=640" \
  -d "height=360"
```

---

## 🌟 Features by Category

### 🖼️ Image Processing
- **15+ Input Formats**: JPEG, PNG, WebP, HEIC, AVIF, RAW (CR2, NEF, ARW), BMP, GIF, TIFF, ICO, and more
- **12+ Output Formats**: JPEG, PNG, WebP, HEIC, AVIF, BMP, GIF, TIFF, ICO, JP2, PDF
- **Advanced Features**: Smart resizing, quality optimization, batch conversion, metadata analysis

### 🎵 Audio Processing  
- **20+ Input Formats**: MP3, WAV, AAC, OGG, FLAC, M4A, WMA, AIFF, AU, and more
- **10+ Output Formats**: MP3, WAV, AAC, OGG, FLAC, M4A, Opus, WebM, AIFF, AU
- **Audio Effects**: Normalize, compress, EQ, reverb, noise reduction, pitch/tempo changes
- **Analysis**: Tempo detection, pitch analysis, spectral features, MFCC coefficients

### 🎬 Video Processing
- **20+ Input Formats**: MP4, MKV, AVI, MOV, WMV, FLV, WebM, OGV, 3GP, MTS, and more
- **10+ Output Formats**: MP4, MKV, WebM, AVI, MOV, WMV, FLV, OGV, M4V, 3GP
- **Video Features**: Format conversion, audio extraction, thumbnail generation, quality presets
- **Codecs**: H.264, H.265, VP8, VP9, AV1 with hardware acceleration support

---

### 👨‍💻 Author
Built with ❤️ and performance in mind by Shivam Pandey.
Optimized for speed, low memory usage, and a seamless developer experience.

