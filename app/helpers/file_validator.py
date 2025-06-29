from os import path
from app.helpers.constants import MAX_UPLOAD_SIZE, EXTENSION_TYPE_MAP


def validate_file_size(file_size: int, _type: str) -> bool:
    if not MAX_UPLOAD_SIZE.get(_type, None):
        return False
    return file_size <= MAX_UPLOAD_SIZE[_type]

def get_file_type(file_name: str) -> tuple[str, str]:
    base, ext = path.splitext(file_name)
    ext = ext.lower().lstrip(".")
    return base, EXTENSION_TYPE_MAP.get(ext, ext or "unknown")
