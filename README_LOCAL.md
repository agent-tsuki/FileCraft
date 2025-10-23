# FileCraft - Local Development Setup

FileCraft is a professional file conversion and processing API. This version has been simplified to run locally without any external dependencies like databases, Redis, or cloud services.

## 🚀 Quick Start

### Prerequisites

- Python 3.12 or higher
- FFmpeg (for audio/video processing)

### Installation

1. **Clone or download the project**
   ```bash
   cd FileCraft
   ```

2. **Run the startup script**
   ```bash
   ./start_local.sh
   ```

That's it! The script will:
- Create a virtual environment
- Install all dependencies
- Set up configuration
- Start the API server

### Manual Setup (Alternative)

If you prefer to set up manually:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.local .env

# Create uploads directory
mkdir -p uploads

# Start the server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## 📍 Access the API

Once running, you can access:

- **API Server**: http://127.0.0.1:8000
- **API Documentation**: http://127.0.0.1:8000/docs
- **Alternative Docs**: http://127.0.0.1:8000/redoc
- **Health Check**: http://127.0.0.1:8000/health
- **API Info**: http://127.0.0.1:8000/api/info

## 🎯 Features

This local version includes:

✅ **File Conversion**
- Image format conversion (JPEG, PNG, WebP, etc.)
- Audio format conversion (MP3, WAV, FLAC, etc.)
- Video format conversion (MP4, AVI, WebM, etc.)
- Document processing

✅ **Encoding/Decoding**
- Base64 encoding/decoding
- JWT token operations
- URL encoding/decoding
- Hash operations

✅ **Compression**
- File compression and decompression
- Archive creation and extraction

❌ **Disabled for Simplicity**
- Database storage
- Background task processing (Celery/Redis)
- Cloud storage (AWS S3)
- Email notifications
- Complex async processing

## 📁 File Limits

- Maximum upload size: 100MB
- Maximum image size: 20MB
- Maximum audio size: 50MB
- Maximum video size: 100MB

## 🛠 Development

The application runs in development mode with:
- Auto-reload enabled
- Debug mode on
- Detailed error messages
- API documentation enabled

## 🔧 Configuration

All configuration is in `.env.local` (copied to `.env`). Key settings:

```env
DEBUG=true
HOST=127.0.0.1
PORT=8000
RELOAD=true
MAX_UPLOAD_SIZE=104857600
ENABLE_ASYNC_PROCESSING=false
```

## 📖 API Usage Examples

### Convert Image Format
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/images/convert" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@image.jpg" \
  -F "target_format=png"
```

### Convert Audio Format
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/audio/convert" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@audio.wav" \
  -F "target_format=mp3"
```

### Encode to Base64
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/encode/base64" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"
```

## 🐛 Troubleshooting

### FFmpeg Not Found
If you get FFmpeg errors, install it:

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from https://ffmpeg.org/download.html

### Permission Errors
Make sure the startup script is executable:
```bash
chmod +x start_local.sh
```

### Port Already in Use
If port 8000 is busy, change it in `.env`:
```env
PORT=8001
```

## 📝 Notes

- This is a simplified local version - no external services required
- Files are processed synchronously (no background tasks)
- Uploads are stored temporarily in the `uploads/` directory
- Perfect for development, testing, and small-scale usage

## 🎉 That's it!

You now have a fully functional file processing API running locally. Check out the API documentation at http://127.0.0.1:8000/docs to explore all available endpoints.