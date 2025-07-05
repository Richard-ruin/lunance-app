# app/main.py (updated untuk Advanced Features + AI)
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
import logging
from datetime import datetime

from .database import connect_to_mongo, close_mongo_connection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for features
DASHBOARD_FEATURES = False
AI_FEATURES = False
ADVANCED_FEATURES = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Lunance API...")
    await connect_to_mongo()
    
    # Create upload directories
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("uploads/profile_pictures", exist_ok=True)
    os.makedirs("uploads/receipts", exist_ok=True)
    
    # Create AI models cache directory
    if AI_FEATURES:
        os.makedirs("ai_models", exist_ok=True)
        os.makedirs("ai_models/indobert", exist_ok=True)
        os.makedirs("ai_models/sentiment", exist_ok=True)
        os.makedirs("ai_models/embeddings", exist_ok=True)
    
    # Initialize AI models if enabled
    if AI_FEATURES:
        try:
            logger.info("🤖 Initializing Luna AI models...")
            from .services.indonesian_nlp import nlp_service
            from .services.intent_classifier import intent_classifier
            
            await nlp_service.initialize_models()
            await intent_classifier.load_intents()
            logger.info("✅ Luna AI models initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize AI models: {e}")
    
    # Initialize Advanced Features if enabled
    if ADVANCED_FEATURES:
        try:
            logger.info("📊 Initializing Advanced Analytics & Prediction models...")
            from .services.financial_predictor import FinancialPredictor
            from .services.notification_service import NotificationService
            
            # Test Facebook Prophet availability
            import prophet
            logger.info("✅ Facebook Prophet available for predictions")
            
            logger.info("✅ Advanced Features initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Advanced Features: {e}")
    
    logger.info("Lunance API started successfully")
    yield
    
    # Shutdown
    logger.info("Shutting down Lunance API...")
    await close_mongo_connection()

app = FastAPI(
    title="Lunance API",
    description="Complete Backend REST API untuk aplikasi manajemen keuangan mahasiswa dengan Dashboard, Analytics, AI Chatbot Luna & Advanced Financial Predictions",
    version="5.0.0",  # Updated version for Advanced Features
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
if os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Import and include all routers
try:
    # Core routers
    from .routers.auth import router as auth_router
    from .routers.universities import router as universities_router
    from .routers.profile import router as profile_router
    from .routers.admin_users import router as admin_users_router
    
    # Financial routers
    from .routers.categories import router as categories_router
    from .routers.transactions import router as transactions_router
    from .routers.analytics import router as analytics_router
    from .routers.budgets import router as budgets_router
    from .routers.export_import import router as export_import_router
    
    # Try to import dashboard routers
    try:
        from .routers.dashboard import router as dashboard_router
        from .routers.savings_goals import router as savings_goals_router
        from .routers.websocket import router as websocket_router
        DASHBOARD_FEATURES = True
        logger.info("✅ Dashboard features loaded")
    except ImportError as e:
        logger.warning(f"⚠️ Dashboard features not available: {e}")
        DASHBOARD_FEATURES = False
    
    # Try to import AI routers
    try:
        from .routers.chat import router as chat_router
        from .routers.websocket_chat import router as websocket_chat_router
        from .routers.admin_ai import router as admin_ai_router
        AI_FEATURES = True
        logger.info("✅ AI Chatbot Luna features loaded")
    except ImportError as e:
        logger.warning(f"⚠️ AI features not available: {e}")
        AI_FEATURES = False
    
    # Try to import Advanced Features routers (NEW)
    try:
        from .routers.predictions import router as predictions_router
        from .routers.notifications import router as notifications_router
        from .routers.recurring_transactions import router as recurring_transactions_router
        from .routers.advanced_analytics import router as advanced_analytics_router
        from .routers.financial_insights import router as financial_insights_router
        ADVANCED_FEATURES = True
        logger.info("✅ Advanced Features (Predictions, Notifications, Recurring) loaded")
    except ImportError as e:
        logger.warning(f"⚠️ Advanced Features not available: {e}")
        ADVANCED_FEATURES = False
    
    # Include core routers
    app.include_router(auth_router)
    app.include_router(universities_router)
    app.include_router(profile_router)
    app.include_router(admin_users_router)
    app.include_router(categories_router)
    app.include_router(transactions_router)
    app.include_router(analytics_router)
    app.include_router(budgets_router)
    app.include_router(export_import_router)
    
    # Include dashboard routers if available
    if DASHBOARD_FEATURES:
        app.include_router(dashboard_router)
        app.include_router(savings_goals_router)
        app.include_router(websocket_router)
        logger.info("✅ Dashboard routers included")
    
    # Include AI routers if available
    if AI_FEATURES:
        app.include_router(chat_router)
        app.include_router(websocket_chat_router)
        app.include_router(admin_ai_router)
        logger.info("✅ AI Luna routers included")
    
    # Include Advanced Features routers if available (NEW)
    if ADVANCED_FEATURES:
        app.include_router(predictions_router)
        app.include_router(notifications_router)
        app.include_router(recurring_transactions_router)
        app.include_router(advanced_analytics_router)
        app.include_router(financial_insights_router)
        logger.info("✅ Advanced Features routers included")
    
    logger.info("✅ All routers loaded successfully")
    
except ImportError as e:
    logger.warning(f"⚠️ Some routers could not be loaded: {e}")

# Import custom exceptions
try:
    from .utils.exceptions import CustomHTTPException
    
    @app.exception_handler(CustomHTTPException)
    async def custom_exception_handler(request: Request, exc: CustomHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "error_code": getattr(exc, 'error_code', None),
                "path": str(request.url),
                "timestamp": str(datetime.utcnow())
            }
        )
    logger.info("✅ Custom exception handlers loaded")
except ImportError as e:
    logger.warning(f"⚠️ Custom exceptions not available: {e}")

@app.get("/")
async def root():
    base_features = [
        "✅ Authentication & Authorization",
        "✅ User Management & Registration", 
        "✅ University Approval System",
        "✅ Category Management (Global + Personal)",
        "✅ Transaction Management with CRUD",
        "✅ Advanced Analytics & Insights",
        "✅ Budget Tracking & Alerts",
        "✅ Data Export/Import (CSV, PDF, JSON)",
        "✅ Smart Transaction Features",
        "✅ Financial Health Scoring"
    ]
    
    # Add dashboard features if available
    if DASHBOARD_FEATURES:
        base_features.extend([
            "✅ Real-time Dashboard",
            "✅ Savings Goals Management",
            "✅ WebSocket Real-time Updates", 
            "✅ Advanced Chart Analytics",
            "✅ Spending Habits Analysis"
        ])
    
    # Add AI features if available
    if AI_FEATURES:
        base_features.extend([
            "🤖 AI Chatbot Luna",
            "🇮🇩 Indonesian Language Processing",
            "💬 Natural Language Transactions",
            "📊 AI-Powered Financial Analysis",
            "🎯 Smart Goal Setting Assistance",
            "💡 Personalized Financial Advice"
        ])
    
    # Add Advanced features if available (NEW)
    if ADVANCED_FEATURES:
        base_features.extend([
            "📈 Facebook Prophet Financial Predictions",
            "🔔 Smart Notification System",
            "🔄 Recurring Transaction Automation",
            "📊 Advanced Analytics & Cash Flow",
            "🎯 Financial Health Scoring",
            "💡 AI-Powered Recommendations",
            "📉 Risk Assessment Analysis",
            "👥 Anonymous Peer Comparison",
            "🔍 Seasonal Spending Patterns",
            "🚨 Predictive Financial Alerts"
        ])
    
    base_endpoints = {
        "auth": "/auth/*",
        "universities": "/universities/*",
        "profile": "/profile/*",
        "admin": "/admin/*",
        "categories": "/categories/*",
        "transactions": "/transactions/*",
        "analytics": "/analytics/*",
        "budgets": "/budgets/*",
        "export_import": "/export-import/*"
    }
    
    # Add dashboard endpoints if available
    if DASHBOARD_FEATURES:
        base_endpoints.update({
            "dashboard": "/dashboard/*",
            "savings_goals": "/savings-goals/*",
            "websocket": "/ws/*"
        })
    
    # Add AI endpoints if available
    if AI_FEATURES:
        base_endpoints.update({
            "ai_chat": "/chat/*",
            "ai_websocket": "/ws/chat/*",
            "ai_admin": "/admin/ai/*"
        })
    
    # Add Advanced endpoints if available (NEW)
    if ADVANCED_FEATURES:
        base_endpoints.update({
            "predictions": "/predictions/*",
            "notifications": "/notifications/*",
            "recurring_transactions": "/recurring-transactions/*",
            "advanced_analytics": "/analytics/*",
            "financial_insights": "/financial-insights/*"
        })
    
    return {
        "message": "Lunance API v5.0.0 - Complete AI-Powered Financial Management System with Advanced Predictions",
        "status": "operational",
        "features": base_features,
        "endpoints": base_endpoints,
        "dashboard_enabled": DASHBOARD_FEATURES,
        "ai_enabled": AI_FEATURES,
        "advanced_enabled": ADVANCED_FEATURES,
        "total_features": len(base_features)
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "5.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected",
        "features_count": (10 + (5 if DASHBOARD_FEATURES else 0) + (6 if AI_FEATURES else 0) + (10 if ADVANCED_FEATURES else 0)),
        "dashboard_features": DASHBOARD_FEATURES,
        "ai_features": AI_FEATURES,
        "advanced_features": ADVANCED_FEATURES
    }

@app.get("/api-info")
async def api_info():
    """Get complete API information"""
    base_features = {
        "authentication": {
            "jwt_tokens": True,
            "otp_verification": True,
            "password_reset": True,
            "academic_email_validation": True
        },
        "user_management": {
            "role_based_access": True,
            "profile_management": True,
            "university_approval": True,
            "admin_dashboard": True
        },
        "financial_features": {
            "transaction_management": True,
            "category_system": True,
            "budget_tracking": True,
            "analytics_insights": True,
            "export_import": True,
            "smart_categorization": True
        },
        "data_formats": {
            "csv_export": True,
            "pdf_reports": True,
            "json_export": True,
            "template_download": True
        }
    }
    
    # Add dashboard features if available
    if DASHBOARD_FEATURES:
        base_features["dashboard_features"] = {
            "real_time_dashboard": True,
            "savings_goals": True,
            "websocket_updates": True,
            "advanced_charts": True,
            "spending_analysis": True,
            "financial_forecasting": True
        }
    
    # Add AI features if available
    if AI_FEATURES:
        base_features["ai_features"] = {
            "indonesian_nlp": True,
            "intent_classification": True,
            "entity_extraction": True,
            "sentiment_analysis": True,
            "natural_language_transactions": True,
            "ai_financial_advice": True,
            "contextual_conversations": True,
            "real_time_chat": True
        }
    
    # Add Advanced features if available (NEW)
    if ADVANCED_FEATURES:
        base_features["advanced_features"] = {
            "facebook_prophet_predictions": True,
            "smart_notifications": True,
            "recurring_transactions": True,
            "advanced_analytics": True,
            "cash_flow_analysis": True,
            "seasonal_patterns": True,
            "financial_health_scoring": True,
            "ai_recommendations": True,
            "risk_assessment": True,
            "peer_comparison": True,
            "predictive_alerts": True
        }
    
    return {
        "title": "Lunance AI-Powered Financial Management API with Advanced Predictions",
        "version": "5.0.0",
        "description": "Complete backend system dengan AI Chatbot Luna, Facebook Prophet predictions, dan advanced analytics untuk manajemen keuangan mahasiswa Indonesia",
        "features": base_features,
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc"
        },
        "dashboard_enabled": DASHBOARD_FEATURES,
        "ai_enabled": AI_FEATURES,
        "advanced_enabled": ADVANCED_FEATURES
    }

# AI-specific endpoints (only if AI features are available)
if AI_FEATURES:
    @app.get("/luna-info")
    async def luna_info():
        """Get Luna AI chatbot information"""
        return {
            "version": "1.0.0",
            "name": "Luna",
            "description": "AI Assistant untuk manajemen keuangan dengan pemahaman bahasa Indonesia",
            "capabilities": [
                "Natural Language Transaction Input",
                "Financial Analysis & Insights", 
                "Budget Monitoring & Alerts",
                "Savings Goal Setting & Tracking",
                "Spending Pattern Analysis",
                "Personalized Financial Advice",
                "Context-Aware Conversations",
                "Real-time WebSocket Communication"
            ],
            "supported_languages": ["Indonesian", "English"],
            "supported_intents": [
                "add_expense", "add_income", "check_balance",
                "spending_analysis", "budget_status", "create_goal",
                "greeting", "help", "goodbye"
            ],
            "models": {
                "language_model": "indolem/indobert-base-uncased",
                "sentiment_model": "w11wo/indonesian-roberta-base-sentiment-classifier",
                "entity_extraction": "custom_indonesian_financial_ner"
            }
        }

# Dashboard-specific endpoints (only if dashboard features are available)
if DASHBOARD_FEATURES:
    @app.get("/dashboard-info")
    async def dashboard_info():
        """Get dashboard-specific information"""
        return {
            "version": "1.0.0",
            "features": [
                "Real-time Financial Dashboard",
                "Savings Goals Management",
                "Advanced Analytics Charts",
                "WebSocket Live Updates",
                "Spending Habits Analysis",
                "Financial Health Scoring",
                "Peak Spending Times Analysis",
                "Income vs Expense Trends",
                "Category Breakdown Visualization"
            ],
            "chart_types": [
                "Line Charts (Trends)",
                "Pie Charts (Categories)",
                "Bar Charts (Daily/Weekly)",
                "Radar Charts (Spending Patterns)"
            ],
            "real_time_features": [
                "Live Balance Updates",
                "Transaction Notifications",
                "Goal Progress Updates",
                "Budget Alert Notifications"
            ]
        }

# Advanced Features endpoints (NEW)
if ADVANCED_FEATURES:
    @app.get("/advanced-info")
    async def advanced_info():
        """Get Advanced Features information"""
        return {
            "version": "1.0.0",
            "name": "Advanced Financial Analytics & Predictions",
            "description": "Facebook Prophet-powered predictions dengan advanced analytics untuk insights mendalam",
            "prediction_features": [
                "Income Forecasting (up to 1 year)",
                "Expense Prediction with Seasonality",
                "Account Balance Forecasting",
                "Category-specific Spending Predictions",
                "Confidence Intervals & Accuracy Metrics",
                "Model Performance Tracking"
            ],
            "notification_features": [
                "Smart Budget Alerts (80%, 100% thresholds)",
                "Savings Goal Reminders",
                "Weekly Financial Summaries",
                "Spending Pattern Insights",
                "Multi-channel Notifications (in-app, email, push)",
                "Customizable Notification Preferences"
            ],
            "recurring_features": [
                "Automated Recurring Transactions",
                "Flexible Scheduling (daily, weekly, monthly, yearly)",
                "Manual Execution Override",
                "Template Management",
                "End Date Configuration"
            ],
            "analytics_features": [
                "Cash Flow Analysis",
                "Seasonal Spending Patterns",
                "Financial Health Scoring",
                "AI-Powered Recommendations",
                "Anonymous Peer Comparison",
                "Financial Risk Assessment",
                "Personalized Insights Generation"
            ],
            "supported_models": {
                "prediction_engine": "Facebook Prophet",
                "time_series_analysis": "Custom algorithms",
                "pattern_recognition": "Statistical models",
                "risk_assessment": "Multi-factor analysis"
            }
        }
    
    @app.get("/features-summary")
    async def features_summary():
        """Get summary of all available features"""
        summary = {
            "api_version": "5.0.0",
            "total_endpoints": 0,
            "feature_modules": {}
        }
        
        # Core features
        summary["feature_modules"]["core"] = {
            "name": "Core Financial Management",
            "endpoints": 9,
            "features": ["Auth", "Users", "Categories", "Transactions", "Analytics", "Budgets", "Export/Import"]
        }
        summary["total_endpoints"] += 9
        
        # Dashboard features
        if DASHBOARD_FEATURES:
            summary["feature_modules"]["dashboard"] = {
                "name": "Real-time Dashboard & Goals",
                "endpoints": 3,
                "features": ["Dashboard", "Savings Goals", "WebSocket"]
            }
            summary["total_endpoints"] += 3
        
        # AI features
        if AI_FEATURES:
            summary["feature_modules"]["ai"] = {
                "name": "Luna AI Chatbot",
                "endpoints": 3,
                "features": ["Chat", "WebSocket Chat", "AI Admin"]
            }
            summary["total_endpoints"] += 3
        
        # Advanced features
        if ADVANCED_FEATURES:
            summary["feature_modules"]["advanced"] = {
                "name": "Advanced Analytics & Predictions",
                "endpoints": 5,
                "features": ["Predictions", "Notifications", "Recurring Transactions", "Advanced Analytics", "Financial Insights"]
            }
            summary["total_endpoints"] += 5
        
        summary["capabilities"] = {
            "real_time": DASHBOARD_FEATURES,
            "ai_powered": AI_FEATURES,
            "predictive_analytics": ADVANCED_FEATURES,
            "multi_language": AI_FEATURES,
            "automated_insights": ADVANCED_FEATURES
        }
        
        return summary

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception at {request.url}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "path": str(request.url),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )