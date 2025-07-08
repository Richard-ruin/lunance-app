# app/middleware/auth.py
"""Authentication middleware and dependencies."""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List
import logging

from ..models.user import UserRole, UserInDB
from ..services.auth_service import AuthService, AuthenticationError
from ..utils.jwt import verify_token, TokenExpiredError, InvalidTokenError

logger = logging.getLogger(__name__)

# HTTP Bearer token security
security = HTTPBearer(auto_error=False)


class AuthenticationMiddleware:
    """Authentication middleware class."""
    
    def __init__(self):
        self.auth_service = AuthService()


# Authentication dependencies
async def get_auth_service() -> AuthService:
    """Get authentication service dependency."""
    return AuthService()


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> UserInDB:
    """
    Get current authenticated user.
    
    Args:
        credentials: HTTP authorization credentials
        auth_service: Authentication service
        
    Returns:
        Current user
        
    Raises:
        HTTPException: If authentication fails
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials not provided",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Verify token
        payload = verify_token(credentials.credentials)
        
        # Get user
        user = await auth_service.get_user_by_id(payload.sub)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is deactivated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
        
    except TokenExpiredError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: UserInDB = Depends(get_current_user)
) -> UserInDB:
    """
    Get current active user.
    
    Args:
        current_user: Current user from token
        
    Returns:
        Active user
        
    Raises:
        HTTPException: If user is not active or verified
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is deactivated"
        )
    
    return current_user


async def get_current_verified_user(
    current_user: UserInDB = Depends(get_current_active_user)
) -> UserInDB:
    """
    Get current verified user.
    
    Args:
        current_user: Current active user
        
    Returns:
        Verified user
        
    Raises:
        HTTPException: If user email is not verified
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email verification required"
        )
    
    return current_user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> Optional[UserInDB]:
    """
    Get optional authenticated user (doesn't raise error if not authenticated).
    
    Args:
        credentials: HTTP authorization credentials
        auth_service: Authentication service
        
    Returns:
        Current user or None if not authenticated
    """
    if not credentials:
        return None
    
    try:
        payload = verify_token(credentials.credentials)
        user = await auth_service.get_user_by_id(payload.sub)
        
        if user and user.is_active:
            return user
        return None
        
    except (TokenExpiredError, InvalidTokenError, Exception):
        return None


def require_roles(allowed_roles: List[UserRole]):
    """
    Create dependency that requires specific user roles.
    
    Args:
        allowed_roles: List of allowed user roles
        
    Returns:
        FastAPI dependency function
    """
    async def role_checker(
        current_user: UserInDB = Depends(get_current_verified_user)
    ) -> UserInDB:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    
    return role_checker


def require_admin():
    """Require admin role dependency."""
    return require_roles([UserRole.ADMIN])


def require_student():
    """Require student role dependency."""
    return require_roles([UserRole.STUDENT])


def require_admin_or_student():
    """Require admin or student role dependency."""
    return require_roles([UserRole.ADMIN, UserRole.STUDENT])


# Rate limiting middleware
from collections import defaultdict
from time import time
from ..config.settings import settings


class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self):
        self.requests = defaultdict(list)
        self.max_requests = settings.rate_limit_requests
        self.window_minutes = settings.rate_limit_minutes
    
    def is_allowed(self, identifier: str) -> bool:
        """
        Check if request is allowed for identifier.
        
        Args:
            identifier: Request identifier (IP, user ID, etc.)
            
        Returns:
            True if allowed, False if rate limited
        """
        now = time()
        window_start = now - (self.window_minutes * 60)
        
        # Clean old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier] 
            if req_time > window_start
        ]
        
        # Check if under limit
        if len(self.requests[identifier]) >= self.max_requests:
            return False
        
        # Add current request
        self.requests[identifier].append(now)
        return True


# Global rate limiter instance
rate_limiter = RateLimiter()


async def rate_limit_dependency(request: Request):
    """
    Rate limiting dependency.
    
    Args:
        request: FastAPI request object
        
    Raises:
        HTTPException: If rate limit exceeded
    """
    # Use IP address as identifier
    client_ip = request.client.host
    
    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )


# Security headers middleware
async def add_security_headers(request: Request, call_next):
    """
    Add security headers to response.
    
    Args:
        request: FastAPI request
        call_next: Next middleware/endpoint
        
    Returns:
        Response with security headers
    """
    response = await call_next(request)
    
    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    return response


# CORS headers for preflight requests
async def handle_cors_preflight(request: Request):
    """
    Handle CORS preflight requests.
    
    Args:
        request: FastAPI request
        
    Returns:
        CORS preflight response or None
    """
    if request.method == "OPTIONS":
        from fastapi.responses import Response
        
        response = Response()
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
        response.headers["Access-Control-Max-Age"] = "86400"
        
        return response
    
    return None


# Authentication utilities
def get_user_id_from_request(request: Request) -> Optional[str]:
    """
    Extract user ID from request authorization header.
    
    Args:
        request: FastAPI request
        
    Returns:
        User ID or None if not authenticated
    """
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        token = auth_header.split(" ")[1]
        payload = verify_token(token)
        return payload.sub
        
    except Exception:
        return None


def get_user_role_from_request(request: Request) -> Optional[UserRole]:
    """
    Extract user role from request authorization header.
    
    Args:
        request: FastAPI request
        
    Returns:
        User role or None if not authenticated
    """
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        token = auth_header.split(" ")[1]
        payload = verify_token(token)
        return payload.role
        
    except Exception:
        return None


# Token blacklist (simple in-memory implementation)
class TokenBlacklist:
    """Simple token blacklist for logout functionality."""
    
    def __init__(self):
        self.blacklisted_tokens = set()
        self.cleanup_interval = 3600  # 1 hour
        self.last_cleanup = time()
    
    def add_token(self, token: str):
        """Add token to blacklist."""
        self.blacklisted_tokens.add(token)
        self._cleanup_if_needed()
    
    def is_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted."""
        self._cleanup_if_needed()
        return token in self.blacklisted_tokens
    
    def _cleanup_if_needed(self):
        """Clean up expired tokens from blacklist."""
        now = time()
        if now - self.last_cleanup > self.cleanup_interval:
            # In a real implementation, you'd check token expiry
            # For now, just clear old tokens periodically
            if len(self.blacklisted_tokens) > 10000:
                self.blacklisted_tokens.clear()
            self.last_cleanup = now


# Global token blacklist instance
token_blacklist = TokenBlacklist()


async def check_token_blacklist(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """
    Check if token is blacklisted.
    
    Args:
        credentials: HTTP authorization credentials
        
    Raises:
        HTTPException: If token is blacklisted
    """
    if credentials and token_blacklist.is_blacklisted(credentials.credentials):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )