"""
Middleware Configuration
Middleware untuk CORS, rate limiting, error handling, dan logging
"""

import time
import logging
import traceback
from typing import Callable
from datetime import datetime

from fastapi import Request, Response, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import ValidationError as PydanticValidationError

from .exceptions import (
    LunanceException, 
    map_exception_to_http,
    create_validation_error_from_pydantic,
    create_database_error
)
from ..config.settings import settings

# Setup logging
logger = logging.getLogger(__name__)

# Rate limiter instance
limiter = Limiter(key_func=get_remote_address)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Middleware untuk handling semua exceptions secara konsisten
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
            
        except LunanceException as exc:
            # Handle custom exceptions
            logger.error(f"Lunance Exception: {exc.message}", extra={
                "error_code": exc.error_code,
                "details": exc.details,
                "path": request.url.path,
                "method": request.method
            })
            
            http_exc = map_exception_to_http(exc)
            return JSONResponse(
                status_code=http_exc.status_code,
                content=http_exc.detail,
                headers=http_exc.headers
            )
            
        except PydanticValidationError as exc:
            # Handle Pydantic validation errors
            validation_error = create_validation_error_from_pydantic(exc)
            logger.warning(f"Validation Error: {validation_error.message}", extra={
                "details": validation_error.details,
                "path": request.url.path,
                "method": request.method
            })
            
            http_exc = map_exception_to_http(validation_error)
            return JSONResponse(
                status_code=http_exc.status_code,
                content=http_exc.detail
            )
            
        except HTTPException as exc:
            # Handle FastAPI HTTP exceptions
            logger.warning(f"HTTP Exception: {exc.detail}", extra={
                "status_code": exc.status_code,
                "path": request.url.path,
                "method": request.method
            })
            
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "success": False,
                    "message": exc.detail,
                    "error_code": f"HTTP_{exc.status_code}",
                    "details": {}
                }
            )
            
        except Exception as exc:
            # Handle unexpected exceptions
            error_id = f"err_{int(time.time())}"
            
            logger.error(f"Unexpected Error [{error_id}]: {str(exc)}", extra={
                "error_id": error_id,
                "error_type": type(exc).__name__,
                "traceback": traceback.format_exc(),
                "path": request.url.path,
                "method": request.method
            })
            
            # Don't expose internal errors in production
            if settings.debug:
                detail = {
                    "success": False,
                    "message": f"Internal server error: {str(exc)}",
                    "error_code": "INTERNAL_SERVER_ERROR",
                    "details": {
                        "error_id": error_id,
                        "error_type": type(exc).__name__,
                        "traceback": traceback.format_exc()
                    }
                }
            else:
                detail = {
                    "success": False,
                    "message": "Internal server error occurred",
                    "error_code": "INTERNAL_SERVER_ERROR", 
                    "details": {"error_id": error_id}
                }
            
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=detail
            )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware untuk logging request dan response
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Log request
        logger.info(f"Request started", extra={
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_ip": get_remote_address(request),
            "user_agent": request.headers.get("user-agent"),
            "timestamp": datetime.utcnow().isoformat()
        })
        
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(f"Request completed", extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "process_time": f"{process_time:.4f}s",
            "client_ip": get_remote_address(request),
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Add process time header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware untuk menambah security headers
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Add custom headers
        response.headers["X-API-Version"] = settings.app_version
        response.headers["X-Powered-By"] = "Lunance API"
        
        return response


class DatabaseConnectionMiddleware(BaseHTTPMiddleware):
    """
    Middleware untuk handling database connection errors
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
            
        except Exception as exc:
            # Check if it's a database-related error
            error_types = [
                "ServerSelectionTimeoutError",
                "ConnectionFailure", 
                "NetworkTimeout",
                "pymongo.errors"
            ]
            
            error_name = type(exc).__name__
            is_db_error = any(error_type in str(type(exc)) for error_type in error_types)
            
            if is_db_error or "database" in str(exc).lower():
                db_error = create_database_error("operation", exc)
                logger.error(f"Database Error: {db_error.message}", extra={
                    "original_error": str(exc),
                    "path": request.url.path,
                    "method": request.method
                })
                
                http_exc = map_exception_to_http(db_error)
                return JSONResponse(
                    status_code=http_exc.status_code,
                    content=http_exc.detail
                )
            
            # Re-raise if not a database error
            raise exc


def setup_cors_middleware(app):
    """
    Setup CORS middleware dengan konfigurasi dari settings
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=settings.allowed_methods,
        allow_headers=settings.allowed_headers,
        expose_headers=["X-Process-Time", "X-API-Version"]
    )


def setup_rate_limiting_middleware(app):
    """
    Setup rate limiting middleware
    """
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


def setup_custom_middlewares(app):
    """
    Setup semua custom middlewares
    """
    # Add middlewares in reverse order (last added = first executed)
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(DatabaseConnectionMiddleware) 
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Only add request logging in development
    if settings.debug:
        app.add_middleware(RequestLoggingMiddleware)


# Rate limiting decorators
def rate_limit_decorator(limit: str):
    """
    Decorator untuk rate limiting pada endpoints
    
    Usage:
        @rate_limit_decorator("5/minute")
        async def my_endpoint():
            pass
    """
    return limiter.limit(limit)


# Common rate limits
def standard_rate_limit():
    """Standard rate limit untuk most endpoints"""
    return rate_limit_decorator(f"{settings.rate_limit_per_minute}/minute")


def strict_rate_limit():
    """Strict rate limit untuk sensitive endpoints"""
    return rate_limit_decorator("10/minute")


def auth_rate_limit():
    """Rate limit untuk authentication endpoints"""
    return rate_limit_decorator("5/minute")


def upload_rate_limit():
    """Rate limit untuk file upload endpoints"""
    return rate_limit_decorator("3/minute")


# Health check rate limit exception handler
async def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded):
    """
    Custom rate limit exception handler dengan response format yang konsisten
    """
    retry_after = exc.detail.split("Retry after ")[1].split(" ")[0] if "Retry after" in exc.detail else "60"
    
    response_content = {
        "success": False,
        "message": "Rate limit exceeded",
        "error_code": "RATE_LIMIT_EXCEEDED",
        "details": {
            "limit": exc.detail,
            "retry_after": f"{retry_after} seconds"
        }
    }
    
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content=response_content,
        headers={"Retry-After": retry_after}
    )


def setup_middleware_stack(app):
    """
    Setup complete middleware stack
    """
    # Setup all middlewares
    setup_cors_middleware(app)
    setup_rate_limiting_middleware(app)
    setup_custom_middlewares(app)
    
    # Override rate limit exception handler
    app.add_exception_handler(RateLimitExceeded, rate_limit_exception_handler)
    
    logger.info("✅ Middleware stack configured successfully")