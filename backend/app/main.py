from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import socket
from dotenv import load_dotenv

from .config.database import db_manager, create_indexes
from .routers import auth

load_dotenv()

def get_local_ip():
    """Mendapatkan IP address lokal"""
    try:
        # Membuat socket connection untuk mendapatkan IP lokal
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "localhost"

# Inisialisasi FastAPI app
app = FastAPI(
    title=os.getenv("APP_NAME", "Lunance API"),
    version=os.getenv("APP_VERSION", "1.0.0"),
    description="Backend API untuk Lunance - Personal Finance AI Chatbot",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
if not allowed_origins or allowed_origins == [""]:
    allowed_origins = ["*"]  # Development only

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Event handlers
@app.on_event("startup")
async def startup_event():
    """Event yang dijalankan saat aplikasi start"""
    try:
        # Koneksi ke database
        db_manager.connect()
        
        # Buat indexes
        create_indexes()
        
        # Dapatkan IP address
        local_ip = get_local_ip()
        port = os.getenv("PORT", "8000")
        
        print("=" * 60)
        print("🚀 Lunance Backend API berhasil dimulai!")
        print(f"🌐 Server berjalan di:")
        print(f"   • Local:   http://localhost:{port}")
        print(f"   • Network: http://{local_ip}:{port}")
        print(f"📝 API Documentation:")
        print(f"   • Swagger UI: http://{local_ip}:{port}/docs")
        print(f"   • ReDoc:      http://{local_ip}:{port}/redoc")
        print(f"🔍 Health Check: http://{local_ip}:{port}/health")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Gagal memulai aplikasi: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Event yang dijalankan saat aplikasi shutdown"""
    db_manager.close()
    print("👋 Lunance Backend API berhasil ditutup")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handler untuk semua exception yang tidak tertangani"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Terjadi kesalahan internal server",
            "errors": [str(exc)] if os.getenv("DEBUG", "False").lower() == "true" else None
        }
    )

# Include routers
app.include_router(auth.router, prefix="/api/v1")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint untuk health check"""
    return {
        "success": True,
        "message": "Lunance Backend API berjalan dengan baik!",
        "data": {
            "app_name": os.getenv("APP_NAME", "Lunance API"),
            "version": os.getenv("APP_VERSION", "1.0.0"),
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Endpoint untuk mengecek kesehatan aplikasi"""
    try:
        # Test database connection
        from .config.database import get_database
        db = get_database()
        db.command("ping")
        
        return {
            "success": True,
            "message": "Aplikasi sehat",
            "data": {
                "database": "connected",
                "status": "healthy"
            }
        }
    except Exception as e:
        return {
            "success": False,
            "message": "Aplikasi tidak sehat",
            "data": {
                "database": "disconnected",
                "status": "unhealthy",
                "error": str(e)
            }
        }

# API Info endpoint
@app.get("/api/v1/info")
async def api_info():
    """Informasi tentang API"""
    return {
        "success": True,
        "message": "Informasi API Lunance",
        "data": {
            "name": "Lunance Backend API",
            "version": "1.0.0",
            "description": "Backend API untuk aplikasi personal finance AI chatbot",
            "features": [
                "User Authentication & Authorization",
                "Profile & Financial Setup",
                "JWT Token Management",
                "MongoDB Integration",
                "AI-Ready Architecture"
            ],
            "endpoints": {
                "auth": "/api/v1/auth",
                "docs": "/docs",
                "health": "/health"
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    
    # Jalankan server untuk development
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if os.getenv("DEBUG", "False").lower() == "true" else False
    )