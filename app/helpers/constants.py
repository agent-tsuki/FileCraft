# File processing constants
CHUNK_SIZE = 8192

# Maximum file sizes (in bytes)
MAX_UPLOAD_SIZE = {
    "img": 50485760,  # 50MB for images (increased for high-resolution images)
    "docs": 5242880,
    "pdf": 15728640,
    "advance": 104857600
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

# File extension to type mapping
EXTENSION_TYPE_MAP = {
    # All image formats
    **{ext: "img" for ext in IMAGE_FORMATS.keys()},
    
    # Additional image extensions
    "jfif": "img", "jpe": "img", "jfi": "img",
    "apng": "img", "mng": "img",
    
    # PDFs
    "pdf": "pdf",

    # Documents
    "doc": "docs", "docx": "docs", "txt": "docs", "md": "docs", "rtf": "docs",

    # Audio/Video
    "mp3": "advance", "wav": "advance", "aac": "advance",
    "mp4": "advance", "mkv": "advance", "mov": "advance",
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
