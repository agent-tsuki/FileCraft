"""
Legacy file validation functions - kept for backward compatibility.
This functionality is now handled by the service layer.
"""
from os import path

from app.helpers.constants import EXTENSION_TYPE_MAP, MAX_UPLOAD_SIZE


def validate_file_size(file_size: int, _type: str) -> bool:
    """
    Legacy file size validation function.
    
    Note: This function is deprecated. Use app.services.file_validation.FileValidationService instead.
    """
    if not MAX_UPLOAD_SIZE.get(_type, None):
        return False
    return file_size <= MAX_UPLOAD_SIZE[_type]


def get_file_type(file_name: str) -> tuple[str, str]:
    """
    Legacy file type detection function.
    
    Note: This function is deprecated. Use app.services.file_validation.FileValidationService instead.
    """
    base, ext = path.splitext(file_name)
    ext = ext.lower().lstrip(".")
    return base, EXTENSION_TYPE_MAP.get(ext, ext or "unknown")
