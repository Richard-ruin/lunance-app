# app/main.py - ENHANCED dengan comprehensive logging dan monitoring
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
# ENHANCED LOGGING SETUP
# ============================================================================

def setup_logging():
    """Setup comprehensive logging untuk Luna AI backend"""
    
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    
    # Configure logging format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Setup main logger
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler("logs/app.log", encoding="utf-8"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Setup specialized loggers
    
    # Luna AI logger
    luna_logger = logging.getLogger("luna_ai")
    luna_handler = logging.FileHandler("logs/luna_responses.log", encoding="utf-8")
    luna_handler.setFormatter(logging.Formatter(log_format, date_format))
    luna_logger.addHandler(luna_handler)
    luna_logger.setLevel(logging.INFO)
    
    # API requests logger
    api_logger = logging.getLogger("api_requests")
    api_handler = logging.FileHandler("logs/api_requests.log", encoding="utf-8")
    api_handler.setFormatter(logging.Formatter(log_format, date_format))
    api_logger.addHandler(api_handler)
    api_logger.setLevel(logging.INFO)
    
    # Financial data logger
    finance_logger = logging.getLogger("financial_data")
    finance_handler = logging.FileHandler("logs/financial_operations.log", encoding="utf-8")
    finance_handler.setFormatter(logging.Formatter(log_format, date_format))
    finance_logger.addHandler(finance_handler)
    finance_logger.setLevel(logging.INFO)
    
    # Errors logger
    error_logger = logging.getLogger("errors")
    error_handler = logging.FileHandler("logs/errors.log", encoding="utf-8")
    error_handler.setFormatter(logging.Formatter(log_format, date_format))
    error_logger.addHandler(error_handler)
    error_logger.setLevel(logging.ERROR)
    
    return {
        "main": logging.getLogger(),
        "luna_ai": luna_logger,
        "api_requests": api_logger,
        "financial_data": finance_logger,
        "errors": error_logger
    }

# Initialize loggers
loggers = setup_logging()
main_logger = loggers["main"]
luna_logger = loggers["luna_ai"]
api_logger = loggers["api_requests"]
finance_logger = loggers["financial_data"]
error_logger = loggers["errors"]

# ============================================================================
# RESPONSE LOGGING UTILITIES
# ============================================================================

class ResponseLogger:
    """Utility class untuk logging responses dalam format JSON"""
    
    def __init__(self):
        self.responses_log_file = "logs/respon.json"
        self.ensure_log_file()
    
    def ensure_log_file(self):
        """Ensure respon.json exists dan memiliki struktur yang benar"""
        try:
            if not os.path.exists(self.responses_log_file):
                initial_data = {
                    "metadata": {
                        "created_at": datetime.now().isoformat(),
                        "version": "1.0.0",
                        "description": "Luna AI Backend Responses Log"
                    },
                    "responses": []
                }
                with open(self.responses_log_file, "w", encoding="utf-8") as f:
                    json.dump(initial_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            main_logger.error(f"Error creating respon.json: {e}")
    
    def log_response(self, 
                    endpoint: str, 
                    method: str, 
                    status_code: int, 
                    response_data: Dict[Any, Any], 
                    request_data: Optional[Dict[Any, Any]] = None,
                    user_id: Optional[str] = None,
                    processing_time: Optional[float] = None,
                    response_type: str = "api"):
        """Log response ke respon.json"""
        try:
            # Load existing data
            with open(self.responses_log_file, "r", encoding="utf-8") as f:
                log_data = json.load(f)
            
            # Extract user message if it's a chat endpoint
            user_message = None
            if request_data and isinstance(request_data, dict):
                user_message = request_data.get("message")
            
            # Create new response entry
            response_entry = {
                "timestamp": datetime.now().isoformat(),
                "response_type": response_type,
                "endpoint": endpoint,
                "method": method,
                "status_code": status_code,
                "user_id": user_id,
                "user_message": user_message,
                "processing_time_ms": round(processing_time * 1000, 2) if processing_time else None,
                "request_data": request_data,
                "response_data": response_data
            }
            
            # Add to responses list
            log_data["responses"].append(response_entry)
            
            # Keep only last 1000 responses to prevent file from getting too large
            if len(log_data["responses"]) > 1000:
                log_data["responses"] = log_data["responses"][-1000:]
            
            # Update metadata
            log_data["metadata"]["last_updated"] = datetime.now().isoformat()
            log_data["metadata"]["total_responses"] = len(log_data["responses"])
            
            # Save back to file
            with open(self.responses_log_file, "w", encoding="utf-8") as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
                
            # Also log to specialized loggers based on response type
            if response_type == "luna_ai":
                luna_logger.info(f"Luna Response | {endpoint} | Status: {status_code} | User: {user_id} | Message: {user_message}")
            elif response_type == "financial":
                finance_logger.info(f"Financial Operation | {endpoint} | Status: {status_code} | User: {user_id}")
            else:
                api_logger.info(f"API Request | {method} {endpoint} | Status: {status_code} | User: {user_id}")
                
        except Exception as e:
            error_logger.error(f"Error logging response to respon.json: {e}")

# Initialize response logger
response_logger = ResponseLogger()

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

# ============================================================================
# REQUEST/RESPONSE MIDDLEWARE
# ============================================================================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware untuk logging semua requests dan responses"""
    start_time = time.time()
    
    # Log incoming request
    user_id = extract_user_id_from_request(request)
    
    # Get request body for logging (if it's JSON)
    request_data = None
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.body()
            if body:
                request_data = json.loads(body.decode())
                # Mask sensitive data
                if isinstance(request_data, dict):
                    if "password" in request_data:
                        request_data["password"] = "***masked***"
                    if "confirm_password" in request_data:
                        request_data["confirm_password"] = "***masked***"
        except Exception:
            pass
        
        # Recreate request with body (since body can only be read once)
        async def receive():
            return {"type": "http.request", "body": body}
        request._receive = receive
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    processing_time = time.time() - start_time
    
    # Log response
    endpoint = str(request.url.path)
    method = request.method
    status_code = response.status_code
    
    # Determine response type
    response_type = "api"
    if "/chat/" in endpoint or "luna" in endpoint.lower():
        response_type = "luna_ai"
    elif "/finance/" in endpoint or "/auth/" in endpoint:
        response_type = "financial"
    
    # Read response body for logging
    response_data = None
    if hasattr(response, 'body') and response.body:
        try:
            response_data = json.loads(response.body.decode())
        except Exception:
            response_data = {"message": "Non-JSON response"}
    
    # Log to file
    response_logger.log_response(
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        response_data=response_data,
        request_data=request_data,
        user_id=user_id,
        processing_time=processing_time,
        response_type=response_type
    )
    
    # Log to console for important endpoints
    if status_code >= 400:
        error_logger.error(f"{method} {endpoint} | Status: {status_code} | Time: {processing_time:.3f}s | User: {user_id}")
    else:
        main_logger.info(f"{method} {endpoint} | Status: {status_code} | Time: {processing_time:.3f}s | User: {user_id}")
    
    return response

# ============================================================================
# IMPORT VALIDATION AND ROUTER LOADING
# ============================================================================

def validate_imports():
    """Validasi semua import yang diperlukan"""
    main_logger.info("🔍 Validating critical imports...")
    
    try:
        # Test database connection
        from .config.database import db_manager, create_indexes, get_database
        main_logger.info("✅ Database imports OK")
        
        # Test services
        from .services.auth_service import AuthService
        from .services.finance_service import FinanceService
        from .services.financial_categories import IndonesianStudentCategories
        main_logger.info("✅ Services imports OK")
        
        # Test models
        from .models.user import User, UserProfile, FinancialSettings
        from .models.finance import Transaction, SavingsGoal
        main_logger.info("✅ Models imports OK")
        
        # Test utils
        from .utils.security import verify_token, create_access_token
        from .utils.timezone_utils import IndonesiaDatetime
        main_logger.info("✅ Utils imports OK")
        
        # Test schemas
        from .schemas.auth_schemas import UserRegister, UserLogin
        from .schemas.finance_schemas import (
            DashboardOverview, 
            AnalyticsResponse, 
            HistoryResponse
        )
        main_logger.info("✅ Schemas imports OK")
        
        # Test specific classes that were problematic
        categories = IndonesianStudentCategories()
        budget_type = categories.get_budget_type("Makanan Pokok")
        main_logger.info(f"✅ IndonesianStudentCategories test: {budget_type}")
        
        return True
        
    except ImportError as e:
        error_logger.error(f"IMPORT ERROR: {e}")
        main_logger.error("💡 Missing dependencies detected!")
        main_logger.error("🔧 Please check:")
        main_logger.error("   - All required files are present")
        main_logger.error("   - Python path is correctly configured")
        main_logger.error("   - All dependencies are installed")
        return False
    except Exception as e:
        error_logger.error(f"VALIDATION ERROR: {e}")
        return False

def safe_import_routers():
    """Safely import routers with proper error handling"""
    routers_loaded = []
    
    # Auth router
    try:
        from .routers import auth
        app.include_router(auth.router, prefix="/api/v1")
        routers_loaded.append("auth")
        main_logger.info("✅ Auth router loaded")
    except Exception as e:
        error_logger.error(f"CRITICAL: Auth router failed to load: {e}")
        main_logger.error("🛑 Server cannot start without auth router")
        sys.exit(1)
    
    # Chat router
    try:
        from .routers import chat
        app.include_router(chat.router, prefix="/api/v1")
        routers_loaded.append("chat")
        main_logger.info("✅ Chat router loaded")
    except Exception as e:
        error_logger.error(f"CRITICAL: Chat router failed to load: {e}")
        main_logger.error("🛑 Server cannot start without chat router")
        sys.exit(1)
    
    # Finance router
    try:
        from .routers import finance
        app.include_router(finance.router, prefix="/api/v1")
        routers_loaded.append("finance")
        main_logger.info("✅ Finance router loaded")
    except Exception as e:
        error_logger.error(f"CRITICAL: Finance router failed to load: {e}")
        main_logger.error("🛑 Server cannot start without finance router")
        sys.exit(1)
    
    # NEW: Predictions router
    try:
        from .routers import predictions
        app.include_router(predictions.router, prefix="/api/v1")
        routers_loaded.append("predictions")
        main_logger.info("✅ Predictions router loaded")
    except ImportError as e:
        error_logger.error(f"WARNING: Predictions router missing Prophet dependency: {e}")
        main_logger.warning("⚠️ Predictions router skipped - install Prophet: pip install prophet")
    except Exception as e:
        error_logger.error(f"WARNING: Predictions router failed to load: {e}")
        main_logger.warning("⚠️ Predictions router skipped - check dependencies")
    
    return routers_loaded

# ============================================================================
# EVENT HANDLERS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Event yang dijalankan saat aplikasi start"""
    main_logger.info("🚀 Starting Lunance Backend API...")
    
    # STEP 1: Validate all imports
    if not validate_imports():
        error_logger.error("Critical import validation failed!")
        main_logger.error("🛑 Server startup aborted")
        sys.exit(1)
    
    # STEP 2: Load routers
    routers_loaded = safe_import_routers()
    main_logger.info(f"✅ Loaded routers: {', '.join(routers_loaded)}")
    
    # STEP 3: Setup database
    try:
        from .config.database import db_manager, create_indexes
        db_manager.connect()
        create_indexes()
        main_logger.info("✅ Database connection established")
    except Exception as e:
        error_logger.error(f"Database connection failed: {e}")
        main_logger.error("🛑 Server cannot start without database")
        sys.exit(1)
    
    # STEP 4: Test critical services
    try:
        from .services.finance_service import FinanceService
        from .services.auth_service import AuthService
        from .services.financial_categories import IndonesianStudentCategories
        
        # Test FinanceService
        finance_service = FinanceService()
        main_logger.info("✅ FinanceService initialized")
        
        # Test AuthService
        auth_service = AuthService()
        main_logger.info("✅ AuthService initialized")
        
        # Test IndonesianStudentCategories
        categories = IndonesianStudentCategories.get_all_needs_categories()
        main_logger.info(f"✅ IndonesianStudentCategories: {len(categories)} needs categories loaded")
        
    except Exception as e:
        error_logger.error(f"Service initialization failed: {e}")
        main_logger.error("🛑 Server cannot start without services")
        sys.exit(1)
    
    # SUCCESS: Display startup information
    local_ip = get_local_ip()
    port = os.getenv("PORT", "8000")
    
    startup_info = {
        "status": "started",
        "server_info": {
            "local_url": f"http://localhost:{port}",
            "network_url": f"http://{local_ip}:{port}",
            "docs_url": f"http://{local_ip}:{port}/docs",
            "health_url": f"http://{local_ip}:{port}/health"
        },
        "routers_loaded": routers_loaded,
        "logging": {
            "app_log": "logs/app.log",
            "luna_responses": "logs/luna_responses.log",
            "api_requests": "logs/api_requests.log",
            "financial_operations": "logs/financial_operations.log",
            "errors": "logs/errors.log",
            "json_responses": "logs/respon.json"
        }
    }
    
    # Log startup info
    main_logger.info("=" * 80)
    main_logger.info("🎉 Lunance Backend API successfully started!")
    main_logger.info(f"🤖 Luna AI Chatbot: Ready with Financial Intelligence")
    main_logger.info(f"💰 Financial Management: Active with 50/30/20 Method")
    main_logger.info(f"🌐 Server running on:")
    main_logger.info(f"   • Local:   http://localhost:{port}")
    main_logger.info(f"   • Network: http://{local_ip}:{port}")
    main_logger.info(f"📝 API Documentation:")
    main_logger.info(f"   • Swagger UI: http://{local_ip}:{port}/docs")
    main_logger.info(f"   • ReDoc:      http://{local_ip}:{port}/redoc")
    main_logger.info(f"🔍 Health Check: http://{local_ip}:{port}/health")
    main_logger.info(f"💬 WebSocket Chat: ws://{local_ip}:{port}/api/v1/chat/ws/{{user_id}}")
    main_logger.info(f"📊 Finance API: http://{local_ip}:{port}/api/v1/finance")
    main_logger.info(f"🔧 Routers Loaded: {', '.join(routers_loaded)}")
    main_logger.info("=" * 80)
    main_logger.info("✨ Luna AI Features:")
    main_logger.info("   • Auto financial data parsing from chat")
    main_logger.info("   • Confirmation before saving transactions")
    main_logger.info("   • Auto-categorization (Indonesian student categories)")
    main_logger.info("   • Savings goal tracking")
    main_logger.info("   • Personal financial tips")
    main_logger.info("   • 50/30/20 budgeting method support")
    main_logger.info("=" * 80)
    main_logger.info("📋 Logging Configuration:")
    main_logger.info("   • All API requests: logs/api_requests.log")
    main_logger.info("   • Luna AI responses: logs/luna_responses.log")  
    main_logger.info("   • Financial operations: logs/financial_operations.log")
    main_logger.info("   • Error logs: logs/errors.log")
    main_logger.info("   • JSON responses: logs/respon.json")
    main_logger.info("   • Main app logs: logs/app.log")
    main_logger.info("=" * 80)
    
    # Log startup to respon.json
    response_logger.log_response(
        endpoint="/startup",
        method="SYSTEM",
        status_code=200,
        response_data=startup_info,
        response_type="system"
    )

@app.on_event("shutdown")
async def shutdown_event():
    """Event yang dijalankan saat aplikasi shutdown"""
    try:
        from .config.database import db_manager
        db_manager.close()
        main_logger.info("✅ Database connection closed")
    except Exception as e:
        error_logger.error(f"Error closing database: {e}")
    
    shutdown_info = {
        "status": "shutdown",
        "timestamp": datetime.now().isoformat()
    }
    
    # Log shutdown
    response_logger.log_response(
        endpoint="/shutdown",
        method="SYSTEM", 
        status_code=200,
        response_data=shutdown_info,
        response_type="system"
    )
    
    main_logger.info("👋 Lunance Backend API gracefully shut down")

# ============================================================================
# GLOBAL EXCEPTION HANDLER
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handler untuk semua exception yang tidak tertangani"""
    error_logger.error(f"🚨 Unhandled exception: {exc}")
    
    error_response = {
        "success": False,
        "message": "Terjadi kesalahan internal server",
        "error_type": type(exc).__name__,
        "errors": [str(exc)] if os.getenv("DEBUG", "False").lower() == "true" else ["Internal server error"]
    }
    
    # Log error response
    response_logger.log_response(
        endpoint=str(request.url.path),
        method=request.method,
        status_code=500,
        response_data=error_response,
        user_id=extract_user_id_from_request(request),
        response_type="error"
    )
    
    return JSONResponse(
        status_code=500,
        content=error_response
    )

# ============================================================================
# ROOT ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint untuk health check"""
    response_data = {
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
                "Bahasa Indonesia Support",
                "Comprehensive Logging System"
            ],
            "docs": "/docs",
            "redoc": "/redoc",
            "logging": {
                "status": "active",
                "files": {
                    "responses": "logs/respon.json",
                    "app_log": "logs/app.log",
                    "luna_responses": "logs/luna_responses.log",
                    "api_requests": "logs/api_requests.log"
                }
            }
        }
    }
    
    return response_data

@app.get("/health")
async def health_check():
    """Endpoint untuk mengecek kesehatan aplikasi"""
    from .utils.timezone_utils import IndonesiaDatetime
    
    health_data = {
        "app_status": "running",
        "database": "unknown",
        "luna_ai": "ready",
        "financial_parser": "ready",
        "websocket": "available",
        "finance_service": "unknown",
        "auth_service": "unknown",
        "categories": "unknown",
        "logging": "active",
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
        
        response_data = {
            "success": True,
            "message": "Aplikasi sehat dan berjalan dengan baik",
            "data": health_data,
            "timestamp": IndonesiaDatetime.now().isoformat()
        }
        
        return response_data
        
    except Exception as e:
        health_data["overall_status"] = "unhealthy"
        health_data["error"] = str(e)
        
        error_response = {
            "success": False,
            "message": "Aplikasi tidak sehat",
            "data": health_data,
            "timestamp": IndonesiaDatetime.now().isoformat()
        }
        
        error_logger.error(f"Health check failed: {e}")
        
        return JSONResponse(
            status_code=503,
            content=error_response
        )

# ============================================================================
# LOGGING AND MONITORING ENDPOINTS
# ============================================================================

@app.get("/logs/status")
async def logs_status():
    """Endpoint untuk mengecek status logging"""
    try:
        log_files = {
            "app.log": os.path.exists("logs/app.log"),
            "luna_responses.log": os.path.exists("logs/luna_responses.log"),
            "api_requests.log": os.path.exists("logs/api_requests.log"),
            "financial_operations.log": os.path.exists("logs/financial_operations.log"),
            "errors.log": os.path.exists("logs/errors.log"),
            "respon.json": os.path.exists("logs/respon.json")
        }
        
        # Get file sizes
        file_sizes = {}
        for filename, exists in log_files.items():
            if exists:
                try:
                    size = os.path.getsize(f"logs/{filename}")
                    file_sizes[filename] = f"{size} bytes"
                except:
                    file_sizes[filename] = "unknown"
        
        response_data = {
            "success": True,
            "message": "Status logging berhasil diambil",
            "data": {
                "logging_active": True,
                "log_files": log_files,
                "file_sizes": file_sizes,
                "logs_directory": "logs/",
                "all_files_exist": all(log_files.values())
            }
        }
        
        return response_data
        
    except Exception as e:
        error_logger.error(f"Error getting logs status: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Gagal mengambil status logging",
                "error": str(e)
            }
        )

@app.post("/test/luna-response")
async def test_luna_response():
    """Test endpoint untuk mencoba logging Luna response (development only)"""
    if os.getenv("DEBUG", "False").lower() != "true":
        raise HTTPException(status_code=404, detail="Endpoint hanya tersedia dalam mode debug")
    
    try:
        # Simulate Luna response
        test_response = {
            "luna_message": "Halo! Saya Luna, asisten keuangan AI untuk mahasiswa Indonesia. Bagaimana saya bisa membantu Anda hari ini?",
            "message_type": "greeting",
            "financial_data_detected": False,
            "suggestions": [
                "Input transaksi keuangan",
                "Cek budget 50/30/20", 
                "Buat target tabungan",
                "Tips hemat mahasiswa"
            ]
        }
        
        # Log this response
        luna_logger.info(f"Test Luna Response: {json.dumps(test_response, ensure_ascii=False)}")
        
        response_data = {
            "success": True,
            "message": "Test Luna response berhasil dan telah dicatat di log",
            "data": test_response
        }
        
        # Also log to respon.json
        response_logger.log_response(
            endpoint="/test/luna-response",
            method="POST",
            status_code=200,
            response_data=response_data,
            response_type="luna_ai"
        )
        
        return response_data
        
    except Exception as e:
        error_logger.error(f"Error in test Luna response: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

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
        
        response_data = {
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
        
        # Log financial parsing
        finance_logger.info(f"Financial Parse Test: {user_message} -> {result}")
        
        return response_data
        
    except Exception as e:
        error_logger.error(f"Error parsing: {e}")
        raise HTTPException(status_code=500, detail=f"Error parsing: {str(e)}")

# ============================================================================
# API INFO ENDPOINT
# ============================================================================

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
            "test_account": {
                "email": "richardpakpahan7383@gmail.com",
                "note": "Available for testing Luna AI responses"
            },
            "logging": {
                "status": "active",
                "description": "Comprehensive logging untuk monitoring Luna AI responses dan API operations",
                "files": {
                    "main_log": "logs/app.log",
                    "luna_responses": "logs/luna_responses.log",
                    "api_requests": "logs/api_requests.log", 
                    "financial_ops": "logs/financial_operations.log",
                    "errors": "logs/errors.log",
                    "json_responses": "logs/respon.json"
                }
            },
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
                    "Conversation History",
                    "Response Logging"
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
                "health": "/health",
                "logs_status": "/logs/status"
            },
            "luna_ai": {
                "name": "Luna",
                "description": "Personal Finance AI Assistant untuk mahasiswa Indonesia",
                "language": "Bahasa Indonesia",
                "budget_method": "50/30/20 Elizabeth Warren",
                "logging": "Semua respon Luna dicatat di logs/luna_responses.log dan logs/respon.json",
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
            }
        }
    }

# ============================================================================
# DEVELOPMENT SERVER RUNNER
# ============================================================================

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
    print(f"📋 Logging: Active (logs/ directory)")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug,
        reload_dirs=["app"] if debug else None,
        log_level="info"
    )