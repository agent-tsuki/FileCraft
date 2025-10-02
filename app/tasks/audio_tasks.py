"""
Celery tasks for audio processing operations.
"""

import io
import os
import tempfile
from typing import Dict, Any, Optional, List
from celery import current_task

from app.celery_app import celery_app
from app.helpers.constants import AUDIO_QUALITY_PRESETS

# Import audio processing libraries
try:
    from pydub import AudioSegment
    from pydub.effects import normalize, compress_dynamic_range
    import librosa
    import numpy as np

    # Optional libraries
    try:
        import noisereduce as nr

        NOISE_REDUCTION_AVAILABLE = True
    except ImportError:
        NOISE_REDUCTION_AVAILABLE = False

    try:
        import pyloudnorm as pyln

        LOUDNORM_AVAILABLE = True
    except ImportError:
        LOUDNORM_AVAILABLE = False

    AUDIO_LIBS_AVAILABLE = True
except ImportError as e:
    AUDIO_LIBS_AVAILABLE = False
    print(f"Warning: Audio processing libraries not available: {e}")


@celery_app.task(
    bind=True,
    name="app.tasks.audio_tasks.convert_audio_async",
    max_retries=3,
    default_retry_delay=60,
)
def convert_audio_async(
    self,
    audio_data: bytes,
    target_format: str,
    bitrate: int = 128,
    sample_rate: Optional[int] = None,
    channels: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Convert audio format asynchronously.

    Args:
        audio_data: Raw audio data as bytes
        target_format: Target format (mp3, wav, aac, etc.)
        bitrate: Audio bitrate in kbps
        sample_rate: Sample rate in Hz
        channels: Number of channels (1=mono, 2=stereo)

    Returns:
        Dictionary with converted audio data and metadata
    """
    if not AUDIO_LIBS_AVAILABLE:
        return {"success": False, "error": "Audio libraries not available"}

    try:
        # Update task state
        self.update_state(state="PROCESSING", meta={"step": "initializing"})

        # Create temporary file for processing
        with tempfile.NamedTemporaryFile(delete=False) as temp_input:
            temp_input.write(audio_data)
            temp_input_path = temp_input.name

        try:
            # Load audio
            audio = AudioSegment.from_file(temp_input_path)
            original_info = {
                "duration": len(audio) / 1000.0,
                "sample_rate": audio.frame_rate,
                "channels": audio.channels,
                "sample_width": audio.sample_width,
            }

            self.update_state(
                state="PROCESSING",
                meta={"step": "loaded", "original_info": original_info},
            )

            # Apply conversions
            if channels:
                audio = audio.set_channels(channels)
                self.update_state(
                    state="PROCESSING", meta={"step": "channels_converted"}
                )

            if sample_rate:
                audio = audio.set_frame_rate(sample_rate)
                self.update_state(
                    state="PROCESSING", meta={"step": "sample_rate_converted"}
                )

            # Export to target format
            output_buffer = io.BytesIO()
            export_params = _get_export_params(target_format, bitrate)

            self.update_state(state="PROCESSING", meta={"step": "exporting"})

            audio.export(output_buffer, format=target_format, **export_params)

            converted_data = output_buffer.getvalue()

            result = {
                "audio_data": converted_data,
                "original_format": "detected",
                "target_format": target_format,
                "original_size": len(audio_data),
                "converted_size": len(converted_data),
                "original_info": original_info,
                "converted_info": {
                    "duration": len(audio) / 1000.0,
                    "sample_rate": sample_rate or audio.frame_rate,
                    "channels": channels or audio.channels,
                    "bitrate": bitrate,
                },
                "success": True,
            }

            return result

        finally:
            # Cleanup temporary file
            if os.path.exists(temp_input_path):
                os.unlink(temp_input_path)

    except Exception as exc:
        # Retry logic
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60, exc=exc)

        return {
            "success": False,
            "error": str(exc),
            "original_size": len(audio_data),
            "target_format": target_format,
        }


@celery_app.task(
    bind=True, name="app.tasks.audio_tasks.batch_convert_audio", max_retries=2
)
def batch_convert_audio(
    self, audio_files_data: List[Dict[str, Any]], conversion_settings: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Convert multiple audio files in batch.

    Args:
        audio_files_data: List of audio data dictionaries
        conversion_settings: Common conversion settings

    Returns:
        Dictionary with batch conversion results
    """
    if not AUDIO_LIBS_AVAILABLE:
        return {"success": False, "error": "Audio libraries not available"}

    results = []
    total_files = len(audio_files_data)

    for i, audio_info in enumerate(audio_files_data):
        try:
            # Update progress
            progress = int((i / total_files) * 100)
            self.update_state(
                state="PROCESSING",
                meta={
                    "progress": progress,
                    "current": i + 1,
                    "total": total_files,
                    "current_file": audio_info.get("filename", f"audio_{i}"),
                },
            )

            # Convert individual audio file
            result = convert_audio_async.apply(
                args=[
                    audio_info["data"],
                    conversion_settings["target_format"],
                    conversion_settings.get("bitrate", 128),
                    conversion_settings.get("sample_rate"),
                    conversion_settings.get("channels"),
                ]
            ).get()

            result["filename"] = audio_info.get("filename", f"audio_{i}")
            results.append(result)

        except Exception as e:
            results.append(
                {
                    "filename": audio_info.get("filename", f"audio_{i}"),
                    "success": False,
                    "error": str(e),
                }
            )

    # Calculate batch statistics
    successful = sum(1 for r in results if r.get("success", False))
    failed = total_files - successful

    return {
        "results": results,
        "total_files": total_files,
        "successful": successful,
        "failed": failed,
        "success_rate": (successful / total_files) * 100 if total_files > 0 else 0,
    }


@celery_app.task(name="app.tasks.audio_tasks.extract_audio_features_async")
def extract_audio_features_async(audio_data: bytes) -> Dict[str, Any]:
    """
    Extract comprehensive audio features and metadata.

    Args:
        audio_data: Raw audio data

    Returns:
        Dictionary with audio analysis data
    """
    if not AUDIO_LIBS_AVAILABLE:
        return {"success": False, "error": "Audio libraries not available"}

    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_path = temp_file.name

        try:
            # Basic analysis with pydub
            audio = AudioSegment.from_file(temp_path)

            basic_info = {
                "duration_seconds": len(audio) / 1000.0,
                "sample_rate": audio.frame_rate,
                "channels": audio.channels,
                "sample_width": audio.sample_width,
                "frame_count": audio.frame_count(),
                "file_size": len(audio_data),
                "bitrate_estimate": _estimate_bitrate(
                    len(audio_data), len(audio) / 1000.0
                ),
            }

            # Advanced analysis with librosa
            try:
                y, sr = librosa.load(temp_path, sr=None)

                # Extract features
                tempo = librosa.beat.tempo(y=y, sr=sr)[0]
                spectral_centroid = np.mean(
                    librosa.feature.spectral_centroid(y=y, sr=sr)
                )
                zero_crossing_rate = np.mean(librosa.feature.zero_crossing_rate(y))
                rms_energy = np.mean(librosa.feature.rms(y=y))
                mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13).mean(axis=1)

                advanced_info = {
                    "tempo_bpm": float(tempo),
                    "spectral_centroid_hz": float(spectral_centroid),
                    "zero_crossing_rate": float(zero_crossing_rate),
                    "rms_energy": float(rms_energy),
                    "mfcc_features": mfcc.tolist(),
                    "spectral_rolloff": float(
                        np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))
                    ),
                    "spectral_bandwidth": float(
                        np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))
                    ),
                }

                # Pitch and harmony analysis
                try:
                    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
                    pitch_mean = (
                        np.mean(pitches[pitches > 0]) if np.any(pitches > 0) else 0
                    )
                    advanced_info["average_pitch_hz"] = float(pitch_mean)
                except Exception:
                    advanced_info["average_pitch_hz"] = None

                # Loudness analysis (if available)
                if LOUDNORM_AVAILABLE:
                    try:
                        meter = pyln.Meter(sr)
                        loudness = meter.integrated_loudness(y)
                        advanced_info["loudness_lufs"] = (
                            float(loudness) if not np.isnan(loudness) else None
                        )
                    except Exception:
                        advanced_info["loudness_lufs"] = None

                basic_info.update(advanced_info)

            except Exception as e:
                basic_info["advanced_analysis_error"] = str(e)

            return {"success": True, "analysis": basic_info}

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    except Exception as e:
        return {"success": False, "error": str(e)}


@celery_app.task(name="app.tasks.audio_tasks.apply_audio_effects_async")
def apply_audio_effects_async(
    audio_data: bytes, effects: List[str], effect_params: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Apply audio effects and processing.

    Args:
        audio_data: Raw audio data
        effects: List of effects to apply
        effect_params: Parameters for effects

    Returns:
        Dictionary with processed audio data
    """
    if not AUDIO_LIBS_AVAILABLE:
        return {"success": False, "error": "Audio libraries not available"}

    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_path = temp_file.name

        try:
            audio = AudioSegment.from_file(temp_path)

            # Apply each effect
            for effect in effects:
                audio = _apply_effect(audio, effect, effect_params)

            # Export processed audio
            output_buffer = io.BytesIO()
            audio.export(output_buffer, format="wav")

            return {
                "success": True,
                "processed_audio_data": output_buffer.getvalue(),
                "original_size": len(audio_data),
                "processed_size": len(output_buffer.getvalue()),
                "effects_applied": effects,
            }

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    except Exception as e:
        return {"success": False, "error": str(e)}


@celery_app.task(name="app.tasks.audio_tasks.optimize_audio_async")
def optimize_audio_async(
    audio_data: bytes,
    optimization_type: str = "balanced",
    target_size_kb: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Optimize audio for size or quality.

    Args:
        audio_data: Raw audio data
        optimization_type: "size", "quality", or "balanced"
        target_size_kb: Target file size in KB

    Returns:
        Dictionary with optimized audio data
    """
    if not AUDIO_LIBS_AVAILABLE:
        return {"success": False, "error": "Audio libraries not available"}

    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_path = temp_file.name

        try:
            audio = AudioSegment.from_file(temp_path)

            if optimization_type == "size":
                # Optimize for smaller file size
                if target_size_kb:
                    optimized_audio = _optimize_for_target_size(
                        audio, target_size_kb * 1024
                    )
                else:
                    # Use aggressive compression
                    optimized_audio = audio.set_channels(1).set_frame_rate(22050)
                    bitrate = "64k"
            elif optimization_type == "quality":
                # Optimize for quality
                optimized_audio = audio
                bitrate = "320k"
            else:  # balanced
                # Balanced approach
                optimized_audio = audio.set_frame_rate(44100)
                bitrate = "128k"

            # Export optimized audio
            output_buffer = io.BytesIO()

            if optimization_type == "quality":
                optimized_audio.export(output_buffer, format="flac")
            else:
                optimized_audio.export(output_buffer, format="mp3", bitrate=bitrate)

            optimized_data = output_buffer.getvalue()

            return {
                "success": True,
                "optimized_audio_data": optimized_data,
                "original_size": len(audio_data),
                "optimized_size": len(optimized_data),
                "compression_ratio": len(audio_data) / len(optimized_data),
                "optimization_type": optimization_type,
            }

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    except Exception as e:
        return {"success": False, "error": str(e)}


# Helper functions
def _get_export_params(format_name: str, bitrate: int) -> Dict[str, Any]:
    """Get export parameters for audio format."""
    params = {}

    if format_name == "mp3":
        params.update({"bitrate": f"{bitrate}k", "parameters": ["-q:a", "0"]})
    elif format_name == "aac":
        params.update({"bitrate": f"{bitrate}k", "codec": "aac"})
    elif format_name == "ogg":
        params.update(
            {"codec": "libvorbis", "parameters": ["-q:a", str(min(10, bitrate // 32))]}
        )
    elif format_name in ["wav", "aiff"]:
        params.update({"parameters": ["-acodec", "pcm_s16le"]})
    elif format_name == "flac":
        params.update({"codec": "flac", "parameters": ["-compression_level", "8"]})

    return params


def _estimate_bitrate(file_size_bytes: int, duration_seconds: float) -> int:
    """Estimate bitrate from file size and duration."""
    if duration_seconds <= 0:
        return 0

    bits = file_size_bytes * 8
    bitrate_bps = bits / duration_seconds
    bitrate_kbps = int(bitrate_bps / 1000)

    return bitrate_kbps


def _apply_effect(
    audio: "AudioSegment", effect: str, params: Dict[str, Any]
) -> "AudioSegment":
    """Apply a single audio effect."""
    if effect == "normalize":
        return normalize(audio, headroom=params.get("headroom", 0.1))
    elif effect == "compress":
        threshold = params.get("threshold", -20.0)
        ratio = params.get("ratio", 4.0)
        return compress_dynamic_range(audio, threshold=threshold, ratio=ratio)
    elif effect == "fade_in":
        duration = params.get("duration", 1000)
        return audio.fade_in(duration)
    elif effect == "fade_out":
        duration = params.get("duration", 1000)
        return audio.fade_out(duration)
    elif effect == "volume_change":
        change_db = params.get("change_db", 0.0)
        return audio + change_db
    elif effect == "noise_reduction" and NOISE_REDUCTION_AVAILABLE:
        # Basic noise reduction implementation
        return audio  # Placeholder for more advanced implementation
    else:
        return audio


def _optimize_for_target_size(
    audio: "AudioSegment", target_bytes: int
) -> "AudioSegment":
    """Optimize audio to achieve target file size."""
    # Start with original audio
    current_audio = audio

    # Try reducing sample rate first
    if len(audio.raw_data) > target_bytes:
        current_audio = current_audio.set_frame_rate(22050)

    # Then try mono conversion
    if len(current_audio.raw_data) > target_bytes:
        current_audio = current_audio.set_channels(1)

    # Finally, try reducing bit depth
    if len(current_audio.raw_data) > target_bytes:
        current_audio = current_audio.set_sample_width(1)

    return current_audio
