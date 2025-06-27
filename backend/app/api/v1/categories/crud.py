# app/api/v1/categories/crud.py
from typing import List, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING

from app.models.category import Category, CategoryCreate, CategoryUpdate, CategoryWithStats
from app.models.base import PyObjectId


class CategoryCRUD:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database
        self.collection = database.categories

    async def create_category(self, category_data: CategoryCreate, user_id: str) -> Category:
        """Create a new category"""
        category_dict = category_data.model_dump()
        category_dict["user_id"] = ObjectId(user_id)
        
        result = await self.collection.insert_one(category_dict)
        category_dict["_id"] = result.inserted_id
        
        return Category(**category_dict)

    async def get_categories_by_user(self, user_id: str, category_type: Optional[str] = None) -> List[Category]:
        """Get all categories for a user, optionally filtered by type"""
        query = {
            "$or": [
                {"user_id": ObjectId(user_id)},  # User's custom categories
                {"is_system": True}  # System default categories
            ]
        }
        
        if category_type:
            query["type"] = category_type
            
        cursor = self.collection.find(query).sort("name", ASCENDING)
        categories = []
        
        async for category_doc in cursor:
            categories.append(Category(**category_doc))
            
        return categories

    async def get_category_by_id(self, category_id: str, user_id: str) -> Optional[Category]:
        """Get a specific category by ID"""
        query = {
            "_id": ObjectId(category_id),
            "$or": [
                {"user_id": ObjectId(user_id)},
                {"is_system": True}
            ]
        }
        
        category_doc = await self.collection.find_one(query)
        
        if category_doc:
            return Category(**category_doc)
        return None

    async def update_category(self, category_id: str, user_id: str, update_data: CategoryUpdate) -> Optional[Category]:
        """Update a category (only user's own categories, not system ones)"""
        query = {
            "_id": ObjectId(category_id),
            "user_id": ObjectId(user_id),
            "is_system": False  # Prevent updating system categories
        }
        
        update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
        
        if not update_dict:
            return await self.get_category_by_id(category_id, user_id)
            
        result = await self.collection.update_one(
            query,
            {"$set": update_dict}
        )
        
        if result.modified_count:
            return await self.get_category_by_id(category_id, user_id)
        return None

    async def delete_category(self, category_id: str, user_id: str) -> bool:
        """Delete a category (only user's own categories, not system ones)"""
        # First check if category is being used in transactions
        transactions_count = await self.database.transactions.count_documents({
            "category_id": ObjectId(category_id),
            "user_id": ObjectId(user_id)
        })
        
        if transactions_count > 0:
            return False  # Cannot delete category that's being used
            
        query = {
            "_id": ObjectId(category_id),
            "user_id": ObjectId(user_id),
            "is_system": False  # Prevent deleting system categories
        }
        
        result = await self.collection.delete_one(query)
        return result.deleted_count > 0

    async def get_categories_with_stats(self, user_id: str, category_type: Optional[str] = None) -> List[CategoryWithStats]:
        """Get categories with transaction statistics"""
        match_stage = {
            "$or": [
                {"user_id": ObjectId(user_id)},
                {"is_system": True}
            ]
        }
        
        if category_type:
            match_stage["type"] = category_type
            
        pipeline = [
            {"$match": match_stage},
            {
                "$lookup": {
                    "from": "transactions",
                    "let": {"cat_id": "$_id", "user_id_obj": ObjectId(user_id)},
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$and": [
                                        {"$eq": ["$category_id", "$$cat_id"]},
                                        {"$eq": ["$user_id", "$$user_id_obj"]}
                                    ]
                                }
                            }
                        }
                    ],
                    "as": "transactions"
                }
            },
            {
                "$addFields": {
                    "transaction_count": {"$size": "$transactions"},
                    "total_amount": {
                        "$cond": {
                            "if": {"$gt": [{"$size": "$transactions"}, 0]},
                            "then": {"$sum": "$transactions.amount"},
                            "else": 0.0
                        }
                    },
                    "avg_amount": {
                        "$cond": {
                            "if": {"$gt": [{"$size": "$transactions"}, 0]},
                            "then": {"$avg": "$transactions.amount"},
                            "else": 0.0
                        }
                    },
                    "last_used": {"$max": "$transactions.created_at"}
                }
            },
            {"$sort": {"name": 1}}
        ]
        
        cursor = self.collection.aggregate(pipeline)
        categories = []
        
        async for category_doc in cursor:
            # Clean up the transactions field as we don't need it in response
            category_doc.pop("transactions", None)
            
            # Ensure numeric fields are not None
            category_doc["transaction_count"] = category_doc.get("transaction_count", 0)
            category_doc["total_amount"] = category_doc.get("total_amount") or 0.0
            category_doc["avg_amount"] = category_doc.get("avg_amount") or 0.0
            category_doc["last_used"] = category_doc.get("last_used")
            
            categories.append(CategoryWithStats(**category_doc))
            
        return categories

    async def search_categories(self, user_id: str, search_term: str, category_type: Optional[str] = None) -> List[Category]:
        """Search categories by name or keywords"""
        query = {
            "$or": [
                {"user_id": ObjectId(user_id)},
                {"is_system": True}
            ],
            "$and": [
                {
                    "$or": [
                        {"name": {"$regex": search_term, "$options": "i"}},
                        {"keywords": {"$in": [search_term.lower()]}}
                    ]
                }
            ]
        }
        
        if category_type:
            query["type"] = category_type
            
        cursor = self.collection.find(query).sort("name", ASCENDING)
        categories = []
        
        async for category_doc in cursor:
            categories.append(Category(**category_doc))
            
        return categories

    async def get_popular_categories(self, user_id: str, category_type: Optional[str] = None, limit: int = 10) -> List[CategoryWithStats]:
        """Get most popular categories based on transaction count"""
        match_stage = {
            "$or": [
                {"user_id": ObjectId(user_id)},
                {"is_system": True}
            ]
        }
        
        if category_type:
            match_stage["type"] = category_type
            
        pipeline = [
            {"$match": match_stage},
            {
                "$lookup": {
                    "from": "transactions",
                    "let": {"cat_id": "$_id", "user_id_obj": ObjectId(user_id)},
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$and": [
                                        {"$eq": ["$category_id", "$$cat_id"]},
                                        {"$eq": ["$user_id", "$$user_id_obj"]}
                                    ]
                                }
                            }
                        }
                    ],
                    "as": "transactions"
                }
            },
            {
                "$addFields": {
                    "transaction_count": {"$size": "$transactions"},
                    "total_amount": {"$sum": "$transactions.amount"},
                    "avg_amount": {
                        "$cond": {
                            "if": {"$gt": [{"$size": "$transactions"}, 0]},
                            "then": {"$avg": "$transactions.amount"},
                            "else": 0.0
                        }
                    },
                    "last_used": {"$max": "$transactions.created_at"}
                }
            },
            {"$match": {"transaction_count": {"$gt": 0}}},  # Only categories with transactions
            {"$sort": {"transaction_count": -1}},
            {"$limit": limit}
        ]
        
        cursor = self.collection.aggregate(pipeline)
        categories = []
        
        async for category_doc in cursor:
            category_doc.pop("transactions", None)
            
            # Ensure numeric fields are not None
            category_doc["transaction_count"] = category_doc.get("transaction_count", 0)
            category_doc["total_amount"] = category_doc.get("total_amount") or 0.0
            category_doc["avg_amount"] = category_doc.get("avg_amount") or 0.0
            category_doc["last_used"] = category_doc.get("last_used")
            
            categories.append(CategoryWithStats(**category_doc))
            
        return categories