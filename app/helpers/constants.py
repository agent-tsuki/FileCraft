CHUNK_SIZE = 8192
MAX_UPLOAD_SIZE = {
    "img": 10485760,
    "docs": 5242880,
    "pdf": 15728640,
    "advance": 104857600
}
EXTENSION_TYPE_MAP = {
    # Images
    "jpg": "img", "jpeg": "img", "png": "img", "gif": "img", "bmp": "img",
    "tiff": "img", "tif": "img", "webp": "img", "heic": "img", "heif": "img",
    "svg": "img", "ico": "img", "raw": "img", "psd": "img", "ai": "img",
    "eps": "img", "jfif": "img", "apng": "img", "avif": "img",

    # PDFs
    "pdf": "pdf",

    # Docs (fill later)
    "doc": "docs", "docx": "docs", "txt": "docs", "md": "docs", "rtf": "docs",

    # Audio/Video (if needed)
    "mp3": "advance", "wav": "advance", "aac": "advance",
    "mp4": "advance", "mkv": "advance", "mov": "advance",
}
