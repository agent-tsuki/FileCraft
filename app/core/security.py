"""
Security configuration and authentication schemas (configuration only).
Authentication implementation is not included.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from enum import Enum

from pydantic import BaseModel, Field

from app.core.config import get_app_config

# Optional imports for authentication (not implemented)
try:
    from passlib.context import CryptContext

    PASSLIB_AVAILABLE = True
except ImportError:
    PASSLIB_AVAILABLE = False

try:
    from jose import JWTError, jwt

    JOSE_AVAILABLE = True
except ImportError:
    JOSE_AVAILABLE = False


class AuthenticationMethod(str, Enum):
    """Available authentication methods."""

    JWT = "jwt"
    API_KEY = "api_key"
    BASIC = "basic"
    OAUTH2 = "oauth2"
    BEARER = "bearer"


class UserRole(str, Enum):
    """User roles for authorization."""

    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"
    PREMIUM = "premium"
    API_CLIENT = "api_client"


class PermissionScope(str, Enum):
    """Permission scopes for different operations."""

    # File operations
    FILE_READ = "file:read"
    FILE_WRITE = "file:write"
    FILE_DELETE = "file:delete"

    # Processing operations
    PROCESS_IMAGE = "process:image"
    PROCESS_AUDIO = "process:audio"
    PROCESS_VIDEO = "process:video"
    PROCESS_DOCUMENT = "process:document"

    # Encoding/Decoding
    ENCODE_DECODE = "encode:decode"

    # Admin operations
    ADMIN_READ = "admin:read"
    ADMIN_WRITE = "admin:write"

    # System operations
    SYSTEM_MONITOR = "system:monitor"
    SYSTEM_CONFIG = "system:config"


class SecurityConfig(BaseModel):
    """Security configuration model."""

    # JWT Configuration
    jwt_secret_key: str = Field(..., description="JWT secret key")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_access_token_expire_minutes: int = Field(
        default=15, description="JWT access token expiry in minutes"
    )
    jwt_refresh_token_expire_days: int = Field(
        default=30, description="JWT refresh token expiry in days"
    )

    # API Key Configuration
    api_key_header: str = Field(default="X-API-Key", description="API key header name")
    enable_api_key_auth: bool = Field(
        default=False, description="Enable API key authentication"
    )

    # Password Configuration
    password_min_length: int = Field(default=8, description="Minimum password length")
    password_require_uppercase: bool = Field(
        default=True, description="Require uppercase letters"
    )
    password_require_lowercase: bool = Field(
        default=True, description="Require lowercase letters"
    )
    password_require_digits: bool = Field(default=True, description="Require digits")
    password_require_special: bool = Field(
        default=True, description="Require special characters"
    )

    # Session Configuration
    session_timeout_minutes: int = Field(
        default=30, description="Session timeout in minutes"
    )
    max_login_attempts: int = Field(
        default=5, description="Maximum login attempts before lockout"
    )
    lockout_duration_minutes: int = Field(
        default=15, description="Account lockout duration in minutes"
    )

    # Rate Limiting for Auth
    auth_rate_limit_requests: int = Field(
        default=10, description="Auth requests per window"
    )
    auth_rate_limit_window: int = Field(
        default=900, description="Auth rate limit window in seconds (15 minutes)"
    )

    # OAuth2 Configuration (placeholder)
    oauth2_enabled: bool = Field(
        default=False, description="Enable OAuth2 authentication"
    )
    oauth2_providers: List[str] = Field(
        default=[], description="Supported OAuth2 providers"
    )

    class Config:
        use_enum_values = True


class TokenConfig(BaseModel):
    """Token configuration model."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: Optional[str] = Field(None, description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiry time in seconds")
    scope: List[str] = Field(default=[], description="Token scopes")


class UserCredentials(BaseModel):
    """User credentials model (for documentation)."""

    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=8, description="Password")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "user@example.com",
                "password": "SecurePassword123!",
            }
        }


class APIKeyConfig(BaseModel):
    """API key configuration model."""

    key_id: str = Field(..., description="API key identifier")
    key_name: str = Field(..., description="Human-readable key name")
    scopes: List[PermissionScope] = Field(default=[], description="API key permissions")
    is_active: bool = Field(default=True, description="Whether the key is active")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )
    expires_at: Optional[datetime] = Field(None, description="Expiry timestamp")
    last_used: Optional[datetime] = Field(None, description="Last usage timestamp")
    usage_count: int = Field(default=0, description="Number of times used")
    rate_limit_per_hour: Optional[int] = Field(
        None, description="Requests per hour limit"
    )

    class Config:
        use_enum_values = True


class RolePermissionMatrix(BaseModel):
    """Role-based permission matrix configuration."""

    role: UserRole
    permissions: List[PermissionScope]
    description: str = Field(..., description="Role description")

    class Config:
        use_enum_values = True


# Default role permissions configuration
DEFAULT_ROLE_PERMISSIONS = [
    RolePermissionMatrix(
        role=UserRole.GUEST,
        permissions=[
            PermissionScope.FILE_READ,
            PermissionScope.ENCODE_DECODE,
        ],
        description="Guest users with basic read and encode/decode permissions",
    ),
    RolePermissionMatrix(
        role=UserRole.USER,
        permissions=[
            PermissionScope.FILE_READ,
            PermissionScope.FILE_WRITE,
            PermissionScope.PROCESS_IMAGE,
            PermissionScope.PROCESS_AUDIO,
            PermissionScope.PROCESS_DOCUMENT,
            PermissionScope.ENCODE_DECODE,
        ],
        description="Regular users with file processing permissions",
    ),
    RolePermissionMatrix(
        role=UserRole.PREMIUM,
        permissions=[
            PermissionScope.FILE_READ,
            PermissionScope.FILE_WRITE,
            PermissionScope.FILE_DELETE,
            PermissionScope.PROCESS_IMAGE,
            PermissionScope.PROCESS_AUDIO,
            PermissionScope.PROCESS_VIDEO,
            PermissionScope.PROCESS_DOCUMENT,
            PermissionScope.ENCODE_DECODE,
        ],
        description="Premium users with advanced processing capabilities",
    ),
    RolePermissionMatrix(
        role=UserRole.API_CLIENT,
        permissions=[
            PermissionScope.FILE_READ,
            PermissionScope.FILE_WRITE,
            PermissionScope.PROCESS_IMAGE,
            PermissionScope.PROCESS_AUDIO,
            PermissionScope.PROCESS_VIDEO,
            PermissionScope.PROCESS_DOCUMENT,
            PermissionScope.ENCODE_DECODE,
        ],
        description="API clients with programmatic access",
    ),
    RolePermissionMatrix(
        role=UserRole.ADMIN,
        permissions=list(PermissionScope),  # All permissions
        description="Administrators with full system access",
    ),
]


class SecurityHeaders(BaseModel):
    """Security headers configuration."""

    # CORS headers
    access_control_allow_origin: str = "*"
    access_control_allow_methods: str = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
    access_control_allow_headers: str = "Content-Type, Authorization, X-API-Key"
    access_control_allow_credentials: bool = True

    # Security headers
    x_content_type_options: str = "nosniff"
    x_frame_options: str = "DENY"
    x_xss_protection: str = "1; mode=block"
    strict_transport_security: str = "max-age=31536000; includeSubDomains"
    content_security_policy: str = (
        "default-src 'self'; connect-src 'self'; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fastapi.tiangolo.com; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; img-src 'self' data: https://fastapi.tiangolo.com https://cdn.jsdelivr.net; font-src 'self' https://cdn.jsdelivr.net"
    )
    referrer_policy: str = "strict-origin-when-cross-origin"

    # Custom headers
    x_api_version: str = "v1.2.0"
    x_rate_limit_limit: Optional[int] = None
    x_rate_limit_remaining: Optional[int] = None
    x_rate_limit_reset: Optional[int] = None


def get_security_config() -> SecurityConfig:
    """Get security configuration from app config."""
    config = get_app_config()

    return SecurityConfig(
        jwt_secret_key=config.jwt_secret_key,
        jwt_algorithm=config.jwt_algorithm,
        jwt_access_token_expire_minutes=config.jwt_access_token_expire_minutes,
        jwt_refresh_token_expire_days=config.jwt_refresh_token_expire_days,
        api_key_header=config.api_key_header,
        enable_api_key_auth=config.enable_api_key_auth,
    )


def get_default_security_headers() -> Dict[str, str]:
    """Get default security headers (excluding CORS headers which are handled by CORSMiddleware)."""
    headers = SecurityHeaders()

    return {
        # Note: CORS headers are handled by FastAPI's CORSMiddleware, not here
        # "Access-Control-Allow-Origin": headers.access_control_allow_origin,
        # "Access-Control-Allow-Methods": headers.access_control_allow_methods,
        # "Access-Control-Allow-Headers": headers.access_control_allow_headers,
        "X-Content-Type-Options": headers.x_content_type_options,
        "X-Frame-Options": headers.x_frame_options,
        "X-XSS-Protection": headers.x_xss_protection,
        "Strict-Transport-Security": headers.strict_transport_security,
        "Content-Security-Policy": headers.content_security_policy,
        "Referrer-Policy": headers.referrer_policy,
        "X-API-Version": headers.x_api_version,
    }


# Password context for hashing (configuration only)
if PASSLIB_AVAILABLE:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
else:
    pwd_context = None  # Authentication not implemented


class AuthenticationSchemes:
    """Authentication scheme configurations for OpenAPI documentation."""

    @staticmethod
    def get_jwt_scheme() -> Dict[str, Any]:
        """JWT Bearer token scheme."""
        return {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter JWT token (authentication not implemented)",
        }

    @staticmethod
    def get_api_key_scheme() -> Dict[str, Any]:
        """API Key scheme."""
        return {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "Enter API key (authentication not implemented)",
        }

    @staticmethod
    def get_basic_scheme() -> Dict[str, Any]:
        """Basic authentication scheme."""
        return {
            "type": "http",
            "scheme": "basic",
            "description": "Basic HTTP authentication (authentication not implemented)",
        }

    @staticmethod
    def get_oauth2_scheme() -> Dict[str, Any]:
        """OAuth2 scheme."""
        return {
            "type": "oauth2",
            "flows": {
                "authorizationCode": {
                    "authorizationUrl": "/auth/oauth2/authorize",
                    "tokenUrl": "/auth/oauth2/token",
                    "scopes": {
                        "read": "Read access",
                        "write": "Write access",
                        "admin": "Admin access",
                    },
                }
            },
            "description": "OAuth2 authentication (authentication not implemented)",
        }


# Export commonly used configurations
__all__ = [
    "AuthenticationMethod",
    "UserRole",
    "PermissionScope",
    "SecurityConfig",
    "TokenConfig",
    "UserCredentials",
    "APIKeyConfig",
    "RolePermissionMatrix",
    "SecurityHeaders",
    "DEFAULT_ROLE_PERMISSIONS",
    "AuthenticationSchemes",
    "get_security_config",
    "get_default_security_headers",
    "pwd_context",
]
