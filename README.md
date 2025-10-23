# 🧠 FileCraft – Local File Processing API

> **Professional file conversion and processing API - Simplified for local development**

FileCraft is a comprehensive file processing API that handles image, audio, video conversion, encoding/decoding operations, and compression tasks. This version has been streamlined to run locally without external dependencies.

## ⚡ Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd FileCraft

# Run the startup script
./start_local.sh
```

🎉 **That's it!** Your API will be running at http://127.0.0.1:8000

## 📖 Documentation

- **API Docs**: http://127.0.0.1:8000/docs
- **Health Check**: http://127.0.0.1:8000/health
- **Detailed Setup**: See [README_LOCAL.md](README_LOCAL.md)

## 🎯 Features

✅ **File Conversion** - Images, Audio, Video formats  
✅ **Encoding/Decoding** - Base64, JWT, URL, Hash operations  
✅ **Compression** - Archives and file compression  
✅ **Local Development** - No external services required  

## 🚀 Endpoints

| Category | Endpoint | Description |
|----------|----------|-------------|
| Images | `/api/v1/images/convert` | Convert image formats |
| Audio | `/api/v1/audio/convert` | Convert audio formats |
| Video | `/api/v1/video/convert` | Convert video formats |
| Encoding | `/api/v1/encode/base64` | Base64 encoding |
| Decoding | `/api/v1/decode/base64` | Base64 decoding |
| Compression | `/api/v1/compress` | File compression |

## 💻 Local Development

This version is optimized for local development:
- No database required
- No Redis/Celery required  
- No cloud services required
- Simple file-based processing
- Auto-reload enabled
- Debug mode on

## 📁 File Limits

- Max upload: 100MB
- Max image: 20MB  
- Max audio: 50MB
- Max video: 100MB

## 🔧 Requirements

- Python 3.12+
- FFmpeg (for audio/video processing)

The startup script handles everything else automatically!

## 📝 Example Usage

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
Install FFmpeg for audio/video processing:

**Ubuntu/Debian:**
```bash
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

### Port Already in Use
Change the port in `.env`:
```env
PORT=8001
```

---

**For detailed setup instructions, troubleshooting, and examples, see [README_LOCAL.md](README_LOCAL.md)**