from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import socket
from dotenv import load_dotenv

from .config.database import db_manager, create_indexes
from .routers import auth, chat, finance

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
    description="Backend API untuk Lunance - Personal Finance AI Chatbot dengan Luna AI dan Financial Management",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware - Konfigurasi yang lebih permissive untuk development
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
        
        print("=" * 80)
        print("🚀 Lunance Backend API berhasil dimulai!")
        print(f"🤖 Luna AI Chatbot: Ready with Financial Intelligence")
        print(f"💰 Financial Management: Active")
        print(f"🌐 Server berjalan di:")
        print(f"   • Local:   http://localhost:{port}")
        print(f"   • Network: http://{local_ip}:{port}")
        print(f"📝 API Documentation:")
        print(f"   • Swagger UI: http://{local_ip}:{port}/docs")
        print(f"   • ReDoc:      http://{local_ip}:{port}/redoc")
        print(f"🔍 Health Check: http://{local_ip}:{port}/health")
        print(f"💬 WebSocket Chat: ws://{local_ip}:{port}/api/v1/chat/ws/{{user_id}}")
        print(f"📊 Finance API: http://{local_ip}:{port}/api/v1/finance")
        print("=" * 80)
        print("✨ Fitur Luna AI:")
        print("   • Parsing otomatis data keuangan dari chat")
        print("   • Konfirmasi sebelum menyimpan transaksi")
        print("   • Auto-kategorisasi pemasukan dan pengeluaran")
        print("   • Tracking target tabungan")
        print("   • Tips keuangan personal")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Gagal memulai aplikasi: {e}")
        # Jangan raise error agar server tetap bisa jalan meskipun ada masalah dengan database
        print("⚠️  Server tetap berjalan tanpa koneksi database")

@app.on_event("shutdown")
async def shutdown_event():
    """Event yang dijalankan saat aplikasi shutdown"""
    try:
        db_manager.close()
    except:
        pass
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
            "errors": [str(exc)] if os.getenv("DEBUG", "False").lower() == "true" else ["Internal server error"]
        }
    )

# Include routers with error handling
try:
    app.include_router(auth.router, prefix="/api/v1")
    print("✅ Auth router loaded")
except Exception as e:
    print(f"⚠️  Auth router gagal dimuat: {e}")

try:
    app.include_router(chat.router, prefix="/api/v1")
    print("✅ Chat router loaded")
except Exception as e:
    print(f"⚠️  Chat router gagal dimuat: {e}")

try:
    app.include_router(finance.router, prefix="/api/v1")
    print("✅ Finance router loaded")
except Exception as e:
    print(f"⚠️  Finance router gagal dimuat: {e}")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint untuk health check"""
    return {
        "success": True,
        "message": "Lunance Backend API dengan Luna AI dan Financial Management berjalan dengan baik!",
        "data": {
            "app_name": os.getenv("APP_NAME", "Lunance API"),
            "version": os.getenv("APP_VERSION", "1.0.0"),
            "features": [
                "Luna AI Chatbot dengan Financial Intelligence",
                "Auto Financial Data Parsing",
                "WebSocket Support untuk Real-time Chat",
                "Transaction & Savings Goal Management",
                "Financial Analytics & Summary",
                "Bahasa Indonesia Support"
            ],
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Endpoint untuk mengecek kesehatan aplikasi"""
    health_data = {
        "database": "unknown",
        "luna_ai": "ready",
        "financial_parser": "ready",
        "websocket": "available",
        "finance_service": "unknown",
        "status": "partial"
    }
    
    try:
        # Test database connection
        from .config.database import get_database
        db = get_database()
        db.command("ping")
        health_data["database"] = "connected"
        
        # Test finance service
        from .services.finance_service import FinanceService
        finance_service = FinanceService()
        health_data["finance_service"] = "active"
        health_data["status"] = "healthy"
        
        return {
            "success": True,
            "message": "Aplikasi sehat",
            "data": health_data
        }
    except Exception as e:
        health_data["database"] = "disconnected"
        health_data["finance_service"] = "inactive"
        health_data["status"] = "unhealthy"
        health_data["error"] = str(e)
        
        return {
            "success": False,
            "message": "Aplikasi tidak sehat",
            "data": health_data
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
            "description": "Backend API untuk aplikasi personal finance AI chatbot dengan Luna AI dan Financial Management",
            "features": [
                "User Authentication & Authorization",
                "Profile & Financial Setup",
                "JWT Token Management",
                "MongoDB Integration",
                "Luna AI Chatbot dengan Financial Intelligence",
                "Real-time WebSocket Chat",
                "Chat History Management",
                "Financial AI Assistant",
                "Auto Financial Data Parsing dari Chat",
                "Transaction Management",
                "Savings Goal Tracking",
                "Financial Analytics & Summary",
                "Bahasa Indonesia Support"
            ],
            "endpoints": {
                "auth": "/api/v1/auth",
                "chat": "/api/v1/chat", 
                "finance": "/api/v1/finance",
                "websocket": "/api/v1/chat/ws/{user_id}",
                "docs": "/docs",
                "health": "/health"
            },
            "luna_ai": {
                "name": "Luna",
                "description": "Personal Finance AI Assistant dengan kemampuan parsing data keuangan",
                "language": "Bahasa Indonesia",
                "capabilities": [
                    "Financial advice and tips",
                    "Budget planning assistance", 
                    "Expense tracking guidance",
                    "Investment basics",
                    "Savings recommendations",
                    "Auto-parsing data keuangan dari chat natural",
                    "Konfirmasi sebelum menyimpan data",
                    "Kategorisasi otomatis transaksi",
                    "Tracking progress target tabungan"
                ],
                "supported_data_types": [
                    "Pemasukan (income): 'Dapat gaji 5 juta'",
                    "Pengeluaran (expense): 'Bayar listrik 200 ribu'",
                    "Target tabungan: 'Mau nabung buat beli laptop 10 juta'"
                ]
            },
            "financial_management": {
                "transactions": {
                    "description": "Manajemen pemasukan dan pengeluaran",
                    "features": ["Auto-parsing dari chat", "Kategorisasi", "Filter & pencarian", "Export data"]
                },
                "savings_goals": {
                    "description": "Tracking target tabungan untuk membeli sesuatu",
                    "features": ["Progress tracking", "Deadline management", "Monthly targets", "Achievement notifications"]
                },
                "analytics": {
                    "description": "Analisis dan ringkasan keuangan",
                    "features": ["Daily/Weekly/Monthly/Yearly summary", "Category breakdown", "Trend analysis", "Budget insights"]
                }
            }
        }
    }

# Demo endpoint untuk testing financial parsing
@app.post("/api/v1/demo/parse-financial")
async def demo_parse_financial(message: dict):
    """Demo endpoint untuk testing financial parsing (development only)"""
    if os.getenv("DEBUG", "False").lower() != "true":
        raise HTTPException(status_code=404, detail="Endpoint tidak tersedia")
    
    try:
        from .services.finance_service import FinanceService
        finance_service = FinanceService()
        
        user_message = message.get("message", "")
        if not user_message:
            raise HTTPException(status_code=400, detail="Message required")
        
        result = finance_service.parse_financial_message(user_message)
        
        return {
            "success": True,
            "message": "Parsing berhasil",
            "data": {
                "original_message": user_message,
                "parse_result": result,
                "examples": [
                    "Dapat gaji 5 juta",
                    "Bayar listrik 200 ribu", 
                    "Belanja groceries 150rb",
                    "Mau nabung buat beli laptop 10 juta",
                    "Target beli motor 20 juta"
                ]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    # Jalankan server untuk development
    host = "0.0.0.0"  # Pastikan bind ke semua interface
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    print(f"🚀 Starting development server...")
    print(f"🌐 Host: {host}")
    print(f"📍 Port: {port}")
    print(f"🔧 Debug: {debug}")
    print(f"🔄 Reload: {debug}")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug,
        reload_dirs=["app"] if debug else None,
        log_level="info"
    )