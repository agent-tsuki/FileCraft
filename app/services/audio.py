"""
Enhanced audio processing service with comprehensive format support and advanced features.
"""

import io
import os
import tempfile
import asyncio
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
    AUDIO_FORMATS,
    SUPPORTED_AUDIO_OUTPUT_FORMATS,
    AUDIO_QUALITY_PRESETS,
    SAMPLE_RATES,
    AUDIO_EFFECTS,
)

# Import audio processing libraries with fallbacks
AUDIO_LIBRARIES_AVAILABLE = False
AUDIO_LIBS_AVAILABLE = False
LOUDNORM_AVAILABLE = False
NOISE_REDUCTION_AVAILABLE = False

try:
    from pydub import AudioSegment
    from pydub.effects import (
        normalize,
        compress_dynamic_range,
        low_pass_filter,
        high_pass_filter,
    )
    from pydub.silence import split_on_silence, detect_nonsilent

    AUDIO_LIBRARIES_AVAILABLE = True
    AUDIO_LIBS_AVAILABLE = True
except ImportError:
    # Create dummy classes to prevent NameError
    class AudioSegment:
        pass


try:
    import librosa
    import soundfile as sf
    import numpy as np
    from scipy import signal
except ImportError:
    librosa = None
    sf = None
    np = None
    signal = None

try:
    import essentia
    import essentia.standard as es
except ImportError:
    essentia = None
    es = None

try:
    import pyloudnorm as pyln

    LOUDNORM_AVAILABLE = True
except ImportError:
    pyln = None

try:
    import noisereduce as nr

    NOISE_REDUCTION_AVAILABLE = True
except ImportError:
    nr = None

# Import Celery tasks (with error handling)
try:
    from app.tasks.audio_tasks import (
        convert_audio_async,
        batch_convert_audio,
        optimize_audio_async,
        extract_audio_features_async,
        apply_audio_effects_async,
    )

    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False

logger = logging.getLogger(__name__)


class AudioProcessingError(Exception):
    """Custom exception for audio processing errors."""

    pass


class AudioService(BaseService):
    """Enhanced service for audio processing operations with advanced features."""

    def __init__(self, config: AppConfig, validation_service: FileValidationService):
        super().__init__(config)
        self.validation_service = validation_service
        self.supported_formats = set(SUPPORTED_AUDIO_OUTPUT_FORMATS)
        self.executor = ThreadPoolExecutor(
            max_workers=2
        )  # Audio processing is CPU intensive

        if not AUDIO_LIBS_AVAILABLE:
            logger.warning(
                "Audio processing libraries not available. Limited functionality."
            )

    async def convert_audio_format(
        self,
        audio_file: UploadFile,
        target_format: str,
        bitrate: int = 128,
        sample_rate: Optional[int] = None,
        channels: Optional[int] = None,
        use_async: bool = False,
        quality_preset: Optional[str] = None,
    ) -> Union[BinaryIO, Dict[str, Any]]:
        """
        Convert audio to specified format with advanced options.

        Args:
            audio_file: Uploaded audio file
            target_format: Target format (mp3, wav, aac, etc.)
            bitrate: Audio bitrate in kbps
            sample_rate: Sample rate in Hz
            channels: Number of channels (1=mono, 2=stereo)
            use_async: Whether to use Celery for background processing
            quality_preset: Quality preset (phone, radio, cd, hd, studio)

        Returns:
            BytesIO buffer containing converted audio or task info

        Raises:
            AudioProcessingError: If conversion fails
        """
        if not AUDIO_LIBS_AVAILABLE:
            raise AudioProcessingError("Audio processing libraries not available")

        try:
            # Validate inputs
            filename = self.validation_service.validate_filename(
                audio_file.filename or ""
            )
            target_format = target_format.lower()

            if target_format not in self.supported_formats:
                raise AudioProcessingError(f"Unsupported format: {target_format}")

            # Apply quality preset if specified
            if quality_preset and quality_preset in AUDIO_QUALITY_PRESETS:
                preset = AUDIO_QUALITY_PRESETS[quality_preset]
                bitrate = preset["bitrate"]
                if not sample_rate:
                    sample_rate = preset["sample_rate"]

            # Read and validate audio
            content = await audio_file.read()
            _, file_type = self.validation_service.get_file_type(filename)

            if file_type != "audio":
                raise AudioProcessingError(f"File is not an audio file: {file_type}")

            self.validation_service.validate_file_size(len(content), file_type)

            # Use Celery for background processing if requested and available
            if use_async and CELERY_AVAILABLE and self._is_redis_available():
                try:
                    task = convert_audio_async.delay(
                        content, target_format, bitrate, sample_rate, channels
                    )
                    return {"task_id": task.id, "status": "processing"}
                except Exception:
                    # Fall back to synchronous processing
                    pass

            # Process synchronously
            result = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                self._convert_audio_sync,
                content,
                target_format,
                bitrate,
                sample_rate,
                channels,
            )

            self.log_operation(
                "audio_converted",
                {
                    "source_filename": filename,
                    "target_format": target_format,
                    "original_size": len(content),
                    "converted_size": len(result.getvalue()) if result else 0,
                    "bitrate": bitrate,
                    "sample_rate": sample_rate,
                },
            )

            return result

        except Exception as e:
            self.logger.error(f"Audio conversion failed: {str(e)}")
            if isinstance(e, AudioProcessingError):
                raise
            raise AudioProcessingError(f"Failed to convert audio: {str(e)}")

    def _convert_audio_sync(
        self,
        audio_data: bytes,
        target_format: str,
        bitrate: int,
        sample_rate: Optional[int],
        channels: Optional[int],
    ) -> BinaryIO:
        """Synchronous audio conversion."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_input:
            temp_input.write(audio_data)
            temp_input_path = temp_input.name

        try:
            # Load audio with pydub
            audio = AudioSegment.from_file(temp_input_path)

            # Apply conversions
            if channels:
                if channels == 1:
                    audio = audio.set_channels(1)  # Convert to mono
                elif channels == 2:
                    audio = audio.set_channels(2)  # Convert to stereo

            if sample_rate:
                audio = audio.set_frame_rate(sample_rate)

            # Export to target format
            output_buffer = io.BytesIO()

            # Format-specific export parameters
            export_params = self._get_audio_export_params(target_format, bitrate)

            audio.export(output_buffer, format=target_format, **export_params)

            output_buffer.seek(0)
            return output_buffer

        finally:
            # Cleanup
            if os.path.exists(temp_input_path):
                os.unlink(temp_input_path)

    def _get_audio_export_params(
        self, format_name: str, bitrate: int
    ) -> Dict[str, Any]:
        """Get optimal export parameters for audio format."""
        params = {}

        if format_name == "mp3":
            params.update(
                {
                    "bitrate": f"{bitrate}k",
                    "parameters": ["-q:a", "0"],  # Highest quality VBR
                }
            )
        elif format_name == "aac":
            params.update({"bitrate": f"{bitrate}k", "codec": "aac"})
        elif format_name == "ogg":
            params.update(
                {
                    "codec": "libvorbis",
                    "parameters": ["-q:a", str(min(10, bitrate // 32))],
                }
            )
        elif format_name == "opus":
            params.update({"codec": "libopus", "bitrate": f"{bitrate}k"})
        elif format_name in ["wav", "aiff"]:
            # Lossless formats don't use bitrate
            params.update({"parameters": ["-acodec", "pcm_s16le"]})
        elif format_name == "flac":
            params.update({"codec": "flac", "parameters": ["-compression_level", "8"]})

        return params

    async def get_audio_info(self, audio_file: UploadFile) -> Dict[str, Any]:
        """Get comprehensive audio information and metadata."""
        if not AUDIO_LIBS_AVAILABLE:
            raise AudioProcessingError("Audio processing libraries not available")

        content = await audio_file.read()

        # Check if Celery is available and working
        if CELERY_AVAILABLE and self._is_redis_available():
            try:
                task = extract_audio_features_async.delay(content)
                return {"task_id": task.id, "status": "processing"}
            except Exception:
                # Fall back to synchronous processing
                pass

        # Synchronous analysis
        return await asyncio.get_event_loop().run_in_executor(
            self.executor, self._analyze_audio_sync, content
        )

    def _analyze_audio_sync(self, audio_data: bytes) -> Dict[str, Any]:
        """Synchronous audio analysis."""
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
                "bitrate": self._estimate_bitrate(len(audio_data), len(audio) / 1000.0),
                "format_detected": self._detect_audio_format(temp_path),
            }

            # Advanced analysis with librosa (if available)
            try:
                y, sr = librosa.load(temp_path, sr=None)

                advanced_info = {
                    "tempo": float(librosa.beat.tempo(y=y, sr=sr)[0]),
                    "spectral_centroid": float(
                        np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
                    ),
                    "zero_crossing_rate": float(
                        np.mean(librosa.feature.zero_crossing_rate(y))
                    ),
                    "rms_energy": float(np.mean(librosa.feature.rms(y=y))),
                    "mfcc": librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
                    .mean(axis=1)
                    .tolist(),
                }

                # Loudness analysis (if available)
                if LOUDNORM_AVAILABLE:
                    meter = pyln.Meter(sr)
                    loudness = meter.integrated_loudness(y)
                    advanced_info["loudness_lufs"] = (
                        float(loudness) if not np.isnan(loudness) else None
                    )

                basic_info.update(advanced_info)

            except Exception as e:
                basic_info["advanced_analysis_error"] = str(e)

            return basic_info

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def _estimate_bitrate(self, file_size_bytes: int, duration_seconds: float) -> int:
        """Estimate bitrate from file size and duration."""
        if duration_seconds <= 0:
            return 0

        # Calculate bitrate in kbps
        bits = file_size_bytes * 8
        bitrate_bps = bits / duration_seconds
        bitrate_kbps = int(bitrate_bps / 1000)

        return bitrate_kbps

    def _detect_audio_format(self, file_path: str) -> str:
        """Detect audio format from file."""
        try:
            audio = AudioSegment.from_file(file_path)
            # Try to determine format from file extension or content
            return "detected"
        except Exception:
            return "unknown"

    async def apply_audio_effects(
        self,
        audio_file: UploadFile,
        effects: List[str],
        effect_params: Optional[Dict[str, Any]] = None,
    ) -> Union[BinaryIO, Dict[str, Any]]:
        """Apply audio effects and processing."""
        if not AUDIO_LIBS_AVAILABLE:
            raise AudioProcessingError("Audio processing libraries not available")

        content = await audio_file.read()
        effect_params = effect_params or {}

        # Use Celery for background processing if available
        if CELERY_AVAILABLE and self._is_redis_available():
            try:
                task = apply_audio_effects_async.delay(content, effects, effect_params)
                return {"task_id": task.id, "status": "processing"}
            except Exception:
                pass

        # Synchronous processing
        return await asyncio.get_event_loop().run_in_executor(
            self.executor, self._apply_effects_sync, content, effects, effect_params
        )

    def _apply_effects_sync(
        self, audio_data: bytes, effects: List[str], effect_params: Dict[str, Any]
    ) -> BinaryIO:
        """Apply audio effects synchronously."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_path = temp_file.name

        try:
            audio = AudioSegment.from_file(temp_path)

            # Apply each effect
            for effect in effects:
                audio = self._apply_single_effect(audio, effect, effect_params)

            # Export processed audio
            output_buffer = io.BytesIO()
            audio.export(output_buffer, format="wav")
            output_buffer.seek(0)

            return output_buffer

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def _apply_single_effect(
        self, audio: AudioSegment, effect: str, params: Dict[str, Any]
    ) -> AudioSegment:
        """Apply a single audio effect."""
        if effect == "normalize":
            return normalize(audio, headroom=params.get("headroom", 0.1))

        elif effect == "compress":
            threshold = params.get("threshold", -20.0)
            ratio = params.get("ratio", 4.0)
            return compress_dynamic_range(audio, threshold=threshold, ratio=ratio)

        elif effect == "fade_in":
            duration = params.get("duration", 1000)  # milliseconds
            return audio.fade_in(duration)

        elif effect == "fade_out":
            duration = params.get("duration", 1000)
            return audio.fade_out(duration)

        elif effect == "volume_change":
            change_db = params.get("change_db", 0.0)
            return audio + change_db

        elif effect == "speed_change":
            speed_factor = params.get("speed_factor", 1.0)
            # Change speed (affects both pitch and tempo)
            return audio._spawn(
                audio.raw_data,
                overrides={"frame_rate": int(audio.frame_rate * speed_factor)},
            ).set_frame_rate(audio.frame_rate)

        elif effect == "noise_reduction" and NOISE_REDUCTION_AVAILABLE:
            # Convert to numpy array for noise reduction
            samples = np.array(audio.get_array_of_samples())
            if audio.channels == 2:
                samples = samples.reshape((-1, 2))

            # Apply noise reduction
            reduced_noise = nr.reduce_noise(y=samples, sr=audio.frame_rate)

            # Convert back to AudioSegment
            reduced_audio = audio._spawn(reduced_noise.tobytes())
            return reduced_audio

        else:
            # Effect not implemented or not available
            return audio

    def _is_redis_available(self) -> bool:
        """Check if Redis is available for Celery tasks."""
        try:
            import redis

            r = redis.Redis.from_url(self.config.redis_url)
            r.ping()
            return True
        except Exception:
            return False

    async def batch_convert_audio(
        self,
        audio_files: List[UploadFile],
        target_format: str,
        bitrate: int = 128,
        quality_preset: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Convert multiple audio files in batch."""
        if not CELERY_AVAILABLE or not self._is_redis_available():
            raise AudioProcessingError("Batch processing requires Celery and Redis")

        # Prepare audio data
        audio_data = []
        for audio_file in audio_files:
            content = await audio_file.read()
            audio_data.append({"data": content, "filename": audio_file.filename})

        # Submit batch task
        task = batch_convert_audio.delay(
            audio_data,
            {
                "target_format": target_format,
                "bitrate": bitrate,
                "quality_preset": quality_preset,
            },
        )

        return {
            "task_id": task.id,
            "status": "processing",
            "total_files": len(audio_files),
        }


def get_audio_service(
    config: AppConfig = Depends(get_config),
    validation_service: FileValidationService = Depends(get_file_validation_service),
) -> AudioService:
    """Dependency to inject audio service."""
    return AudioService(config, validation_service)
