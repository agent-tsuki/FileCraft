"""
Advanced FastAPI and OpenAPI configuration.
"""
from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from fastapi.openapi.models import OpenAPI, Info, Contact, License, Tag
from fastapi.openapi.utils import get_openapi

from app.core.config import get_app_config
from app.core.security import AuthenticationSchemes


def get_openapi_schema(app: FastAPI) -> Dict[str, Any]:
    """
    Generate custom OpenAPI schema with enhanced security definitions.
    """
    config = get_app_config()
    
    if app.openapi_schema:
        return app.openapi_schema
    
    # Get basic OpenAPI schema
    openapi_schema = get_openapi(
        title=config.project_name,
        version=config.version,
        description=config.project_description,
        routes=app.routes,
        servers=[
            {
                "url": f"http://{config.host}:{config.port}",
                "description": f"{config.environment.title()} server"
            }
        ]
    )
    
    # Add custom info
    openapi_schema["info"]["contact"] = {
        "name": config.contact_name,
        "email": config.contact_email,
        "url": config.contact_url
    }
    
    openapi_schema["info"]["license"] = {
        "name": config.license_name,
        "url": config.license_url
    }
    
    openapi_schema["info"]["termsOfService"] = config.terms_of_service
    
    # Add external documentation
    openapi_schema["externalDocs"] = {
        "description": "FileCraft Documentation",
        "url": "https://docs.filecraft.com"
    }
    
    # Add security schemes (documentation only - not implemented)
    auth_schemes = AuthenticationSchemes()
    openapi_schema["components"]["securitySchemes"] = {
        "JWTBearer": auth_schemes.get_jwt_scheme(),
        "ApiKeyAuth": auth_schemes.get_api_key_scheme(),
        "BasicAuth": auth_schemes.get_basic_scheme(),
        "OAuth2": auth_schemes.get_oauth2_scheme()
    }
    
    # Add custom extensions
    openapi_schema["x-logo"] = {
        "url": "https://filecraft.com/logo.png",
        "altText": "FileCraft Logo"
    }
    
    # Add API versioning information
    openapi_schema["x-api-version"] = config.version
    openapi_schema["x-api-release-date"] = "2025-10-02"
    openapi_schema["x-api-status"] = "stable"
    
    # Add rate limiting information
    rate_limit_config = config.get_rate_limit_config()
    if rate_limit_config["enabled"]:
        openapi_schema["x-rate-limiting"] = {
            "requests-per-window": rate_limit_config["requests"],
            "window-seconds": rate_limit_config["window"],
            "per-ip-limit": rate_limit_config["per_ip"]
        }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


def get_api_tags() -> List[Dict[str, Any]]:
    """
    Get API tags with descriptions for better documentation organization.
    """
    return [
        {
            "name": "System",
            "description": "System health, monitoring, and status endpoints",
            "externalDocs": {
                "description": "System monitoring guide",
                "url": "https://docs.filecraft.com/monitoring"
            }
        },
        {
            "name": "Authentication",
            "description": "Authentication and authorization endpoints (Not implemented - Configuration only)",
            "externalDocs": {
                "description": "Authentication documentation",
                "url": "https://docs.filecraft.com/auth"
            }
        },
        {
            "name": "File Management",
            "description": "File upload, download, and management operations",
            "externalDocs": {
                "description": "File management guide",
                "url": "https://docs.filecraft.com/files"
            }
        },
        {
            "name": "Image Processing", 
            "description": "Image format conversion, resizing, and optimization",
            "externalDocs": {
                "description": "Image processing documentation",
                "url": "https://docs.filecraft.com/images"
            }
        },
        {
            "name": "Audio Processing",
            "description": "Audio format conversion, compression, and metadata editing",
            "externalDocs": {
                "description": "Audio processing guide",
                "url": "https://docs.filecraft.com/audio"
            }
        },
        {
            "name": "Video Processing",
            "description": "Video format conversion, compression, and editing",
            "externalDocs": {
                "description": "Video processing documentation", 
                "url": "https://docs.filecraft.com/video"
            }
        },
        {
            "name": "Document Processing",
            "description": "Document format conversion and text extraction",
            "externalDocs": {
                "description": "Document processing guide",
                "url": "https://docs.filecraft.com/documents"
            }
        },
        {
            "name": "Encoding/Decoding",
            "description": "Text and data encoding/decoding operations (Base64, Hex, URL, etc.)",
            "externalDocs": {
                "description": "Encoding guide",
                "url": "https://docs.filecraft.com/encoding"
            }
        },
        {
            "name": "Compression",
            "description": "File compression, archiving, and extraction",
            "externalDocs": {
                "description": "Compression documentation",
                "url": "https://docs.filecraft.com/compression"
            }
        },
        {
            "name": "JWT Operations",
            "description": "JWT token encoding, decoding, and validation (No authentication required)",
            "externalDocs": {
                "description": "JWT operations guide",
                "url": "https://docs.filecraft.com/jwt"
            }
        },
        {
            "name": "Hash Operations", 
            "description": "Cryptographic hashing operations (MD5, SHA1, SHA256, etc.)",
            "externalDocs": {
                "description": "Hashing documentation",
                "url": "https://docs.filecraft.com/hashing"
            }
        },
        {
            "name": "Base64 Operations",
            "description": "Base64 encoding and decoding for text and files",
            "externalDocs": {
                "description": "Base64 operations guide", 
                "url": "https://docs.filecraft.com/base64"
            }
        }
    ]


def get_swagger_ui_config() -> Dict[str, Any]:
    """
    Get Swagger UI configuration for enhanced documentation experience.
    """
    return {
        "deepLinking": True,
        "displayOperationId": False,
        "defaultModelsExpandDepth": 1,
        "defaultModelExpandDepth": 1,  
        "defaultModelRendering": "example",
        "displayRequestDuration": True,
        "docExpansion": "list",
        "filter": True,
        "showExtensions": True,
        "showCommonExtensions": True,
        "tryItOutEnabled": True,
        "persistAuthorization": True,
    }


def get_redoc_config() -> Dict[str, Any]:
    """
    Get ReDoc configuration for alternative documentation.
    """
    return {
        "expandResponses": "200,201",
        "hideDownloadButton": False,
        "hideHostname": False,
        "hideLoading": False,
        "menuToggle": True,
        "nativeScrollbars": False,
        "noAutoAuth": False,
        "onlyRequiredInSamples": False,
        "pathInMiddlePanel": False,
        "requiredPropsFirst": False,
        "scrollYOffset": 0,
        "showExtensions": True,
        "sortPropsAlphabetically": True,
        "suppressWarnings": False,
        "theme": {
            "colors": {
                "primary": {
                    "main": "#32329f"
                }
            },
            "typography": {
                "fontSize": "14px",
                "lineHeight": "1.5em",
                "code": {
                    "fontSize": "13px",
                    "fontFamily": "Courier, monospace"
                },
                "headings": {
                    "fontFamily": "Montserrat, sans-serif",
                    "fontWeight": "400"
                }
            },
            "sidebar": {
                "width": "260px"
            },
            "rightPanel": {
                "backgroundColor": "#263238",
                "width": "40%"
            }
        }
    }


class APIConfiguration:
    """
    Centralized API configuration class.
    """
    
    def __init__(self):
        self.config = get_app_config()
        
    def get_app_metadata(self) -> Dict[str, Any]:
        """Get comprehensive application metadata."""
        return {
            "name": self.config.project_name,
            "version": self.config.version,
            "description": self.config.project_description,
            "environment": self.config.environment,
            "debug": self.config.debug,
            "features": {
                "authentication": False,  # Not implemented
                "rate_limiting": self.config.rate_limit_enabled,
                "async_processing": self.config.enable_async_processing,
                "batch_processing": self.config.enable_batch_processing,
                "real_time_processing": self.config.enable_real_time_processing,
                "webhooks": self.config.enable_webhooks,
                "metrics": self.config.enable_metrics,
                "health_checks": self.config.enable_health_check,
                "admin_panel": self.config.enable_admin_panel,
                "s3_storage": self.config.enable_s3_storage,
                "email_notifications": self.config.enable_email_notifications,
                "response_cache": self.config.enable_response_cache,
                "profiling": self.config.enable_profiling,
            },
            "limits": {
                "max_upload_size": self.config.max_upload_size,
                "max_concurrent_tasks": self.config.max_concurrent_tasks,
                "task_timeout": self.config.task_timeout,
                "rate_limit_requests": self.config.rate_limit_requests if self.config.rate_limit_enabled else None,
                "rate_limit_window": self.config.rate_limit_window if self.config.rate_limit_enabled else None,
            },
            "supported_formats": {
                "images": ["jpg", "jpeg", "png", "gif", "bmp", "webp", "tiff", "svg"],
                "audio": ["mp3", "wav", "flac", "aac", "ogg", "m4a", "wma"],
                "video": ["mp4", "avi", "mkv", "mov", "wmv", "flv", "webm", "m4v"],
                "documents": ["pdf", "txt", "doc", "docx", "rtf", "odt"],
                "archives": ["zip", "rar", "7z", "tar", "gz", "bz2"],
            },
            "endpoints": {
                "documentation": self.config.docs_url,
                "redoc": self.config.redoc_url,
                "openapi": self.config.openapi_url,
                "health": self.config.health_check_endpoint,
                "metrics": self.config.metrics_endpoint if self.config.enable_metrics else None,
            }
        }
    
    def get_security_requirements(self) -> List[Dict[str, List[str]]]:
        """Get security requirements for endpoints (documentation only)."""
        return [
            # No security required (authentication not implemented)
            {},
            # Optional API key (if configured)
            {"ApiKeyAuth": []} if self.config.enable_api_key_auth else {},
            # Optional JWT (documentation only)
            {"JWTBearer": []},
            # Optional Basic Auth (documentation only)
            {"BasicAuth": []},
        ]
    
    def get_example_responses(self) -> Dict[str, Any]:
        """Get example responses for common scenarios."""
        return {
            "success": {
                "status": "success",
                "message": "Operation completed successfully",
                "data": {},
                "timestamp": "2025-10-02T12:00:00Z"
            },
            "error": {
                "status": "error",
                "message": "An error occurred",
                "error_code": "GENERIC_ERROR",
                "timestamp": "2025-10-02T12:00:00Z"
            },
            "validation_error": {
                "status": "error",
                "message": "Validation failed",
                "error_code": "VALIDATION_ERROR",
                "details": [
                    {
                        "field": "field_name",
                        "message": "Field is required"
                    }
                ],
                "timestamp": "2025-10-02T12:00:00Z"
            },
            "rate_limit_exceeded": {
                "status": "error",
                "message": "Rate limit exceeded",
                "error_code": "RATE_LIMIT_EXCEEDED",
                "retry_after": 3600,
                "timestamp": "2025-10-02T12:00:00Z"
            },
            "unauthorized": {
                "status": "error",
                "message": "Authentication required (not implemented)",
                "error_code": "UNAUTHORIZED",
                "timestamp": "2025-10-02T12:00:00Z"
            },
            "forbidden": {
                "status": "error",
                "message": "Insufficient permissions (not implemented)",
                "error_code": "FORBIDDEN",
                "timestamp": "2025-10-02T12:00:00Z"
            }
        }


# Global API configuration instance
api_config = APIConfiguration()


# Export main functions and classes
__all__ = [
    "get_openapi_schema",
    "get_api_tags", 
    "get_swagger_ui_config",
    "get_redoc_config",
    "APIConfiguration",
    "api_config"
]