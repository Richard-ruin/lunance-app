# app/services/transaction_service.py
"""Transaction management service with comprehensive analytics."""

from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any, Tuple
import logging
from bson import ObjectId
from pymongo import ASCENDING, DESCENDING
import calendar

from ..config.database import get_database
from ..models.transaction import (
    TransactionInDB, TransactionCreate, TransactionUpdate, TransactionResponse,
    TransactionWithCategory, TransactionSummary, MonthlyTransactionSummary,
    CategoryTransactionSummary, DailyTransactionSummary, TransactionFilters,
    TransactionBulkCreate, TransactionType
)
from ..models.common import PaginatedResponse, PaginationParams
from ..services.category_service import category_service

logger = logging.getLogger(__name__)


class TransactionServiceError(Exception):
    """Transaction service related error."""
    pass


class TransactionService:
    """Transaction management service."""
    
    def __init__(self):
        self.collection_name = "transactions"
    
    async def create_transaction(
        self,
        user_id: str,
        transaction_data: TransactionCreate
    ) -> TransactionResponse:
        """
        Create new transaction.
        
        Args:
            user_id: User ID
            transaction_data: Transaction creation data
            
        Returns:
            Created transaction response
            
        Raises:
            TransactionServiceError: If creation fails
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Verify category exists and user has access to it
            category = await category_service.get_category_by_id(
                transaction_data.category_id, 
                user_id
            )
            if not category:
                raise TransactionServiceError("Category not found or access denied")
            
            # Create transaction document
            transaction_doc = TransactionInDB(
                user_id=user_id,
                category_id=transaction_data.category_id,
                type=transaction_data.type,
                amount=transaction_data.amount,
                description=transaction_data.description,
                date=transaction_data.date,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Insert transaction
            result = await collection.insert_one(
                transaction_doc.model_dump(by_alias=True, exclude={"id"})
            )
            
            transaction_id = str(result.inserted_id)
            
            # Get created transaction
            created_transaction_doc = await collection.find_one({"_id": result.inserted_id})
            created_transaction = TransactionInDB(**created_transaction_doc)
            
            logger.info(f"Transaction created: {transaction_id} by user {user_id}")
            
            return TransactionResponse(
                id=transaction_id,
                user_id=created_transaction.user_id,
                category_id=created_transaction.category_id,
                type=created_transaction.type,
                amount=created_transaction.amount,
                description=created_transaction.description,
                date=created_transaction.date,
                created_at=created_transaction.created_at,
                updated_at=created_transaction.updated_at
            )
            
        except TransactionServiceError:
            raise
        except Exception as e:
            logger.error(f"Error creating transaction: {e}")
            raise TransactionServiceError("Failed to create transaction")
    
    async def get_transaction_by_id(
        self,
        transaction_id: str,
        user_id: str
    ) -> Optional[TransactionWithCategory]:
        """
        Get transaction by ID with category details.
        
        Args:
            transaction_id: Transaction ID
            user_id: User ID for access control
            
        Returns:
            Transaction with category details or None
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Aggregation pipeline to join with category
            pipeline = [
                {
                    "$match": {
                        "_id": ObjectId(transaction_id),
                        "user_id": user_id
                    }
                },
                {
                    "$lookup": {
                        "from": "categories",
                        "localField": "category_id",
                        "foreignField": "_id",
                        "as": "category"
                    }
                },
                {"$unwind": "$category"},
                {
                    "$addFields": {
                        "category_name": "$category.name",
                        "category_icon": "$category.icon",
                        "category_color": "$category.color"
                    }
                }
            ]
            
            result = await collection.aggregate(pipeline).to_list(1)
            
            if not result:
                return None
            
            transaction_doc = result[0]
            
            return TransactionWithCategory(
                id=str(transaction_doc["_id"]),
                user_id=transaction_doc["user_id"],
                category_id=transaction_doc["category_id"],
                type=TransactionType(transaction_doc["type"]),
                amount=transaction_doc["amount"],
                description=transaction_doc["description"],
                date=transaction_doc["date"],
                created_at=transaction_doc["created_at"],
                updated_at=transaction_doc["updated_at"],
                category_name=transaction_doc["category_name"],
                category_icon=transaction_doc["category_icon"],
                category_color=transaction_doc["category_color"]
            )
            
        except Exception as e:
            logger.error(f"Error getting transaction {transaction_id}: {e}")
            return None
    
    async def list_transactions(
        self,
        user_id: str,
        pagination: PaginationParams,
        filters: Optional[TransactionFilters] = None
    ) -> PaginatedResponse[TransactionWithCategory]:
        """
        List user transactions with filtering and pagination.
        
        Args:
            user_id: User ID
            pagination: Pagination parameters
            filters: Transaction filters
            
        Returns:
            Paginated transaction response
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Build match query
            match_query = {"user_id": user_id}
            
            if filters:
                # Date range filter
                if filters.start_date or filters.end_date:
                    date_filter = {}
                    if filters.start_date:
                        date_filter["$gte"] = filters.start_date
                    if filters.end_date:
                        date_filter["$lte"] = filters.end_date
                    match_query["date"] = date_filter
                
                # Category filter
                if filters.category_id:
                    match_query["category_id"] = filters.category_id
                
                # Transaction type filter
                if filters.transaction_type:
                    match_query["type"] = filters.transaction_type.value
                
                # Amount range filter
                if filters.min_amount is not None or filters.max_amount is not None:
                    amount_filter = {}
                    if filters.min_amount is not None:
                        amount_filter["$gte"] = filters.min_amount
                    if filters.max_amount is not None:
                        amount_filter["$lte"] = filters.max_amount
                    match_query["amount"] = amount_filter
                
                # Search in description
                if filters.search:
                    match_query["description"] = {"$regex": filters.search, "$options": "i"}
            
            # Build aggregation pipeline
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
                {"$unwind": "$category"},
                {
                    "$addFields": {
                        "category_name": "$category.name",
                        "category_icon": "$category.icon",
                        "category_color": "$category.color"
                    }
                }
            ]
            
            # Get total count
            count_pipeline = pipeline + [{"$count": "total"}]
            count_result = await collection.aggregate(count_pipeline).to_list(1)
            total = count_result[0]["total"] if count_result else 0
            
            # Add sorting and pagination
            sort_field = pagination.sort_by or "created_at"
            sort_direction = DESCENDING if pagination.sort_order.value == "desc" else ASCENDING
            
            pipeline.extend([
                {"$sort": {sort_field: sort_direction}},
                {"$skip": (pagination.page - 1) * pagination.per_page},
                {"$limit": pagination.per_page}
            ])
            
            # Execute aggregation
            transactions_docs = await collection.aggregate(pipeline).to_list(pagination.per_page)
            
            # Convert to response format
            transactions = []
            for transaction_doc in transactions_docs:
                transactions.append(TransactionWithCategory(
                    id=str(transaction_doc["_id"]),
                    user_id=transaction_doc["user_id"],
                    category_id=transaction_doc["category_id"],
                    type=TransactionType(transaction_doc["type"]),
                    amount=transaction_doc["amount"],
                    description=transaction_doc["description"],
                    date=transaction_doc["date"],
                    created_at=transaction_doc["created_at"],
                    updated_at=transaction_doc["updated_at"],
                    category_name=transaction_doc["category_name"],
                    category_icon=transaction_doc["category_icon"],
                    category_color=transaction_doc["category_color"]
                ))
            
            return PaginatedResponse.create(
                items=transactions,
                total=total,
                page=pagination.page,
                per_page=pagination.per_page
            )
            
        except Exception as e:
            logger.error(f"Error listing transactions: {e}")
            raise TransactionServiceError("Failed to list transactions")
    
    async def update_transaction(
        self,
        transaction_id: str,
        user_id: str,
        update_data: TransactionUpdate
    ) -> Optional[TransactionResponse]:
        """
        Update transaction.
        
        Args:
            transaction_id: Transaction ID
            user_id: User ID
            update_data: Update data
            
        Returns:
            Updated transaction response
            
        Raises:
            TransactionServiceError: If update fails
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Check if transaction exists and belongs to user
            existing_transaction = await collection.find_one({
                "_id": ObjectId(transaction_id),
                "user_id": user_id
            })
            
            if not existing_transaction:
                raise TransactionServiceError("Transaction not found")
            
            # Prepare update data
            update_fields = {}
            for field, value in update_data.model_dump(exclude_none=True).items():
                if value is not None:
                    update_fields[field] = value
            
            if not update_fields:
                # No updates provided, return current transaction
                transaction = TransactionInDB(**existing_transaction)
                return TransactionResponse(
                    id=str(transaction.id),
                    user_id=transaction.user_id,
                    category_id=transaction.category_id,
                    type=transaction.type,
                    amount=transaction.amount,
                    description=transaction.description,
                    date=transaction.date,
                    created_at=transaction.created_at,
                    updated_at=transaction.updated_at
                )
            
            # Verify category if being updated
            if "category_id" in update_fields:
                category = await category_service.get_category_by_id(
                    update_fields["category_id"], 
                    user_id
                )
                if not category:
                    raise TransactionServiceError("Category not found or access denied")
            
            # Add updated timestamp
            update_fields["updated_at"] = datetime.utcnow()
            
            # Update transaction
            result = await collection.update_one(
                {"_id": ObjectId(transaction_id)},
                {"$set": update_fields}
            )
            
            if result.modified_count == 0:
                raise TransactionServiceError("Failed to update transaction")
            
            # Get updated transaction
            updated_transaction_doc = await collection.find_one({"_id": ObjectId(transaction_id)})
            updated_transaction = TransactionInDB(**updated_transaction_doc)
            
            logger.info(f"Transaction updated: {transaction_id} by user {user_id}")
            
            return TransactionResponse(
                id=str(updated_transaction.id),
                user_id=updated_transaction.user_id,
                category_id=updated_transaction.category_id,
                type=updated_transaction.type,
                amount=updated_transaction.amount,
                description=updated_transaction.description,
                date=updated_transaction.date,
                created_at=updated_transaction.created_at,
                updated_at=updated_transaction.updated_at
            )
            
        except TransactionServiceError:
            raise
        except Exception as e:
            logger.error(f"Error updating transaction {transaction_id}: {e}")
            raise TransactionServiceError("Failed to update transaction")
    
    async def delete_transaction(
        self,
        transaction_id: str,
        user_id: str
    ) -> bool:
        """
        Delete transaction.
        
        Args:
            transaction_id: Transaction ID
            user_id: User ID
            
        Returns:
            True if successful
            
        Raises:
            TransactionServiceError: If deletion fails
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Delete transaction (only if belongs to user)
            result = await collection.delete_one({
                "_id": ObjectId(transaction_id),
                "user_id": user_id
            })
            
            if result.deleted_count == 0:
                raise TransactionServiceError("Transaction not found")
            
            logger.info(f"Transaction deleted: {transaction_id} by user {user_id}")
            return True
            
        except TransactionServiceError:
            raise
        except Exception as e:
            logger.error(f"Error deleting transaction {transaction_id}: {e}")
            raise TransactionServiceError("Failed to delete transaction")
    
    async def get_transaction_summary(
        self,
        user_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> TransactionSummary:
        """
        Get transaction summary for user.
        
        Args:
            user_id: User ID
            start_date: Start date filter
            end_date: End date filter
            
        Returns:
            Transaction summary
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Build match query
            match_query = {"user_id": user_id}
            
            if start_date or end_date:
                date_filter = {}
                if start_date:
                    date_filter["$gte"] = start_date
                if end_date:
                    date_filter["$lte"] = end_date
                match_query["date"] = date_filter
            
            # Aggregation pipeline for summary
            pipeline = [
                {"$match": match_query},
                {
                    "$group": {
                        "_id": None,
                        "total_income": {
                            "$sum": {
                                "$cond": [{"$eq": ["$type", "income"]}, "$amount", 0]
                            }
                        },
                        "total_expense": {
                            "$sum": {
                                "$cond": [{"$eq": ["$type", "expense"]}, "$amount", 0]
                            }
                        },
                        "total_amount": {"$sum": "$amount"},
                        "transaction_count": {"$sum": 1},
                        "largest_income": {
                            "$max": {
                                "$cond": [{"$eq": ["$type", "income"]}, "$amount", 0]
                            }
                        },
                        "largest_expense": {
                            "$max": {
                                "$cond": [{"$eq": ["$type", "expense"]}, "$amount", 0]
                            }
                        }
                    }
                }
            ]
            
            result = await collection.aggregate(pipeline).to_list(1)
            
            if not result:
                return TransactionSummary(
                    total_income=0.0,
                    total_expense=0.0,
                    net_amount=0.0,
                    transaction_count=0,
                    average_transaction=0.0,
                    largest_expense=None,
                    largest_income=None
                )
            
            data = result[0]
            total_income = data["total_income"]
            total_expense = data["total_expense"]
            transaction_count = data["transaction_count"]
            total_amount = data["total_amount"]
            
            return TransactionSummary(
                total_income=total_income,
                total_expense=total_expense,
                net_amount=total_income - total_expense,
                transaction_count=transaction_count,
                average_transaction=total_amount / transaction_count if transaction_count > 0 else 0.0,
                largest_expense=data["largest_expense"] if data["largest_expense"] > 0 else None,
                largest_income=data["largest_income"] if data["largest_income"] > 0 else None
            )
            
        except Exception as e:
            logger.error(f"Error getting transaction summary: {e}")
            return TransactionSummary(
                total_income=0.0,
                total_expense=0.0,
                net_amount=0.0,
                transaction_count=0,
                average_transaction=0.0,
                largest_expense=None,
                largest_income=None
            )
    
    async def get_monthly_summary(
        self,
        user_id: str,
        year: Optional[int] = None,
        limit: int = 12
    ) -> List[MonthlyTransactionSummary]:
        """
        Get monthly transaction summary.
        
        Args:
            user_id: User ID
            year: Year filter (current year if None)
            limit: Number of months to return
            
        Returns:
            List of monthly summaries
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            if year is None:
                year = datetime.utcnow().year
            
            # Build match query
            start_date = date(year, 1, 1)
            end_date = date(year, 12, 31)
            
            match_query = {
                "user_id": user_id,
                "date": {"$gte": start_date, "$lte": end_date}
            }
            
            # Aggregation pipeline
            pipeline = [
                {"$match": match_query},
                {
                    "$group": {
                        "_id": {
                            "year": {"$year": "$date"},
                            "month": {"$month": "$date"}
                        },
                        "total_income": {
                            "$sum": {
                                "$cond": [{"$eq": ["$type", "income"]}, "$amount", 0]
                            }
                        },
                        "total_expense": {
                            "$sum": {
                                "$cond": [{"$eq": ["$type", "expense"]}, "$amount", 0]
                            }
                        },
                        "transaction_count": {"$sum": 1}
                    }
                },
                {"$sort": {"_id.year": 1, "_id.month": 1}},
                {"$limit": limit}
            ]
            
            result = await collection.aggregate(pipeline).to_list(limit)
            
            monthly_summaries = []
            for data in result:
                year_val = data["_id"]["year"]
                month_val = data["_id"]["month"]
                total_income = data["total_income"]
                total_expense = data["total_expense"]
                
                monthly_summaries.append(MonthlyTransactionSummary(
                    year=year_val,
                    month=month_val,
                    month_name=calendar.month_name[month_val],
                    total_income=total_income,
                    total_expense=total_expense,
                    net_amount=total_income - total_expense,
                    transaction_count=data["transaction_count"]
                ))
            
            return monthly_summaries
            
        except Exception as e:
            logger.error(f"Error getting monthly summary: {e}")
            return []
    
    async def get_category_summary(
        self,
        user_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        transaction_type: Optional[TransactionType] = None
    ) -> List[CategoryTransactionSummary]:
        """
        Get transaction summary by category.
        
        Args:
            user_id: User ID
            start_date: Start date filter
            end_date: End date filter
            transaction_type: Transaction type filter
            
        Returns:
            List of category summaries
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Build match query
            match_query = {"user_id": user_id}
            
            if start_date or end_date:
                date_filter = {}
                if start_date:
                    date_filter["$gte"] = start_date
                if end_date:
                    date_filter["$lte"] = end_date
                match_query["date"] = date_filter
            
            if transaction_type:
                match_query["type"] = transaction_type.value
            
            # Aggregation pipeline
            pipeline = [
                {"$match": match_query},
                {
                    "$group": {
                        "_id": "$category_id",
                        "total_amount": {"$sum": "$amount"},
                        "transaction_count": {"$sum": 1},
                        "average_amount": {"$avg": "$amount"}
                    }
                },
                {
                    "$lookup": {
                        "from": "categories",
                        "localField": "_id",
                        "foreignField": "_id",
                        "as": "category"
                    }
                },
                {"$unwind": "$category"},
                {
                    "$addFields": {
                        "category_name": "$category.name",
                        "category_icon": "$category.icon",
                        "category_color": "$category.color"
                    }
                },
                {"$sort": {"total_amount": -1}}
            ]
            
            result = await collection.aggregate(pipeline).to_list(None)
            
            # Calculate total for percentage calculation
            total_amount = sum(item["total_amount"] for item in result)
            
            category_summaries = []
            for data in result:
                percentage = (data["total_amount"] / total_amount * 100) if total_amount > 0 else 0
                
                category_summaries.append(CategoryTransactionSummary(
                    category_id=str(data["_id"]),
                    category_name=data["category_name"],
                    category_icon=data["category_icon"],
                    category_color=data["category_color"],
                    total_amount=data["total_amount"],
                    transaction_count=data["transaction_count"],
                    percentage=round(percentage, 2),
                    average_amount=data["average_amount"]
                ))
            
            return category_summaries
            
        except Exception as e:
            logger.error(f"Error getting category summary: {e}")
            return []
    
    async def get_daily_summary(
        self,
        user_id: str,
        start_date: date,
        end_date: date
    ) -> List[DailyTransactionSummary]:
        """
        Get daily transaction summary for date range.
        
        Args:
            user_id: User ID
            start_date: Start date
            end_date: End date
            
        Returns:
            List of daily summaries
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Build match query
            match_query = {
                "user_id": user_id,
                "date": {"$gte": start_date, "$lte": end_date}
            }
            
            # Aggregation pipeline
            pipeline = [
                {"$match": match_query},
                {
                    "$group": {
                        "_id": "$date",
                        "total_income": {
                            "$sum": {
                                "$cond": [{"$eq": ["$type", "income"]}, "$amount", 0]
                            }
                        },
                        "total_expense": {
                            "$sum": {
                                "$cond": [{"$eq": ["$type", "expense"]}, "$amount", 0]
                            }
                        },
                        "transaction_count": {"$sum": 1}
                    }
                },
                {"$sort": {"_id": 1}}
            ]
            
            result = await collection.aggregate(pipeline).to_list(None)
            
            daily_summaries = []
            for data in result:
                total_income = data["total_income"]
                total_expense = data["total_expense"]
                
                daily_summaries.append(DailyTransactionSummary(
                    date=data["_id"],
                    total_income=total_income,
                    total_expense=total_expense,
                    net_amount=total_income - total_expense,
                    transaction_count=data["transaction_count"]
                ))
            
            return daily_summaries
            
        except Exception as e:
            logger.error(f"Error getting daily summary: {e}")
            return []
    
    async def bulk_create_transactions(
        self,
        user_id: str,
        transactions_data: TransactionBulkCreate
    ) -> Dict[str, Any]:
        """
        Create multiple transactions at once.
        
        Args:
            user_id: User ID
            transactions_data: Bulk transaction data
            
        Returns:
            Bulk creation results
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            created_transactions = []
            failed_transactions = []
            
            for i, transaction_data in enumerate(transactions_data.transactions):
                try:
                    # Verify category exists and user has access
                    category = await category_service.get_category_by_id(
                        transaction_data.category_id, 
                        user_id
                    )
                    if not category:
                        failed_transactions.append({
                            "index": i,
                            "error": "Category not found or access denied",
                            "data": transaction_data.model_dump()
                        })
                        continue
                    
                    # Create transaction document
                    transaction_doc = TransactionInDB(
                        user_id=user_id,
                        category_id=transaction_data.category_id,
                        type=transaction_data.type,
                        amount=transaction_data.amount,
                        description=transaction_data.description,
                        date=transaction_data.date,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    
                    # Insert transaction
                    result = await collection.insert_one(
                        transaction_doc.model_dump(by_alias=True, exclude={"id"})
                    )
                    
                    created_transactions.append({
                        "index": i,
                        "id": str(result.inserted_id),
                        "data": transaction_data.model_dump()
                    })
                    
                except Exception as e:
                    failed_transactions.append({
                        "index": i,
                        "error": str(e),
                        "data": transaction_data.model_dump()
                    })
            
            logger.info(f"Bulk created {len(created_transactions)} transactions, {len(failed_transactions)} failed")
            
            return {
                "success_count": len(created_transactions),
                "failure_count": len(failed_transactions),
                "total_count": len(transactions_data.transactions),
                "created_transactions": created_transactions,
                "failed_transactions": failed_transactions
            }
            
        except Exception as e:
            logger.error(f"Error in bulk transaction creation: {e}")
            raise TransactionServiceError("Bulk transaction creation failed")


# Global transaction service instance
transaction_service = TransactionService()