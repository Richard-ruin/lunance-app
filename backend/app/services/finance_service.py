# app/services/finance_service_updated.py - Fixed logic untuk tabungan awal
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from bson import ObjectId

from ..config.database import get_database
from ..models.finance import (
    Transaction, SavingsGoal, FinancialSummary, PendingFinancialData,
    TransactionType, TransactionStatus, SavingsGoalStatus
)
from ..models.user import User, FinancialSettings
from ..utils.timezone_utils import IndonesiaDatetime, now_for_db
from .enhanced_financial_parser import EnhancedFinancialParser

class FinanceService:
    """Enhanced Finance Service dengan logika yang diperbaiki untuk mahasiswa Indonesia"""
    
    def __init__(self):
        self.db = get_database()
        self.parser = EnhancedFinancialParser()
    
    # === FIXED: User Financial Settings Integration ===
    
    async def sync_user_financial_settings(self, user_id: str) -> Dict[str, Any]:
        """
        Sinkronisasi financial settings dengan logika yang diperbaiki:
        - current_savings tetap sebagai tabungan awal, BUKAN dari savings goals
        - Tracking total savings real-time = initial + income - expense
        """
        try:
            # Calculate real total savings = initial_savings + all_income - all_expense
            real_total_savings = await self._calculate_real_total_savings(user_id)
            
            # Get monthly progress (income - expense this month)
            monthly_progress = await self._calculate_monthly_savings_progress(user_id)
            
            # DON'T update current_savings in user financial settings
            # Keep it as initial savings amount only
            
            return {
                "success": True,
                "real_total_savings": real_total_savings,
                "monthly_progress": monthly_progress,
                "initial_savings_unchanged": True,
                "message": "Sinkronisasi berhasil - tabungan awal tetap, total real dihitung dari transaksi"
            }
            
        except Exception as e:
            print(f"Error in sync_user_financial_settings: {e}")
            return {
                "success": False,
                "error": str(e),
                "real_total_savings": 0.0,
                "monthly_progress": {}
            }
    
    async def _calculate_real_total_savings(self, user_id: str) -> float:
        """
        Hitung total tabungan real-time:
        Total = Tabungan awal (dari financial setup) + Semua pemasukan - Semua pengeluaran
        """
        try:
            # Get initial savings from user financial settings
            user_doc = self.db.users.find_one({"_id": ObjectId(user_id)})
            initial_savings = 0.0
            
            if user_doc and user_doc.get("financial_settings"):
                initial_savings = user_doc["financial_settings"].get("current_savings", 0.0)
            
            # Get all confirmed transactions
            pipeline = [
                {"$match": {
                    "user_id": user_id,
                    "status": TransactionStatus.CONFIRMED.value
                }},
                {"$group": {
                    "_id": "$type",
                    "total": {"$sum": "$amount"}
                }}
            ]
            
            transaction_summary = list(self.db.transactions.aggregate(pipeline))
            total_income = 0.0
            total_expense = 0.0
            
            for item in transaction_summary:
                if item["_id"] == TransactionType.INCOME.value:
                    total_income = item["total"]
                elif item["_id"] == TransactionType.EXPENSE.value:
                    total_expense = item["total"]
            
            # Real total = initial + income - expense
            real_total_savings = initial_savings + total_income - total_expense
            
            return max(real_total_savings, 0.0)  # Cannot be negative
            
        except Exception as e:
            print(f"Error calculating real total savings: {e}")
            return 0.0
    
    async def _calculate_total_current_savings_from_goals(self, user_id: str) -> float:
        """
        Hitung total dari savings goals (untuk tracking target tabungan, bukan total savings)
        """
        pipeline = [
            {"$match": {
                "user_id": user_id,
                "status": {"$in": [SavingsGoalStatus.ACTIVE.value, SavingsGoalStatus.COMPLETED.value]}
            }},
            {"$group": {
                "_id": None,
                "total_current": {"$sum": "$current_amount"}
            }}
        ]
        
        result = list(self.db.savings_goals.aggregate(pipeline))
        return result[0]["total_current"] if result else 0.0
    
    async def _calculate_monthly_savings_progress(self, user_id: str) -> Dict[str, Any]:
        """
        Hitung progress tabungan bulanan = pemasukan - pengeluaran bulan ini
        """
        now = IndonesiaDatetime.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_of_month_utc = IndonesiaDatetime.to_utc(start_of_month).replace(tzinfo=None)
        
        # Get user's monthly target
        user_doc = self.db.users.find_one({"_id": ObjectId(user_id)})
        monthly_target = 0.0
        if user_doc and user_doc.get("financial_settings"):
            monthly_target = user_doc["financial_settings"].get("monthly_savings_target", 0)
        
        # Calculate actual savings this month (income - expense)
        pipeline = [
            {"$match": {
                "user_id": user_id,
                "status": TransactionStatus.CONFIRMED.value,
                "date": {"$gte": start_of_month_utc}
            }},
            {"$group": {
                "_id": "$type",
                "total": {"$sum": "$amount"}
            }}
        ]
        
        transaction_summary = list(self.db.transactions.aggregate(pipeline))
        income_this_month = 0.0
        expense_this_month = 0.0
        
        for item in transaction_summary:
            if item["_id"] == TransactionType.INCOME.value:
                income_this_month = item["total"]
            elif item["_id"] == TransactionType.EXPENSE.value:
                expense_this_month = item["total"]
        
        net_savings_this_month = income_this_month - expense_this_month
        progress_percentage = (net_savings_this_month / monthly_target * 100) if monthly_target > 0 else 0
        
        return {
            "monthly_target": monthly_target,
            "income_this_month": income_this_month,
            "expense_this_month": expense_this_month,
            "net_savings_this_month": net_savings_this_month,
            "progress_percentage": min(progress_percentage, 100),
            "remaining_to_target": max(monthly_target - net_savings_this_month, 0),
            "status": "excellent" if progress_percentage >= 100 else "good" if progress_percentage >= 75 else "needs_improvement"
        }
    
    # === ENHANCED Transaction Management ===
    
    async def create_transaction(self, user_id: str, transaction_data: Dict[str, Any], 
                               chat_context: Dict[str, Any] = None) -> Transaction:
        """Membuat transaksi baru"""
        now = now_for_db()
        
        # Enhanced category detection using Indonesian student categories
        category = transaction_data.get("category")
        if not category or category == "lainnya":
            from .financial_categories import IndonesianStudentCategories
            if transaction_data["type"] == "income":
                category = IndonesianStudentCategories.get_income_category(
                    transaction_data.get("description", "")
                )
            else:
                category = IndonesianStudentCategories.get_expense_category(
                    transaction_data.get("description", "")
                )
        
        # Prepare transaction data
        trans_data = {
            "user_id": user_id,
            "type": transaction_data["type"],
            "amount": transaction_data["amount"],
            "category": category,
            "description": transaction_data.get("description"),
            "date": transaction_data.get("date", now),
            "status": TransactionStatus.PENDING.value,
            "source": chat_context.get("source", "manual") if chat_context else "manual",
            "tags": transaction_data.get("tags", []),
            "notes": transaction_data.get("notes"),
            "created_at": now,
            "updated_at": now
        }
        
        # Add chat context if available
        if chat_context:
            trans_data.update({
                "chat_message_id": chat_context.get("message_id"),
                "conversation_id": chat_context.get("conversation_id")
            })
        
        # Insert to database
        result = self.db.transactions.insert_one(trans_data)
        transaction_id = str(result.inserted_id)
        
        # Return transaction object
        trans_data["_id"] = transaction_id
        return Transaction.from_mongo(trans_data)
    
    async def confirm_transaction(self, transaction_id: str, user_id: str) -> bool:
        """Konfirmasi transaksi"""
        result = self.db.transactions.update_one(
            {"_id": ObjectId(transaction_id), "user_id": user_id},
            {"$set": {
                "status": TransactionStatus.CONFIRMED.value,
                "confirmed_at": now_for_db(),
                "updated_at": now_for_db()
            }}
        )
        
        return result.modified_count > 0
    
    async def get_user_transactions(self, user_id: str, filters: Dict[str, Any] = None,
                                  limit: int = 50, offset: int = 0) -> List[Transaction]:
        """Mengambil transaksi user dengan filter"""
        query = {"user_id": user_id}
        
        if filters:
            if filters.get("type"):
                query["type"] = filters["type"]
            if filters.get("category"):
                query["category"] = filters["category"]
            if filters.get("status"):
                query["status"] = filters["status"]
            if filters.get("start_date") or filters.get("end_date"):
                date_filter = {}
                if filters.get("start_date"):
                    date_filter["$gte"] = filters["start_date"]
                if filters.get("end_date"):
                    date_filter["$lte"] = filters["end_date"]
                query["date"] = date_filter
        
        cursor = self.db.transactions.find(query).sort("date", -1).skip(offset).limit(limit)
        
        transactions = []
        for doc in cursor:
            transactions.append(Transaction.from_mongo(doc))
        
        return transactions
    
    # === ENHANCED Savings Goal Management ===
    
    async def create_savings_goal(self, user_id: str, goal_data: Dict[str, Any],
                                chat_context: Dict[str, Any] = None) -> SavingsGoal:
        """Membuat target tabungan baru (BUKAN untuk tabungan awal)"""
        now = now_for_db()
        
        # Prepare goal data
        goal_data_prepared = {
            "user_id": user_id,
            "item_name": goal_data["item_name"],
            "target_amount": goal_data["target_amount"],
            "current_amount": 0.0,  # Always start with 0 for new goals
            "description": goal_data.get("description"),
            "target_date": goal_data.get("target_date"),
            "status": SavingsGoalStatus.ACTIVE.value,
            "monthly_target": goal_data.get("monthly_target"),
            "source": chat_context.get("source", "manual") if chat_context else "manual",
            "tags": goal_data.get("tags", []),
            "notes": goal_data.get("notes"),
            "created_at": now,
            "updated_at": now
        }
        
        # Add chat context if available
        if chat_context:
            goal_data_prepared.update({
                "chat_message_id": chat_context.get("message_id"),
                "conversation_id": chat_context.get("conversation_id")
            })
        
        # Insert to database
        result = self.db.savings_goals.insert_one(goal_data_prepared)
        goal_id = str(result.inserted_id)
        
        # Return goal object
        goal_data_prepared["_id"] = goal_id
        return SavingsGoal.from_mongo(goal_data_prepared)
    
    async def add_savings_to_goal(self, goal_id: str, user_id: str, amount: float) -> bool:
        """Menambah tabungan ke target"""
        # Get current goal
        goal_doc = self.db.savings_goals.find_one({
            "_id": ObjectId(goal_id),
            "user_id": user_id
        })
        
        if not goal_doc:
            return False
        
        goal = SavingsGoal.from_mongo(goal_doc)
        new_amount = goal.current_amount + amount
        
        update_data = {
            "current_amount": new_amount,
            "updated_at": now_for_db()
        }
        
        # Check if goal is completed
        if new_amount >= goal.target_amount and goal.status == SavingsGoalStatus.ACTIVE:
            update_data["status"] = SavingsGoalStatus.COMPLETED.value
            update_data["completed_at"] = now_for_db()
        
        result = self.db.savings_goals.update_one(
            {"_id": ObjectId(goal_id), "user_id": user_id},
            {"$set": update_data}
        )
        
        return result.modified_count > 0
    
    async def get_user_savings_goals(self, user_id: str, status: str = None) -> List[SavingsGoal]:
        """Mengambil target tabungan user"""
        query = {"user_id": user_id}
        if status:
            query["status"] = status
        
        cursor = self.db.savings_goals.find(query).sort("created_at", -1)
        
        goals = []
        for doc in cursor:
            goals.append(SavingsGoal.from_mongo(doc))
        
        return goals
    
    # === ENHANCED Financial Dashboard ===
    
    async def get_financial_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Mendapatkan dashboard keuangan dengan logika yang diperbaiki"""
        # Get user financial settings
        user_doc = self.db.users.find_one({"_id": ObjectId(user_id)})
        financial_settings = user_doc.get("financial_settings", {}) if user_doc else {}
        
        # Get real total savings (initial + income - expense)
        real_total_savings = await self._calculate_real_total_savings(user_id)
        
        # Get monthly progress
        monthly_progress = await self._calculate_monthly_savings_progress(user_id)
        
        # Get savings goals summary (separate from total savings)
        goals_total = await self._calculate_total_current_savings_from_goals(user_id)
        active_goals = await self.get_user_savings_goals(user_id, "active")
        
        # Get recent transactions
        recent_transactions = await self.get_user_transactions(
            user_id, {"status": "confirmed"}, 5, 0
        )
        
        # Get monthly summary
        monthly_summary = await self.get_financial_summary(user_id, "monthly")
        
        return {
            "user_financial_settings": {
                "initial_savings": financial_settings.get("current_savings", 0),  # Keep as initial amount
                "monthly_savings_target": financial_settings.get("monthly_savings_target", 0),
                "emergency_fund": financial_settings.get("emergency_fund", 0),
                "primary_bank": financial_settings.get("primary_bank", "")
            },
            "calculated_totals": {
                "actual_current_savings": real_total_savings,  # Real total = initial + income - expense
                "initial_savings": financial_settings.get("current_savings", 0),
                "total_income": monthly_summary.total_income,
                "total_expense": monthly_summary.total_expense,
                "net_balance": monthly_summary.net_balance
            },
            "monthly_progress": monthly_progress,
            "savings_goals_summary": {
                "total_in_goals": goals_total,  # Money allocated to specific goals
                "active_goals_count": len(active_goals),
                "goals": [goal.dict() for goal in active_goals[:3]],  # Top 3 goals
                "total_target": sum(goal.target_amount for goal in active_goals),
                "available_for_allocation": max(real_total_savings - goals_total - financial_settings.get("emergency_fund", 0), 0)
            },
            "recent_activity": {
                "transactions": [trans.dict() for trans in recent_transactions],
                "monthly_summary": monthly_summary.dict()
            },
            "sync_status": {
                "last_synced": now_for_db(),
                "logic_fixed": True,
                "description": "Total tabungan = tabungan awal + pemasukan - pengeluaran"
            }
        }
    
    # === Pending Data Management (unchanged) ===
    
    async def create_pending_financial_data(self, user_id: str, conversation_id: str,
                                          message_id: str, parsed_data: Dict[str, Any],
                                          original_message: str, luna_response: str) -> PendingFinancialData:
        """Membuat data keuangan yang menunggu konfirmasi"""
        now = now_for_db()
        expires_at = now + timedelta(hours=24)
        
        pending_data = {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "chat_message_id": message_id,
            "data_type": parsed_data.get("data_type", "transaction"),
            "parsed_data": parsed_data,
            "original_message": original_message,
            "luna_response": luna_response,
            "is_confirmed": False,
            "expires_at": expires_at,
            "created_at": now
        }
        
        result = self.db.pending_financial_data.insert_one(pending_data)
        pending_id = str(result.inserted_id)
        
        pending_data["_id"] = pending_id
        return PendingFinancialData.from_mongo(pending_data)
    
    def confirm_pending_data(self, pending_id: str, user_id: str, 
                           confirmed: bool, modifications: Dict[str, Any] = None) -> Dict[str, Any]:
        """Konfirmasi atau batalkan data keuangan yang pending - FIXED sync method"""
        # Get pending data
        pending_doc = self.db.pending_financial_data.find_one({
            "_id": ObjectId(pending_id),
            "user_id": user_id,
            "is_confirmed": False
        })
        
        if not pending_doc:
            return {"success": False, "message": "Data pending tidak ditemukan"}
        
        pending = PendingFinancialData.from_mongo(pending_doc)
        
        # Check if expired
        if pending.expires_at < now_for_db():
            return {"success": False, "message": "Data pending sudah expired"}
        
        if confirmed:
            # Apply modifications if any
            data_to_save = pending.parsed_data.copy()
            if modifications:
                data_to_save.update(modifications)
            
            try:
                # Save to appropriate collection
                if pending.data_type == "transaction" or pending.data_type in ["income", "expense"]:
                    # Create transaction using SYNCHRONOUS method
                    transaction_data = {
                        "type": data_to_save.get("type", pending.data_type),
                        "amount": data_to_save["amount"],
                        "category": data_to_save["category"],
                        "description": data_to_save["description"],
                        "date": data_to_save.get("date")
                    }
                    
                    # Convert ISO string back to datetime if needed
                    if isinstance(transaction_data["date"], str):
                        try:
                            transaction_data["date"] = datetime.fromisoformat(transaction_data["date"].replace('Z', '+00:00'))
                        except:
                            transaction_data["date"] = now_for_db()
                    
                    # Create transaction DIRECTLY in database (synchronous)
                    now = now_for_db()
                    
                    # Enhanced category detection
                    category = transaction_data.get("category")
                    if not category or category == "lainnya":
                        from .financial_categories import IndonesianStudentCategories
                        if transaction_data["type"] == "income":
                            category = IndonesianStudentCategories.get_income_category(
                                transaction_data.get("description", "")
                            )
                        else:
                            category = IndonesianStudentCategories.get_expense_category(
                                transaction_data.get("description", "")
                            )
                    
                    # Prepare transaction data for database
                    trans_data = {
                        "user_id": user_id,
                        "type": transaction_data["type"],
                        "amount": transaction_data["amount"],
                        "category": category,
                        "description": transaction_data["description"],
                        "date": transaction_data["date"],
                        "status": "confirmed",  # Auto-confirm from chat
                        "source": "chat",
                        "tags": [],
                        "notes": "Dibuat melalui chat Luna AI",
                        "chat_message_id": pending.chat_message_id,
                        "conversation_id": pending.conversation_id,
                        "created_at": now,
                        "updated_at": now,
                        "confirmed_at": now
                    }
                    
                    # Insert to database
                    result = self.db.transactions.insert_one(trans_data)
                    transaction_id = str(result.inserted_id)
                    
                    # Prepare return data
                    created_object = {
                        "id": transaction_id,
                        "type": trans_data["type"],
                        "amount": trans_data["amount"],
                        "category": trans_data["category"],
                        "description": trans_data["description"],
                        "date": trans_data["date"],
                        "status": trans_data["status"]
                    }
                    
                elif pending.data_type == "savings_goal":
                    # Create savings goal DIRECTLY in database (synchronous)
                    goal_data = {
                        "item_name": data_to_save["item_name"],
                        "target_amount": data_to_save["target_amount"],
                        "description": data_to_save.get("description"),
                        "target_date": data_to_save.get("target_date")
                    }
                    
                    # Convert ISO string back to datetime if needed
                    if isinstance(goal_data.get("target_date"), str):
                        try:
                            goal_data["target_date"] = datetime.fromisoformat(goal_data["target_date"].replace('Z', '+00:00'))
                        except:
                            goal_data["target_date"] = None
                    
                    now = now_for_db()
                    
                    # Prepare goal data for database
                    goal_data_prepared = {
                        "user_id": user_id,
                        "item_name": goal_data["item_name"],
                        "target_amount": goal_data["target_amount"],
                        "current_amount": 0.0,
                        "description": goal_data.get("description"),
                        "target_date": goal_data.get("target_date"),
                        "status": "active",
                        "monthly_target": None,
                        "source": "chat",
                        "tags": [],
                        "notes": "Dibuat melalui chat Luna AI",
                        "chat_message_id": pending.chat_message_id,
                        "conversation_id": pending.conversation_id,
                        "created_at": now,
                        "updated_at": now
                    }
                    
                    # Insert to database
                    result = self.db.savings_goals.insert_one(goal_data_prepared)
                    goal_id = str(result.inserted_id)
                    
                    # Prepare return data
                    created_object = {
                        "id": goal_id,
                        "item_name": goal_data_prepared["item_name"],
                        "target_amount": goal_data_prepared["target_amount"],
                        "current_amount": goal_data_prepared["current_amount"],
                        "target_date": goal_data_prepared["target_date"],
                        "status": goal_data_prepared["status"]
                    }
                
                # Mark as confirmed
                self.db.pending_financial_data.update_one(
                    {"_id": ObjectId(pending_id)},
                    {"$set": {
                        "is_confirmed": True,
                        "confirmed_at": now_for_db()
                    }}
                )
                
                return {
                    "success": True,
                    "message": "Data berhasil disimpan",
                    "data": created_object,
                    "type": pending.data_type
                }
                
            except Exception as e:
                print(f"Error creating financial data: {e}")
                return {"success": False, "message": f"Gagal menyimpan data: {str(e)}"}
        else:
            # Mark as cancelled (delete)
            self.db.pending_financial_data.delete_one({"_id": ObjectId(pending_id)})
            return {"success": True, "message": "Data dibatalkan"}
    
    async def get_user_pending_data(self, user_id: str) -> List[PendingFinancialData]:
        """Mengambil data pending user"""
        now = now_for_db()
        
        # Remove expired data first
        self.db.pending_financial_data.delete_many({
            "user_id": user_id,
            "expires_at": {"$lt": now}
        })
        
        # Get active pending data
        cursor = self.db.pending_financial_data.find({
            "user_id": user_id,
            "is_confirmed": False
        }).sort("created_at", -1)
        
        pending_data = []
        for doc in cursor:
            pending_data.append(PendingFinancialData.from_mongo(doc))
        
        return pending_data
    
    # === Financial Analysis ===
    
    async def get_financial_summary(self, user_id: str, period: str = "monthly",
                                  start_date: datetime = None, end_date: datetime = None) -> FinancialSummary:
        """Generate ringkasan keuangan"""
        if not start_date or not end_date:
            now = IndonesiaDatetime.now()
            if period == "daily":
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = start_date + timedelta(days=1)
            elif period == "weekly":
                start_date = now - timedelta(days=now.weekday())
                start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = start_date + timedelta(days=7)
            elif period == "monthly":
                start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                if now.month == 12:
                    end_date = start_date.replace(year=now.year + 1, month=1)
                else:
                    end_date = start_date.replace(month=now.month + 1)
            elif period == "yearly":
                start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
                end_date = start_date.replace(year=now.year + 1)
        
        # Convert to UTC for database query
        start_date_utc = IndonesiaDatetime.to_utc(start_date).replace(tzinfo=None)
        end_date_utc = IndonesiaDatetime.to_utc(end_date).replace(tzinfo=None)
        
        # Get transactions in period
        transactions = self.db.transactions.find({
            "user_id": user_id,
            "status": TransactionStatus.CONFIRMED.value,
            "date": {"$gte": start_date_utc, "$lt": end_date_utc}
        })
        
        # Calculate summary
        total_income = 0.0
        total_expense = 0.0
        income_count = 0
        expense_count = 0
        income_categories = {}
        expense_categories = {}
        
        for trans in transactions:
            if trans["type"] == TransactionType.INCOME.value:
                total_income += trans["amount"]
                income_count += 1
                category = trans["category"]
                income_categories[category] = income_categories.get(category, 0) + trans["amount"]
            else:
                total_expense += trans["amount"]
                expense_count += 1
                category = trans["category"]
                expense_categories[category] = expense_categories.get(category, 0) + trans["amount"]
        
        # Get savings goals summary
        active_goals = self.db.savings_goals.count_documents({
            "user_id": user_id,
            "status": SavingsGoalStatus.ACTIVE.value
        })
        
        goals_cursor = self.db.savings_goals.find({
            "user_id": user_id,
            "status": {"$ne": SavingsGoalStatus.CANCELLED.value}
        })
        
        total_savings_target = 0.0
        total_savings_current = 0.0
        for goal in goals_cursor:
            total_savings_target += goal["target_amount"]
            total_savings_current += goal["current_amount"]
        
        return FinancialSummary(
            user_id=user_id,
            period=period,
            total_income=total_income,
            income_count=income_count,
            income_categories=income_categories,
            total_expense=total_expense,
            expense_count=expense_count,
            expense_categories=expense_categories,
            net_balance=total_income - total_expense,
            active_goals_count=active_goals,
            total_savings_target=total_savings_target,
            total_savings_current=total_savings_current,
            start_date=start_date_utc,
            end_date=end_date_utc
        )
    
    # === Chat Integration ===
    
    def parse_financial_message(self, message: str) -> Dict[str, Any]:
        """Parse pesan chat untuk mengekstrak data keuangan"""
        return self.parser.parse_financial_data(message)
    
    # === Student-Specific Financial Methods ===
    
    async def get_student_financial_recommendations(self, user_id: str) -> List[Dict[str, Any]]:
        """Rekomendasi keuangan khusus mahasiswa Indonesia"""
        try:
            recommendations = []
            
            # Get financial data
            real_total_savings = await self._calculate_real_total_savings(user_id)
            monthly_progress = await self._calculate_monthly_savings_progress(user_id)
            monthly_summary = await self.get_financial_summary(user_id, "monthly")
            
            # Emergency fund recommendation
            if real_total_savings < 500000:  # Less than 500k
                recommendations.append({
                    "type": "emergency_fund",
                    "priority": "high",
                    "title": "Bangun Dana Darurat",
                    "description": "Mahasiswa perlu dana darurat minimal Rp 500.000 untuk situasi mendesak seperti biaya kesehatan atau keperluan kuliah mendadak.",
                    "action": "Sisihkan Rp 25.000 per minggu sampai mencapai Rp 500.000",
                    "target_amount": 500000,
                    "current_amount": real_total_savings,
                    "weekly_target": 25000
                })
            
            # Savings rate recommendation
            if monthly_progress["progress_percentage"] < 50:
                recommendations.append({
                    "type": "savings_rate",
                    "priority": "medium",
                    "title": "Tingkatkan Tingkat Tabungan",
                    "description": "Target tabungan bulanan Anda baru tercapai {:.1f}%. Ideal untuk mahasiswa adalah 15-20% dari pemasukan.".format(monthly_progress["progress_percentage"]),
                    "action": "Review pengeluaran harian dan kurangi kategori hiburan atau jajan",
                    "current_rate": monthly_progress["progress_percentage"],
                    "target_rate": 20
                })
            
            # Food expense optimization
            food_expense = monthly_summary.expense_categories.get("Makanan & Minuman", 0)
            if food_expense > monthly_progress["income_this_month"] * 0.4:  # More than 40%
                recommendations.append({
                    "type": "expense_optimization",
                    "priority": "medium",
                    "title": "Optimalkan Pengeluaran Makan",
                    "description": "Pengeluaran makan Anda {:.1f}% dari pemasukan. Ideal untuk mahasiswa adalah 30-35%.".format((food_expense / monthly_progress["income_this_month"]) * 100),
                    "action": "Coba masak sendiri, beli bahan makanan bareng teman kos, atau cari tempat makan dengan harga mahasiswa",
                    "current_percentage": (food_expense / monthly_progress["income_this_month"]) * 100,
                    "target_percentage": 35
                })
            
            # Part-time job recommendation
            if monthly_progress["income_this_month"] < 1000000 and not monthly_summary.income_categories.get("Part-time Job"):
                recommendations.append({
                    "type": "income_increase",
                    "priority": "low",
                    "title": "Pertimbangkan Kerja Sampingan",
                    "description": "Pemasukan bulanan bisa ditingkatkan dengan pekerjaan paruh waktu yang fleksibel dengan jadwal kuliah.",
                    "action": "Cari part-time job online seperti freelance writing, design, atau les private",
                    "current_income": monthly_progress["income_this_month"],
                    "potential_additional": 500000
                })
            
            # Savings goal recommendation
            active_goals = await self.get_user_savings_goals(user_id, "active")
            if len(active_goals) == 0 and real_total_savings > 1000000:
                recommendations.append({
                    "type": "savings_goal",
                    "priority": "low",
                    "title": "Buat Target Tabungan",
                    "description": "Anda sudah punya tabungan yang cukup. Saatnya membuat target untuk barang atau keperluan spesifik.",
                    "action": "Buat target tabungan untuk laptop, HP baru, atau liburan. Contoh: 'Mau nabung buat beli laptop 10 juta pada tanggal 22 januari 2026'",
                    "suggested_targets": ["Laptop untuk kuliah", "Smartphone baru", "Dana liburan", "Kursus online"]
                })
            
            return recommendations
            
        except Exception as e:
            print(f"Error getting student recommendations: {e}")
            return []
    
    async def calculate_goal_affordability(self, user_id: str, target_amount: float, target_date: datetime = None) -> Dict[str, Any]:
        """Hitung apakah target tabungan realistis untuk mahasiswa"""
        try:
            real_total_savings = await self._calculate_real_total_savings(user_id)
            monthly_progress = await self._calculate_monthly_savings_progress(user_id)
            
            # Calculate available for new goals
            user_doc = self.db.users.find_one({"_id": ObjectId(user_id)})
            emergency_fund = 0.0
            if user_doc and user_doc.get("financial_settings"):
                emergency_fund = user_doc["financial_settings"].get("emergency_fund", 0)
            
            # Reserve emergency fund and 1 month of average expenses
            reserved_amount = emergency_fund + monthly_progress["expense_this_month"]
            available_now = max(real_total_savings - reserved_amount, 0)
            
            # Calculate monthly savings capacity
            monthly_capacity = monthly_progress["net_savings_this_month"]
            
            result = {
                "target_amount": target_amount,
                "available_now": available_now,
                "monthly_capacity": monthly_capacity,
                "can_afford_now": available_now >= target_amount,
                "affordability_status": "",
                "recommended_strategy": "",
                "time_needed_months": 0,
                "suggested_monthly_allocation": 0
            }
            
            if target_date:
                months_until_target = max((target_date - datetime.now()).days / 30, 1)
                needed_monthly = (target_amount - available_now) / months_until_target
                
                result["target_date"] = target_date
                result["months_until_target"] = months_until_target
                result["needed_monthly"] = needed_monthly
                
                if needed_monthly <= monthly_capacity * 0.5:  # Only use 50% of capacity
                    result["affordability_status"] = "realistic"
                    result["recommended_strategy"] = f"Sisihkan Rp {needed_monthly:,.0f} per bulan dari tabungan bulanan Anda"
                elif needed_monthly <= monthly_capacity:
                    result["affordability_status"] = "challenging"
                    result["recommended_strategy"] = f"Perlu disiplin tinggi - sisihkan Rp {needed_monthly:,.0f} per bulan"
                else:
                    result["affordability_status"] = "unrealistic"
                    result["recommended_strategy"] = f"Target terlalu tinggi. Pertimbangkan memperpanjang waktu atau mengurangi target"
            else:
                # No target date, calculate optimal time
                if monthly_capacity > 0:
                    optimal_months = (target_amount - available_now) / (monthly_capacity * 0.3)  # Use 30% of capacity
                    result["time_needed_months"] = max(optimal_months, 1)
                    result["suggested_monthly_allocation"] = (target_amount - available_now) / optimal_months
                    result["affordability_status"] = "feasible"
                    result["recommended_strategy"] = f"Target bisa dicapai dalam {optimal_months:.1f} bulan dengan alokasi Rp {result['suggested_monthly_allocation']:,.0f} per bulan"
            
            return result
            
        except Exception as e:
            print(f"Error calculating goal affordability: {e}")
            return {
                "target_amount": target_amount,
                "affordability_status": "error",
                "recommended_strategy": "Tidak dapat menghitung, coba lagi nanti"
            }