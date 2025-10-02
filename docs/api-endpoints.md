# API Endpoints Reference

## Base64 & File Processing

### POST /base64/encode
Convert any file to Base64 format.

**Request:**
- `file`: Uploaded file (multipart/form-data)
- `compress`: Optional compression (boolean)

**Response:**
```json
{
    "success": true,
    "data": {
        "base64_data": "JVBERi0xLjQ...",
        "filename": "document.pdf",
        "size": 1024,
        "compressed": false
    }
}
```

### POST /base64/decode
Decode Base64 data back to file.

**Request:**
```json
{
    "base64_data": "JVBERi0xLjQ...",
    "filename": "output.pdf"
}
```

## Encoder/Decoder System

### JWT Operations
- `POST /codec/encode/jwt/payload` - Create JWT from JSON payload
- `POST /codec/decode/jwt/token` - Decode and verify JWT
- `POST /codec/decode/jwt/inspect` - Inspect token without verification

### Hash Operations  
- `POST /codec/encode/hash/md5` - Generate MD5 hash
- `POST /codec/encode/hash/sha256` - Generate SHA256 hash
- `POST /codec/encode/hash/sha512` - Generate SHA512 hash

### URL Operations
- `POST /codec/encode/url` - URL encode text
- `POST /codec/decode/url` - URL decode text

## Image Processing

### Format Conversion
- `POST /images/convert` - Convert image formats
- `POST /images/batch-convert` - Batch convert multiple images
- `POST /images/resize` - Resize images with presets
- `POST /images/optimize` - Optimize image quality and size

### Image Analysis
- `POST /images/analyze` - Get image metadata and properties
- `GET /images/formats` - List supported formats

## Audio Processing

### Format Conversion
- `POST /audio/convert` - Convert audio formats
- `POST /audio/batch-convert` - Batch convert audio files

### Audio Effects
- `POST /audio/normalize` - Normalize audio levels
- `POST /audio/compress` - Apply audio compression
- `POST /audio/effects` - Apply multiple effects

### Audio Analysis
- `POST /audio/analyze` - Extract audio features and metadata
- `GET /audio/formats` - List supported formats

## Video Processing

### Format Conversion
- `POST /video/convert` - Convert video formats
- `POST /video/extract-audio` - Extract audio from video
- `POST /video/thumbnail` - Generate video thumbnails

### Video Analysis
- `POST /video/analyze` - Get video metadata and properties
- `GET /video/formats` - List supported formats

## System Endpoints

### Health & Status
- `GET /health` - Application health check
- `GET /status` - System status and metrics
- `GET /info` - Application information

### Documentation
- `GET /docs` - Swagger UI documentation
- `GET /redoc` - ReDoc documentation
- `GET /openapi.json` - OpenAPI specification