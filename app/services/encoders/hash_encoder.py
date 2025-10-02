"""
Hash encoder service for various hash algorithms.
"""
import hashlib
import hmac
from typing import Union, BinaryIO, Optional
from fastapi import UploadFile, HTTPException

from .base_encoder import BaseEncoderService


class HashEncoderService(BaseEncoderService):
    """
    Service for hash encoding operations (MD5, SHA1, SHA256, etc.).
    """
    
    def __init__(self):
        super().__init__()
        self.encoding_name = "hash"
        self.supported_algorithms = hashlib.algorithms_available
        self.common_algorithms = [
            'md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512',
            'sha3_224', 'sha3_256', 'sha3_384', 'sha3_512',
            'blake2b', 'blake2s'
        ]
    
    async def encode(
        self, 
        data: Union[str, bytes, BinaryIO, UploadFile], 
        **kwargs
    ) -> str:
        """
        Generate hash of data.
        
        Args:
            data: Input data to hash
            **kwargs: Additional parameters
                - algorithm: Hash algorithm (default: 'sha256')
                - output_format: Output format 'hex'/'base64'/'bytes' (default: 'hex')
                - salt: Salt for hashing (default: None)
                - hmac_key: Key for HMAC (default: None)
                
        Returns:
            Hash string
        """
        if not self.validate_input(data):
            raise ValueError("Invalid input data")
        
        if isinstance(data, UploadFile):
            return await self.encode_file(data, **kwargs)
        
        # Prepare data as bytes
        byte_data = self._prepare_data(data)
        
        # Get algorithm and validate
        algorithm = kwargs.get('algorithm', 'sha256').lower()
        if algorithm not in self.supported_algorithms:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported hash algorithm: {algorithm}. Supported: {list(self.common_algorithms)}"
            )
        
        # Add salt if provided
        salt = kwargs.get('salt')
        if salt:
            if isinstance(salt, str):
                salt = salt.encode('utf-8')
            byte_data = salt + byte_data
        
        # Check for HMAC
        hmac_key = kwargs.get('hmac_key')
        if hmac_key:
            if isinstance(hmac_key, str):
                hmac_key = hmac_key.encode('utf-8')
            hash_obj = hmac.new(hmac_key, byte_data, getattr(hashlib, algorithm))
            hash_bytes = hash_obj.digest()
        else:
            # Regular hash
            hash_obj = hashlib.new(algorithm)
            hash_obj.update(byte_data)
            hash_bytes = hash_obj.digest()
        
        # Format output
        output_format = kwargs.get('output_format', 'hex').lower()
        return self._format_hash_output(hash_bytes, output_format)
    
    async def encode_file(
        self, 
        file: UploadFile, 
        **kwargs
    ) -> str:
        """
        Generate hash of file content.
        
        Args:
            file: Input file to hash
            **kwargs: Additional parameters
                
        Returns:
            Hash string
        """
        content = await self._read_file_content(file)
        return await self.encode(content, **kwargs)
    
    async def encode_stream(
        self, 
        data: Union[str, bytes, BinaryIO, UploadFile], 
        **kwargs
    ):
        """
        Generate hash as stream (for large files).
        
        Args:
            data: Input data
            **kwargs: Additional parameters
                - chunk_size: Chunk size for streaming (default: 8192)
                
        Yields:
            Final hash result
        """
        if isinstance(data, UploadFile):
            algorithm = kwargs.get('algorithm', 'sha256').lower()
            hash_obj = hashlib.new(algorithm)
            
            chunk_size = kwargs.get('chunk_size', 8192)
            
            while True:
                chunk = await data.read(chunk_size)
                if not chunk:
                    break
                hash_obj.update(chunk)
            
            await data.seek(0)  # Reset file position
            
            hash_bytes = hash_obj.digest()
            output_format = kwargs.get('output_format', 'hex').lower()
            result = self._format_hash_output(hash_bytes, output_format)
            
            yield result.encode('utf-8')
        else:
            # For non-file data, use regular encode
            result = await self.encode(data, **kwargs)
            yield result.encode('utf-8')
    
    async def verify_hash(
        self, 
        data: Union[str, bytes], 
        expected_hash: str, 
        **kwargs
    ) -> bool:
        """
        Verify data against expected hash.
        
        Args:
            data: Data to verify
            expected_hash: Expected hash value
            **kwargs: Hash parameters
            
        Returns:
            True if hash matches, False otherwise
        """
        try:
            computed_hash = await self.encode(data, **kwargs)
            return computed_hash.lower() == expected_hash.lower()
        except Exception:
            return False
    
    def get_algorithm_info(self, algorithm: str) -> dict:
        """
        Get information about hash algorithm.
        
        Args:
            algorithm: Algorithm name
            
        Returns:
            Algorithm information
        """
        algorithm = algorithm.lower()
        
        if algorithm not in self.supported_algorithms:
            raise HTTPException(status_code=400, detail=f"Unsupported algorithm: {algorithm}")
        
        try:
            hash_obj = hashlib.new(algorithm)
            return {
                "name": algorithm,
                "digest_size": hash_obj.digest_size,
                "block_size": getattr(hash_obj, 'block_size', None),
                "supported": True
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get algorithm info: {str(e)}")
    
    def list_algorithms(self) -> dict:
        """
        List all supported hash algorithms.
        
        Returns:
            Dictionary with algorithm categories
        """
        return {
            "common": self.common_algorithms,
            "all_available": sorted(list(self.supported_algorithms)),
            "count": len(self.supported_algorithms)
        }
    
    def _format_hash_output(self, hash_bytes: bytes, output_format: str) -> str:
        """
        Format hash output in requested format.
        
        Args:
            hash_bytes: Hash bytes
            output_format: Output format
            
        Returns:
            Formatted hash string
        """
        if output_format == 'hex':
            return hash_bytes.hex()
        elif output_format == 'base64':
            import base64
            return base64.b64encode(hash_bytes).decode('ascii')
        elif output_format == 'bytes':
            return str(hash_bytes)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported output format: {output_format}")
    
    def get_output_filename(self, original_filename: str, **kwargs) -> str:
        """
        Generate output filename for hash.
        
        Args:
            original_filename: Original filename
            **kwargs: Additional parameters
            
        Returns:
            Generated output filename
        """
        algorithm = kwargs.get('algorithm', 'sha256').lower()
        
        if not original_filename or original_filename == "unknown":
            return f"hash.{algorithm}"
        
        return f"{original_filename}.{algorithm}"
    
    def get_content_type(self) -> str:
        """
        Get content type for hash output.
        
        Returns:
            Content type string
        """
        return "text/plain"
    
    def validate_input(self, data) -> bool:
        """
        Validate input data for hashing.
        
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
            return True
        
        if hasattr(data, 'read'):
            return True
        
        return False


# Dependency injection
def get_hash_encoder_service() -> HashEncoderService:
    """
    Dependency injection for HashEncoderService.
    
    Returns:
        HashEncoderService instance
    """
    return HashEncoderService()