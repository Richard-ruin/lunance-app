# app/services/recurring_transaction_service.py
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from bson import ObjectId
import calendar

from ..database import get_database
from ..models.recurring_transaction import RecurringTransaction, TransactionData, RecurrencePattern
from ..models.transaction import Transaction

logger = logging.getLogger(__name__)

class RecurringTransactionService:
    def __init__(self):
        self.db = None
    
    async def get_database(self):
        if not self.db:
            self.db = await get_database()
        return self.db
    
    async def create_recurring_transaction(
        self,
        user_id: str,
        template_name: str,
        transaction_data: Dict[str, Any],
        recurrence_pattern: Dict[str, Any]
    ) -> str:
        """Create a new recurring transaction template"""
        try:
            db = await self.get_database()
            
            # Calculate next execution date
            next_execution = self.calculate_next_execution(recurrence_pattern)
            
            recurring_transaction = RecurringTransaction(
                user_id=ObjectId(user_id),
                template_name=template_name,
                transaction_data=TransactionData(**transaction_data),
                recurrence_pattern=RecurrencePattern(**recurrence_pattern),
                next_execution=next_execution
            )
            
            result = await db.recurring_transactions.insert_one(
                recurring_transaction.dict(by_alias=True)
            )
            
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error creating recurring transaction: {str(e)}")
            raise
    
    async def get_user_recurring_transactions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all recurring transactions for a user"""
        try:
            db = await self.get_database()
            
            pipeline = [
                {"$match": {"user_id": ObjectId(user_id)}},
                {
                    "$lookup": {
                        "from": "categories",
                        "localField": "transaction_data.category_id",
                        "foreignField": "_id",
                        "as": "category"
                    }
                },
                {"$unwind": "$category"},
                {"$sort": {"next_execution": 1}}
            ]
            
            results = await db.recurring_transactions.aggregate(pipeline).to_list(None)
            
            formatted_results = []
            for result in results:
                # Calculate days until next execution
                days_until = (result["next_execution"] - datetime.utcnow()).days
                
                formatted_results.append({
                    "id": str(result["_id"]),
                    "template_name": result["template_name"],
                    "transaction_data": {
                        "type": result["transaction_data"]["type"],
                        "amount": result["transaction_data"]["amount"],
                        "description": result["transaction_data"]["description"],
                        "payment_method": result["transaction_data"]["payment_method"],
                        "category": {
                            "id": str(result["category"]["_id"]),
                            "nama": result["category"]["nama_kategori"],
                            "icon": result["category"]["icon"],
                            "color": result["category"]["color"]
                        }
                    },
                    "recurrence_pattern": result["recurrence_pattern"],
                    "next_execution": result["next_execution"],
                    "days_until_next": max(0, days_until),
                    "is_active": result["is_active"],
                    "created_at": result["created_at"],
                    "last_executed": result.get("last_executed")
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error getting recurring transactions: {str(e)}")
            raise
    
    async def update_recurring_transaction(
        self,
        recurring_id: str,
        user_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update a recurring transaction"""
        try:
            db = await self.get_database()
            
            # Prepare update document
            update_doc = {}
            
            if "template_name" in updates:
                update_doc["template_name"] = updates["template_name"]
            
            if "transaction_data" in updates:
                for key, value in updates["transaction_data"].items():
                    update_doc[f"transaction_data.{key}"] = value
            
            if "recurrence_pattern" in updates:
                for key, value in updates["recurrence_pattern"].items():
                    update_doc[f"recurrence_pattern.{key}"] = value
                
                # Recalculate next execution if pattern changed
                if any(key in updates["recurrence_pattern"] for key in ["frequency", "interval", "day_of_week", "day_of_month"]):
                    current_recurring = await db.recurring_transactions.find_one({
                        "_id": ObjectId(recurring_id),
                        "user_id": ObjectId(user_id)
                    })
                    
                    if current_recurring:
                        updated_pattern = current_recurring["recurrence_pattern"].copy()
                        updated_pattern.update(updates["recurrence_pattern"])
                        update_doc["next_execution"] = self.calculate_next_execution(updated_pattern)
            
            if "is_active" in updates:
                update_doc["is_active"] = updates["is_active"]
            
            result = await db.recurring_transactions.update_one(
                {
                    "_id": ObjectId(recurring_id),
                    "user_id": ObjectId(user_id)
                },
                {"$set": update_doc}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating recurring transaction: {str(e)}")
            return False
    
    async def delete_recurring_transaction(self, recurring_id: str, user_id: str) -> bool:
        """Delete a recurring transaction"""
        try:
            db = await self.get_database()
            
            result = await db.recurring_transactions.delete_one({
                "_id": ObjectId(recurring_id),
                "user_id": ObjectId(user_id)
            })
            
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting recurring transaction: {str(e)}")
            return False
    
    async def execute_recurring_transaction(self, recurring_id: str, user_id: str) -> Optional[str]:
        """Execute a recurring transaction manually"""
        try:
            db = await self.get_database()
            
            # Get recurring transaction
            recurring_transaction = await db.recurring_transactions.find_one({
                "_id": ObjectId(recurring_id),
                "user_id": ObjectId(user_id),
                "is_active": True
            })
            
            if not recurring_transaction:
                return None
            
            # Create actual transaction
            transaction_data = recurring_transaction["transaction_data"]
            transaction = Transaction(
                user_id=ObjectId(user_id),
                type=transaction_data["type"],
                amount=transaction_data["amount"],
                description=f"[Recurring] {transaction_data['description']}",
                category_id=ObjectId(transaction_data["category_id"]),
                payment_method=transaction_data["payment_method"],
                date=datetime.utcnow()
            )
            
            result = await db.transactions.insert_one(transaction.dict(by_alias=True))
            
            # Update recurring transaction
            next_execution = self.calculate_next_execution(
                recurring_transaction["recurrence_pattern"],
                from_date=datetime.utcnow()
            )
            
            await db.recurring_transactions.update_one(
                {"_id": ObjectId(recurring_id)},
                {
                    "$set": {
                        "last_executed": datetime.utcnow(),
                        "next_execution": next_execution
                    }
                }
            )
            
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error executing recurring transaction: {str(e)}")
            return None
    
    async def process_due_recurring_transactions(self) -> Dict[str, Any]:
        """Process all due recurring transactions (background job)"""
        try:
            db = await self.get_database()
            
            # Find all due recurring transactions
            now = datetime.utcnow()
            due_transactions = await db.recurring_transactions.find({
                "is_active": True,
                "next_execution": {"$lte": now}
            }).to_list(None)
            
            processed = 0
            failed = 0
            created_transaction_ids = []
            
            for recurring_transaction in due_transactions:
                try:
                    # Create actual transaction
                    transaction_data = recurring_transaction["transaction_data"]
                    transaction = Transaction(
                        user_id=recurring_transaction["user_id"],
                        type=transaction_data["type"],
                        amount=transaction_data["amount"],
                        description=f"[Auto-Recurring] {transaction_data['description']}",
                        category_id=ObjectId(transaction_data["category_id"]),
                        payment_method=transaction_data["payment_method"],
                        date=now
                    )
                    
                    result = await db.transactions.insert_one(transaction.dict(by_alias=True))
                    created_transaction_ids.append(str(result.inserted_id))
                    
                    # Calculate next execution
                    next_execution = self.calculate_next_execution(
                        recurring_transaction["recurrence_pattern"],
                        from_date=now
                    )
                    
                    # Check if recurring transaction should end
                    should_deactivate = False
                    if recurring_transaction["recurrence_pattern"].get("end_date"):
                        if next_execution > recurring_transaction["recurrence_pattern"]["end_date"]:
                            should_deactivate = True
                    
                    # Update recurring transaction
                    update_data = {
                        "last_executed": now,
                        "next_execution": next_execution
                    }
                    
                    if should_deactivate:
                        update_data["is_active"] = False
                    
                    await db.recurring_transactions.update_one(
                        {"_id": recurring_transaction["_id"]},
                        {"$set": update_data}
                    )
                    
                    processed += 1
                    
                except Exception as e:
                    logger.error(f"Error processing recurring transaction {recurring_transaction['_id']}: {str(e)}")
                    failed += 1
            
            return {
                "processed": processed,
                "failed": failed,
                "created_transactions": created_transaction_ids,
                "processed_at": now
            }
            
        except Exception as e:
            logger.error(f"Error processing due recurring transactions: {str(e)}")
            return {"processed": 0, "failed": 0, "created_transactions": [], "error": str(e)}
    
    def calculate_next_execution(
        self,
        pattern: Dict[str, Any],
        from_date: Optional[datetime] = None
    ) -> datetime:
        """Calculate next execution date based on recurrence pattern"""
        base_date = from_date or datetime.utcnow()
        frequency = pattern["frequency"]
        interval = pattern.get("interval", 1)
        
        if frequency == "daily":
            return base_date + timedelta(days=interval)
        
        elif frequency == "weekly":
            # Find next occurrence of specified day of week
            current_weekday = base_date.weekday()
            target_weekday = pattern.get("day_of_week", current_weekday)
            
            # Convert from Sunday=0 to Monday=0 format if needed
            if target_weekday == 0:  # Sunday
                target_weekday = 6
            else:
                target_weekday -= 1
            
            days_ahead = target_weekday - current_weekday
            if days_ahead <= 0:  # Target day already passed this week
                days_ahead += 7 * interval
            else:
                days_ahead += 7 * (interval - 1)
            
            return base_date + timedelta(days=days_ahead)
        
        elif frequency == "monthly":
            # Calculate next month occurrence
            target_day = pattern.get("day_of_month", base_date.day)
            
            next_month = base_date.month + interval
            next_year = base_date.year
            
            while next_month > 12:
                next_month -= 12
                next_year += 1
            
            # Handle end of month cases
            last_day_of_month = calendar.monthrange(next_year, next_month)[1]
            target_day = min(target_day, last_day_of_month)
            
            return datetime(next_year, next_month, target_day, base_date.hour, base_date.minute)
        
        elif frequency == "yearly":
            return base_date.replace(year=base_date.year + interval)
        
        else:
            # Default to daily if unknown frequency
            return base_date + timedelta(days=1)