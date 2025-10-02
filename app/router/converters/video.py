"""
Enhanced video conversion router with comprehensive format support and advanced features.
"""
from typing import List, Optional, Dict, Any, Union
from fastapi import APIRouter, Depends, Form, Query, UploadFile, File, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
from enum import Enum

from app.schemas.responses import FileProcessingResponse
from app.services.video import VideoService, get_video_service
from app.helpers.constants import (
    SUPPORTED_VIDEO_OUTPUT_FORMATS, VIDEO_QUALITY_PRESETS, 
    VIDEO_FRAME_RATES, VIDEO_EFFECTS, VIDEO_CODECS
)

video_router = APIRouter(prefix="/video", tags=["Video Converter"])


class VideoFormat(str, Enum):
    """Supported video output formats."""
    mp4 = "mp4"
    mkv = "mkv"
    webm = "webm"
    avi = "avi"
    mov = "mov"
    wmv = "wmv"
    flv = "flv"
    ogv = "ogv"
    m4v = "m4v"
    three_gp = "3gp"


class VideoCodec(str, Enum):
    """Video codec options."""
    h264 = "h264"
    h265 = "h265"
    vp8 = "vp8"
    vp9 = "vp9"
    av1 = "av1"
    xvid = "xvid"
    auto = "auto"


class VideoQualityPreset(str, Enum):
    """Video quality presets for easy selection."""
    mobile = "mobile"
    sd = "sd"
    hd = "hd"
    full_hd = "full_hd"
    two_k = "2k"
    four_k = "4k"
    eight_k = "8k"


class AudioFormat(str, Enum):
    """Audio extraction formats."""
    mp3 = "mp3"
    aac = "aac"
    wav = "wav"
    ogg = "ogg"
    flac = "flac"


@video_router.get("/formats", summary="Get supported video formats")
async def get_supported_formats() -> Dict[str, Any]:
    """Get information about supported video formats and capabilities."""
    return {
        "input_formats": list(VIDEO_CODECS.keys()),
        "output_formats": SUPPORTED_VIDEO_OUTPUT_FORMATS,
        "codecs": VIDEO_CODECS,
        "quality_presets": VIDEO_QUALITY_PRESETS,
        "frame_rates": VIDEO_FRAME_RATES,
        "effects": VIDEO_EFFECTS
    }


@video_router.post(
    "/convert",
    summary="Convert video format with advanced options",
    description="Convert video from one format to another with comprehensive customization options",
    response_model=None
)
async def convert_video_format(
    video: UploadFile = File(..., description="Video file to convert"),
    target_format: VideoFormat = Form(..., description="Target format for conversion"),
    quality_preset: Optional[VideoQualityPreset] = Query(
        default=None,
        description="Quality preset (overrides resolution and bitrate if specified)"
    ),
    codec: Optional[VideoCodec] = Query(
        default=VideoCodec.auto,
        description="Video codec to use for encoding"
    ),
    bitrate: Optional[str] = Query(
        default=None,
        description="Video bitrate (e.g., '1000k', '5M')"
    ),
    # Resolution options
    width: Optional[int] = Query(
        default=None,
        ge=64,
        le=7680,
        description="Target width in pixels"
    ),
    height: Optional[int] = Query(
        default=None,
        ge=64,
        le=4320,
        description="Target height in pixels"
    ),
    frame_rate: Optional[float] = Query(
        default=None,
        ge=12.0,
        le=120.0,
        description="Target frame rate (fps)"
    ),
    use_async: bool = Query(
        default=False,
        description="Use background processing (returns task ID)"
    ),
    video_service: VideoService = Depends(get_video_service)
) -> Union[StreamingResponse, JSONResponse]:
    """
    Convert video to specified format with advanced options.
    
    **Features:**
    - Support for 10+ output formats (MP4, MKV, WebM, AVI, MOV, etc.)
    - Quality presets from mobile to 8K
    - Multiple codec options (H.264, H.265, VP9, AV1, etc.)
    - Custom resolution, bitrate, and frame rate
    - Background processing for large files
    
    **Parameters:**
    - **video**: Video file to convert (supports 20+ input formats)
    - **target_format**: Output format from dropdown
    - **quality_preset**: Predefined quality settings
    - **codec**: Video codec for encoding
    - **bitrate**: Video bitrate (e.g., '1000k', '5M')
    - **width/height**: Custom resolution
    - **frame_rate**: Target frame rate
    - **use_async**: Background processing for large files
    
    **Returns:**
    - Synchronous: Converted video as streaming response
    - Asynchronous: JSON with task ID for status checking
    """
    # Prepare conversion options
    resolution = (width, height) if width and height else None
    
    # Convert video
    result = await video_service.convert_video_format(
        video,
        target_format.value,
        quality_preset.value if quality_preset else None,
        codec.value if codec != VideoCodec.auto else None,
        bitrate,
        resolution,
        frame_rate,
        use_async
    )
    
    # Handle async response
    if isinstance(result, dict) and "task_id" in result:
        return JSONResponse(content=result)
    
    # Handle sync response
    original_filename = video.filename or "video"
    base_name = original_filename.rsplit(".", 1)[0] if "." in original_filename else original_filename
    output_filename = f"{base_name}.{target_format.value}"
    
    # Determine content type
    content_type_map = {
        "mp4": "video/mp4",
        "mkv": "video/x-matroska",
        "webm": "video/webm",
        "avi": "video/x-msvideo",
        "mov": "video/quicktime",
        "wmv": "video/x-ms-wmv",
        "flv": "video/x-flv",
        "ogv": "video/ogg",
        "m4v": "video/x-m4v",
        "3gp": "video/3gpp"
    }
    
    content_type = content_type_map.get(target_format.value, "video/mp4")
    
    return StreamingResponse(
        result,
        media_type=content_type,
        headers={
            "Content-Disposition": f"attachment; filename={output_filename}",
            "X-Original-Format": video.content_type or "unknown",
            "X-Target-Format": target_format.value,
            "X-Codec": codec.value if codec != VideoCodec.auto else "auto",
            "X-Quality-Preset": quality_preset.value if quality_preset else "custom"
        }
    )


@video_router.post(
    "/batch-convert",
    summary="Batch convert multiple videos",
    description="Convert multiple videos at once with same settings"
)
async def batch_convert_videos(
    videos: List[UploadFile] = File(..., description="List of video files to convert"),
    target_format: VideoFormat = Form(..., description="Target format for all videos"),
    quality_preset: Optional[VideoQualityPreset] = Query(
        default=VideoQualityPreset.hd,
        description="Quality preset for all videos"
    ),
    codec: Optional[VideoCodec] = Query(
        default=VideoCodec.auto,
        description="Video codec to use"
    ),
    video_service: VideoService = Depends(get_video_service)
) -> JSONResponse:
    """
    Convert multiple videos in batch with progress tracking.
    
    **Features:**
    - Process multiple videos with same settings
    - Background processing with progress tracking
    - Detailed results for each video
    
    Returns task ID for tracking batch conversion progress.
    """
    result = await video_service.batch_convert_videos(
        videos, 
        target_format.value, 
        quality_preset.value if quality_preset else None,
        codec=codec.value if codec != VideoCodec.auto else None
    )
    
    return JSONResponse(content=result)


@video_router.post(
    "/extract-audio",
    summary="Extract audio from video",
    description="Extract audio track from video file in specified format",
    response_model=None
)
async def extract_audio_from_video(
    video: UploadFile = File(..., description="Video file to extract audio from"),
    audio_format: AudioFormat = Query(
        default=AudioFormat.mp3,
        description="Output audio format"
    ),
    audio_bitrate: Optional[str] = Query(
        default=None,
        description="Audio bitrate (e.g., '128k', '320k')"
    ),
    video_service: VideoService = Depends(get_video_service)
) -> Union[StreamingResponse, JSONResponse]:
    """
    Extract audio track from video file.
    
    **Features:**
    - Extract to multiple audio formats (MP3, AAC, WAV, OGG, FLAC)
    - Custom audio bitrate control
    - Preserves original audio quality when possible
    
    **Parameters:**
    - **video**: Video file with audio track
    - **audio_format**: Target audio format
    - **audio_bitrate**: Audio quality setting
    
    Returns extracted audio file as streaming response.
    """
    # Extract audio
    result = await video_service.extract_audio_from_video(
        video,
        audio_format.value,
        audio_bitrate
    )
    
    # Create output filename
    original_filename = video.filename or "video"
    base_name = original_filename.rsplit(".", 1)[0] if "." in original_filename else original_filename
    output_filename = f"{base_name}.{audio_format.value}"
    
    # Determine content type
    content_type_map = {
        "mp3": "audio/mpeg",
        "aac": "audio/aac",
        "wav": "audio/wav",
        "ogg": "audio/ogg",
        "flac": "audio/flac"
    }
    
    content_type = content_type_map.get(audio_format.value, "audio/mpeg")
    
    return StreamingResponse(
        result,
        media_type=content_type,
        headers={
            "Content-Disposition": f"attachment; filename={output_filename}",
            "X-Original-Format": video.content_type or "unknown",
            "X-Audio-Format": audio_format.value,
            "X-Audio-Bitrate": audio_bitrate or "default"
        }
    )


@video_router.post(
    "/thumbnail",
    summary="Generate video thumbnail",
    description="Generate thumbnail image from video at specified timestamp",
    response_model=None
)
async def generate_video_thumbnail(
    video: UploadFile = File(..., description="Video file to generate thumbnail from"),
    timestamp: float = Query(
        default=1.0,
        ge=0.0,
        le=3600.0,
        description="Time position for thumbnail (seconds)"
    ),
    width: int = Query(
        default=320,
        ge=64,
        le=1920,
        description="Thumbnail width"
    ),
    height: int = Query(
        default=240,
        ge=64,
        le=1080,
        description="Thumbnail height"
    ),
    image_format: str = Query(
        default="jpg",
        regex="^(jpg|jpeg|png|webp)$",
        description="Output image format"
    ),
    video_service: VideoService = Depends(get_video_service)
) -> Union[StreamingResponse, JSONResponse]:
    """
    Generate thumbnail from video at specified timestamp.
    
    **Features:**
    - Extract thumbnail at any time position
    - Custom dimensions and format
    - Multiple output formats (JPEG, PNG, WebP)
    
    **Parameters:**
    - **video**: Video file
    - **timestamp**: Time position in seconds
    - **width/height**: Thumbnail dimensions
    - **image_format**: Output format
    
    Returns thumbnail image as streaming response.
    """
    # Generate thumbnail
    result = await video_service.generate_thumbnail(
        video,
        timestamp,
        width,
        height,
        image_format
    )
    
    # Create output filename
    original_filename = video.filename or "video"
    base_name = original_filename.rsplit(".", 1)[0] if "." in original_filename else original_filename
    output_filename = f"{base_name}_thumbnail_{timestamp}s.{image_format}"
    
    # Determine content type
    content_type_map = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "webp": "image/webp"
    }
    
    content_type = content_type_map.get(image_format, "image/jpeg")
    
    return StreamingResponse(
        result,
        media_type=content_type,
        headers={
            "Content-Disposition": f"attachment; filename={output_filename}",
            "X-Original-Format": video.content_type or "unknown",
            "X-Timestamp": str(timestamp),
            "X-Dimensions": f"{width}x{height}",
            "X-Image-Format": image_format
        }
    )


@video_router.post(
    "/info",
    summary="Get video information and analysis",
    description="Analyze video properties, format, streams, and metadata"
)
async def get_video_info(
    video: UploadFile = File(..., description="Video file to analyze"),
    video_service: VideoService = Depends(get_video_service)
) -> JSONResponse:
    """
    Get comprehensive video information and analysis.
    
    **Analysis includes:**
    - Format and container information
    - Video stream properties (codec, resolution, fps, bitrate)
    - Audio stream properties (codec, sample rate, channels)
    - Duration and file size
    - Metadata and technical specifications
    
    Returns detailed video analysis data.
    """
    result = await video_service.get_video_info(video)
    return JSONResponse(content=result)


@video_router.get(
    "/task/{task_id}",
    summary="Get task status",
    description="Check status of background video processing task"
)
async def get_video_task_status(task_id: str) -> JSONResponse:
    """
    Check the status of a background video processing task.
    
    **Task Types:**
    - Video conversion
    - Batch conversion
    - Audio extraction
    - Thumbnail generation
    
    Returns current task status, progress, and results when complete.
    """
    try:
        from celery.result import AsyncResult
        from app.celery_app import celery_app
        
        # Get task result
        task_result = AsyncResult(task_id, app=celery_app)
        
        if task_result.state == 'PENDING':
            response = {
                'task_id': task_id,
                'state': task_result.state,
                'status': 'Task is waiting to be processed'
            }
        elif task_result.state == 'PROGRESS':
            response = {
                'task_id': task_id,
                'state': task_result.state,
                'progress': task_result.info.get('progress', 0),
                'status': task_result.info.get('status', 'Processing')
            }
            
            # Add additional info for batch tasks
            if 'current' in task_result.info:
                response.update({
                    'current': task_result.info['current'],
                    'total': task_result.info['total']
                })
        elif task_result.state == 'SUCCESS':
            response = {
                'task_id': task_id,
                'state': task_result.state,
                'result': task_result.result
            }
        else:  # FAILURE
            response = {
                'task_id': task_id,
                'state': task_result.state,
                'error': str(task_result.info)
            }
        
        return JSONResponse(content=response)
    
    except ImportError:
        return JSONResponse(
            content={
                "error": "Task system not available",
                "task_id": task_id
            },
            status_code=503
        )
    except Exception as e:
        return JSONResponse(
            content={
                "error": f"Failed to get task status: {str(e)}",
                "task_id": task_id
            },
            status_code=500
        )


# Keep backward compatibility
videoRouter = video_router