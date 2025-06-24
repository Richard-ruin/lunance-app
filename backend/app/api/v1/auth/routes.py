import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time
import uvicorn

from app.config.settings import settings, get_logging_config
from app.config.database import connect_to_mongo, close_mongo_connection, check_database_health
from app.api.v1.auth.routes import router as auth_router
from app.core.exceptions import LunanceException, to_http_exception

# Configure logging
logging.config.dictConfig(get_logging_config())
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for FastAPI app"""
    # Startup
    logger.info("Starting Lunance Finance Tracker API...")
    
    try:
        # Connect to database
        await connect_to_mongo()
        logger.info("Database connection established")
        
        # Additional startup tasks can be added here
        # - Load prediction models
        # - Initialize cache
        # - Set up background tasks
        
        logger.info("Lunance API startup completed successfully")
        
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        raise
    
    yield  # App is running
    
    # Shutdown
    logger.info("Shutting down Lunance API...")
    
    try:
        # Close database connection
        await close_mongo_connection()
        logger.info("Database connection closed")
        
        # Additional cleanup tasks
        logger.info("Lunance API shutdown completed")
        
    except Exception as e:
        logger.error(f"Shutdown error: {str(e)}")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Personal Finance Tracker API for Indonesian Students",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add trusted host middleware (security)
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["lunance.app", "*.lunance.com", "localhost"]
    )


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    start_time = time.time()
    
    # Log request
    logger.info(
        f"Request: {request.method} {request.url.path} "
        f"from {request.client.host if request.client else 'unknown'}"
    )
    
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(
        f"Response: {response.status_code} "
        f"({process_time:.3f}s)"
    )
    
    return response


# Global exception handlers
@app.exception_handler(LunanceException)
async def lunance_exception_handler(request: Request, exc: LunanceException):
    """Handle custom Lunance exceptions"""
    logger.warning(f"Lunance exception: {exc.message} - {exc.details}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.message,
                "type": exc.__class__.__name__,
                "details": exc.details
            },
            "timestamp": time.time(),
            "path": request.url.path
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle FastAPI HTTP exceptions"""
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.detail,
                "type": "HTTPException"
            },
            "timestamp": time.time(),
            "path": request.url.path
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    
    # In production, don't expose internal errors
    error_message = str(exc) if settings.DEBUG else "Internal server error"
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "message": error_message,
                "type": "InternalServerError"
            },
            "timestamp": time.time(),
            "path": request.url.path
        }
    )


# Include routers
app.include_router(
    auth_router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["Authentication"]
)

# Future routers will be added here:
# app.include_router(student_router, prefix=f"{settings.API_V1_STR}/students", tags=["Students"])
# app.include_router(transaction_router, prefix=f"{settings.API_V1_STR}/transactions", tags=["Transactions"])
# app.include_router(category_router, prefix=f"{settings.API_V1_STR}/categories", tags=["Categories"])
# app.include_router(analytics_router, prefix=f"{settings.API_V1_STR}/analytics", tags=["Analytics"])
# app.include_router(chat_router, prefix=f"{settings.API_V1_STR}/chat", tags=["Chat"])


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Lunance Finance Tracker API",
        "version": settings.APP_VERSION,
        "docs_url": "/docs" if settings.DEBUG else "Contact admin for API documentation",
        "status": "running"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Application health check"""
    try:
        # Check database connectivity
        db_healthy = await check_database_health()
        
        health_status = {
            "status": "healthy" if db_healthy else "unhealthy",
            "timestamp": time.time(),
            "version": settings.APP_VERSION,
            "environment": "development" if settings.DEBUG else "production",
            "services": {
                "database": "healthy" if db_healthy else "unhealthy",
                "api": "healthy"
            }
        }
        
        # Return appropriate status code
        status_code = 200 if db_healthy else 503
        
        return JSONResponse(
            status_code=status_code,
            content=health_status
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": time.time(),
                "error": str(e) if settings.DEBUG else "Service unavailable"
            }
        )


# API info endpoint
@app.get("/info")
async def api_info():
    """API information endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "Personal Finance Tracker API for Indonesian Students",
        "features": [
            "Student Registration & Authentication",
            "Transaction Management",
            "Expense Categorization",
            "Savings Goals Tracking",
            "Expense Sharing with Friends",
            "Financial Analytics & Insights",
            "AI-Powered Financial Assistant",
            "Academic Calendar Integration",
            "Gamification & Achievements"
        ],
        "supported_universities": settings.SUPPORTED_UNIVERSITIES[:5],  # Show first 5
        "total_supported_universities": len(settings.SUPPORTED_UNIVERSITIES),
        "default_currency": settings.DEFAULT_CURRENCY,
        "api_version": "v1",
        "endpoints": {
            "auth": f"{settings.API_V1_STR}/auth",
            "docs": "/docs" if settings.DEBUG else None,
            "health": "/health"
        }
    }


# Development server runner
if __name__ == "__main__":
    # This block only runs when the file is executed directly
    # In production, use a proper ASGI server like uvicorn or gunicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=settings.DEBUG
    )