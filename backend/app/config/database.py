from pymongo import MongoClient
from pymongo.database import Database
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    _instance = None
    _client = None
    _database = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance
    
    def connect(self):
        """Membuat koneksi ke MongoDB"""
        if self._client is None:
            mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
            self._client = MongoClient(mongodb_url)
            
            database_name = os.getenv("DATABASE_NAME", "lunance_db")
            self._database = self._client[database_name]
            
            # Test koneksi
            try:
                self._client.admin.command('ping')
                print(f"✅ Berhasil terhubung ke MongoDB: {database_name}")
            except Exception as e:
                print(f"❌ Gagal terhubung ke MongoDB: {e}")
                raise
    
    def get_database(self) -> Database:
        """Mendapatkan instance database"""
        if self._database is None:
            self.connect()
        return self._database
    
    def close(self):
        """Menutup koneksi database"""
        if self._client:
            self._client.close()
            self._client = None
            self._database = None
            print("🔐 Koneksi MongoDB ditutup")

# Instance global untuk database
db_manager = DatabaseManager()

def get_database():
    """Helper function untuk mendapatkan database instance"""
    return db_manager.get_database()

def create_indexes():
    """Membuat indexes untuk performa yang lebih baik"""
    db = get_database()
    
    # Index untuk users collection
    db.users.create_index("email", unique=True)
    db.users.create_index("username", unique=True)
    db.users.create_index("created_at")
    
    # Index untuk conversations collection
    db.conversations.create_index([("user_id", 1), ("created_at", -1)])
    
    # Index untuk messages collection
    db.messages.create_index([("conversation_id", 1), ("timestamp", 1)])
    
    # Index untuk transactions collection
    db.transactions.create_index([("user_id", 1), ("date", -1)])
    db.transactions.create_index([("user_id", 1), ("category", 1)])
    
    # Index untuk savings_goals collection
    db.savings_goals.create_index([("user_id", 1), ("status", 1)])
    
    print("✅ Database indexes berhasil dibuat")