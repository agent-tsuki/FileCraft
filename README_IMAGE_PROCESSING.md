# 🎨 FileCraft Image Processing API

A high-performance, feature-rich image processing API built with FastAPI, supporting 20+ image formats with advanced optimization and background processing capabilities.

## ✨ Features

### 📸 Comprehensive Format Support
- **Input Formats**: JPEG, PNG, WebP, BMP, GIF, TIFF, HEIC, HEIF, AVIF, RAW (CR2, NEF, ARW, DNG, etc.), ICO, PCX, TGA, and more
- **Output Formats**: JPEG, PNG, WebP, BMP, GIF, TIFF, HEIC, HEIF, AVIF, ICO, JP2, PDF
- **Historical Coverage**: From oldest formats (1980s) to cutting-edge modern formats (2020s)

### 🎚️ Quality & Optimization
- **Quality Presets**: Low, Medium, High, Maximum, Lossless
- **Custom Quality**: 1-100 scale for fine-tuned control
- **Optimization Levels**: Low, Medium, High, Maximum
- **Smart Algorithms**: Automatic format detection and optimization recommendations

### 📏 Advanced Resizing
- **Size Presets**: Thumbnail, Small, Medium, Large, HD, Full HD, 2K, 4K, 8K
- **Custom Dimensions**: Precise width/height control
- **Aspect Ratio**: Intelligent preservation or custom ratios
- **Smart Upscaling**: Optional high-quality enlargement

### 🚀 Performance & Scalability
- **Background Processing**: Celery-based async processing for large files
- **Batch Operations**: Convert multiple images simultaneously
- **Progress Tracking**: Real-time status updates
- **Memory Optimization**: Efficient processing of high-resolution images

### 🛠️ Professional Tools
- **Image Analysis**: Comprehensive metadata and statistics
- **Size Optimization**: Target specific file sizes
- **Format Recommendations**: AI-powered format suggestions
- **Compression Analysis**: Quality estimation and artifact detection

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.12+
- Redis (for background processing)

### Installation & Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd FileCraft
```

2. **Environment Setup**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start All Services**
```bash
./start.sh
```

This will start:
- FastAPI Application (http://localhost:8080)
- Redis (Background task queue)
- Celery Worker (Image processing)
- Flower (Task monitoring at http://localhost:5555)
- PostgreSQL Database

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

### Key Endpoints

#### 🔍 Get Supported Formats
```http
GET /images/formats
```
Returns all supported input/output formats with capabilities.

#### 🔄 Convert Image Format
```http
POST /images/convert
```

**Parameters:**
- `image`: Image file (multipart/form-data)
- `target_format`: Output format (dropdown selection)
- `quality`: Quality level (1-100) or preset
- `optimization_level`: Processing optimization
- `resize_width/height`: Optional resizing
- `size_preset`: Common size presets
- `use_async`: Background processing toggle

**Example:**
```bash
curl -X POST \
  -F "image=@photo.jpg" \
  -F "target_format=webp" \
  -F "quality=90" \
  -F "optimization_level=high" \
  http://localhost:8080/images/convert
```

#### 📦 Batch Convert
```http
POST /images/batch-convert
```
Convert multiple images with same settings.

#### 🎯 Optimize Image
```http
POST /images/optimize
```
Optimize for size, quality, or balanced approach.

#### 📊 Image Analysis
```http
POST /images/info
```
Get comprehensive image information and metadata.

#### 📈 Task Status
```http
GET /images/task/{task_id}
```
Check background task progress.

## 🎛️ Configuration Options

### Quality Presets
- **Low (50)**: Maximum compression, smaller files
- **Medium (75)**: Balanced quality/size
- **High (90)**: High quality, larger files
- **Maximum (95)**: Near-lossless quality
- **Lossless (100)**: No quality loss

### Size Presets
- **Thumbnail**: 150×150px
- **Small**: 320×240px
- **Medium**: 640×480px
- **Large**: 1024×768px
- **HD**: 1280×720px
- **Full HD**: 1920×1080px
- **2K**: 2048×1080px
- **4K**: 3840×2160px
- **8K**: 7680×4320px

### Optimization Levels
- **Low**: Basic optimization
- **Medium**: Standard optimization (default)
- **High**: Advanced algorithms, better quality
- **Maximum**: Maximum quality, slower processing

## 🔧 Advanced Usage

### Background Processing
For large images or batch operations, enable async processing:

```python
# Python example
import requests

response = requests.post(
    "http://localhost:8080/images/convert",
    files={"image": open("large_image.tiff", "rb")},
    data={
        "target_format": "webp",
        "quality": 90,
        "use_async": True
    }
)

task_id = response.json()["task_id"]

# Check status
status = requests.get(f"http://localhost:8080/images/task/{task_id}")
```

### Batch Processing
```python
files = [
    ("images", open("image1.jpg", "rb")),
    ("images", open("image2.png", "rb")),
    ("images", open("image3.tiff", "rb"))
]

response = requests.post(
    "http://localhost:8080/images/batch-convert",
    files=files,
    data={
        "target_format": "webp",
        "quality": 85,
        "optimization_level": "high"
    }
)
```

### Size Optimization
```python
response = requests.post(
    "http://localhost:8080/images/optimize",
    files={"image": open("large_photo.jpg", "rb")},
    data={
        "optimization_type": "size",
        "target_size_kb": 500  # Target 500KB
    }
)
```

## 🐳 Docker Configuration

### Development Setup
```bash
docker-compose up --build
```

### Production Deployment
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Scaling Workers
```bash
docker-compose up --scale celery_worker=4
```

## 📊 Monitoring & Debugging

### Celery Monitoring
Access Flower dashboard at http://localhost:5555 to monitor:
- Active/completed tasks
- Worker status and performance
- Task execution times
- Memory usage

### Logs
```bash
# Application logs
docker-compose logs fastapi

# Worker logs
docker-compose logs celery_worker

# All services
docker-compose logs -f
```

## 🔒 Security & Performance

### File Size Limits
- **Images**: 50MB (configurable)
- **Memory Limit**: 256MB per processing task
- **Pixel Limit**: 178MP (PIL safety limit)

### Security Features
- File type validation
- Extension verification
- Memory usage monitoring
- Rate limiting (configurable)

### Performance Optimizations
- Multi-threaded processing
- Memory-efficient image handling
- Progressive JPEG encoding
- Smart caching strategies

## 🌟 Supported Image Formats

### Raster Formats
| Format | Year | Lossy | Transparency | Animation | Notes |
|--------|------|-------|--------------|-----------|-------|
| JPEG/JPG | 1992 | ✅ | ❌ | ❌ | Most common format |
| PNG | 1996 | ❌ | ✅ | ❌ | Web standard |
| WebP | 2010 | ✅ | ✅ | ✅ | Modern web format |
| AVIF | 2019 | ✅ | ✅ | ✅ | Next-gen format |
| HEIC/HEIF | 2015 | ✅ | ✅ | ❌ | Apple standard |
| GIF | 1987 | ❌ | ✅ | ✅ | Animation support |
| BMP | 1985 | ❌ | ❌ | ❌ | Windows bitmap |
| TIFF | 1992 | ❌ | ✅ | ❌ | Professional |

### RAW Formats
- Canon: CR2, CRW
- Nikon: NEF, NRW
- Sony: ARW, SR2
- Adobe: DNG
- Olympus: ORF
- Panasonic: RW2

### Legacy Formats
- PCX (1985) - PC Paintbrush
- TGA (1984) - Truevision
- XBM/XPM (1989) - X Window System

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- PIL/Pillow team for excellent image processing
- FastAPI team for the amazing web framework
- Celery team for robust task processing
- Contributors to all the image format libraries

---

**Made with ❤️ for the image processing community**

For support and questions, please open an issue or contact the development team.