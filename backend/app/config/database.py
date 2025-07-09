from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ServerSelectionTimeoutError
import asyncio
import logging
from .settings import settings

logger = logging.getLogger(__name__)


class Database:
    """Database connection manager using Motor (async MongoDB driver)."""
    
    client: AsyncIOMotorClient = None
    database: AsyncIOMotorDatabase = None


# Database instance
db = Database()


async def connect_to_mongo():
    """Create database connection."""
    try:
        logger.info("Connecting to MongoDB...")
        
        # Create MongoDB client
        db.client = AsyncIOMotorClient(
            settings.mongodb_url,
            serverSelectionTimeoutMS=5000,  # 5 second timeout
            connectTimeoutMS=10000,  # 10 second timeout
            socketTimeoutMS=10000,   # 10 second timeout
        )
        
        # Select database
        db.database = db.client[settings.mongodb_db_name]
        
        # Test connection
        await db.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB!")
        
        # Create indexes
        await create_indexes()
        
    except ServerSelectionTimeoutError as e:
        logger.error(f"Could not connect to MongoDB: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error connecting to MongoDB: {e}")
        raise


async def close_mongo_connection():
    """Close database connection."""
    if db.client:
        logger.info("Closing MongoDB connection...")
        db.client.close()
        logger.info("MongoDB connection closed.")


async def create_indexes():
    """Create database indexes for better performance."""
    try:
        logger.info("Creating database indexes...")
        
        # User collection indexes
        await db.database.users.create_index("email", unique=True)
        await db.database.users.create_index("created_at")
        
        # Transaction collection indexes
        await db.database.transactions.create_index("user_id")
        await db.database.transactions.create_index("created_at")
        await db.database.transactions.create_index("category")
        await db.database.transactions.create_index([("user_id", 1), ("created_at", -1)])
        
        # Budget collection indexes
        await db.database.budgets.create_index("user_id")
        await db.database.budgets.create_index("category")
        await db.database.budgets.create_index([("user_id", 1), ("category", 1)], unique=True)
        
        # Goal collection indexes
        await db.database.goals.create_index("user_id")
        await db.database.goals.create_index("created_at")
        await db.database.goals.create_index("target_date")
        
        # Notification collection indexes
        await db.database.notifications.create_index("user_id")
        await db.database.notifications.create_index("created_at")
        await db.database.notifications.create_index("is_read")
        
        logger.info("Database indexes created successfully!")
        
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")
        # Don't raise here, indexes are not critical for startup


async def get_database() -> AsyncIOMotorDatabase:
    """Get database instance."""
    return db.database


async def ping_database():
    """Ping database to check connection."""
    try:
        await db.client.admin.command('ping')
        return True
    except Exception as e:
        logger.error(f"Database ping failed: {e}")
        return False


# Database dependency for FastAPI
async def get_db():
    """FastAPI dependency to get database instance."""
    return await get_database()


# Health check function
async def check_database_health():
    """Check database health status."""
    try:
        # Check connection
        await db.client.admin.command('ping')
        
        # Check database stats
        stats = await db.database.command("dbStats")
        
        return {
            "status": "healthy",
            "database": settings.mongodb_db_name,
            "collections": stats.get("collections", 0),
            "objects": stats.get("objects", 0),
            "dataSize": stats.get("dataSize", 0)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


# Collection getter functions
def get_users_collection():
    """Get users collection."""
    return db.database.users


def get_transactions_collection():
    """Get transactions collection."""
    return db.database.transactions


def get_budgets_collection():
    """Get budgets collection."""
    return db.database.budgets


def get_goals_collection():
    """Get goals collection."""
    return db.database.goals


def get_notifications_collection():
    """Get notifications collection."""
    return db.database.notifications


def get_categories_collection():
    """Get categories collection."""
    return db.database.categories