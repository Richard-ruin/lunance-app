# app/database.py (updated)
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING
from typing import Optional
from .config import settings

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database = None

database = Database()

async def get_database():
    return database.database

async def connect_to_mongo():
    """Create database connection"""
    database.client = AsyncIOMotorClient(settings.mongodb_url)
    database.database = database.client.lunance
    
    # Create indexes for optimization
    await create_indexes()
    
    print("Connected to MongoDB")

async def close_mongo_connection():
    """Close database connection"""
    if database.client:
        database.client.close()
        print("Disconnected from MongoDB")

async def create_indexes():
    """Create database indexes for optimization"""
    try:
        # User collection indexes
        await database.database.users.create_index("email", unique=True)
        await database.database.users.create_index("universitas_id")
        await database.database.users.create_index("role")
        await database.database.users.create_index("is_active")
        await database.database.users.create_index("is_verified")
        await database.database.users.create_index("created_at")
        await database.database.users.create_index([("nama_lengkap", "text"), ("email", "text")])
        
        # University collection indexes
        await database.database.universities.create_index("nama_universitas")
        await database.database.universities.create_index("status")
        await database.database.universities.create_index("created_at")
        await database.database.universities.create_index([("nama_universitas", "text")])
        
        # University requests collection indexes
        await database.database.university_requests.create_index("status")
        await database.database.university_requests.create_index("user_id")
        await database.database.university_requests.create_index("created_at")
        await database.database.university_requests.create_index([("user_id", ASCENDING), ("status", ASCENDING)])
        
        print("Database indexes created successfully")
        
    except Exception as e:
        print(f"Error creating indexes: {str(e)}")