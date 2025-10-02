"""
Logging configuration for the FileCraft application.
"""

import logging
import sys
from typing import Any, Dict

from config.settings import settings


def setup_logging() -> None:
    """Configure application logging."""

    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt="%(asctime)s | %(name)s | %(levelname)s | %(message)s | %(pathname)s:%(lineno)d",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    simple_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO if not settings.DEBUG else logging.DEBUG)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)

    # Application logger
    app_logger = logging.getLogger("app")
    app_logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

    # File handler for errors (optional, uncomment if needed)
    # if not settings.DEBUG:
    #     file_handler = logging.FileHandler("logs/error.log")
    #     file_handler.setLevel(logging.ERROR)
    #     file_handler.setFormatter(detailed_formatter)
    #     root_logger.addHandler(file_handler)

    # Third-party loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)

    app_logger.info("Logging configuration completed")


class StructuredLogger:
    """Structured logger for consistent log formatting."""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message with structured data."""
        extra_data = self._format_extra(**kwargs)
        self.logger.info(f"{message} {extra_data}".strip())

    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message with structured data."""
        extra_data = self._format_extra(**kwargs)
        self.logger.error(f"{message} {extra_data}".strip())

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message with structured data."""
        extra_data = self._format_extra(**kwargs)
        self.logger.warning(f"{message} {extra_data}".strip())

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message with structured data."""
        extra_data = self._format_extra(**kwargs)
        self.logger.debug(f"{message} {extra_data}".strip())

    def _format_extra(self, **kwargs: Any) -> str:
        """Format extra data for logging."""
        if not kwargs:
            return ""

        formatted = []
        for key, value in kwargs.items():
            formatted.append(f"{key}={value}")

        return f"[{', '.join(formatted)}]"
