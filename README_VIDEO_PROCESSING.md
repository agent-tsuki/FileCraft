# 🎬 FileCraft Video Processing API

## Overview

FileCraft's Video Processing API provides comprehensive video conversion, manipulation, and analysis capabilities. Built with FFmpeg for professional-grade video processing, it supports a wide range of formats and advanced features.

## 🚀 Features

### Core Capabilities
- **Format Conversion**: Convert between 10+ video formats
- **Audio Extraction**: Extract audio tracks from videos
- **Thumbnail Generation**: Create video thumbnails at any timestamp
- **Batch Processing**: Process multiple videos simultaneously
- **Quality Presets**: From mobile to 8K quality settings
- **Advanced Codecs**: H.264, H.265, VP9, AV1 support
- **Background Processing**: Async processing for large files

### Input Formats
- **Modern**: MP4, MKV, WebM, MOV, AVI, WMV
- **Streaming**: FLV, OGV, M4V, 3GP
- **Professional**: MXF, ProRes, DNxHD, MTS, M2TS
- **Legacy**: ASF, RM, VOB, DV, MPG, MPEG

### Output Formats
- **Web Optimized**: MP4, WebM, OGV
- **Universal**: AVI, MOV, MKV
- **Mobile**: 3GP, M4V
- **Windows**: WMV
- **Flash**: FLV

## 📚 API Endpoints

### 🔄 Format Conversion

#### Convert Video Format
```http
POST /video/convert
```

**Features:**
- Support for 10+ output formats
- Quality presets (mobile to 8K)
- Custom resolution, bitrate, frame rate
- Multiple codec options
- Background processing for large files

**Parameters:**
- `video` (file): Video file to convert
- `target_format` (enum): Output format (mp4, mkv, webm, etc.)
- `quality_preset` (enum): mobile, sd, hd, full_hd, 2k, 4k, 8k
- `codec` (enum): h264, h265, vp8, vp9, av1, auto
- `bitrate` (string): Video bitrate (e.g., "1000k", "5M")
- `width` (int): Target width (64-7680)
- `height` (int): Target height (64-4320)
- `frame_rate` (float): Target fps (12-120)
- `use_async` (bool): Background processing

**Example:**
```bash
curl -X POST "http://localhost:8000/video/convert" \
  -F "video=@input.avi" \
  -F "target_format=mp4" \
  -d "quality_preset=hd" \
  -d "codec=h264"
```

#### Batch Convert Videos
```http
POST /video/batch-convert
```

Convert multiple videos with same settings in background.

**Parameters:**
- `videos` (files): List of video files
- `target_format` (enum): Target format for all videos
- `quality_preset` (enum): Quality preset for batch
- `codec` (enum): Video codec to use

### 🎵 Audio Extraction

#### Extract Audio from Video
```http
POST /video/extract-audio
```

**Features:**
- Extract to multiple audio formats
- Custom audio bitrate control
- Preserves original quality when possible

**Parameters:**
- `video` (file): Video file with audio track
- `audio_format` (enum): mp3, aac, wav, ogg, flac
- `audio_bitrate` (string): Audio bitrate (e.g., "128k", "320k")

**Example:**
```bash
curl -X POST "http://localhost:8000/video/extract-audio" \
  -F "video=@movie.mp4" \
  -d "audio_format=mp3" \
  -d "audio_bitrate=320k"
```

### 🖼️ Thumbnail Generation

#### Generate Video Thumbnail
```http
POST /video/thumbnail
```

**Features:**
- Extract thumbnail at any time position
- Custom dimensions and format
- Multiple output formats (JPEG, PNG, WebP)

**Parameters:**
- `video` (file): Video file
- `timestamp` (float): Time position in seconds (0-3600)
- `width` (int): Thumbnail width (64-1920)
- `height` (int): Thumbnail height (64-1080)
- `image_format` (enum): jpg, jpeg, png, webp

**Example:**
```bash
curl -X POST "http://localhost:8000/video/thumbnail" \
  -F "video=@movie.mp4" \
  -d "timestamp=30.5" \
  -d "width=640" \
  -d "height=360" \
  -d "image_format=jpg"
```

### 📊 Analysis & Information

#### Get Video Information
```http
POST /video/info
```

**Analysis includes:**
- Format and container information
- Video stream properties (codec, resolution, fps, bitrate)
- Audio stream properties (codec, sample rate, channels)
- Duration and file size
- Metadata and technical specifications

**Example Response:**
```json
{
  "filename": "sample.mp4",
  "format": "mov,mp4,m4a,3gp,3g2,mj2",
  "duration": 120.5,
  "size": 15728640,
  "bitrate": 1048576,
  "streams": 2,
  "video": {
    "codec": "h264",
    "width": 1920,
    "height": 1080,
    "fps": 30.0,
    "aspect_ratio": "16:9",
    "pixel_format": "yuv420p",
    "bitrate": 1000000
  },
  "audio": {
    "codec": "aac",
    "sample_rate": 48000,
    "channels": 2,
    "bitrate": 128000
  }
}
```

### 📋 Utility Endpoints

#### Get Supported Formats
```http
GET /video/formats
```

Returns information about supported formats, codecs, and capabilities.

#### Get Task Status
```http
GET /video/task/{task_id}
```

Check status of background video processing tasks.

## 🎯 Quality Presets

| Preset | Resolution | Bitrate | Use Case |
|--------|------------|---------|----------|
| mobile | 480x360 | 500k | Mobile devices, low bandwidth |
| sd | 720x480 | 1.5M | Standard definition |
| hd | 1280x720 | 3M | HD streaming, web |
| full_hd | 1920x1080 | 5M | Full HD, broadcast |
| 2k | 2048x1080 | 8M | Cinema, professional |
| 4k | 3840x2160 | 15M | Ultra HD, premium content |
| 8k | 7680x4320 | 50M | Future-proofing, cinema |

## 🔧 Video Codecs

| Codec | Name | Year | Hardware Acceleration | Best For |
|-------|------|------|---------------------|----------|
| H.264 | AVC | 2003 | ✅ | Universal compatibility |
| H.265 | HEVC | 2013 | ✅ | Better compression, 4K+ |
| VP8 | VP8 | 2008 | ✅ | Open source, WebM |
| VP9 | VP9 | 2013 | ✅ | YouTube, WebM, efficient |
| AV1 | AV1 | 2018 | ✅ | Next-gen, royalty-free |

## 📐 Format Specifications

### Container Formats

| Format | Extension | Year | Streaming | HDR | Max Resolution |
|--------|-----------|------|-----------|-----|---------------|
| MP4 | .mp4 | 2001 | ✅ | ✅ | Unlimited |
| MKV | .mkv | 2002 | ❌ | ✅ | Unlimited |
| WebM | .webm | 2010 | ✅ | ✅ | Unlimited |
| AVI | .avi | 1992 | ❌ | ❌ | Unlimited |
| MOV | .mov | 1991 | ❌ | ❌ | Unlimited |
| WMV | .wmv | 1999 | ✅ | ❌ | 1920x1080 |

### Professional Formats

| Format | Use Case | Year | Features |
|--------|----------|------|----------|
| MXF | Broadcast | 2004 | Professional metadata |
| ProRes | Apple ecosystem | 2007 | High quality, editing |
| DNxHD | Avid systems | 2004 | Broadcast quality |
| MTS/M2TS | Cameras, Blu-ray | 2006 | AVCHD, high bitrate |

## 🛠️ Advanced Usage

### Custom FFmpeg Parameters

For advanced users, you can pass custom FFmpeg parameters:

```python
import requests

response = requests.post(
    "http://localhost:8000/video/convert",
    files={"video": open("input.mp4", "rb")},
    data={
        "target_format": "mp4",
        "codec": "h264",
        "custom_args": {
            "preset": "slow",
            "crf": "18",
            "profile:v": "high"
        }
    }
)
```

### Background Processing

For large files, use async processing:

```bash
# Start conversion
curl -X POST "http://localhost:8000/video/convert" \
  -F "video=@large_video.mkv" \
  -F "target_format=mp4" \
  -d "use_async=true"

# Response: {"task_id": "abc123", "status": "processing"}

# Check status
curl "http://localhost:8000/video/task/abc123"
```

### Batch Processing

Process multiple videos efficiently:

```bash
curl -X POST "http://localhost:8000/video/batch-convert" \
  -F "videos=@video1.avi" \
  -F "videos=@video2.mov" \
  -F "videos=@video3.wmv" \
  -F "target_format=mp4" \
  -d "quality_preset=hd"
```

## 🔧 Installation & Setup

### Prerequisites

1. **FFmpeg**: Required for video processing
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install ffmpeg
   
   # macOS
   brew install ffmpeg
   
   # Windows
   # Download from https://ffmpeg.org/download.html
   ```

2. **Python Dependencies**: Already included in requirements.txt
   ```bash
   pip install ffmpeg-python
   ```

### Verification

Test FFmpeg installation:
```bash
ffmpeg -version
```

Test video processing:
```bash
curl -X POST "http://localhost:8000/video/formats"
```

## 💡 Best Practices

### Performance Optimization

1. **Use appropriate quality presets** for target use case
2. **Enable async processing** for files > 100MB
3. **Choose efficient codecs** (H.264 for compatibility, H.265 for size)
4. **Batch process** multiple files when possible

### Quality vs Size

- **Web streaming**: Use H.264 with 720p/1080p
- **Mobile**: Use H.264 with mobile preset
- **Archival**: Use H.265 or lossless codecs
- **Social media**: Use platform-specific presets

### Hardware Acceleration

FileCraft automatically uses hardware acceleration when available:
- **NVIDIA**: NVENC for H.264/H.265
- **Intel**: Quick Sync Video
- **AMD**: VCE/AMF encoding

## 🚨 Error Handling

Common error scenarios:

### Unsupported Format
```json
{
  "detail": "Unsupported target format: xyz",
  "error_code": "UNSUPPORTED_FORMAT"
}
```

### FFmpeg Not Available
```json
{
  "detail": "Video processing libraries not available",
  "error_code": "FFMPEG_MISSING"
}
```

### File Too Large
```json
{
  "detail": "File size exceeds maximum limit (500MB)",
  "error_code": "FILE_TOO_LARGE"
}
```

## 📊 Performance Metrics

Typical processing speeds (depends on hardware):

| Quality | Resolution | Speed (relative to real-time) |
|---------|------------|-------------------------------|
| Mobile | 480p | 5-10x faster |
| HD | 720p | 2-4x faster |
| Full HD | 1080p | 1-2x faster |
| 4K | 2160p | 0.2-0.5x (slower than real-time) |

## 🔮 Future Features

Coming soon:
- **Video effects and filters** (blur, sharpen, color correction)
- **Advanced encoding options** (VBR, CBR, CRF modes)
- **GPU acceleration support** for faster processing
- **Video concatenation and splitting**
- **Subtitle extraction and embedding**
- **Motion detection and analysis**

## 🆘 Troubleshooting

### Common Issues

1. **FFmpeg not found**
   - Ensure FFmpeg is installed and in PATH
   - Check with `ffmpeg -version`

2. **Slow processing**
   - Use hardware acceleration if available
   - Choose appropriate quality preset
   - Enable async processing for large files

3. **Out of memory**
   - Process videos in smaller batches
   - Use lower quality presets
   - Enable streaming processing

### Support

For issues and feature requests:
- Check logs in `/logs` directory
- Verify FFmpeg installation
- Test with sample files first
- Use async processing for large files

---

*Part of the FileCraft Professional File Processing Suite*