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
    
    print("🔧 Membuat database indexes...")
    
    # Index untuk users collection
    try:
        db.users.create_index("email", unique=True)
        db.users.create_index("username", unique=True)
        db.users.create_index("created_at")
        print("✅ Users indexes berhasil dibuat")
    except Exception as e:
        print(f"⚠️ Warning creating users indexes: {e}")
    
    # Index untuk conversations collection
    try:
        db.conversations.create_index([("user_id", 1), ("created_at", -1)])
        db.conversations.create_index([("user_id", 1), ("status", 1)])
        db.conversations.create_index([("user_id", 1), ("updated_at", -1)])
        print("✅ Conversations indexes berhasil dibuat")
    except Exception as e:
        print(f"⚠️ Warning creating conversations indexes: {e}")
    
    # Index untuk messages collection
    try:
        db.messages.create_index([("conversation_id", 1), ("timestamp", 1)])
        db.messages.create_index([("sender_id", 1), ("timestamp", -1)])
        db.messages.create_index([("message_type", 1)])
        db.messages.create_index([("conversation_id", 1), ("sender_type", 1)])
        print("✅ Messages indexes berhasil dibuat")
    except Exception as e:
        print(f"⚠️ Warning creating messages indexes: {e}")
    
    # Index untuk transactions collection (Financial Management)
    try:
        db.transactions.create_index([("user_id", 1), ("date", -1)])
        db.transactions.create_index([("user_id", 1), ("type", 1), ("date", -1)])
        db.transactions.create_index([("user_id", 1), ("category", 1)])
        db.transactions.create_index([("user_id", 1), ("status", 1)])
        db.transactions.create_index([("user_id", 1), ("source", 1)])
        db.transactions.create_index([("conversation_id", 1)])
        db.transactions.create_index([("created_at", -1)])
        # Compound index untuk filtering
        db.transactions.create_index([("user_id", 1), ("type", 1), ("status", 1), ("date", -1)])
        print("✅ Transactions indexes berhasil dibuat")
    except Exception as e:
        print(f"⚠️ Warning creating transactions indexes: {e}")
    
    # Index untuk savings_goals collection
    try:
        db.savings_goals.create_index([("user_id", 1), ("status", 1)])
        db.savings_goals.create_index([("user_id", 1), ("created_at", -1)])
        db.savings_goals.create_index([("user_id", 1), ("target_date", 1)])
        db.savings_goals.create_index([("status", 1), ("target_date", 1)])
        print("✅ Savings Goals indexes berhasil dibuat")
    except Exception as e:
        print(f"⚠️ Warning creating savings_goals indexes: {e}")
    
    print("✅ Semua database indexes berhasil dibuat")

def create_initial_data():
    """Membuat data awal jika diperlukan"""
    db = get_database()
    pass