"""
Enhanced video processing service with comprehensive format support and advanced features.
"""

import io
import os
import tempfile
import asyncio
import json
import subprocess
from typing import BinaryIO, Dict, Any, Optional, List, Tuple, Union
from concurrent.futures import ThreadPoolExecutor
import logging

from fastapi import Depends, UploadFile

from app.core.config import AppConfig, get_config
from app.exceptions import ImageProcessingError
from app.services.base import BaseService
from app.services.file_validation import (
    FileValidationService,
    get_file_validation_service,
)
from app.helpers.constants import (
    VIDEO_FORMATS,
    SUPPORTED_VIDEO_OUTPUT_FORMATS,
    VIDEO_QUALITY_PRESETS,
    VIDEO_FRAME_RATES,
    VIDEO_EFFECTS,
    VIDEO_CODECS,
)

# Import video processing libraries with fallbacks
VIDEO_LIBRARIES_AVAILABLE = False
FFMPEG_AVAILABLE = False

try:
    import ffmpeg

    FFMPEG_AVAILABLE = True
    VIDEO_LIBRARIES_AVAILABLE = True
except ImportError:
    ffmpeg = None

try:
    import cv2

    CV2_AVAILABLE = True
except ImportError:
    cv2 = None
    CV2_AVAILABLE = False

try:
    import subprocess

    SUBPROCESS_AVAILABLE = True
except ImportError:
    SUBPROCESS_AVAILABLE = False

logger = logging.getLogger(__name__)


class VideoProcessingError(Exception):
    """Custom exception for video processing errors."""

    pass


class VideoService(BaseService):
    """Enhanced service for video processing operations with advanced features."""

    def __init__(self, config: AppConfig, validation_service: FileValidationService):
        super().__init__(config)
        self.validation_service = validation_service
        self.supported_formats = set(SUPPORTED_VIDEO_OUTPUT_FORMATS)
        self.executor = ThreadPoolExecutor(
            max_workers=2
        )  # Limited for video processing

        # Check for FFmpeg installation
        if not self._check_ffmpeg():
            logger.warning(
                "FFmpeg not found. Video processing capabilities will be limited."
            )

    def _check_ffmpeg(self) -> bool:
        """Check if FFmpeg is available."""
        try:
            subprocess.run(
                ["ffmpeg", "-version"], capture_output=True, check=True, timeout=5
            )
            return True
        except (
            subprocess.CalledProcessError,
            FileNotFoundError,
            subprocess.TimeoutExpired,
        ):
            return False

    async def _validate_video_file(self, video_file: UploadFile) -> bytes:
        """
        Validate video file and return its content.

        Args:
            video_file: Uploaded video file

        Returns:
            File content as bytes

        Raises:
            VideoProcessingError: If validation fails
        """
        try:
            # Validate filename
            filename = self.validation_service.validate_filename(
                video_file.filename or ""
            )

            # Read file content for validation
            content = await video_file.read()
            await video_file.seek(0)  # Reset file pointer for later use

            # Get file type and validate size
            _, file_type = self.validation_service.get_file_type(filename)
            if file_type != "video":
                raise VideoProcessingError(
                    f"Invalid file type: {file_type}. Expected video file."
                )

            self.validation_service.validate_file_size(len(content), file_type)

            return content

        except Exception as e:
            if isinstance(e, VideoProcessingError):
                raise
            raise VideoProcessingError(f"File validation failed: {str(e)}")

    async def convert_video_format(
        self,
        video_file: UploadFile,
        target_format: str,
        quality_preset: Optional[str] = None,
        codec: Optional[str] = None,
        bitrate: Optional[str] = None,
        resolution: Optional[Tuple[int, int]] = None,
        frame_rate: Optional[float] = None,
        use_async: bool = False,
        **kwargs,
    ) -> Union[BinaryIO, Dict[str, Any]]:
        """
        Convert video to specified format with advanced options.

        Args:
            video_file: Input video file
            target_format: Target output format
            quality_preset: Quality preset (mobile, sd, hd, full_hd, 4k, etc.)
            codec: Video codec (h264, h265, vp9, etc.)
            bitrate: Video bitrate (e.g., "1000k", "5M")
            resolution: Target resolution as (width, height) tuple
            frame_rate: Target frame rate
            use_async: Whether to process asynchronously
            **kwargs: Additional FFmpeg parameters

        Returns:
            Video stream or task information for async processing
        """
        if not VIDEO_LIBRARIES_AVAILABLE:
            raise VideoProcessingError("Video processing libraries not available")

        # Validate input file
        await self._validate_video_file(video_file)

        if target_format not in self.supported_formats:
            raise VideoProcessingError(f"Unsupported target format: {target_format}")

        if use_async:
            # For async processing, we'll use Celery tasks
            try:
                from app.tasks.video_tasks import convert_video_task

                task = convert_video_task.delay(
                    await video_file.read(),
                    video_file.filename,
                    target_format,
                    quality_preset,
                    codec,
                    bitrate,
                    resolution,
                    frame_rate,
                    kwargs,
                )
                return {"task_id": task.id, "status": "processing"}
            except ImportError:
                logger.warning("Celery not available, falling back to sync processing")

        # Synchronous processing
        return await self._convert_video_sync(
            video_file,
            target_format,
            quality_preset,
            codec,
            bitrate,
            resolution,
            frame_rate,
            **kwargs,
        )

    async def _convert_video_sync(
        self,
        video_file: UploadFile,
        target_format: str,
        quality_preset: Optional[str],
        codec: Optional[str],
        bitrate: Optional[str],
        resolution: Optional[Tuple[int, int]],
        frame_rate: Optional[float],
        **kwargs,
    ) -> BinaryIO:
        """Synchronous video conversion using FFmpeg."""

        # Read input file (reset to start in case it was read during validation)
        await video_file.seek(0)
        input_data = await video_file.read()

        with tempfile.NamedTemporaryFile(
            delete=False, suffix=f".{video_file.filename.split('.')[-1]}"
        ) as input_temp:
            input_temp.write(input_data)
            input_temp.flush()
            input_path = input_temp.name

        with tempfile.NamedTemporaryFile(
            delete=False, suffix=f".{target_format}"
        ) as output_temp:
            output_path = output_temp.name

        try:
            # Build FFmpeg command
            input_stream = ffmpeg.input(input_path)

            # Apply quality preset if specified
            if quality_preset and quality_preset in VIDEO_QUALITY_PRESETS:
                preset = VIDEO_QUALITY_PRESETS[quality_preset]
                if not resolution:
                    resolution = (preset["width"], preset["height"])
                if not bitrate:
                    bitrate = preset["bitrate"]

            # Apply video filters
            output_args = {}

            # Set codec
            if codec:
                if codec in ["h264", "libx264"]:
                    output_args["vcodec"] = "libx264"
                elif codec in ["h265", "hevc", "libx265"]:
                    output_args["vcodec"] = "libx265"
                elif codec in ["vp8", "libvpx"]:
                    output_args["vcodec"] = "libvpx"
                elif codec in ["vp9", "libvpx-vp9"]:
                    output_args["vcodec"] = "libvpx-vp9"
                elif codec in ["av1", "libaom-av1"]:
                    output_args["vcodec"] = "libaom-av1"
            else:
                # Default codecs for formats
                if target_format == "mp4":
                    output_args["vcodec"] = "libx264"
                elif target_format == "webm":
                    output_args["vcodec"] = "libvpx-vp9"
                elif target_format == "mkv":
                    output_args["vcodec"] = "libx264"

            # Set bitrate
            if bitrate:
                output_args["video_bitrate"] = bitrate

            # Set frame rate
            if frame_rate:
                output_args["r"] = frame_rate

            # Apply resolution scaling
            if resolution:
                width, height = resolution
                input_stream = input_stream.filter("scale", width, height)

            # Add additional arguments from kwargs
            output_args.update(kwargs)

            # Run FFmpeg conversion
            output_stream = ffmpeg.output(input_stream, output_path, **output_args)
            ffmpeg.run(output_stream, overwrite_output=True, quiet=True)

            # Read converted video
            with open(output_path, "rb") as f:
                converted_data = f.read()

            return io.BytesIO(converted_data)

        finally:
            # Cleanup temporary files
            try:
                os.unlink(input_path)
                os.unlink(output_path)
            except OSError:
                pass

    async def extract_audio_from_video(
        self,
        video_file: UploadFile,
        audio_format: str = "mp3",
        audio_bitrate: Optional[str] = None,
    ) -> BinaryIO:
        """Extract audio track from video file."""

        if not VIDEO_LIBRARIES_AVAILABLE:
            raise VideoProcessingError("Video processing libraries not available")

        # Validate input file and get content
        input_data = await self._validate_video_file(video_file)

        with tempfile.NamedTemporaryFile(
            delete=False, suffix=f".{video_file.filename.split('.')[-1]}"
        ) as input_temp:
            input_temp.write(input_data)
            input_temp.flush()
            input_path = input_temp.name

        with tempfile.NamedTemporaryFile(
            delete=False, suffix=f".{audio_format}"
        ) as output_temp:
            output_path = output_temp.name

        try:
            # Build FFmpeg command for audio extraction
            input_stream = ffmpeg.input(input_path)

            output_args = {
                "vn": None,  # No video
                "acodec": "libmp3lame" if audio_format == "mp3" else "copy",
            }

            if audio_bitrate:
                output_args["audio_bitrate"] = audio_bitrate

            # Run FFmpeg
            output_stream = ffmpeg.output(input_stream, output_path, **output_args)
            ffmpeg.run(output_stream, overwrite_output=True, quiet=True)

            # Read extracted audio
            with open(output_path, "rb") as f:
                audio_data = f.read()

            return io.BytesIO(audio_data)

        finally:
            # Cleanup
            try:
                os.unlink(input_path)
                os.unlink(output_path)
            except OSError:
                pass

    async def generate_thumbnail(
        self,
        video_file: UploadFile,
        timestamp: float = 1.0,
        width: int = 320,
        height: int = 240,
        image_format: str = "jpg",
    ) -> BinaryIO:
        """Generate thumbnail from video at specified timestamp."""

        if not VIDEO_LIBRARIES_AVAILABLE:
            raise VideoProcessingError("Video processing libraries not available")

        # Validate input file and get content
        input_data = await self._validate_video_file(video_file)

        with tempfile.NamedTemporaryFile(
            delete=False, suffix=f".{video_file.filename.split('.')[-1]}"
        ) as input_temp:
            input_temp.write(input_data)
            input_temp.flush()
            input_path = input_temp.name

        with tempfile.NamedTemporaryFile(
            delete=False, suffix=f".{image_format}"
        ) as output_temp:
            output_path = output_temp.name

        try:
            # Generate thumbnail using FFmpeg
            input_stream = ffmpeg.input(input_path, ss=timestamp)
            output_stream = ffmpeg.output(
                input_stream, output_path, vframes=1, s=f"{width}x{height}"
            )
            ffmpeg.run(output_stream, overwrite_output=True, quiet=True)

            # Read thumbnail
            with open(output_path, "rb") as f:
                thumbnail_data = f.read()

            return io.BytesIO(thumbnail_data)

        finally:
            # Cleanup
            try:
                os.unlink(input_path)
                os.unlink(output_path)
            except OSError:
                pass

    async def get_video_info(self, video_file: UploadFile) -> Dict[str, Any]:
        """Get comprehensive video information and metadata."""

        if not VIDEO_LIBRARIES_AVAILABLE:
            raise VideoProcessingError("Video processing libraries not available")

        # Validate input file and get content
        input_data = await self._validate_video_file(video_file)

        with tempfile.NamedTemporaryFile(
            delete=False, suffix=f".{video_file.filename.split('.')[-1]}"
        ) as input_temp:
            input_temp.write(input_data)
            input_temp.flush()
            input_path = input_temp.name

        try:
            # Get video info using FFprobe
            probe = ffmpeg.probe(input_path)

            # Extract video stream info
            video_stream = next(
                (
                    stream
                    for stream in probe["streams"]
                    if stream["codec_type"] == "video"
                ),
                None,
            )
            audio_stream = next(
                (
                    stream
                    for stream in probe["streams"]
                    if stream["codec_type"] == "audio"
                ),
                None,
            )

            info = {
                "filename": video_file.filename,
                "format": probe["format"]["format_name"],
                "duration": float(probe["format"]["duration"]),
                "size": int(probe["format"]["size"]),
                "bitrate": int(probe["format"]["bit_rate"]),
                "streams": len(probe["streams"]),
            }

            if video_stream:
                info["video"] = {
                    "codec": video_stream.get("codec_name"),
                    "width": video_stream.get("width"),
                    "height": video_stream.get("height"),
                    "fps": eval(video_stream.get("r_frame_rate", "0/1")),
                    "aspect_ratio": video_stream.get("display_aspect_ratio"),
                    "pixel_format": video_stream.get("pix_fmt"),
                    "bitrate": (
                        int(video_stream.get("bit_rate", 0))
                        if video_stream.get("bit_rate")
                        else None
                    ),
                }

            if audio_stream:
                info["audio"] = {
                    "codec": audio_stream.get("codec_name"),
                    "sample_rate": int(audio_stream.get("sample_rate", 0)),
                    "channels": audio_stream.get("channels"),
                    "bitrate": (
                        int(audio_stream.get("bit_rate", 0))
                        if audio_stream.get("bit_rate")
                        else None
                    ),
                }

            return info

        finally:
            # Cleanup
            try:
                os.unlink(input_path)
            except OSError:
                pass

    async def batch_convert_videos(
        self,
        video_files: List[UploadFile],
        target_format: str,
        quality_preset: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Convert multiple videos in batch with progress tracking."""

        try:
            from app.tasks.video_tasks import batch_convert_videos_task

            # Prepare video data for task
            videos_data = []
            for video_file in video_files:
                videos_data.append(
                    {"data": await video_file.read(), "filename": video_file.filename}
                )

            # Submit batch conversion task
            task = batch_convert_videos_task.delay(
                videos_data, target_format, quality_preset, kwargs
            )

            return {
                "task_id": task.id,
                "status": "processing",
                "total_videos": len(video_files),
                "message": f"Batch conversion of {len(video_files)} videos started",
            }

        except ImportError:
            raise VideoProcessingError("Batch processing requires Celery worker")


# Dependency function
def get_video_service(
    config: AppConfig = Depends(get_config),
    validation_service: FileValidationService = Depends(get_file_validation_service),
) -> VideoService:
    """Dependency to get VideoService instance."""
    return VideoService(config, validation_service)
