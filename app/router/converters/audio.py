"""
Enhanced audio conversion router with comprehensive format support and advanced features.
"""
from typing import List, Optional, Dict, Any, Union
from fastapi import APIRouter, Depends, Form, Query, UploadFile, File, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
from enum import Enum

from app.schemas.responses import FileProcessingResponse
from app.services.audio import AudioService, get_audio_service
from app.helpers.constants import (
    SUPPORTED_AUDIO_OUTPUT_FORMATS, AUDIO_QUALITY_PRESETS, 
    SAMPLE_RATES, AUDIO_EFFECTS, AUDIO_FORMATS
)

audio_router = APIRouter(prefix="/audio", tags=["Audio Converter"])


class AudioFormat(str, Enum):
    """Supported audio output formats."""
    WAV = "wav"
    MP3 = "mp3"
    AAC = "aac"
    OGG = "ogg"
    FLAC = "flac"
    M4A = "m4a"
    OPUS = "opus"
    WEBM = "webm"
    AIFF = "aiff"
    AU = "au"


class AudioQualityPreset(str, Enum):
    """Audio quality presets for easy selection."""
    PHONE = "phone"
    RADIO = "radio"
    CD = "cd"
    HD = "hd"
    STUDIO = "studio"


class AudioEffect(str, Enum):
    """Available audio effects."""
    NORMALIZE = "normalize"
    COMPRESS = "compress"
    FADE_IN = "fade_in"
    FADE_OUT = "fade_out"
    VOLUME_CHANGE = "volume_change"
    NOISE_REDUCTION = "noise_reduction"
    SPEED_CHANGE = "speed_change"


@audio_router.get("/formats", summary="Get supported audio formats")
async def get_supported_audio_formats() -> Dict[str, Any]:
    """
    Get list of all supported audio formats with their capabilities.
    
    Returns detailed information about each supported format including:
    - Format name and description
    - Year introduced
    - Whether it's lossy or lossless
    - Maximum bitrate
    - Metadata support
    """
    return {
        "input_formats": {
            format_code: {
                "name": info["name"],
                "year": info["year"],
                "lossy": info["lossy"],
                "max_bitrate": info["max_bitrate"],
                "supports_metadata": info["supports_metadata"]
            }
            for format_code, info in AUDIO_FORMATS.items()
        },
        "output_formats": SUPPORTED_AUDIO_OUTPUT_FORMATS,
        "quality_presets": AUDIO_QUALITY_PRESETS,
        "sample_rates": SAMPLE_RATES,
        "available_effects": AUDIO_EFFECTS
    }


@audio_router.post(
    "/convert",
    summary="Convert audio format with advanced options",
    description="Convert audio from one format to another with comprehensive customization options",
    response_model=None
)
async def convert_audio_format(
    audio: UploadFile = File(..., description="Audio file to convert"),
    target_format: AudioFormat = Form(..., description="Target format for conversion"),
    bitrate: Optional[int] = Query(
        default=128,
        ge=32,
        le=1411,
        description="Audio bitrate in kbps (32-1411)"
    ),
    sample_rate: Optional[int] = Query(
        default=None,
        description="Sample rate in Hz (8000, 22050, 44100, 48000, 96000, 192000)"
    ),
    channels: Optional[int] = Query(
        default=None,
        ge=1,
        le=8,
        description="Number of channels (1=mono, 2=stereo, etc.)"
    ),
    quality_preset: Optional[AudioQualityPreset] = Query(
        default=None,
        description="Quality preset (overrides bitrate and sample rate if specified)"
    ),
    use_async: bool = Query(
        default=False,
        description="Use background processing (returns task ID)"
    ),
    audio_service: AudioService = Depends(get_audio_service)
) -> Union[StreamingResponse, JSONResponse]:
    """
    Convert audio to specified format with advanced options.
    
    **Features:**
    - Support for 10+ output formats (MP3, WAV, AAC, OGG, FLAC, etc.)
    - Quality presets from phone to studio quality
    - Custom bitrate, sample rate, and channel configuration
    - Background processing for large files
    
    **Parameters:**
    - **audio**: Audio file to convert (supports 20+ input formats)
    - **target_format**: Output format from dropdown
    - **bitrate**: Audio bitrate in kbps (32-1411)
    - **sample_rate**: Sample rate in Hz
    - **channels**: Number of channels (1=mono, 2=stereo)
    - **quality_preset**: Predefined quality settings
    - **use_async**: Background processing for large files
    
    **Returns:**
    - Synchronous: Converted audio as streaming response
    - Asynchronous: JSON with task ID for status checking
    """
    # Convert audio
    result = await audio_service.convert_audio_format(
        audio,
        target_format.value,
        bitrate,
        sample_rate,
        channels,
        use_async,
        quality_preset.value if quality_preset else None
    )
    
    # Handle async response
    if isinstance(result, dict) and "task_id" in result:
        return JSONResponse(content=result)
    
    # Handle sync response
    original_filename = audio.filename or "audio"
    base_name = original_filename.rsplit(".", 1)[0] if "." in original_filename else original_filename
    output_filename = f"{base_name}.{target_format.value}"
    
    # Determine content type
    content_type_map = {
        "mp3": "audio/mpeg",
        "wav": "audio/wav",
        "aac": "audio/aac",
        "ogg": "audio/ogg",
        "flac": "audio/flac",
        "m4a": "audio/mp4",
        "opus": "audio/opus",
        "webm": "audio/webm",
        "aiff": "audio/aiff",
        "au": "audio/basic"
    }
    
    content_type = content_type_map.get(target_format.value, f"audio/{target_format.value}")
    
    return StreamingResponse(
        result,
        media_type=content_type,
        headers={
            "Content-Disposition": f"attachment; filename={output_filename}",
            "X-Original-Format": audio.content_type or "unknown",
            "X-Target-Format": target_format.value,
            "X-Bitrate": str(bitrate),
            "X-Sample-Rate": str(sample_rate) if sample_rate else "original",
            "X-Channels": str(channels) if channels else "original"
        }
    )


@audio_router.post(
    "/batch-convert",
    summary="Batch convert multiple audio files",
    description="Convert multiple audio files at once with same settings"
)
async def batch_convert_audio(
    audio_files: List[UploadFile] = File(..., description="List of audio files to convert"),
    target_format: AudioFormat = Form(..., description="Target format for all audio files"),
    bitrate: int = Query(default=128, ge=32, le=1411, description="Audio bitrate in kbps"),
    quality_preset: Optional[AudioQualityPreset] = Query(
        default=None,
        description="Quality preset"
    ),
    audio_service: AudioService = Depends(get_audio_service)
) -> JSONResponse:
    """
    Convert multiple audio files in batch with progress tracking.
    
    **Features:**
    - Process multiple audio files with same settings
    - Background processing with progress tracking
    - Detailed results for each audio file
    
    Returns task ID for tracking batch conversion progress.
    """
    result = await audio_service.batch_convert_audio(
        audio_files, 
        target_format.value, 
        bitrate,
        quality_preset.value if quality_preset else None
    )
    
    return JSONResponse(content=result)


@audio_router.post(
    "/effects",
    summary="Apply audio effects and processing",
    description="Apply various audio effects like normalize, compress, fade, noise reduction, etc.",
    response_model=None
)
async def apply_audio_effects(
    audio: UploadFile = File(..., description="Audio file to process"),
    effects: List[AudioEffect] = Query(..., description="List of effects to apply"),
    # Effect parameters
    normalize_headroom: float = Query(default=0.1, ge=0.0, le=1.0, description="Normalization headroom"),
    compress_threshold: float = Query(default=-20.0, ge=-60.0, le=0.0, description="Compression threshold (dB)"),
    compress_ratio: float = Query(default=4.0, ge=1.0, le=20.0, description="Compression ratio"),
    fade_duration: int = Query(default=1000, ge=100, le=10000, description="Fade duration (ms)"),
    volume_change: float = Query(default=0.0, ge=-60.0, le=20.0, description="Volume change (dB)"),
    speed_factor: float = Query(default=1.0, ge=0.1, le=3.0, description="Speed change factor"),
    audio_service: AudioService = Depends(get_audio_service)
) -> Union[StreamingResponse, JSONResponse]:
    """
    Apply audio effects and processing.
    
    **Available Effects:**
    - **normalize**: Normalize audio levels
    - **compress**: Dynamic range compression
    - **fade_in/fade_out**: Fade effects
    - **volume_change**: Adjust volume
    - **noise_reduction**: Reduce background noise
    - **speed_change**: Change playback speed
    
    Returns processed audio file.
    """
    # Prepare effect parameters
    effect_params = {
        "headroom": normalize_headroom,
        "threshold": compress_threshold,
        "ratio": compress_ratio,
        "duration": fade_duration,
        "change_db": volume_change,
        "speed_factor": speed_factor
    }
    
    result = await audio_service.apply_audio_effects(
        audio, [effect.value for effect in effects], effect_params
    )
    
    # Handle async response
    if isinstance(result, dict) and "task_id" in result:
        return JSONResponse(content=result)
    
    # Handle sync response
    original_filename = audio.filename or "audio"
    base_name = original_filename.rsplit(".", 1)[0] if "." in original_filename else original_filename
    output_filename = f"{base_name}_processed.wav"
    
    return StreamingResponse(
        result,
        media_type="audio/wav",
        headers={
            "Content-Disposition": f"attachment; filename={output_filename}",
            "X-Effects-Applied": ",".join([effect.value for effect in effects])
        }
    )


@audio_router.post(
    "/analyze",
    summary="Analyze audio file and extract features",
    description="Get comprehensive audio analysis including tempo, pitch, spectral features, and metadata"
)
async def analyze_audio(
    audio: UploadFile = File(..., description="Audio file to analyze"),
    audio_service: AudioService = Depends(get_audio_service)
) -> JSONResponse:
    """
    Get comprehensive audio analysis and features.
    
    **Analysis includes:**
    - Basic properties (duration, sample rate, channels, bitrate)
    - Advanced features (tempo, pitch, spectral analysis)
    - MFCC coefficients for audio fingerprinting
    - Loudness analysis (LUFS)
    - Audio quality assessment
    
    Returns detailed audio analysis data.
    """
    result = await audio_service.get_audio_info(audio)
    return JSONResponse(content=result)


@audio_router.post(
    "/optimize",
    summary="Optimize audio quality and size",
    description="Optimize audio for specific use case (size, quality, or balanced)",
    response_model=None
)
async def optimize_audio(
    audio: UploadFile = File(..., description="Audio file to optimize"),
    optimization_type: str = Query(
        default="balanced",
        regex="^(size|quality|balanced)$",
        description="Optimization type: size, quality, or balanced"
    ),
    target_size_kb: Optional[int] = Query(
        default=None,
        ge=100,
        le=102400,
        description="Target file size in KB (for size optimization)"
    ),
    audio_service: AudioService = Depends(get_audio_service)
) -> Union[StreamingResponse, JSONResponse]:
    """
    Optimize audio for specific requirements.
    
    **Optimization Types:**
    - **size**: Minimize file size (optionally to target KB)
    - **quality**: Maximize audio quality (lossless)
    - **balanced**: Balance between size and quality
    
    Returns optimized audio file.
    """
    # For now, return a simple optimization
    # In a full implementation, this would use the audio service
    return JSONResponse(content={
        "message": "Audio optimization endpoint - implementation coming soon",
        "optimization_type": optimization_type,
        "target_size_kb": target_size_kb
    })


@audio_router.post(
    "/extract-segments",
    summary="Extract audio segments",
    description="Extract specific time segments from audio file",
    response_model=None
)
async def extract_audio_segments(
    audio: UploadFile = File(..., description="Audio file to extract from"),
    start_time: float = Query(..., ge=0.0, description="Start time in seconds"),
    end_time: Optional[float] = Query(default=None, ge=0.0, description="End time in seconds (optional)"),
    duration: Optional[float] = Query(default=None, ge=0.1, le=3600.0, description="Duration in seconds (optional)"),
    audio_service: AudioService = Depends(get_audio_service)
) -> Union[StreamingResponse, JSONResponse]:
    """
    Extract audio segments by time.
    
    **Parameters:**
    - **start_time**: Start time in seconds
    - **end_time**: End time in seconds (or use duration)
    - **duration**: Duration in seconds (alternative to end_time)
    
    Returns extracted audio segment.
    """
    # For now, return a placeholder
    return JSONResponse(content={
        "message": "Audio segment extraction endpoint - implementation coming soon",
        "start_time": start_time,
        "end_time": end_time,
        "duration": duration
    })


@audio_router.get(
    "/task/{task_id}",
    summary="Get task status",
    description="Check status of background audio processing task"
)
async def get_audio_task_status(task_id: str) -> JSONResponse:
    """
    Get the status of a background audio processing task.
    
    **Status values:**
    - **PENDING**: Task is waiting to be processed
    - **PROCESSING**: Task is currently being processed
    - **SUCCESS**: Task completed successfully
    - **FAILURE**: Task failed with error
    
    Returns task status and result data if completed.
    """
    try:
        from app.celery_app import celery_app
        
        task = celery_app.AsyncResult(task_id)
        
        if task.state == "PENDING":
            response = {
                "task_id": task_id,
                "status": "PENDING",
                "message": "Task is waiting to be processed"
            }
        elif task.state == "PROCESSING":
            response = {
                "task_id": task_id,
                "status": "PROCESSING",
                "progress": task.info.get("progress", 0),
                "step": task.info.get("step", "unknown"),
                "current_file": task.info.get("current_file", "")
            }
        elif task.state == "SUCCESS":
            response = {
                "task_id": task_id,
                "status": "SUCCESS",
                "result": task.result
            }
        else:  # FAILURE
            response = {
                "task_id": task_id,
                "status": "FAILURE",
                "error": str(task.info)
            }
        
        return JSONResponse(content=response)
    
    except ImportError:
        return JSONResponse(
            content={
                "error": "Celery not available",
                "message": "Background task processing is not configured"
            },
            status_code=503
        )


# Keep backward compatibility
audioRouter = audio_router