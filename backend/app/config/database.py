"""
Database Configuration
MongoDB connection dengan Beanie ODM dan Motor async driver
"""

import logging
from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure

from .settings import settings

logger = logging.getLogger(__name__)


class Database:
    """Database connection manager"""
    
    client: Optional[AsyncIOMotorClient] = None
    database = None
    
    @classmethod
    async def connect_db(cls) -> None:
        """
        Inisialisasi koneksi database MongoDB
        """
        try:
            # Create MongoDB client
            cls.client = AsyncIOMotorClient(
                settings.mongodb_url,
                serverSelectionTimeoutMS=5000,  # 5 seconds timeout
                maxPoolSize=50,  # Maximum connection pool size
                minPoolSize=10,  # Minimum connection pool size
                maxIdleTimeMS=30000,  # 30 seconds max idle time
                retryWrites=True,
                w="majority"  # Write concern
            )
            
            # Get database
            cls.database = cls.client[settings.database_name]
            
            # Test connection
            await cls.client.server_info()
            
            # Import all models untuk Beanie initialization
            from ..models.user import User
            from ..models.university import University, Faculty, Department
            from ..models.category import Category
            from ..models.transaction import Transaction
            from ..models.savings_target import SavingsTarget
            
            # Initialize Beanie dengan semua document models
            await init_beanie(
                database=cls.database,
                document_models=[
                    User,
                    University,
                    Faculty,
                    Department,
                    Category,
                    Transaction,
                    SavingsTarget
                ]
            )
            
            logger.info(f"✅ Connected to MongoDB database: {settings.database_name}")
            
        except (ServerSelectionTimeoutError, ConnectionFailure) as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            raise Exception(f"Database connection failed: {e}")
        except Exception as e:
            logger.error(f"❌ Unexpected error during database initialization: {e}")
            raise
    
    @classmethod
    async def close_db(cls) -> None:
        """
        Tutup koneksi database
        """
        if cls.client:
            cls.client.close()
            logger.info("🔌 Database connection closed")
    
    @classmethod
    async def ping_db(cls) -> bool:
        """
        Test database connection
        """
        try:
            if cls.client:
                await cls.client.admin.command('ping')
                return True
            return False
        except Exception as e:
            logger.error(f"Database ping failed: {e}")
            return False
    
    @classmethod
    async def get_db_stats(cls) -> dict:
        """
        Get database statistics
        """
        try:
            if cls.database:
                stats = await cls.database.command("dbStats")
                return {
                    "db_name": stats.get("db"),
                    "collections": stats.get("collections"),
                    "objects": stats.get("objects"),
                    "dataSize": stats.get("dataSize"),
                    "storageSize": stats.get("storageSize"),
                    "indexes": stats.get("indexes"),
                    "indexSize": stats.get("indexSize")
                }
            return {}
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {}
    
    @classmethod
    async def create_indexes(cls) -> None:
        """
        Create database indexes untuk performance optimization
        """
        try:
            if not cls.database:
                logger.warning("Database not connected, skipping index creation")
                return
            
            # User indexes
            await cls.database.users.create_index("email", unique=True)
            await cls.database.users.create_index("university_id")
            await cls.database.users.create_index("faculty_id")
            await cls.database.users.create_index("department_id")
            
            # University indexes
            await cls.database.universities.create_index("domain", unique=True)
            await cls.database.universities.create_index("is_approved")
            
            # Faculty indexes
            await cls.database.faculties.create_index("university_id")
            await cls.database.faculties.create_index([("university_id", 1), ("name", 1)], unique=True)
            
            # Department indexes
            await cls.database.departments.create_index("faculty_id")
            await cls.database.departments.create_index([("faculty_id", 1), ("name", 1)], unique=True)
            
            # Category indexes
            await cls.database.categories.create_index("is_global")
            await cls.database.categories.create_index("created_by")
            await cls.database.categories.create_index("type")
            
            # Transaction indexes
            await cls.database.transactions.create_index("user_id")
            await cls.database.transactions.create_index("category_id")
            await cls.database.transactions.create_index("date")
            await cls.database.transactions.create_index("type")
            await cls.database.transactions.create_index([("user_id", 1), ("date", -1)])
            
            # SavingsTarget indexes
            await cls.database.savings_targets.create_index("user_id")
            await cls.database.savings_targets.create_index("target_date")
            await cls.database.savings_targets.create_index("is_achieved")
            
            logger.info("✅ Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to create indexes: {e}")
            # Don't raise exception here, indexes are not critical for basic functionality


# Database instance
database = Database()


# Dependency untuk mendapatkan database session
async def get_database():
    """
    FastAPI dependency untuk mendapatkan database instance
    """
    return database.database


# Database event handlers untuk FastAPI
async def connect_to_mongo():
    """Connect to MongoDB on startup"""
    await database.connect_db()
    await database.create_indexes()


async def close_mongo_connection():
    """Close MongoDB connection on shutdown"""
    await database.close_db()


# Health check function
async def check_database_health() -> dict:
    """
    Check database health status
    """
    try:
        is_connected = await database.ping_db()
        if is_connected:
            stats = await database.get_db_stats()
            return {
                "status": "healthy",
                "connected": True,
                "database": settings.database_name,
                "stats": stats
            }
        else:
            return {
                "status": "unhealthy",
                "connected": False,
                "error": "Cannot ping database"
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "connected": False,
            "error": str(e)
        }