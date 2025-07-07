from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from app.config.settings import Config
import logging

logger = logging.getLogger(__name__)

class Database:
    client = None
    db = None

def init_db():
    """Initialize database connection"""
    try:
        Database.client = MongoClient(
            Config.MONGODB_URL,
            maxPoolSize=50,
            minPoolSize=10,
            serverSelectionTimeoutMS=5000,
            socketTimeoutMS=20000,
            connectTimeoutMS=20000,
            maxIdleTimeMS=30000
        )
        
        # Test connection
        Database.client.admin.command('ping')
        Database.db = Database.client[Config.DATABASE_NAME]
        
        logger.info("Koneksi MongoDB berhasil")
        
        # Create indexes
        create_indexes()
        
    except ConnectionFailure as e:
        logger.error(f"Gagal terhubung ke MongoDB: {e}")
        raise

def get_db():
    """Get database instance"""
    if Database.db is None:
        init_db()
    return Database.db

def create_indexes():
    """Create database indexes for better performance"""
    try:
        db = get_db()
        
        # University indexes
        db.universities.create_index("kode", unique=True)
        db.universities.create_index("nama")
        db.universities.create_index("status_aktif")
        db.universities.create_index("created_at")
        
        # Fakultas indexes
        db.fakultas.create_index("kode")
        db.fakultas.create_index("university_id")
        db.fakultas.create_index([("university_id", 1), ("kode", 1)], unique=True)
        db.fakultas.create_index("nama")
        
        # Program Studi indexes
        db.program_studi.create_index("kode")
        db.program_studi.create_index("fakultas_id")
        db.program_studi.create_index([("fakultas_id", 1), ("kode", 1)], unique=True)
        db.program_studi.create_index("nama")
        db.program_studi.create_index("jenjang")
        
        # Users indexes
        db.users.create_index("email", unique=True)
        db.users.create_index("status")
        db.users.create_index("role")
        db.users.create_index("university_id")
        db.users.create_index("fakultas_id")
        db.users.create_index("prodi_id")
        db.users.create_index("created_at")
        db.users.create_index("last_login")
        db.users.create_index("otp_code", sparse=True)
        db.users.create_index("otp_expires", sparse=True)
        
        # University requests indexes
        db.university_requests.create_index("email")
        db.university_requests.create_index("status")
        db.university_requests.create_index("created_at")
        db.university_requests.create_index("processed_at", sparse=True)
        
        # Admin activities indexes
        db.admin_activities.create_index("admin_id")
        db.admin_activities.create_index("action")
        db.admin_activities.create_index("created_at")
        db.admin_activities.create_index("target_id", sparse=True)
        
        # System settings indexes
        db.system_settings.create_index("key", unique=True)
        
        # System logs indexes
        db.system_logs.create_index("level")
        db.system_logs.create_index("created_at")
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")

async def close_db():
    """Close database connection"""
    if Database.client:
        Database.client.close()
        logger.info("Database connection closed")

def get_collection(collection_name: str):
    """Get specific collection"""
    db = get_db()
    return db[collection_name]

def check_db_health():
    """Check database health"""
    try:
        db = get_db()
        result = db.command("ping")
        return {"status": "healthy", "result": result}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}