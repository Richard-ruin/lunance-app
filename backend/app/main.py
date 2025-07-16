# app/main.py - FIXED dengan proper error handling
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import socket
import sys
from dotenv import load_dotenv

load_dotenv()

def get_local_ip():
    """Mendapatkan IP address lokal"""
    try:
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

# CRITICAL: Import semua dependencies yang diperlukan di startup
def validate_imports():
    """Validasi semua import yang diperlukan"""
    print("🔍 Validating critical imports...")
    
    try:
        # Test database connection
        from .config.database import db_manager, create_indexes, get_database
        print("✅ Database imports OK")
        
        # Test services
        from .services.auth_service import AuthService
        from .services.finance_service import FinanceService
        from .services.financial_categories import IndonesianStudentCategories
        print("✅ Services imports OK")
        
        # Test models
        from .models.user import User, UserProfile, FinancialSettings
        from .models.finance import Transaction, SavingsGoal
        print("✅ Models imports OK")
        
        # Test utils
        from .utils.security import verify_token, create_access_token
        from .utils.timezone_utils import IndonesiaDatetime
        print("✅ Utils imports OK")
        
        # Test schemas
        from .schemas.auth_schemas import UserRegister, UserLogin
        from .schemas.finance_schemas import (
            DashboardOverview, 
            AnalyticsResponse, 
            HistoryResponse
        )
        print("✅ Schemas imports OK")
        
        # Test specific classes that were problematic
        categories = IndonesianStudentCategories()
        budget_type = categories.get_budget_type("Makanan Pokok")
        print(f"✅ IndonesianStudentCategories test: {budget_type}")
        
        return True
        
    except ImportError as e:
        print(f"❌ IMPORT ERROR: {e}")
        print("💡 Missing dependencies detected!")
        print("🔧 Please check:")
        print("   - All required files are present")
        print("   - Python path is correctly configured")
        print("   - All dependencies are installed")
        return False
    except Exception as e:
        print(f"❌ VALIDATION ERROR: {e}")
        return False

def safe_import_routers():
    """Safely import routers with proper error handling"""
    routers_loaded = []
    
    # Auth router
    try:
        from .routers import auth
        app.include_router(auth.router, prefix="/api/v1")
        routers_loaded.append("auth")
        print("✅ Auth router loaded")
    except Exception as e:
        print(f"❌ CRITICAL: Auth router failed to load: {e}")
        print("🛑 Server cannot start without auth router")
        sys.exit(1)
    
    # Chat router
    try:
        from .routers import chat
        app.include_router(chat.router, prefix="/api/v1")
        routers_loaded.append("chat")
        print("✅ Chat router loaded")
    except Exception as e:
        print(f"❌ CRITICAL: Chat router failed to load: {e}")
        print("🛑 Server cannot start without chat router")
        sys.exit(1)
    
    # Finance router
    try:
        from .routers import finance
        app.include_router(finance.router, prefix="/api/v1")
        routers_loaded.append("finance")
        print("✅ Finance router loaded")
    except Exception as e:
        print(f"❌ CRITICAL: Finance router failed to load: {e}")
        print("🛑 Server cannot start without finance router")
        sys.exit(1)
    
    return routers_loaded

# Event handlers
@app.on_event("startup")
async def startup_event():
    """Event yang dijalankan saat aplikasi start"""
    print("🚀 Starting Lunance Backend API...")
    
    # STEP 1: Validate all imports
    if not validate_imports():
        print("❌ Critical import validation failed!")
        print("🛑 Server startup aborted")
        sys.exit(1)
    
    # STEP 2: Load routers
    routers_loaded = safe_import_routers()
    print(f"✅ Loaded routers: {', '.join(routers_loaded)}")
    
    # STEP 3: Setup database
    try:
        from .config.database import db_manager, create_indexes
        db_manager.connect()
        create_indexes()
        print("✅ Database connection established")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("🛑 Server cannot start without database")
        sys.exit(1)
    
    # STEP 4: Test critical services
    try:
        from .services.finance_service import FinanceService
        from .services.auth_service import AuthService
        from .services.financial_categories import IndonesianStudentCategories
        
        # Test FinanceService
        finance_service = FinanceService()
        print("✅ FinanceService initialized")
        
        # Test AuthService
        auth_service = AuthService()
        print("✅ AuthService initialized")
        
        # Test IndonesianStudentCategories
        categories = IndonesianStudentCategories.get_all_needs_categories()
        print(f"✅ IndonesianStudentCategories: {len(categories)} needs categories loaded")
        
    except Exception as e:
        print(f"❌ Service initialization failed: {e}")
        print("🛑 Server cannot start without services")
        sys.exit(1)
    
    # SUCCESS: Display startup information
    local_ip = get_local_ip()
    port = os.getenv("PORT", "8000")
    
    print("=" * 80)
    print("🎉 Lunance Backend API successfully started!")
    print(f"🤖 Luna AI Chatbot: Ready with Financial Intelligence")
    print(f"💰 Financial Management: Active with 50/30/20 Method")
    print(f"🌐 Server running on:")
    print(f"   • Local:   http://localhost:{port}")
    print(f"   • Network: http://{local_ip}:{port}")
    print(f"📝 API Documentation:")
    print(f"   • Swagger UI: http://{local_ip}:{port}/docs")
    print(f"   • ReDoc:      http://{local_ip}:{port}/redoc")
    print(f"🔍 Health Check: http://{local_ip}:{port}/health")
    print(f"💬 WebSocket Chat: ws://{local_ip}:{port}/api/v1/chat/ws/{{user_id}}")
    print(f"📊 Finance API: http://{local_ip}:{port}/api/v1/finance")
    print(f"🔧 Routers Loaded: {', '.join(routers_loaded)}")
    print("=" * 80)
    print("✨ Luna AI Features:")
    print("   • Auto financial data parsing from chat")
    print("   • Confirmation before saving transactions")
    print("   • Auto-categorization (Indonesian student categories)")
    print("   • Savings goal tracking")
    print("   • Personal financial tips")
    print("   • 50/30/20 budgeting method support")
    print("=" * 80)

@app.on_event("shutdown")
async def shutdown_event():
    """Event yang dijalankan saat aplikasi shutdown"""
    try:
        from .config.database import db_manager
        db_manager.close()
        print("✅ Database connection closed")
    except Exception as e:
        print(f"⚠️ Error closing database: {e}")
    
    print("👋 Lunance Backend API gracefully shut down")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handler untuk semua exception yang tidak tertangani"""
    print(f"🚨 Unhandled exception: {exc}")
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Terjadi kesalahan internal server",
            "error_type": type(exc).__name__,
            "errors": [str(exc)] if os.getenv("DEBUG", "False").lower() == "true" else ["Internal server error"]
        }
    )

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
            "method": "50/30/20 Elizabeth Warren Budgeting",
            "features": [
                "Luna AI Chatbot dengan Financial Intelligence",
                "Auto Financial Data Parsing",
                "WebSocket Support untuk Real-time Chat",
                "Transaction & Savings Goal Management",
                "Financial Analytics & Summary dengan 50/30/20 Method",
                "Indonesian Student Categories",
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
        "app_status": "running",
        "database": "unknown",
        "luna_ai": "ready",
        "financial_parser": "ready",
        "websocket": "available",
        "finance_service": "unknown",
        "auth_service": "unknown",
        "categories": "unknown",
        "overall_status": "unknown"
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
        
        # Test auth service
        from .services.auth_service import AuthService
        auth_service = AuthService()
        health_data["auth_service"] = "active"
        
        # Test categories
        from .services.financial_categories import IndonesianStudentCategories
        categories_count = len(IndonesianStudentCategories.get_all_expense_categories())
        health_data["categories"] = f"loaded ({categories_count} categories)"
        
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
        
        return {
            "success": False,
            "message": "Aplikasi tidak sehat",
            "data": health_data,
            "timestamp": IndonesiaDatetime.now().isoformat()
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
            "budget_method": "50/30/20 Elizabeth Warren",
            "target_audience": "Indonesian University Students",
            "features": {
                "authentication": [
                    "User Registration & Login",
                    "JWT Token Management",
                    "Profile & Financial Setup",
                    "50/30/20 Budget Setup"
                ],
                "chat": [
                    "Real-time WebSocket Chat",
                    "Luna AI Financial Assistant",
                    "Auto Financial Data Parsing",
                    "Natural Language Processing",
                    "Conversation History"
                ],
                "finance": [
                    "Transaction Management",
                    "Savings Goal Tracking",
                    "Financial Analytics & Summary",
                    "50/30/20 Budget Tracking",
                    "Indonesian Student Categories",
                    "Export Functionality"
                ]
            },
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
                "description": "Personal Finance AI Assistant untuk mahasiswa Indonesia",
                "language": "Bahasa Indonesia",
                "budget_method": "50/30/20 Elizabeth Warren",
                "capabilities": [
                    "Financial advice and tips",
                    "Budget planning assistance (50/30/20)",
                    "Expense tracking guidance",
                    "Investment basics for students",
                    "Savings recommendations",
                    "Auto-parsing data keuangan dari chat natural",
                    "Konfirmasi sebelum menyimpan data",
                    "Kategorisasi otomatis transaksi mahasiswa Indonesia",
                    "Tracking progress target tabungan"
                ],
                "supported_data_types": [
                    "Pemasukan (income): 'Dapat uang saku 2 juta'",
                    "Pengeluaran (expense): 'Bayar kos 800 ribu'",
                    "Target tabungan: 'Mau nabung buat beli laptop 10 juta'"
                ],
                "categories": {
                    "needs_50_percent": "Kos, makan, transport, pendidikan, kesehatan",
                    "wants_30_percent": "Hiburan, jajan, fashion, organisasi, target tabungan barang",
                    "savings_20_percent": "Tabungan umum, dana darurat, investasi, modal usaha"
                }
            },
            "financial_management": {
                "method": "50/30/20 Elizabeth Warren",
                "description": "Budgeting method yang membagi income menjadi 3 kategori utama",
                "allocation": {
                    "needs": "50% - Kebutuhan pokok yang wajib",
                    "wants": "30% - Keinginan dan lifestyle",
                    "savings": "20% - Tabungan masa depan"
                },
                "features": {
                    "transactions": "Auto-parsing, kategorisasi, filter, export",
                    "savings_goals": "Progress tracking, deadline, notifications",
                    "analytics": "Daily/Weekly/Monthly summary, trend analysis",
                    "budget_tracking": "Real-time budget monitoring, recommendations"
                }
            }
        }
    }

# Demo endpoint untuk testing financial parsing
@app.post("/api/v1/demo/parse-financial")
async def demo_parse_financial(message: dict):
    """Demo endpoint untuk testing financial parsing (development only)"""
    if os.getenv("DEBUG", "False").lower() != "true":
        raise HTTPException(status_code=404, detail="Endpoint hanya tersedia dalam mode debug")
    
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
                "budget_method": "50/30/20 Elizabeth Warren",
                "examples": [
                    "Dapat uang saku 2 juta",
                    "Bayar kos 800 ribu",
                    "Belanja groceries 150rb",
                    "Jajan di cafe 50rb",
                    "Mau nabung buat beli laptop 10 juta",
                    "Target beli motor 20 juta"
                ]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing: {str(e)}")

# Development server runner
if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting development server...")
    
    # Jalankan server untuk development
    host = "0.0.0.0"  # Bind ke semua interface
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    print(f"🌐 Host: {host}")
    print(f"📍 Port: {port}")
    print(f"🔧 Debug Mode: {debug}")
    print(f"🔄 Auto Reload: {debug}")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug,
        reload_dirs=["app"] if debug else None,
        log_level="info"
    )