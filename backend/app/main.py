# app/main.py - CLEANED VERSION - No AI responses, no predictions, no finance dependencies
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import socket
import sys
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# BASIC LOGGING SETUP
# ============================================================================

def setup_logging():
    """Setup basic logging"""
    os.makedirs("logs", exist_ok=True)
    
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler("logs/app.log", encoding="utf-8"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger()

logger = setup_logging()

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_local_ip():
    """Mendapatkan IP address lokal"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "localhost"

def extract_user_id_from_request(request: Request) -> Optional[str]:
    """Extract user ID dari request headers"""
    try:
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            from .utils.security import extract_user_id_from_token
            token = auth_header.split(" ")[1]
            return extract_user_id_from_token(token)
    except Exception:
        pass
    return None

# ============================================================================
# FASTAPI APP INITIALIZATION
# ============================================================================

app = FastAPI(
    title=os.getenv("APP_NAME", "Lunance API"),
    version=os.getenv("APP_VERSION", "1.0.0"),
    description="Backend API untuk Lunance - Personal Finance Management",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
if not allowed_origins or allowed_origins == [""]:
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ============================================================================
# REQUEST LOGGING MIDDLEWARE
# ============================================================================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware untuk logging requests"""
    start_time = time.time()
    
    user_id = extract_user_id_from_request(request)
    
    response = await call_next(request)
    
    processing_time = time.time() - start_time
    endpoint = str(request.url.path)
    method = request.method
    status_code = response.status_code
    
    if status_code >= 400:
        logger.error(f"{method} {endpoint} | Status: {status_code} | Time: {processing_time:.3f}s | User: {user_id}")
    else:
        logger.info(f"{method} {endpoint} | Status: {status_code} | Time: {processing_time:.3f}s | User: {user_id}")
    
    return response

# ============================================================================
# IMPORT VALIDATION AND ROUTER LOADING
# ============================================================================

def validate_imports():
    """Validasi imports yang diperlukan"""
    logger.info("🔍 Validating imports...")
    
    try:
        from .config.database import db_manager, create_indexes, get_database
        logger.info("✅ Database imports OK")
        
        from .services.auth_service import AuthService
        logger.info("✅ Auth service imports OK")
        
        from .models.user import User, UserProfile, FinancialSettings
        logger.info("✅ User models imports OK")
        
        from .utils.security import verify_token, create_access_token
        from .utils.timezone_utils import IndonesiaDatetime
        logger.info("✅ Utils imports OK")
        
        return True
        
    except ImportError as e:
        logger.error(f"IMPORT ERROR: {e}")
        return False
    except Exception as e:
        logger.error(f"VALIDATION ERROR: {e}")
        return False

def safe_import_routers():
    """Import routers dengan error handling"""
    routers_loaded = []
    
    # Auth router
    try:
        from .routers import auth
        app.include_router(auth.router, prefix="/api/v1")
        routers_loaded.append("auth")
        logger.info("✅ Auth router loaded")
    except Exception as e:
        logger.error(f"CRITICAL: Auth router failed: {e}")
        sys.exit(1)
    
    # Chat router (cleaned)
    try:
        from .routers import chat
        app.include_router(chat.router, prefix="/api/v1")
        routers_loaded.append("chat")
        logger.info("✅ Chat router loaded")
    except Exception as e:
        logger.error(f"CRITICAL: Chat router failed: {e}")
        sys.exit(1)
    
    # Note: Finance router removed as finance service no longer exists
    
    return routers_loaded

# ============================================================================
# EVENT HANDLERS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Event startup"""
    logger.info("🚀 Starting Lunance Backend API...")
    
    if not validate_imports():
        logger.error("Critical import validation failed!")
        sys.exit(1)
    
    routers_loaded = safe_import_routers()
    logger.info(f"✅ Loaded routers: {', '.join(routers_loaded)}")
    
    try:
        from .config.database import db_manager, create_indexes
        db_manager.connect()
        create_indexes()
        logger.info("✅ Database connection established")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        sys.exit(1)
    
    local_ip = get_local_ip()
    port = os.getenv("PORT", "8000")
    
    logger.info("=" * 80)
    logger.info("🎉 Lunance Backend API successfully started!")
    logger.info(f"👤 User Management: Active")
    logger.info(f"💬 Chat System: Active (No AI)")
    logger.info(f"🌐 Server running on:")
    logger.info(f"   • Local:   http://localhost:{port}")
    logger.info(f"   • Network: http://{local_ip}:{port}")
    logger.info(f"📝 API Documentation:")
    logger.info(f"   • Swagger UI: http://{local_ip}:{port}/docs")
    logger.info(f"🔍 Health Check: http://{local_ip}:{port}/health")
    logger.info(f"🔧 Routers Loaded: {', '.join(routers_loaded)}")
    logger.info("=" * 80)

@app.on_event("shutdown")
async def shutdown_event():
    """Event shutdown"""
    try:
        from .config.database import db_manager
        db_manager.close()
        logger.info("✅ Database connection closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")
    
    logger.info("👋 Lunance Backend API gracefully shut down")

# ============================================================================
# GLOBAL EXCEPTION HANDLER
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handler untuk semua exception"""
    logger.error(f"🚨 Unhandled exception: {exc}")
    
    error_response = {
        "success": False,
        "message": "Terjadi kesalahan internal server",
        "error_type": type(exc).__name__,
        "errors": [str(exc)] if os.getenv("DEBUG", "False").lower() == "true" else ["Internal server error"]
    }
    
    return JSONResponse(
        status_code=500,
        content=error_response
    )

# ============================================================================
# ROOT ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "success": True,
        "message": "Lunance Backend API berjalan dengan baik!",
        "data": {
            "app_name": os.getenv("APP_NAME", "Lunance API"),
            "version": os.getenv("APP_VERSION", "1.0.0"),
            "features": [
                "Simple Chat Interface (No AI responses)",
                "User Authentication & Profile Management",
                "Indonesian Student Categories",
                "Budget Planning Framework"
            ],
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from .utils.timezone_utils import IndonesiaDatetime
    
    health_data = {
        "app_status": "running",
        "database": "unknown",
        "chat_service": "ready (no AI)",
        "auth_service": "unknown",
        "overall_status": "unknown"
    }
    
    try:
        from .config.database import get_database
        db = get_database()
        db.command("ping")
        health_data["database"] = "connected"
        
        from .services.auth_service import AuthService
        auth_service = AuthService()
        health_data["auth_service"] = "active"
        
        health_data["overall_status"] = "healthy"
        
        return {
            "success": True,
            "message": "Aplikasi sehat dan berjalan dengan baik",
            "data": health_data,
            "timestamp": IndonesiaDatetime.now().isoformat()
        }
        
    except Exception as e:
        health_data["overall_status"] = "unhealthy"
        health_data["error"] = str(e)
        
        logger.error(f"Health check failed: {e}")
        
        return JSONResponse(
            status_code=503,
            content={
                "success": False,
                "message": "Aplikasi tidak sehat",
                "data": health_data,
                "timestamp": IndonesiaDatetime.now().isoformat()
            }
        )

@app.get("/api/v1/info")
async def api_info():
    """Informasi tentang API"""
    return {
        "success": True,
        "message": "Informasi API Lunance",
        "data": {
            "name": "Lunance Backend API",
            "version": "1.0.0", 
            "description": "Backend API untuk aplikasi personal finance management",
            "target_audience": "Indonesian University Students",
            "features": {
                "authentication": [
                    "User Registration & Login",
                    "JWT Token Management",
                    "Profile & Financial Setup"
                ],
                "chat": [
                    "Simple Chat Interface",
                    "No AI Responses",
                    "Conversation History"
                ],
                "budget_planning": [
                    "50/30/20 Budget Framework",
                    "Indonesian Student Categories",
                    "Financial Goal Setting"
                ]
            },
            "endpoints": {
                "auth": "/api/v1/auth",
                "chat": "/api/v1/chat", 
                "docs": "/docs",
                "health": "/health"
            }
        }
    }

# ============================================================================
# DEVELOPMENT SERVER RUNNER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting development server...")
    
    host = "0.0.0.0"
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    print(f"🌐 Host: {host}")
    print(f"📍 Port: {port}")
    print(f"🔧 Debug Mode: {debug}")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug,
        reload_dirs=["app"] if debug else None,
        log_level="info"
    )