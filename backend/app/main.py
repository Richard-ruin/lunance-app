# app/main.py
"""Updated FastAPI application with WebSocket and real-time features integration."""

import os
import socket
from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
import time
import asyncio
from contextlib import asynccontextmanager

from app.config.settings import settings
from app.config.database import connect_to_mongo, close_mongo_connection, check_database_health
from app.config.database_indexes import create_all_indexes
from app.api.v1.endpoints import router as api_v1_router
from app.middleware.auth import add_security_headers, require_admin
from app.models.user import UserInDB

# WebSocket imports
from app.websocket.endpoints import router as websocket_router
from app.websocket.websocket_manager import connection_manager, connection_cleanup_task

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(settings.log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def get_local_ip():
    """Get local IP address."""
    try:
        # Connect to a remote server to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager with WebSocket cleanup."""
    # Startup
    logger.info("🚀 Memulai Lunance Backend dengan fitur real-time...")
    
    # Get IP information
    local_ip = get_local_ip()
    port = getattr(settings, 'port', 8000)
    
    try:
        # Connect to MongoDB
        await connect_to_mongo()
        logger.info("✅ Database terhubung")
        
        # Create database indexes
        db_health = await check_database_health()
        if db_health["status"] == "healthy":
            from app.config.database import get_database
            database = await get_database()
            await create_all_indexes(database)
            logger.info("✅ Index database dibuat")
        
        # Start background tasks
        asyncio.create_task(connection_cleanup_task())
        logger.info("✅ Background tasks dimulai")
        
        # Run startup initialization tasks
        try:
            from app.core.startup import run_startup_tasks
            await run_startup_tasks()
        except ImportError:
            logger.warning("⚠️ Core startup module tidak ditemukan, melanjutkan tanpa startup tasks")
        
        logger.info("🎉 Lunance Backend dengan WebSocket siap digunakan!")
        logger.info(f"🌐 Server dapat diakses di:")
        logger.info(f"   - Local: http://localhost:{port}")
        logger.info(f"   - Network: http://{local_ip}:{port}")
        logger.info(f"   - Documentation: http://{local_ip}:{port}/docs")
        
    except Exception as e:
        logger.error(f"❌ Startup gagal: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Mematikan Lunance Backend...")
    
    # Cleanup WebSocket connections
    try:
        for connection_type in connection_manager.active_connections:
            active_users = list(connection_manager.active_connections[connection_type].keys())
            for user_id in active_users:
                await connection_manager.disconnect(connection_type, user_id)
        logger.info("✅ Koneksi WebSocket dibersihkan")
    except Exception as e:
        logger.error(f"Error cleanup WebSocket: {e}")
    
    await close_mongo_connection()
    logger.info("✅ Shutdown selesai!")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    # 🌙 Lunance - Smart Personal Finance Management API
    
    Sistem manajemen keuangan personal yang komprehensif khusus untuk mahasiswa dengan fitur-fitur canggih:
    
    ## 🔐 Autentikasi & Manajemen User
    - Autentikasi JWT dengan verifikasi OTP
    - Kontrol akses berbasis role (Admin/Student)
    - Verifikasi email dan pemulihan password
    - Manajemen profil user dengan integrasi universitas
    
    ## 🏫 Sistem Universitas
    - Hierarki universitas lengkap (Universitas → Fakultas → Jurusan)
    - Daftar universitas publik untuk mahasiswa
    - Tools manajemen admin untuk data universitas
    - Sistem permintaan mahasiswa untuk universitas baru
    
    ## 📂 Manajemen Kategori
    - Kategori global tersedia untuk semua user
    - Kategori personal untuk kustomisasi individual
    - Statistik penggunaan dan analitik
    - Tools admin untuk manajemen kategori global
    
    ## 💰 Manajemen Transaksi
    - Pelacakan pemasukan/pengeluaran komprehensif
    - Kemampuan filter dan pencarian canggih
    - Operasi transaksi massal
    - Analitik dan ringkasan real-time
    
    ## 🎯 Sistem Target Tabungan
    - Pelacakan tujuan tabungan pintar
    - Proyeksi progress dan analitik
    - Manajemen kontribusi dan penarikan
    - Pelacakan pencapaian dengan riwayat
    
    ## 📊 Analitik & Wawasan
    - Ringkasan transaksi bulanan/harian
    - Analisis pengeluaran per kategori
    - Pelacakan progress tabungan
    - Dashboard keuangan dengan metrik kunci
    
    ## 🔔 Sistem Notifikasi Real-time
    - Notifikasi berbagai channel (WebSocket, Email, Push)
    - Pengaturan notifikasi personal
    - Broadcasting sistem dan pengumuman
    - Template notifikasi dalam bahasa Indonesia
    
    ## 💬 Fitur Real-time
    - Dukungan WebSocket untuk update real-time
    - Notifikasi dan alert langsung
    - Update dashboard real-time
    - Sistem chat untuk dukungan user
    
    ## 🚀 Fitur Teknis
    - Desain API RESTful dengan dokumentasi lengkap
    - Rate limiting dan security headers
    - Dukungan pagination untuk dataset besar
    - Validasi data real-time
    - Error handling komprehensif
    - Integrasi WebSocket untuk fitur real-time
    
    ---
    
    **🌟 Sempurna untuk mahasiswa yang ingin mengontrol keuangan mereka!**
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    contact={
        "name": "Lunance Support",
        "email": "support@lunance.app",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    }
)

# Enhanced CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Mengizinkan semua origin
    allow_credentials=True,
    allow_methods=["*"],  # Mengizinkan semua methods (GET, POST, PUT, DELETE, dll)
    allow_headers=["*"],  # Mengizinkan semua headers
    expose_headers=["*"],  # Expose semua headers ke client
)

# Add security headers middleware
app.middleware("http")(add_security_headers)


# Request timing and logging middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers and log requests."""
    start_time = time.time()
    
    # Log incoming request
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"[REQUEST] {request.method} {request.url.path} from {client_ip}")
    
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Add custom headers
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Server-Info"] = "Lunance-API"
    response.headers["X-Powered-By"] = "FastAPI"
    
    # Log response
    logger.info(f"[RESPONSE] {request.method} {request.url.path} - {response.status_code} ({process_time:.3f}s)")
    
    return response


# Exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions."""
    logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": time.time(),
            "path": str(request.url.path)
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    logger.warning(f"Validation Error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "Error Validasi",
            "details": exc.errors(),
            "status_code": 422,
            "timestamp": time.time(),
            "path": str(request.url.path)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
            "status_code": 500,
            "timestamp": time.time(),
            "path": str(request.url.path)
        }
    )


# Include API routers
app.include_router(
    api_v1_router,
    prefix="/api/v1",
    tags=["API v1"]
)

# Include WebSocket router
app.include_router(
    websocket_router,
    tags=["WebSocket Real-time"]
)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with basic API information."""
    local_ip = get_local_ip()
    port = getattr(settings, 'port', 8000)
    
    return {
        "pesan": "Selamat datang di Lunance API! 🌙",
        "versi": settings.app_version,
        "status": "berjalan",
        "deskripsi": "Sistem Manajemen Keuangan Pintar untuk Mahasiswa Indonesia",
        "mode": "development" if settings.debug else "production",
        "akses": {
            "local": f"http://localhost:{port}",
            "network": f"http://{local_ip}:{port}",
            "dokumentasi": f"http://{local_ip}:{port}/docs",
            "redoc": f"http://{local_ip}:{port}/redoc"
        },
        "endpoints": {
            "autentikasi": "/api/v1/auth",
            "users": "/api/v1/users",
            "universitas": "/api/v1/universities", 
            "permintaan_universitas": "/api/v1/university-requests",
            "kategori": "/api/v1/categories",
            "transaksi": "/api/v1/transactions",
            "target_tabungan": "/api/v1/savings-targets",
            "notifikasi": "/api/v1/notifications"
        },
        "websocket_endpoints": {
            "chat": "/ws/chat/{user_id}",
            "dashboard": "/ws/dashboard/{user_id}",
            "notifikasi": "/ws/notifications/{user_id}",
            "admin": "/ws/admin/{admin_id}"
        }
    }


# Health check
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    try:
        db_health = await check_database_health()
        websocket_stats = connection_manager.get_connection_stats()
        
        return {
            "status": "sehat" if db_health["status"] == "healthy" else "tidak_sehat",
            "versi": settings.app_version,
            "timestamp": time.time(),
            "server_info": {
                "local_ip": get_local_ip(),
                "port": getattr(settings, 'port', 8000),
                "mode": "development" if settings.debug else "production"
            },
            "database": db_health,
            "websocket": {
                "status": "aktif",
                "total_koneksi": websocket_stats["active_connections"],
                "koneksi_per_tipe": websocket_stats["connections_by_type"]
            }
        }
        
    except Exception as e:
        logger.error(f"Health check gagal: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "tidak_sehat",
                "error": str(e),
                "timestamp": time.time()
            }
        )


# Kubernetes readiness and liveness probes
@app.get("/health/ready", tags=["Health"])
async def readiness_check():
    """Kubernetes readiness check."""
    db_health = await check_database_health()
    if db_health["status"] != "healthy":
        raise HTTPException(status_code=503, detail="Database not ready")
    
    return {"status": "ready", "timestamp": time.time()}


@app.get("/health/live", tags=["Health"])
async def liveness_check():
    """Kubernetes liveness check."""
    return {"status": "alive", "timestamp": time.time()}


# WebSocket stats endpoint for monitoring
@app.get("/ws/stats", tags=["WebSocket"])
async def get_websocket_stats():
    """WebSocket statistics for monitoring."""
    try:
        stats = connection_manager.get_connection_stats()
        return {
            "total_koneksi": stats["active_connections"],
            "koneksi_per_tipe": stats["connections_by_type"],
            "pesan_terkirim": stats["messages_sent"],
            "pesan_diterima": stats["messages_received"],
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Error mendapatkan stats WebSocket: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal mendapatkan statistik WebSocket"
        )


# Admin WebSocket monitoring (Admin only)
@app.get("/admin/websocket/stats", tags=["Admin"])
async def get_websocket_admin_stats(
    current_user: UserInDB = Depends(require_admin())
):
    """Detailed WebSocket statistics for admin."""
    try:
        stats = connection_manager.get_connection_stats()
        
        admin_stats = {
            "statistik_umum": stats,
            "koneksi_aktif_detail": {},
            "admin_info": {
                "admin_id": str(current_user.id),
                "admin_email": current_user.email,
                "waktu_akses": time.time()
            }
        }
        
        # Detail koneksi per tipe untuk admin
        for conn_type, connections in connection_manager.active_connections.items():
            admin_stats["koneksi_aktif_detail"][conn_type] = {
                "jumlah": len(connections),
                "user_ids": list(connections.keys())
            }
        
        return admin_stats
        
    except Exception as e:
        logger.error(f"Error mendapatkan stats WebSocket admin: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal mendapatkan statistik WebSocket"
        )


# Development info endpoint
@app.get("/dev/info", tags=["Development"])
async def dev_info():
    """Development information endpoint."""
    local_ip = get_local_ip()
    port = getattr(settings, 'port', 8000)
    
    return {
        "development_mode": True,
        "server_info": {
            "local_ip": local_ip,
            "port": port,
            "host": "0.0.0.0",
            "debug": settings.debug
        },
        "access_urls": {
            "local": f"http://localhost:{port}",
            "network": f"http://{local_ip}:{port}",
            "docs": f"http://{local_ip}:{port}/docs",
            "redoc": f"http://{local_ip}:{port}/redoc"
        },
        "cors_settings": {
            "allow_origins": ["*"],
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"]
        },
        "tips": [
            "Gunakan network IP untuk mengakses dari device lain di jaringan yang sama",
            "Dokumentasi API tersedia di /docs",
            "WebSocket testing bisa dilakukan melalui browser console",
            "CORS sudah dikonfigurasi untuk development"
        ]
    }


# Development server
if __name__ == "__main__":
    import uvicorn
    
    # Get configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", getattr(settings, 'port', 8000)))
    
    logger.info("🚀 Starting Lunance Backend in development mode...")
    logger.info(f"🌐 Host: {host}")
    logger.info(f"🔌 Port: {port}")
    logger.info(f"🔧 Debug: {settings.debug}")
    
    # Get local IP for network access
    local_ip = get_local_ip()
    
    print("\n" + "="*60)
    print("🌙 LUNANCE API SERVER - DEVELOPMENT MODE")
    print("="*60)
    print(f"📍 Local Access:   http://localhost:{port}")
    print(f"🌐 Network Access: http://{local_ip}:{port}")
    print(f"📚 Documentation:  http://{local_ip}:{port}/docs")
    print(f"📖 ReDoc:          http://{local_ip}:{port}/redoc")
    print(f"🔧 Dev Info:       http://{local_ip}:{port}/dev/info")
    print("="*60)
    print("💡 Tips:")
    print("   - Gunakan network IP untuk akses dari device lain")
    print("   - CORS sudah dikonfigurasi untuk development")
    print("   - Auto-reload aktif untuk development")
    print("="*60 + "\n")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=settings.debug,
        log_level=settings.log_level.lower() if hasattr(settings, 'log_level') else "info",
        access_log=True
    )