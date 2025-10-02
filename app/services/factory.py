"""
Service factory for dependency injection.
"""
from functools import lru_cache
from typing import Dict, Type

from fastapi import Depends

from app.core.config import AppConfig, get_config
from app.services.base import BaseService
from app.services.base64 import Base64Service
from app.services.compression import CompressionService
from app.services.file_validation import FileValidationService
from app.services.image import ImageService


class ServiceFactory:
    """Factory for creating and managing services."""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self._services: Dict[Type[BaseService], BaseService] = {}
    
    def get_service(self, service_class: Type[BaseService]) -> BaseService:
        """Get or create a service instance."""
        if service_class not in self._services:
            if service_class == FileValidationService:
                self._services[service_class] = FileValidationService(self.config)
            elif service_class == Base64Service:
                validation_service = self.get_service(FileValidationService)
                self._services[service_class] = Base64Service(self.config, validation_service)
            elif service_class == ImageService:
                validation_service = self.get_service(FileValidationService)
                self._services[service_class] = ImageService(self.config, validation_service)
            elif service_class == CompressionService:
                validation_service = self.get_service(FileValidationService)
                self._services[service_class] = CompressionService(self.config, validation_service)
            else:
                raise ValueError(f"Unknown service class: {service_class}")
        
        return self._services[service_class]


@lru_cache()
def get_service_factory(config: AppConfig = Depends(get_config)) -> ServiceFactory:
    """Get cached service factory."""
    return ServiceFactory(config)