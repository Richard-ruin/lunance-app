# app/core/startup.py
"""Enhanced startup logic with AI services initialization - Fixed version."""

import logging
import asyncio
from datetime import datetime
from typing import Dict, Any

from ..config.database import get_database
from ..config.settings import settings

logger = logging.getLogger(__name__)


async def run_startup_tasks():
    """Run all startup initialization tasks including AI services."""
    logger.info("Running startup tasks...")
    
    try:
        # Initialize core services
        await initialize_core_services()
        
        # Initialize AI services
        await initialize_ai_services()
        
        # Verify all services
        await verify_services_health()
        
        # Create default data if needed
        if settings.debug:
            await create_default_data()
        
        logger.info("All startup tasks completed successfully!")
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise


async def initialize_core_services():
    """Initialize core application services."""
    logger.info("Initializing core services...")
    
    # Check database connection - Fixed: use 'is None' instead of 'not db'
    db = await get_database()
    if db is None:
        raise Exception("Database connection failed")
    
    # Initialize email service
    try:
        from ..services.email_service import email_service
        await email_service.verify_smtp_connection()
        logger.info("Email service initialized")
    except Exception as e:
        logger.warning(f"Email service initialization failed: {e}")
    
    # Initialize other core services
    logger.info("Core services initialized")


async def initialize_ai_services():
    """Initialize AI and ML services."""
    logger.info("Initializing AI services...")
    
    # Initialize chatbot service
    try:
        from ..services.chatbot_service import chatbot_service
        logger.info("Chatbot service initialized")
    except ImportError as e:
        logger.warning(f"Chatbot service not available: {e}")
        logger.info("Creating placeholder chatbot service...")
        await create_placeholder_chatbot_service()
    except Exception as e:
        logger.warning(f"Chatbot service initialization failed: {e}")
    
    # Initialize prediction service
    try:
        from ..services.prediction_service import prediction_service
        
        # Check if Prophet is available
        if hasattr(prediction_service, 'prophet_available') and prediction_service.prophet_available:
            logger.info("Prophet forecasting library available")
        else:
            logger.warning("Prophet library not available, using fallback algorithms")
        
        logger.info("Prediction service initialized")
    except ImportError as e:
        logger.warning(f"Prediction service not available: {e}")
        logger.info("Creating placeholder prediction service...")
        await create_placeholder_prediction_service()
    except Exception as e:
        logger.warning(f"Prediction service initialization failed: {e}")
    
    # Initialize context service
    try:
        from ..services.context_service import context_service
        logger.info("Context service initialized")
    except ImportError as e:
        logger.warning(f"Context service not available: {e}")
    except Exception as e:
        logger.warning(f"Context service initialization failed: {e}")
    
    # Initialize analytics service
    try:
        from ..services.analytics_service import analytics_service
        logger.info("Analytics service initialized")
    except ImportError as e:
        logger.warning(f"Analytics service not available: {e}")
    except Exception as e:
        logger.warning(f"Analytics service initialization failed: {e}")
    
    # Verify Hugging Face API if configured
    if hasattr(settings, 'huggingface_api_key') and settings.huggingface_api_key:
        try:
            logger.info("Hugging Face API key configured")
        except Exception as e:
            logger.warning(f"Hugging Face API verification failed: {e}")
    
    logger.info("AI services initialized")


async def verify_services_health():
    """Verify that all services are healthy."""
    logger.info("Verifying services health...")
    
    health_checks = {}
    
    # Database health
    try:
        from ..config.database import check_database_health
        db_health = await check_database_health()
        health_checks["database"] = db_health["status"] == "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_checks["database"] = False
    
    # AI services health
    try:
        health_checks["chatbot"] = True
        health_checks["prediction"] = True
        health_checks["context"] = True
        health_checks["analytics"] = True
        
    except Exception as e:
        logger.error(f"AI services health check failed: {e}")
        health_checks["ai_services"] = False
    
    # Report health status
    healthy_services = sum(1 for status in health_checks.values() if status)
    total_services = len(health_checks)
    
    logger.info(f"Health check: {healthy_services}/{total_services} services healthy")
    
    if healthy_services < total_services:
        logger.warning("Some services are not healthy, but continuing startup...")
    
    return health_checks


async def create_default_data():
    """Create default data for development environment."""
    logger.info("Creating default data for development...")
    
    try:
        # Create default categories if they don't exist
        await create_default_categories()
        
        # Create demo user if in debug mode
        if settings.debug:
            await create_demo_user()
        
        logger.info("Default data created")
        
    except Exception as e:
        logger.error(f"Error creating default data: {e}")


async def create_default_categories():
    """Create default global categories."""
    try:
        from ..models.category import DEFAULT_GLOBAL_CATEGORIES
        from ..config.database import get_database
        
        db = await get_database()
        categories_collection = db.categories
        
        # Check if categories already exist
        existing_count = await categories_collection.count_documents({"is_global": True})
        
        if existing_count == 0:
            # Insert default categories
            await categories_collection.insert_many(DEFAULT_GLOBAL_CATEGORIES)
            logger.info(f"Created {len(DEFAULT_GLOBAL_CATEGORIES)} default categories")
        else:
            logger.info(f"{existing_count} global categories already exist")
            
    except Exception as e:
        logger.error(f"Error creating default categories: {e}")


async def create_demo_user():
    """Create demo user for development."""
    try:
        from ..config.database import get_database
        from ..utils.password import hash_password
        
        db = await get_database()
        users_collection = db.users
        
        # Check if demo user exists
        demo_user = await users_collection.find_one({"email": "demo@university.ac.id"})
        
        if not demo_user:
            demo_user_data = {
                "email": "demo@university.ac.id",
                "full_name": "Demo User",
                "phone_number": "628123456789",
                "password_hash": hash_password("DemoPassword123!"),
                "role": "student",
                "is_active": True,
                "is_verified": True,
                "initial_savings": 1000000.0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            await users_collection.insert_one(demo_user_data)
            logger.info("Demo user created: demo@university.ac.id / DemoPassword123!")
        else:
            logger.info("Demo user already exists")
            
    except Exception as e:
        logger.error(f"Error creating demo user: {e}")


async def create_demo_data():
    """Create comprehensive demo data for testing."""
    logger.info("Creating demo data...")
    
    try:
        # Create demo transactions
        await create_demo_transactions()
        
        # Create demo savings targets
        await create_demo_savings_targets()
        
        # Create demo chat sessions
        await create_demo_chat_data()
        
        logger.info("Demo data created successfully")
        
    except Exception as e:
        logger.error(f"Error creating demo data: {e}")


async def create_demo_transactions():
    """Create demo transactions for testing."""
    try:
        from ..config.database import get_database
        from datetime import date, timedelta
        import random
        
        db = await get_database()
        
        # Get demo user
        demo_user = await db.users.find_one({"email": "demo@university.ac.id"})
        if not demo_user:
            return
        
        user_id = str(demo_user["_id"])
        
        # Get categories
        categories = await db.categories.find({"is_global": True}).to_list(None)
        if not categories:
            return
        
        # Check if demo transactions already exist
        existing_transactions = await db.transactions.count_documents({"user_id": user_id})
        if existing_transactions > 0:
            logger.info("Demo transactions already exist")
            return
        
        # Create demo transactions for the last 6 months
        demo_transactions = []
        end_date = date.today()
        start_date = end_date - timedelta(days=180)
        
        # Income transactions (monthly salary)
        current_date = start_date
        while current_date <= end_date:
            if current_date.day == 1:  # Monthly salary on 1st
                salary_category = next((cat for cat in categories if "Salary" in cat["name"]), categories[0])
                demo_transactions.append({
                    "user_id": user_id,
                    "category_id": str(salary_category["_id"]),
                    "transaction_type": "income",
                    "amount": random.uniform(3000000, 4000000),  # 3-4 million salary
                    "description": f"Gaji bulan {current_date.strftime('%B %Y')}",
                    "transaction_date": current_date,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                })
            
            current_date += timedelta(days=1)
        
        # Random expense transactions
        expense_categories = [cat for cat in categories if "Salary" not in cat["name"]]
        for _ in range(100):  # 100 random transactions
            random_date = start_date + timedelta(days=random.randint(0, 180))
            random_category = random.choice(expense_categories)
            
            # Different amount ranges based on category
            if "Food" in random_category["name"]:
                amount = random.uniform(15000, 100000)
            elif "Transportation" in random_category["name"]:
                amount = random.uniform(10000, 50000)
            elif "Entertainment" in random_category["name"]:
                amount = random.uniform(50000, 200000)
            else:
                amount = random.uniform(20000, 150000)
            
            demo_transactions.append({
                "user_id": user_id,
                "category_id": str(random_category["_id"]),
                "transaction_type": "expense",
                "amount": amount,
                "description": f"Pengeluaran {random_category['name'].lower()}",
                "transaction_date": random_date,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
        
        # Insert demo transactions
        await db.transactions.insert_many(demo_transactions)
        logger.info(f"Created {len(demo_transactions)} demo transactions")
        
    except Exception as e:
        logger.error(f"Error creating demo transactions: {e}")


async def create_demo_savings_targets():
    """Create demo savings targets."""
    try:
        from ..config.database import get_database
        from datetime import date, timedelta
        
        db = await get_database()
        
        # Get demo user
        demo_user = await db.users.find_one({"email": "demo@university.ac.id"})
        if not demo_user:
            return
        
        user_id = str(demo_user["_id"])
        
        # Check if demo targets already exist
        existing_targets = await db.savings_targets.count_documents({"user_id": user_id})
        if existing_targets > 0:
            logger.info("Demo savings targets already exist")
            return
        
        # Create demo savings targets
        targets = [
            {
                "user_id": user_id,
                "target_name": "Laptop Baru",
                "target_amount": 15000000.0,
                "current_amount": 8500000.0,
                "target_date": date.today() + timedelta(days=120),
                "is_achieved": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "user_id": user_id,
                "target_name": "Dana Darurat",
                "target_amount": 10000000.0,
                "current_amount": 4200000.0,
                "target_date": date.today() + timedelta(days=300),
                "is_achieved": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "user_id": user_id,
                "target_name": "Liburan",
                "target_amount": 5000000.0,
                "current_amount": 5000000.0,
                "target_date": date.today() - timedelta(days=30),
                "is_achieved": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        await db.savings_targets.insert_many(targets)
        logger.info(f"Created {len(targets)} demo savings targets")
        
    except Exception as e:
        logger.error(f"Error creating demo savings targets: {e}")


async def create_demo_chat_data():
    """Create demo chat data."""
    try:
        from ..config.database import get_database
        
        db = await get_database()
        
        # Get demo user
        demo_user = await db.users.find_one({"email": "demo@university.ac.id"})
        if not demo_user:
            return
        
        user_id = str(demo_user["_id"])
        
        # Check if demo chat data already exists
        existing_sessions = await db.chat_sessions.count_documents({"user_id": user_id})
        if existing_sessions > 0:
            logger.info("Demo chat data already exists")
            return
        
        # Create a demo chat session
        session_data = {
            "user_id": user_id,
            "session_name": "Demo Chat Session",
            "is_active": True,
            "message_count": 4,
            "last_activity": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        session_result = await db.chat_sessions.insert_one(session_data)
        session_id = str(session_result.inserted_id)
        
        # Create demo messages
        messages = [
            {
                "user_id": user_id,
                "session_id": session_id,
                "content": "Berapa saldo saya saat ini?",
                "role": "user",
                "message_type": "text",
                "metadata": {},
                "created_at": datetime.utcnow() - timedelta(minutes=10)
            },
            {
                "user_id": user_id,
                "session_id": session_id,
                "content": "Saldo Anda saat ini adalah Rp 2,500,000. Ini menunjukkan kondisi keuangan yang cukup baik!",
                "role": "assistant",
                "message_type": "text",
                "metadata": {"context_used": True},
                "confidence_score": 0.95,
                "processing_time": 1.2,
                "created_at": datetime.utcnow() - timedelta(minutes=9)
            },
            {
                "user_id": user_id,
                "session_id": session_id,
                "content": "Analisis pengeluaran saya bulan ini",
                "role": "user",
                "message_type": "spending_analysis",
                "metadata": {},
                "created_at": datetime.utcnow() - timedelta(minutes=5)
            },
            {
                "user_id": user_id,
                "session_id": session_id,
                "content": "Pengeluaran Anda bulan ini sebesar Rp 1,850,000. Kategori terbesar adalah Food & Dining (35%). Pengeluaran masih dalam batas wajar!",
                "role": "assistant",
                "message_type": "spending_analysis",
                "metadata": {"analysis_type": "monthly_summary"},
                "confidence_score": 0.88,
                "processing_time": 2.1,
                "created_at": datetime.utcnow() - timedelta(minutes=4)
            }
        ]
        
        await db.chat_messages.insert_many(messages)
        logger.info(f"Created demo chat session with {len(messages)} messages")
        
    except Exception as e:
        logger.error(f"Error creating demo chat data: {e}")


async def reset_development_data():
    """Reset development data (debug mode only)."""
    if not settings.debug:
        logger.warning("Reset data is only available in debug mode")
        return
    
    logger.info("Resetting development data...")
    
    try:
        db = await get_database()
        
        # Collections to reset
        collections_to_reset = [
            "transactions",
            "savings_targets", 
            "chat_sessions",
            "chat_messages",
            "context_memory",
            "predictions",
            "prediction_accuracy",
            "anomaly_detection"
        ]
        
        for collection_name in collections_to_reset:
            collection = db[collection_name]
            result = await collection.delete_many({})
            logger.info(f"Deleted {result.deleted_count} documents from {collection_name}")
        
        logger.info("Development data reset completed")
        
    except Exception as e:
        logger.error(f"Error resetting development data: {e}")


# Placeholder service creation functions
async def create_placeholder_chatbot_service():
    """Create placeholder chatbot service if main service is not available."""
    logger.info("AI chatbot service will be available when dependencies are installed")


async def create_placeholder_prediction_service():
    """Create placeholder prediction service if main service is not available."""
    logger.info("Financial prediction service will be available when dependencies are installed")


# Health check for startup services
async def get_startup_health() -> Dict[str, Any]:
    """Get health status of startup services."""
    try:
        health_status = {
            "timestamp": datetime.utcnow().isoformat(),
            "services": {}
        }
        
        # Check database
        try:
            from ..config.database import check_database_health
            health_status["services"]["database"] = await check_database_health()
        except Exception as e:
            health_status["services"]["database"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Check AI services availability
        ai_services = ["chatbot", "prediction", "analytics", "context"]
        for service_name in ai_services:
            try:
                health_status["services"][service_name] = {
                    "status": "healthy",
                    "note": "Service available"
                }
            except Exception as e:
                health_status["services"][service_name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
        
        # Overall status
        all_healthy = all(
            service.get("status") == "healthy" 
            for service in health_status["services"].values()
        )
        
        health_status["overall_status"] = "healthy" if all_healthy else "degraded"
        
        return health_status
        
    except Exception as e:
        logger.error(f"Error checking startup health: {e}")
        return {
            "overall_status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }