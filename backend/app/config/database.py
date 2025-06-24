import asyncio
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure
import logging
from .settings import settings

logger = logging.getLogger(__name__)

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None

# Create global database instance
database = Database()

async def connect_to_mongo():
    """Create database connection"""
    try:
        logger.info("Connecting to MongoDB...")
        database.client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            maxPoolSize=10,
            minPoolSize=10,
            serverSelectionTimeoutMS=5000,
        )
        
        # Test the connection
        await database.client.admin.command('ping')
        database.database = database.client[settings.DATABASE_NAME]
        
        logger.info(f"Successfully connected to MongoDB database: {settings.DATABASE_NAME}")
        
        # Create indexes
        await create_indexes()
        
    except ConnectionFailure as e:
        logger.error(f"Could not connect to MongoDB: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error connecting to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Close database connection"""
    if database.client:
        logger.info("Closing MongoDB connection...")
        database.client.close()
        logger.info("MongoDB connection closed")

async def create_indexes():
    """Create database indexes for optimal performance"""
    try:
        # Students collection indexes
        students_collection = database.database.students
        
        # Unique email index
        await students_collection.create_index("email", unique=True)
        
        # Student ID index (for university info)
        await students_collection.create_index("profile.student_id")
        
        # University index for filtering
        await students_collection.create_index("profile.university")
        
        # OTP verification indexes
        await students_collection.create_index("otp_records.code")
        await students_collection.create_index("otp_records.expires_at")
        await students_collection.create_index("otp_records.type")
        
        # Password reset token index
        await students_collection.create_index("password_reset_token")
        
        # Account status indexes
        await students_collection.create_index("is_active")
        await students_collection.create_index("verification.email_verified")
        await students_collection.create_index("account_locked_until")
        
        # Timestamps
        await students_collection.create_index("created_at")
        await students_collection.create_index("last_login")
        
        # Transactions collection indexes (for future use)
        transactions_collection = database.database.transactions
        await transactions_collection.create_index("user_id")
        await transactions_collection.create_index("created_at")
        await transactions_collection.create_index("type")
        await transactions_collection.create_index("category")
        
        # Expense splits collection indexes (for future use)
        expense_splits_collection = database.database.expense_splits
        await expense_splits_collection.create_index("creator_id")
        await expense_splits_collection.create_index("participants.user_id")
        await expense_splits_collection.create_index("status")
        
        # Savings challenges collection indexes (for future use)
        savings_challenges_collection = database.database.savings_challenges
        await savings_challenges_collection.create_index("user_id")
        await savings_challenges_collection.create_index("challenge_type")
        await savings_challenges_collection.create_index("is_active")
        
        # Chat sessions collection indexes (for future use)
        chat_sessions_collection = database.database.chat_sessions
        await chat_sessions_collection.create_index("user_id")
        await chat_sessions_collection.create_index("created_at")
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")
        # Don't raise here as the app can still function without indexes

def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    if database.database is None:
        raise RuntimeError("Database not initialized. Call connect_to_mongo() first.")
    return database.database

async def get_collection(collection_name: str):
    """Get collection by name"""
    db = get_database()
    return db[collection_name]

# Health check function
async def check_database_health() -> bool:
    """Check if database is healthy"""
    try:
        if database.client is None:
            return False
        
        # Ping the database
        await database.client.admin.command('ping')
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False

# Collection helpers
async def get_students_collection():
    """Get students collection"""
    return await get_collection("students")

async def get_transactions_collection():
    """Get transactions collection"""
    return await get_collection("transactions")

async def get_expense_splits_collection():
    """Get expense splits collection"""
    return await get_collection("expense_splits")

async def get_savings_challenges_collection():
    """Get savings challenges collection"""
    return await get_collection("savings_challenges")

async def get_scholarships_collection():
    """Get scholarships collection"""
    return await get_collection("scholarships")

async def get_chat_sessions_collection():
    """Get chat sessions collection"""
    return await get_collection("chat_sessions")

# Utility functions for testing
async def drop_database():
    """Drop entire database - USE ONLY FOR TESTING"""
    if database.client and settings.DEBUG:
        await database.client.drop_database(settings.DATABASE_NAME)
        logger.warning(f"Database {settings.DATABASE_NAME} dropped!")
    else:
        logger.error("Cannot drop database in production mode")

async def reset_collections():
    """Reset all collections - USE ONLY FOR TESTING"""
    if database.database and settings.DEBUG:
        collections = await database.database.list_collection_names()
        for collection_name in collections:
            await database.database[collection_name].delete_many({})
        logger.warning("All collections reset!")
    else:
        logger.error("Cannot reset collections in production mode")