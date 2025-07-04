"""
Lunance Backend Main Application
FastAPI application untuk Lunance - Manajemen Keuangan Mahasiswa Indonesia
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.gzip import GZipMiddleware

from .config.settings import settings
from .config.database import connect_to_mongo, close_mongo_connection, check_database_health
from .core.middleware import setup_middleware_stack
from .api.v1.router import api_router

# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # Startup
    logger.info("🚀 Starting Lunance Backend API...")
    
    try:
        # Connect to database
        await connect_to_mongo()
        logger.info("✅ Database connection established")
        
        # Initialize default data if needed
        await initialize_default_data()
        
        logger.info(f"✅ Lunance Backend API v{settings.app_version} started successfully")
        logger.info(f"📖 API Documentation: http://{settings.host}:{settings.port}/docs")
        logger.info(f"🔧 Environment: {'Development' if settings.debug else 'Production'}")
        
    except Exception as e:
        logger.error(f"❌ Failed to start application: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Lunance Backend API...")
    
    try:
        # Close database connection
        await close_mongo_connection()
        logger.info("✅ Database connection closed")
        
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")
    
    logger.info("✅ Lunance Backend API shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    ## Lunance Backend API
    
    Backend API untuk aplikasi Lunance - Manajemen Keuangan berbasis mobile untuk mahasiswa Indonesia.
    
    ### Features
    
    * **User Management** - Registrasi dan manajemen mahasiswa & admin
    * **University Management** - Manajemen data universitas dengan approval system  
    * **Category Management** - Kategori transaksi global & personal
    * **Transaction Management** - Pencatatan income & expense
    * **Savings Target** - Target tabungan dengan tracking progress
    * **Analytics** - Analisis keuangan dan laporan
    
    ### Authentication
    
    API menggunakan JWT token untuk authentication. Akses endpoint `/auth/login` untuk mendapatkan token.
    
    ### Rate Limiting
    
    API menerapkan rate limiting untuk mencegah abuse:
    - Standard endpoints: 60 requests/minute
    - Auth endpoints: 5 requests/minute
    - Upload endpoints: 3 requests/minute
    
    ### Error Handling
    
    Semua error response mengikuti format standar:
    ```json
    {
        "success": false,
        "message": "Error message",
        "error_code": "ERROR_CODE",
        "details": {}
    }
    ```
    """,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
    lifespan=lifespan
)

# Setup middleware stack
setup_middleware_stack(app)

# Add gzip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include API router
app.include_router(
    api_router,
    prefix=settings.api_v1_prefix
)


# Root endpoint
@app.get(
    "/",
    tags=["root"],
    summary="API Root",
    description="Root endpoint untuk informasi API"
)
async def root():
    """
    Root endpoint - API information
    """
    return {
        "message": "Welcome to Lunance Backend API",
        "version": settings.app_version,
        "status": "running",
        "docs_url": "/docs" if settings.debug else "Contact admin for documentation",
        "environment": "development" if settings.debug else "production"
    }


# Health check endpoint
@app.get(
    "/health",
    tags=["health"],
    summary="Health Check",
    description="Endpoint untuk monitoring health aplikasi"
)
async def health_check():
    """
    Health check endpoint
    
    Returns application health status including:
    - API status
    - Database connectivity
    - System information
    """
    try:
        # Check database health
        db_health = await check_database_health()
        
        return {
            "status": "healthy",
            "version": settings.app_version,
            "environment": "development" if settings.debug else "production",
            "database": db_health,
            "api": {
                "status": "running",
                "docs_available": settings.debug
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "version": settings.app_version,
                "error": str(e),
                "database": {
                    "status": "unhealthy",
                    "connected": False
                }
            }
        )


# Custom 404 handler
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Custom 404 error handler"""
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "message": f"Endpoint not found: {request.method} {request.url.path}",
            "error_code": "NOT_FOUND",
            "details": {
                "method": request.method,
                "path": request.url.path,
                "available_docs": "/docs" if settings.debug else "Contact admin"
            }
        }
    )


# Custom 405 handler  
@app.exception_handler(405)
async def method_not_allowed_handler(request: Request, exc):
    """Custom 405 error handler"""
    return JSONResponse(
        status_code=405,
        content={
            "success": False,
            "message": f"Method {request.method} not allowed for {request.url.path}",
            "error_code": "METHOD_NOT_ALLOWED",
            "details": {
                "method": request.method,
                "path": request.url.path
            }
        }
    )


async def initialize_default_data():
    """
    Initialize default data untuk aplikasi
    
    - Create default global categories
    - Create admin user jika belum ada
    - Setup default configurations
    """
    try:
        logger.info("🔧 Initializing default data...")
        
        # Create default global categories
        from .crud.category import crud_category
        from .crud.user import crud_user
        from .models.user import UserRole
        
        # Check if admin exists
        admins = await crud_user.get_admins(limit=1)
        
        if admins:
            admin_id = str(admins[0].id)
            
            # Create default categories jika belum ada
            try:
                await crud_category.create_default_categories(admin_id)
                logger.info("✅ Default categories initialized")
            except Exception as e:
                logger.warning(f"Default categories already exist or error: {e}")
        else:
            logger.warning("⚠️  No admin user found. Default categories not created.")
            logger.info("💡 Create an admin user first, then restart the application.")
        
        logger.info("✅ Default data initialization complete")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize default data: {e}")
        # Don't raise here, let the app continue


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )