# app/api/v1/transactions/crud.py
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING

from app.models.transaction import (
    Transaction, TransactionCreate, TransactionUpdate,
    TransactionFilter, TransactionSort, TransactionSummary,
    CategoryBreakdown, PeriodSummary
)

class TransactionCRUD:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database
        self.collection = database.transactions

    async def create_transaction(self, student_id: str, transaction_data: TransactionCreate) -> Transaction:
        """Create a new transaction"""
        transaction_dict = transaction_data.model_dump()
        transaction_dict["student_id"] = student_id
        transaction_dict["created_at"] = datetime.utcnow()
        transaction_dict["updated_at"] = datetime.utcnow()
        
        # Set transaction_date if not provided
        if not transaction_dict.get("transaction_date"):
            transaction_dict["transaction_date"] = datetime.utcnow()
        
        # Initialize metadata if not provided
        if "metadata" not in transaction_dict:
            transaction_dict["metadata"] = {}
        
        result = await self.collection.insert_one(transaction_dict)
        transaction_dict["_id"] = str(result.inserted_id)
        
        return Transaction(**transaction_dict)

    async def get_transaction(self, transaction_id: str, student_id: str) -> Optional[Transaction]:
        """Get a single transaction by ID for a specific student"""
        if not ObjectId.is_valid(transaction_id):
            return None
            
        transaction = await self.collection.find_one({
            "_id": ObjectId(transaction_id),
            "student_id": student_id
        })
        
        if transaction:
            transaction["_id"] = str(transaction["_id"])
            return Transaction(**transaction)
        return None

    async def get_transactions(
        self, 
        student_id: str,
        skip: int = 0,
        limit: int = 20,
        filters: Optional[TransactionFilter] = None,
        sort: TransactionSort = TransactionSort.DATE_DESC
    ) -> Dict[str, Any]:
        """Get transactions with pagination and filtering"""
        
        # Build query
        query = {"student_id": student_id}
        
        if filters:
            if filters.type:
                query["type"] = filters.type
            if filters.category_id:
                query["category_id"] = filters.category_id
            if filters.payment_method:
                query["payment_method"] = filters.payment_method
            if filters.start_date or filters.end_date:
                date_filter = {}
                if filters.start_date:
                    date_filter["$gte"] = filters.start_date
                if filters.end_date:
                    date_filter["$lte"] = filters.end_date
                query["transaction_date"] = date_filter
            if filters.min_amount is not None or filters.max_amount is not None:
                amount_filter = {}
                if filters.min_amount is not None:
                    amount_filter["$gte"] = filters.min_amount
                if filters.max_amount is not None:
                    amount_filter["$lte"] = filters.max_amount
                query["amount"] = amount_filter
            if filters.search:
                query["$or"] = [
                    {"title": {"$regex": filters.search, "$options": "i"}},
                    {"notes": {"$regex": filters.search, "$options": "i"}},
                    {"account_name": {"$regex": filters.search, "$options": "i"}}
                ]
        
        # Build sort
        sort_mapping = {
            TransactionSort.DATE_DESC: [("transaction_date", DESCENDING)],
            TransactionSort.DATE_ASC: [("transaction_date", ASCENDING)],
            TransactionSort.AMOUNT_DESC: [("amount", DESCENDING)],
            TransactionSort.AMOUNT_ASC: [("amount", ASCENDING)],
            TransactionSort.TITLE_ASC: [("title", ASCENDING)],
            TransactionSort.TITLE_DESC: [("title", DESCENDING)]
        }
        
        # Get total count
        total = await self.collection.count_documents(query)
        
        # Get transactions
        cursor = self.collection.find(query).sort(sort_mapping[sort]).skip(skip).limit(limit)
        transactions = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string
        for transaction in transactions:
            transaction["_id"] = str(transaction["_id"])
        
        return {
            "transactions": [Transaction(**t) for t in transactions],
            "total": total,
            "page": (skip // limit) + 1,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }

    async def update_transaction(
        self, 
        transaction_id: str, 
        student_id: str, 
        update_data: TransactionUpdate
    ) -> Optional[Transaction]:
        """Update a transaction"""
        if not ObjectId.is_valid(transaction_id):
            return None
            
        update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
        update_dict["updated_at"] = datetime.utcnow()
        
        result = await self.collection.update_one(
            {"_id": ObjectId(transaction_id), "student_id": student_id},
            {"$set": update_dict}
        )
        
        if result.modified_count:
            return await self.get_transaction(transaction_id, student_id)
        return None

    async def delete_transaction(self, transaction_id: str, student_id: str) -> bool:
        """Delete a transaction"""
        if not ObjectId.is_valid(transaction_id):
            return False
            
        result = await self.collection.delete_one({
            "_id": ObjectId(transaction_id),
            "student_id": student_id
        })
        
        return result.deleted_count > 0

    async def bulk_delete_transactions(self, transaction_ids: List[str], student_id: str) -> Dict[str, Any]:
        """Delete multiple transactions"""
        valid_ids = []
        invalid_ids = []
        
        for id_str in transaction_ids:
            if ObjectId.is_valid(id_str):
                valid_ids.append(ObjectId(id_str))
            else:
                invalid_ids.append(id_str)
        
        if valid_ids:
            result = await self.collection.delete_many({
                "_id": {"$in": valid_ids},
                "student_id": student_id
            })
            deleted_count = result.deleted_count
        else:
            deleted_count = 0
        
        return {
            "deleted_count": deleted_count,
            "failed_ids": invalid_ids
        }

    async def get_transaction_summary(
        self, 
        student_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> TransactionSummary:
        """Get transaction summary for a period"""
        
        # Default to current month if no dates provided
        if not start_date:
            start_date = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if not end_date:
            end_date = datetime.utcnow()
        
        pipeline = [
            {
                "$match": {
                    "student_id": student_id,
                    "transaction_date": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$group": {
                    "_id": "$type",
                    "total": {"$sum": "$amount"},
                    "count": {"$sum": 1}
                }
            }
        ]
        
        results = await self.collection.aggregate(pipeline).to_list(length=None)
        
        total_income = 0
        total_expense = 0
        total_count = 0
        
        for result in results:
            if result["_id"] == "income":
                total_income = result["total"]
            elif result["_id"] == "expense":
                total_expense = result["total"]
            total_count += result["count"]
        
        net_balance = total_income - total_expense
        days_in_period = (end_date - start_date).days + 1
        daily_average = total_expense / max(days_in_period, 1)
        
        return TransactionSummary(
            total_income=total_income,
            total_expense=total_expense,
            net_balance=net_balance,
            transaction_count=total_count,
            daily_average=daily_average
        )

    async def get_category_breakdown(
        self, 
        student_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        transaction_type: Optional[str] = None
    ) -> List[CategoryBreakdown]:
        """Get spending breakdown by category"""
        
        # Default to current month if no dates provided
        if not start_date:
            start_date = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if not end_date:
            end_date = datetime.utcnow()
        
        match_query = {
            "student_id": student_id,
            "transaction_date": {"$gte": start_date, "$lte": end_date}
        }
        
        if transaction_type:
            match_query["type"] = transaction_type
        
        pipeline = [
            {"$match": match_query},
            {
                "$lookup": {
                    "from": "categories",
                    "localField": "category_id",
                    "foreignField": "_id",
                    "as": "category"
                }
            },
            {
                "$group": {
                    "_id": "$category_id",
                    "category_name": {"$first": {"$arrayElemAt": ["$category.name", 0]}},
                    "total": {"$sum": "$amount"},
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"total": -1}}
        ]
        
        results = await self.collection.aggregate(pipeline).to_list(length=None)
        
        # Calculate total for percentage
        total_amount = sum(result["total"] for result in results)
        
        breakdown = []
        for result in results:
            percentage = (result["total"] / total_amount * 100) if total_amount > 0 else 0
            breakdown.append(CategoryBreakdown(
                category_id=str(result["_id"]),
                category_name=result.get("category_name", "Unknown"),
                amount=result["total"],
                percentage=round(percentage, 2),
                transaction_count=result["count"]
            ))
        
        return breakdown

    async def get_recent_transactions(self, student_id: str, limit: int = 5) -> List[Transaction]:
        """Get recent transactions for dashboard"""
        cursor = self.collection.find(
            {"student_id": student_id}
        ).sort("transaction_date", DESCENDING).limit(limit)
        
        transactions = await cursor.to_list(length=limit)
        
        for transaction in transactions:
            transaction["_id"] = str(transaction["_id"])
        
        return [Transaction(**t) for t in transactions]

    async def search_transactions(
        self, 
        student_id: str, 
        search_term: str,
        limit: int = 20
    ) -> List[Transaction]:
        """Search transactions by title, notes, or account name"""
        query = {
            "student_id": student_id,
            "$or": [
                {"title": {"$regex": search_term, "$options": "i"}},
                {"notes": {"$regex": search_term, "$options": "i"}},
                {"account_name": {"$regex": search_term, "$options": "i"}}
            ]
        }
        
        cursor = self.collection.find(query).sort("transaction_date", DESCENDING).limit(limit)
        transactions = await cursor.to_list(length=limit)
        
        for transaction in transactions:
            transaction["_id"] = str(transaction["_id"])
        
        return [Transaction(**t) for t in transactions]