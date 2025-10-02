"""
Base service class with common functionality.
"""
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from fastapi import Depends

from app.core.config import AppConfig, get_config

logger = logging.getLogger(__name__)


class BaseService(ABC):
    """Base service class with dependency injection."""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def log_operation(self, operation: str, details: Optional[Dict[str, Any]] = None):
        """Log service operations."""
        if details:
            # Convert details to a safe format for logging
            safe_details = {f"operation_{k}": v for k, v in details.items()}
            self.logger.info(f"Operation: {operation} - Details: {details}")
        else:
            self.logger.info(f"Operation: {operation}")