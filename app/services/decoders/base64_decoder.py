"""
Base64 decoder service.
"""
import base64
from typing import Union, BinaryIO
from fastapi import UploadFile, HTTPException

from .base_decoder import BaseDecoderService


class Base64DecoderService(BaseDecoderService):
    """
    Service for Base64 decoding operations.
    """
    
    def __init__(self):
        super().__init__()
        self.decoding_name = "base64"
    
    async def decode(
        self, 
        data: Union[str, bytes, BinaryIO, UploadFile], 
        **kwargs
    ) -> bytes:
        """
        Decode Base64 data.
        
        Args:
            data: Input Base64 data to decode
            **kwargs: Additional parameters
                - url_safe: Use URL-safe Base64 decoding (default: auto-detect)
                - validate: Validate Base64 format (default: True)
                
        Returns:
            Decoded bytes
        """
        if not self.validate_input(data):
            raise ValueError("Invalid input data")
        
        if isinstance(data, UploadFile):
            return await self.decode_file(data, **kwargs)
        
        # Prepare data as string
        string_data = self._prepare_data(data)
        if isinstance(string_data, bytes):
            string_data = string_data.decode('utf-8')
        
        # Clean the input (remove whitespace and newlines)
        string_data = ''.join(string_data.split())
        
        # Validate Base64 format if requested
        if kwargs.get('validate', True):
            if not self._is_valid_base64(string_data):
                raise HTTPException(status_code=400, detail="Invalid Base64 format")
        
        # Auto-detect URL-safe or use explicit parameter
        url_safe = kwargs.get('url_safe')
        if url_safe is None:
            url_safe = self._is_url_safe_base64(string_data)
        
        try:
            if url_safe:
                # Add padding if necessary
                string_data = self._add_padding(string_data)
                decoded_bytes = base64.urlsafe_b64decode(string_data)
            else:
                decoded_bytes = base64.b64decode(string_data)
            
            return decoded_bytes
        
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Base64 decoding failed: {str(e)}")
    
    async def decode_file(
        self, 
        file: UploadFile, 
        **kwargs
    ) -> bytes:
        """
        Decode Base64 file content.
        
        Args:
            file: Input file containing Base64 data
            **kwargs: Additional parameters
                - url_safe: Use URL-safe Base64 decoding (default: auto-detect)
                - validate: Validate Base64 format (default: True)
                
        Returns:
            Decoded bytes
        """
        content = await self._read_file_content(file)
        
        # Convert bytes to string if necessary
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        
        return await self.decode(content, **kwargs)
    
    def _is_valid_base64(self, s: str) -> bool:
        """
        Check if string is valid Base64.
        
        Args:
            s: String to validate
            
        Returns:
            True if valid Base64, False otherwise
        """
        import re
        
        # Check for valid Base64 characters
        if not re.match(r'^[A-Za-z0-9+/]*={0,2}$', s) and not re.match(r'^[A-Za-z0-9_-]*$', s):
            return False
        
        # Check length (must be multiple of 4 for standard Base64)
        if not self._is_url_safe_base64(s) and len(s) % 4 != 0:
            return False
        
        return True
    
    def _is_url_safe_base64(self, s: str) -> bool:
        """
        Check if string is URL-safe Base64.
        
        Args:
            s: String to check
            
        Returns:
            True if URL-safe Base64, False otherwise
        """
        return '-' in s or '_' in s
    
    def _add_padding(self, s: str) -> str:
        """
        Add padding to Base64 string if necessary.
        
        Args:
            s: Base64 string
            
        Returns:
            Padded Base64 string
        """
        missing_padding = len(s) % 4
        if missing_padding:
            s += '=' * (4 - missing_padding)
        return s
    
    def validate_input(self, data) -> bool:
        """
        Validate input data for Base64 decoding.
        
        Args:
            data: Input data to validate
            
        Returns:
            True if valid, False otherwise
        """
        if data is None:
            return False
        
        if isinstance(data, UploadFile):
            return True
        
        if isinstance(data, (str, bytes)):
            return len(str(data).strip()) > 0
        
        if hasattr(data, 'read'):
            return True
        
        return False
    
    def get_output_filename(self, original_filename: str, **kwargs) -> str:
        """
        Generate output filename for decoded data.
        
        Args:
            original_filename: Original filename
            **kwargs: Additional parameters
            
        Returns:
            Generated output filename
        """
        if not original_filename or original_filename == "unknown":
            return "decoded"
        
        # Remove Base64 extensions
        for ext in ['.b64', '.b64url', '.base64']:
            if original_filename.endswith(ext):
                return original_filename[:-len(ext)]
        
        return f"{original_filename}.decoded"


# Dependency injection
def get_base64_decoder_service() -> Base64DecoderService:
    """
    Dependency injection for Base64DecoderService.
    
    Returns:
        Base64DecoderService instance
    """
    return Base64DecoderService()