"""
Video processing tasks for Celery background processing.
"""

import io
import os
import tempfile
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from celery import shared_task

logger = logging.getLogger(__name__)

# Import video processing libraries with fallbacks
try:
    import ffmpeg

    FFMPEG_AVAILABLE = True
except ImportError:
    ffmpeg = None
    FFMPEG_AVAILABLE = False


class VideoTaskError(Exception):
    """Custom exception for video task errors."""

    pass


@shared_task(bind=True, name="video.convert")
def convert_video_task(
    self,
    video_data: bytes,
    filename: str,
    target_format: str,
    quality_preset: Optional[str] = None,
    codec: Optional[str] = None,
    bitrate: Optional[str] = None,
    resolution: Optional[Tuple[int, int]] = None,
    frame_rate: Optional[float] = None,
    extra_args: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Convert video format in background task.

    Args:
        video_data: Input video data as bytes
        filename: Original filename
        target_format: Target output format
        quality_preset: Quality preset name
        codec: Video codec to use
        bitrate: Video bitrate
        resolution: Target resolution (width, height)
        frame_rate: Target frame rate
        extra_args: Additional FFmpeg arguments

    Returns:
        Task result with converted video data or error information
    """
    try:
        if not FFMPEG_AVAILABLE:
            raise VideoTaskError("FFmpeg not available for video processing")

        # Update task progress
        self.update_state(
            state="PROGRESS", meta={"progress": 0, "status": "Starting conversion"}
        )

        # Create temporary files
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=f".{filename.split('.')[-1]}"
        ) as input_temp:
            input_temp.write(video_data)
            input_temp.flush()
            input_path = input_temp.name

        with tempfile.NamedTemporaryFile(
            delete=False, suffix=f".{target_format}"
        ) as output_temp:
            output_path = output_temp.name

        try:
            # Update progress
            self.update_state(
                state="PROGRESS", meta={"progress": 20, "status": "Processing video"}
            )

            # Build FFmpeg command
            input_stream = ffmpeg.input(input_path)

            # Apply quality preset if specified
            from app.helpers.constants import VIDEO_QUALITY_PRESETS

            if quality_preset and quality_preset in VIDEO_QUALITY_PRESETS:
                preset = VIDEO_QUALITY_PRESETS[quality_preset]
                if not resolution:
                    resolution = (preset["width"], preset["height"])
                if not bitrate:
                    bitrate = preset["bitrate"]

            # Build output arguments
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

            # Set other parameters
            if bitrate:
                output_args["video_bitrate"] = bitrate
            if frame_rate:
                output_args["r"] = frame_rate

            # Apply resolution scaling
            if resolution:
                width, height = resolution
                input_stream = input_stream.filter("scale", width, height)

            # Add extra arguments
            if extra_args:
                output_args.update(extra_args)

            # Update progress
            self.update_state(
                state="PROGRESS", meta={"progress": 50, "status": "Converting video"}
            )

            # Run conversion
            output_stream = ffmpeg.output(input_stream, output_path, **output_args)
            ffmpeg.run(output_stream, overwrite_output=True, quiet=True)

            # Update progress
            self.update_state(
                state="PROGRESS", meta={"progress": 90, "status": "Finalizing"}
            )

            # Read converted video
            with open(output_path, "rb") as f:
                converted_data = f.read()

            # Get file size for statistics
            output_size = len(converted_data)
            input_size = len(video_data)
            compression_ratio = (
                (1 - output_size / input_size) * 100 if input_size > 0 else 0
            )

            return {
                "status": "SUCCESS",
                "video_data": converted_data,
                "original_filename": filename,
                "output_format": target_format,
                "input_size": input_size,
                "output_size": output_size,
                "compression_ratio": compression_ratio,
                "codec": codec or output_args.get("vcodec", "default"),
                "resolution": resolution,
                "bitrate": bitrate,
            }

        finally:
            # Cleanup temporary files
            try:
                os.unlink(input_path)
                os.unlink(output_path)
            except OSError:
                pass

    except Exception as e:
        logger.error(f"Video conversion task failed: {str(e)}")
        return {"status": "FAILURE", "error": str(e), "original_filename": filename}


@shared_task(bind=True, name="video.batch_convert")
def batch_convert_videos_task(
    self,
    videos_data: List[Dict[str, Any]],
    target_format: str,
    quality_preset: Optional[str] = None,
    extra_args: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Convert multiple videos in batch.

    Args:
        videos_data: List of video data dictionaries with 'data' and 'filename'
        target_format: Target output format
        quality_preset: Quality preset name
        extra_args: Additional conversion arguments

    Returns:
        Batch conversion results
    """
    try:
        total_videos = len(videos_data)
        results = []
        successful_conversions = 0
        failed_conversions = 0

        # Update initial progress
        self.update_state(
            state="PROGRESS",
            meta={
                "progress": 0,
                "current": 0,
                "total": total_videos,
                "status": "Starting batch conversion",
            },
        )

        for i, video_info in enumerate(videos_data):
            try:
                # Update progress
                progress = int((i / total_videos) * 100)
                self.update_state(
                    state="PROGRESS",
                    meta={
                        "progress": progress,
                        "current": i + 1,
                        "total": total_videos,
                        "status": f'Converting {video_info["filename"]}',
                    },
                )

                # Convert individual video using the convert task logic
                result = convert_video_task.apply(
                    args=[
                        video_info["data"],
                        video_info["filename"],
                        target_format,
                        quality_preset,
                        None,  # codec
                        None,  # bitrate
                        None,  # resolution
                        None,  # frame_rate
                        extra_args,
                    ]
                ).get()

                if result.get("status") == "SUCCESS":
                    successful_conversions += 1
                else:
                    failed_conversions += 1

                results.append(result)

            except Exception as e:
                logger.error(
                    f"Error converting video {video_info['filename']}: {str(e)}"
                )
                failed_conversions += 1
                results.append(
                    {
                        "status": "FAILURE",
                        "error": str(e),
                        "original_filename": video_info["filename"],
                    }
                )

        # Final result
        return {
            "status": "COMPLETED",
            "total_videos": total_videos,
            "successful_conversions": successful_conversions,
            "failed_conversions": failed_conversions,
            "target_format": target_format,
            "quality_preset": quality_preset,
            "results": results,
        }

    except Exception as e:
        logger.error(f"Batch video conversion task failed: {str(e)}")
        return {"status": "FAILURE", "error": str(e), "total_videos": len(videos_data)}


@shared_task(bind=True, name="video.extract_audio")
def extract_audio_task(
    self,
    video_data: bytes,
    filename: str,
    audio_format: str = "mp3",
    audio_bitrate: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Extract audio from video in background task.

    Args:
        video_data: Input video data as bytes
        filename: Original filename
        audio_format: Output audio format
        audio_bitrate: Audio bitrate

    Returns:
        Task result with extracted audio data
    """
    try:
        if not FFMPEG_AVAILABLE:
            raise VideoTaskError("FFmpeg not available for audio extraction")

        # Update task progress
        self.update_state(
            state="PROGRESS",
            meta={"progress": 0, "status": "Starting audio extraction"},
        )

        # Create temporary files
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=f".{filename.split('.')[-1]}"
        ) as input_temp:
            input_temp.write(video_data)
            input_temp.flush()
            input_path = input_temp.name

        with tempfile.NamedTemporaryFile(
            delete=False, suffix=f".{audio_format}"
        ) as output_temp:
            output_path = output_temp.name

        try:
            # Update progress
            self.update_state(
                state="PROGRESS", meta={"progress": 50, "status": "Extracting audio"}
            )

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

            # Update progress
            self.update_state(
                state="PROGRESS", meta={"progress": 90, "status": "Finalizing"}
            )

            # Read extracted audio
            with open(output_path, "rb") as f:
                audio_data = f.read()

            return {
                "status": "SUCCESS",
                "audio_data": audio_data,
                "original_filename": filename,
                "audio_format": audio_format,
                "audio_bitrate": audio_bitrate,
                "output_size": len(audio_data),
            }

        finally:
            # Cleanup temporary files
            try:
                os.unlink(input_path)
                os.unlink(output_path)
            except OSError:
                pass

    except Exception as e:
        logger.error(f"Audio extraction task failed: {str(e)}")
        return {"status": "FAILURE", "error": str(e), "original_filename": filename}


@shared_task(bind=True, name="video.generate_thumbnail")
def generate_thumbnail_task(
    self,
    video_data: bytes,
    filename: str,
    timestamp: float = 1.0,
    width: int = 320,
    height: int = 240,
    image_format: str = "jpg",
) -> Dict[str, Any]:
    """
    Generate video thumbnail in background task.

    Args:
        video_data: Input video data as bytes
        filename: Original filename
        timestamp: Time position for thumbnail (seconds)
        width: Thumbnail width
        height: Thumbnail height
        image_format: Output image format

    Returns:
        Task result with thumbnail data
    """
    try:
        if not FFMPEG_AVAILABLE:
            raise VideoTaskError("FFmpeg not available for thumbnail generation")

        # Update task progress
        self.update_state(
            state="PROGRESS",
            meta={"progress": 0, "status": "Starting thumbnail generation"},
        )

        # Create temporary files
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=f".{filename.split('.')[-1]}"
        ) as input_temp:
            input_temp.write(video_data)
            input_temp.flush()
            input_path = input_temp.name

        with tempfile.NamedTemporaryFile(
            delete=False, suffix=f".{image_format}"
        ) as output_temp:
            output_path = output_temp.name

        try:
            # Update progress
            self.update_state(
                state="PROGRESS",
                meta={"progress": 50, "status": "Generating thumbnail"},
            )

            # Generate thumbnail using FFmpeg
            input_stream = ffmpeg.input(input_path, ss=timestamp)
            output_stream = ffmpeg.output(
                input_stream, output_path, vframes=1, s=f"{width}x{height}"
            )
            ffmpeg.run(output_stream, overwrite_output=True, quiet=True)

            # Update progress
            self.update_state(
                state="PROGRESS", meta={"progress": 90, "status": "Finalizing"}
            )

            # Read thumbnail
            with open(output_path, "rb") as f:
                thumbnail_data = f.read()

            return {
                "status": "SUCCESS",
                "thumbnail_data": thumbnail_data,
                "original_filename": filename,
                "timestamp": timestamp,
                "width": width,
                "height": height,
                "format": image_format,
                "output_size": len(thumbnail_data),
            }

        finally:
            # Cleanup temporary files
            try:
                os.unlink(input_path)
                os.unlink(output_path)
            except OSError:
                pass

    except Exception as e:
        logger.error(f"Thumbnail generation task failed: {str(e)}")
        return {"status": "FAILURE", "error": str(e), "original_filename": filename}
