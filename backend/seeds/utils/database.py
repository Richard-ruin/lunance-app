from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, List, Dict, Any
from ..config import SEED_CONFIG

class SeedDatabase:
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database = None

    async def connect(self):
        """Connect to MongoDB"""
        self.client = AsyncIOMotorClient(SEED_CONFIG["mongodb_url"])
        self.database = self.client[SEED_CONFIG["database_name"]]
        print(f"Connected to MongoDB: {SEED_CONFIG['database_name']}")

    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            print("Disconnected from MongoDB")

    async def clear_collection(self, collection_name: str):
        """Clear all documents from a collection"""
        if SEED_CONFIG["clear_existing"]:
            result = await self.database[collection_name].delete_many({})
            print(f"Cleared {result.deleted_count} documents from {collection_name}")

    async def insert_batch(self, collection_name: str, documents: List[Dict[str, Any]]):
        """Insert documents in batches"""
        collection = self.database[collection_name]
        batch_size = SEED_CONFIG["batch_size"]
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            result = await collection.insert_many(batch)
            print(f"Inserted batch {i//batch_size + 1}: {len(result.inserted_ids)} documents into {collection_name}")

    async def get_collection_count(self, collection_name: str) -> int:
        """Get document count in collection"""
        return await self.database[collection_name].count_documents({})

db = SeedDatabase()