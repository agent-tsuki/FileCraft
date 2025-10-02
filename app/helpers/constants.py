# File processing constants
CHUNK_SIZE = 8192

# Maximum file sizes (in bytes)
MAX_UPLOAD_SIZE = {
    "img": 50485760,     # 50MB for images (increased for high-resolution images)
    "audio": 209715200,  # 200MB for audio files (high-quality audio)
    "docs": 5242880,     # 5MB for documents
    "pdf": 15728640,     # 15MB for PDFs
    "video": 524288000,  # 500MB for video files
    "advance": 1073741824  # 1GB for advanced processing
}

# Image formats chronologically from oldest to newest
IMAGE_FORMATS = {
    # 1970s-1980s (Oldest formats)
    "pbm": {"name": "Portable Bitmap", "year": 1988, "lossy": False, "transparency": False, "animation": False},
    "pgm": {"name": "Portable Graymap", "year": 1989, "lossy": False, "transparency": False, "animation": False},
    "ppm": {"name": "Portable Pixmap", "year": 1989, "lossy": False, "transparency": False, "animation": False},
    "xbm": {"name": "X BitMap", "year": 1989, "lossy": False, "transparency": True, "animation": False},
    "xpm": {"name": "X PixMap", "year": 1989, "lossy": False, "transparency": True, "animation": False},
    
    # 1980s-1990s
    "pcx": {"name": "PC Paintbrush", "year": 1985, "lossy": False, "transparency": False, "animation": False},
    "tga": {"name": "Truevision TGA", "year": 1984, "lossy": False, "transparency": True, "animation": False},
    "bmp": {"name": "Windows Bitmap", "year": 1985, "lossy": False, "transparency": False, "animation": False},
    "gif": {"name": "Graphics Interchange Format", "year": 1987, "lossy": False, "transparency": True, "animation": True},
    "jpeg": {"name": "Joint Photographic Experts Group", "year": 1992, "lossy": True, "transparency": False, "animation": False},
    "jpg": {"name": "JPEG", "year": 1992, "lossy": True, "transparency": False, "animation": False},
    "png": {"name": "Portable Network Graphics", "year": 1996, "lossy": False, "transparency": True, "animation": False},
    "tiff": {"name": "Tagged Image File Format", "year": 1992, "lossy": False, "transparency": True, "animation": False},
    "tif": {"name": "TIFF", "year": 1992, "lossy": False, "transparency": True, "animation": False},
    
    # 2000s
    "jp2": {"name": "JPEG 2000", "year": 2000, "lossy": True, "transparency": True, "animation": False},
    "jpx": {"name": "JPEG 2000 Extended", "year": 2004, "lossy": True, "transparency": True, "animation": False},
    "webp": {"name": "WebP", "year": 2010, "lossy": True, "transparency": True, "animation": True},
    "ico": {"name": "Windows Icon", "year": 1985, "lossy": False, "transparency": True, "animation": False},
    "icns": {"name": "Apple Icon Image", "year": 1991, "lossy": False, "transparency": True, "animation": False},
    
    # 2010s-Modern
    "heic": {"name": "High Efficiency Image Container", "year": 2015, "lossy": True, "transparency": True, "animation": False},
    "heif": {"name": "High Efficiency Image Format", "year": 2015, "lossy": True, "transparency": True, "animation": False},
    "avif": {"name": "AV1 Image File Format", "year": 2019, "lossy": True, "transparency": True, "animation": True},
    "jxl": {"name": "JPEG XL", "year": 2021, "lossy": True, "transparency": True, "animation": True},
    
    # RAW formats (Professional cameras)
    "raw": {"name": "Camera RAW", "year": 1990, "lossy": False, "transparency": False, "animation": False},
    "cr2": {"name": "Canon RAW v2", "year": 2004, "lossy": False, "transparency": False, "animation": False},
    "nef": {"name": "Nikon Electronic Format", "year": 1999, "lossy": False, "transparency": False, "animation": False},
    "arw": {"name": "Sony Alpha RAW", "year": 2005, "lossy": False, "transparency": False, "animation": False},
    "dng": {"name": "Digital Negative", "year": 2004, "lossy": False, "transparency": False, "animation": False},
    "orf": {"name": "Olympus RAW Format", "year": 2000, "lossy": False, "transparency": False, "animation": False},
    "rw2": {"name": "Panasonic RAW", "year": 2006, "lossy": False, "transparency": False, "animation": False},
    
    # Vector and specialized formats
    "svg": {"name": "Scalable Vector Graphics", "year": 2001, "lossy": False, "transparency": True, "animation": True},
    "eps": {"name": "Encapsulated PostScript", "year": 1985, "lossy": False, "transparency": True, "animation": False},
    "pdf": {"name": "Portable Document Format", "year": 1993, "lossy": False, "transparency": True, "animation": False},
    "psd": {"name": "Photoshop Document", "year": 1988, "lossy": False, "transparency": True, "animation": False},
    "ai": {"name": "Adobe Illustrator", "year": 1987, "lossy": False, "transparency": True, "animation": False},
}

# Supported output formats for conversion
SUPPORTED_OUTPUT_FORMATS = [
    "jpeg", "jpg", "png", "webp", "bmp", "gif", "tiff", "tif", 
    "avif", "heic", "heif", "ico", "jp2", "pdf"
]

# Quality presets
QUALITY_PRESETS = {
    "low": 50,
    "medium": 75,
    "high": 90,
    "maximum": 95,
    "lossless": 100
}

# Size presets for image resizing
SIZE_PRESETS = {
    "thumbnail": (150, 150),
    "small": (320, 240),
    "medium": (640, 480),
    "large": (1024, 768),
    "hd": (1280, 720),
    "full_hd": (1920, 1080),
    "2k": (2048, 1080),
    "4k": (3840, 2160),
    "8k": (7680, 4320)
}

# Compression algorithms
COMPRESSION_ALGORITHMS = {
    "png": ["png", "zip"],
    "tiff": ["none", "lzw", "jpeg", "packbits", "zip"],
    "webp": ["lossless", "lossy"],
    "jpeg": ["baseline", "progressive"],
    "avif": ["lossless", "lossy"]
}

# Audio formats chronologically from oldest to newest
AUDIO_FORMATS = {
    # 1980s-1990s (Oldest formats)
    "wav": {"name": "Waveform Audio File", "year": 1991, "lossy": False, "max_bitrate": "Uncompressed", "supports_metadata": True},
    "au": {"name": "Audio File Format", "year": 1992, "lossy": False, "max_bitrate": "Uncompressed", "supports_metadata": False},
    "aiff": {"name": "Audio Interchange File Format", "year": 1988, "lossy": False, "max_bitrate": "Uncompressed", "supports_metadata": True},
    
    # 1990s Compression Era
    "mp2": {"name": "MPEG Audio Layer II", "year": 1993, "lossy": True, "max_bitrate": "384 kbps", "supports_metadata": False},
    "mp3": {"name": "MPEG Audio Layer III", "year": 1993, "lossy": True, "max_bitrate": "320 kbps", "supports_metadata": True},
    "ra": {"name": "RealAudio", "year": 1995, "lossy": True, "max_bitrate": "128 kbps", "supports_metadata": False},
    
    # 2000s Advanced Compression
    "aac": {"name": "Advanced Audio Coding", "year": 2000, "lossy": True, "max_bitrate": "529 kbps", "supports_metadata": True},
    "ogg": {"name": "Ogg Vorbis", "year": 2000, "lossy": True, "max_bitrate": "500 kbps", "supports_metadata": True},
    "wma": {"name": "Windows Media Audio", "year": 1999, "lossy": True, "max_bitrate": "768 kbps", "supports_metadata": True},
    "ac3": {"name": "Dolby Digital", "year": 1991, "lossy": True, "max_bitrate": "640 kbps", "supports_metadata": False},
    
    # 2000s Lossless Formats
    "flac": {"name": "Free Lossless Audio Codec", "year": 2001, "lossy": False, "max_bitrate": "Lossless", "supports_metadata": True},
    "ape": {"name": "Monkey's Audio", "year": 2000, "lossy": False, "max_bitrate": "Lossless", "supports_metadata": True},
    "wv": {"name": "WavPack", "year": 2002, "lossy": False, "max_bitrate": "Lossless", "supports_metadata": True},
    "alac": {"name": "Apple Lossless", "year": 2004, "lossy": False, "max_bitrate": "Lossless", "supports_metadata": True},
    
    # 2010s Modern Formats
    "opus": {"name": "Opus", "year": 2012, "lossy": True, "max_bitrate": "510 kbps", "supports_metadata": True},
    "webm": {"name": "WebM Audio", "year": 2010, "lossy": True, "max_bitrate": "500 kbps", "supports_metadata": True},
    "m4a": {"name": "MPEG-4 Audio", "year": 2001, "lossy": True, "max_bitrate": "529 kbps", "supports_metadata": True},
    
    # Professional/Specialized
    "dsd": {"name": "Direct Stream Digital", "year": 1999, "lossy": False, "max_bitrate": "Lossless", "supports_metadata": True},
    "mqa": {"name": "Master Quality Authenticated", "year": 2014, "lossy": False, "max_bitrate": "Lossless", "supports_metadata": True},
    
    # Legacy/Rare formats
    "snd": {"name": "Sound File", "year": 1983, "lossy": False, "max_bitrate": "Uncompressed", "supports_metadata": False},
    "voc": {"name": "Creative Voice File", "year": 1989, "lossy": False, "max_bitrate": "Uncompressed", "supports_metadata": False},
    "amr": {"name": "Adaptive Multi-Rate", "year": 1999, "lossy": True, "max_bitrate": "23.85 kbps", "supports_metadata": False},
    "3gp": {"name": "3GPP Audio", "year": 2001, "lossy": True, "max_bitrate": "128 kbps", "supports_metadata": True},
}

# Supported output audio formats
SUPPORTED_AUDIO_OUTPUT_FORMATS = [
    "wav", "mp3", "aac", "ogg", "flac", "m4a", "opus", "webm", "aiff", "au"
]

# Audio quality presets
AUDIO_QUALITY_PRESETS = {
    "phone": {"bitrate": 64, "sample_rate": 22050, "description": "Phone quality"},
    "radio": {"bitrate": 128, "sample_rate": 44100, "description": "Radio quality"},
    "cd": {"bitrate": 320, "sample_rate": 44100, "description": "CD quality"},
    "hd": {"bitrate": 500, "sample_rate": 48000, "description": "HD quality"},
    "studio": {"bitrate": 1411, "sample_rate": 96000, "description": "Studio quality"},
}

# Sample rate options
SAMPLE_RATES = [8000, 11025, 16000, 22050, 32000, 44100, 48000, 88200, 96000, 192000]

# Audio effects and processing options
AUDIO_EFFECTS = {
    "normalize": "Normalize audio levels",
    "compress": "Dynamic range compression", 
    "eq": "Equalization",
    "reverb": "Add reverb effect",
    "echo": "Add echo effect",
    "fade_in": "Fade in at start",
    "fade_out": "Fade out at end",
    "noise_reduction": "Reduce background noise",
    "pitch_shift": "Change pitch without tempo",
    "tempo_change": "Change tempo without pitch",
    "stereo_width": "Adjust stereo width",
    "bass_boost": "Enhance bass frequencies",
    "treble_boost": "Enhance treble frequencies"
}

# Video formats chronologically from oldest to newest
VIDEO_FORMATS = {
    # 1980s-1990s (Oldest formats)
    "avi": {"name": "Audio Video Interleave", "year": 1992, "container": True, "streaming": False, "hdr": False, "max_resolution": "Unlimited"},
    "mov": {"name": "QuickTime Movie", "year": 1991, "container": True, "streaming": False, "hdr": False, "max_resolution": "Unlimited"},
    "mpg": {"name": "MPEG-1 Video", "year": 1993, "container": False, "streaming": False, "hdr": False, "max_resolution": "704x576"},
    "mpeg": {"name": "MPEG Video", "year": 1993, "container": False, "streaming": False, "hdr": False, "max_resolution": "704x576"},
    "wmv": {"name": "Windows Media Video", "year": 1999, "container": True, "streaming": True, "hdr": False, "max_resolution": "1920x1080"},
    
    # 2000s Digital Era
    "mp4": {"name": "MPEG-4 Part 14", "year": 2001, "container": True, "streaming": True, "hdr": True, "max_resolution": "Unlimited"},
    "3gp": {"name": "3GPP Multimedia", "year": 2001, "container": True, "streaming": True, "hdr": False, "max_resolution": "352x288"},
    "flv": {"name": "Flash Video", "year": 2003, "container": True, "streaming": True, "hdr": False, "max_resolution": "1920x1080"},
    "m4v": {"name": "iTunes Video", "year": 2005, "container": True, "streaming": False, "hdr": True, "max_resolution": "Unlimited"},
    
    # 2010s Modern Formats
    "webm": {"name": "WebM", "year": 2010, "container": True, "streaming": True, "hdr": True, "max_resolution": "Unlimited"},
    "mkv": {"name": "Matroska Video", "year": 2002, "container": True, "streaming": False, "hdr": True, "max_resolution": "Unlimited"},
    "ogv": {"name": "Ogg Video", "year": 2007, "container": True, "streaming": True, "hdr": False, "max_resolution": "Unlimited"},
    "ts": {"name": "MPEG Transport Stream", "year": 1995, "container": True, "streaming": True, "hdr": True, "max_resolution": "Unlimited"},
    "mts": {"name": "AVCHD Video", "year": 2006, "container": True, "streaming": False, "hdr": True, "max_resolution": "1920x1080"},
    "m2ts": {"name": "Blu-ray BDAV", "year": 2006, "container": True, "streaming": False, "hdr": True, "max_resolution": "3840x2160"},
    
    # Professional/Broadcast
    "mxf": {"name": "Material Exchange Format", "year": 2004, "container": True, "streaming": False, "hdr": True, "max_resolution": "Unlimited"},
    "prores": {"name": "Apple ProRes", "year": 2007, "container": False, "streaming": False, "hdr": True, "max_resolution": "8192x4320"},
    "dnxhd": {"name": "Avid DNxHD", "year": 2004, "container": False, "streaming": False, "hdr": True, "max_resolution": "1920x1080"},
    
    # Legacy formats
    "asf": {"name": "Advanced Systems Format", "year": 1996, "container": True, "streaming": True, "hdr": False, "max_resolution": "1920x1080"},
    "rm": {"name": "RealMedia", "year": 1995, "container": True, "streaming": True, "hdr": False, "max_resolution": "720x480"},
    "vob": {"name": "Video Object", "year": 1997, "container": True, "streaming": False, "hdr": False, "max_resolution": "720x480"},
    "dv": {"name": "Digital Video", "year": 1995, "container": False, "streaming": False, "hdr": False, "max_resolution": "720x480"},
}

# Supported output video formats
SUPPORTED_VIDEO_OUTPUT_FORMATS = [
    "mp4", "mkv", "webm", "avi", "mov", "wmv", "flv", "ogv", "m4v", "3gp"
]

# Video codecs
VIDEO_CODECS = {
    "h264": {"name": "H.264/AVC", "year": 2003, "hardware_acc": True, "max_bitrate": "62.5 Mbps"},
    "h265": {"name": "H.265/HEVC", "year": 2013, "hardware_acc": True, "max_bitrate": "40 Mbps"},
    "vp8": {"name": "VP8", "year": 2008, "hardware_acc": True, "max_bitrate": "Unlimited"},
    "vp9": {"name": "VP9", "year": 2013, "hardware_acc": True, "max_bitrate": "Unlimited"},
    "av1": {"name": "AV1", "year": 2018, "hardware_acc": True, "max_bitrate": "Unlimited"},
    "xvid": {"name": "Xvid", "year": 2001, "hardware_acc": False, "max_bitrate": "Unlimited"},
    "divx": {"name": "DivX", "year": 1999, "hardware_acc": False, "max_bitrate": "Unlimited"},
}

# Video quality presets
VIDEO_QUALITY_PRESETS = {
    "mobile": {"width": 480, "height": 360, "bitrate": "500k", "description": "Mobile optimized"},
    "sd": {"width": 720, "height": 480, "bitrate": "1500k", "description": "Standard Definition"},
    "hd": {"width": 1280, "height": 720, "bitrate": "3000k", "description": "HD 720p"},
    "full_hd": {"width": 1920, "height": 1080, "bitrate": "5000k", "description": "Full HD 1080p"},
    "2k": {"width": 2048, "height": 1080, "bitrate": "8000k", "description": "2K Cinema"},
    "4k": {"width": 3840, "height": 2160, "bitrate": "15000k", "description": "4K Ultra HD"},
    "8k": {"width": 7680, "height": 4320, "bitrate": "50000k", "description": "8K Ultra HD"},
}

# Video frame rates
VIDEO_FRAME_RATES = [12, 15, 23.976, 24, 25, 29.97, 30, 50, 59.94, 60, 120]

# Video effects and filters
VIDEO_EFFECTS = {
    "scale": "Resize video dimensions",
    "crop": "Crop video area",
    "rotate": "Rotate video",
    "flip": "Flip video horizontally/vertically",
    "stabilize": "Video stabilization",
    "noise_reduction": "Reduce video noise",
    "sharpen": "Sharpen video",
    "blur": "Blur effect",
    "brightness": "Adjust brightness",
    "contrast": "Adjust contrast",
    "saturation": "Adjust color saturation",
    "fade_in": "Fade in at start",
    "fade_out": "Fade out at end",
    "speed_change": "Change playback speed",
    "reverse": "Reverse video playback",
}

# File extension to type mapping
EXTENSION_TYPE_MAP = {
    # All image formats
    **{ext: "img" for ext in IMAGE_FORMATS.keys()},
    
    # Additional image extensions
    "jfif": "img", "jpe": "img", "jfi": "img",
    "apng": "img", "mng": "img",
    
    # All audio formats
    **{ext: "audio" for ext in AUDIO_FORMATS.keys()},
    
    # All video formats
    **{ext: "video" for ext in VIDEO_FORMATS.keys()},
    
    # Additional video extensions
    "webm": "video", "f4v": "video", "m2v": "video", "3g2": "video",
    
    # PDFs
    "pdf": "pdf",

    # Documents
    "doc": "docs", "docx": "docs", "txt": "docs", "md": "docs", "rtf": "docs",
}

# Celery task priorities
TASK_PRIORITIES = {
    "high": 9,
    "normal": 5,
    "low": 1
}

# Image optimization settings
IMAGE_OPTIMIZATION = {
    "max_pixels": 178956970,  # 178MP limit for PIL
    "chunk_size": 8192,
    "memory_limit": 256 * 1024 * 1024,  # 256MB
    "thumbnail_size": (256, 256),
    "progressive_jpeg_threshold": 10240  # 10KB
}
