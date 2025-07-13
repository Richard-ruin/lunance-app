# app/services/finance_service.py (Enhanced Version)
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

class FinancialDataParser:
    """Parser untuk mengekstrak data keuangan dari pesan chat"""
    
    def __init__(self):
        # Keywords untuk mengidentifikasi tipe transaksi
        self.income_keywords = [
            'gaji', 'pendapatan', 'pemasukan', 'terima', 'bonus', 'komisi',
            'freelance', 'usaha', 'bisnis', 'investasi', 'bunga', 'dividen',
            'hadiah', 'dapat', 'penghasilan', 'income'
        ]
        
        self.expense_keywords = [
            'bayar', 'beli', 'belanja', 'buat', 'pengeluaran', 'keluar',
            'spend', 'biaya', 'ongkos', 'cicilan', 'tagihan', 'hutang',
            'kredit', 'pinjam', 'transfer', 'kirim', 'expense'
        ]
        
        self.savings_keywords = [
            'nabung', 'tabung', 'target', 'ingin beli', 'mau beli', 'pengen beli',
            'saving', 'goal', 'impian', 'rencana beli', 'kepengen'
        ]
        
        # Pattern untuk mendeteksi jumlah uang
        self.money_patterns = [
            r'(?:rp\.?\s*)?(\d{1,3}(?:\.\d{3})*(?:\,\d{1,2})?)\s*(?:ribu|rb)',  # 500 ribu
            r'(?:rp\.?\s*)?(\d{1,3}(?:\.\d{3})*(?:\,\d{1,2})?)\s*(?:juta|jt)',  # 5 juta
            r'(?:rp\.?\s*)?(\d{1,3}(?:\.\d{3})*(?:\,\d{1,2})?)\s*(?:miliar|m)', # 1 miliar
            r'(?:rp\.?\s*)?(\d{1,3}(?:\.\d{3})*(?:\,\d{1,2})?)',  # angka biasa
        ]
        
        # Categories default
        self.default_income_categories = [
            'gaji', 'freelance', 'bisnis', 'investasi', 'bonus', 'lainnya'
        ]
        
        self.default_expense_categories = [
            'makanan', 'transportasi', 'belanja', 'hiburan', 'kesehatan',
            'pendidikan', 'tagihan', 'rumah tangga', 'lainnya'
        ]
    
    def parse_amount(self, text: str) -> Optional[float]:
        """Parse jumlah uang dari teks"""
        text_lower = text.lower()
        
        for pattern in self.money_patterns:
            match = re.search(pattern, text_lower)
            if match:
                amount_str = match.group(1).replace('.', '').replace(',', '.')
                try:
                    amount = float(amount_str)
                    
                    # Apply multiplier based on unit
                    if 'ribu' in text_lower or 'rb' in text_lower:
                        amount *= 1000
                    elif 'juta' in text_lower or 'jt' in text_lower:
                        amount *= 1000000
                    elif 'miliar' in text_lower or 'm' in text_lower:
                        amount *= 1000000000
                    
                    return amount
                except ValueError:
                    continue
        
        return None
    
    def detect_transaction_type(self, text: str) -> Optional[str]:
        """Deteksi tipe transaksi dari teks"""
        text_lower = text.lower()
        
        # Check for savings goal keywords first
        if any(keyword in text_lower for keyword in self.savings_keywords):
            return "savings_goal"
        
        # Check for income
        income_score = sum(1 for keyword in self.income_keywords if keyword in text_lower)
        
        # Check for expense
        expense_score = sum(1 for keyword in self.expense_keywords if keyword in text_lower)
        
        if income_score > expense_score:
            return "income"
        elif expense_score > income_score:
            return "expense"
        
        return None
    
    def extract_category(self, text: str, transaction_type: str) -> str:
        """Ekstrak kategori dari teks"""
        text_lower = text.lower()
        
        if transaction_type == "income":
            categories = self.default_income_categories
        else:
            categories = self.default_expense_categories
        
        # Simple keyword matching untuk kategori
        category_matches = {}
        for category in categories:
            if category in text_lower:
                category_matches[category] = text_lower.count(category)
        
        if category_matches:
            return max(category_matches, key=category_matches.get)
        
        return "lainnya"
    
    def extract_description(self, text: str, amount: float) -> str:
        """Ekstrak deskripsi dari teks"""
        # Remove amount patterns from text for cleaner description
        clean_text = text
        for pattern in self.money_patterns:
            clean_text = re.sub(pattern, '', clean_text, flags=re.IGNORECASE)
        
        # Clean up and return first part as description
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        return clean_text[:100] if clean_text else "Transaksi melalui chat"
    
    def parse_financial_data(self, text: str) -> Dict[str, Any]:
        """Parse data keuangan dari teks chat"""
        result = {
            "is_financial_data": False,
            "confidence": 0.0,
            "data_type": None,
            "parsed_data": None,
            "suggestions": [],
            "validation_errors": []
        }
        
        # Detect amount first
        amount = self.parse_amount(text)
        if not amount:
            return result
        
        # Detect transaction type
        data_type = self.detect_transaction_type(text)
        if not data_type:
            return result
        
        result["is_financial_data"] = True
        result["data_type"] = data_type
        
        if data_type in ["income", "expense"]:
            category = self.extract_category(text, data_type)
            description = self.extract_description(text, amount)
            
            result["parsed_data"] = {
                "type": data_type,
                "amount": amount,
                "category": category,
                "description": description,
                "date": now_for_db()
            }
            result["confidence"] = 0.8
            
        elif data_type == "savings_goal":
            # Extract item name from text
            item_name = self.extract_description(text, amount)
            if "target" in text.lower() or "nabung" in text.lower():
                item_name = item_name.replace("target", "").replace("nabung", "").strip()
            
            result["parsed_data"] = {
                "item_name": item_name or "Target tabungan",
                "target_amount": amount,
                "description": f"Target tabungan melalui chat: {text[:100]}"
            }
            result["confidence"] = 0.7
        
        return result

class FinanceService:
    """Service untuk mengelola data keuangan dengan integrasi User Financial Settings"""
    
    def __init__(self):
        self.db = get_database()
        self.parser = FinancialDataParser()
    
    # === User Financial Settings Integration ===
    
    async def sync_user_financial_settings(self, user_id: str) -> Dict[str, Any]:
        """Sinkronisasi financial settings user dengan data aktual"""
        # Calculate actual current savings from all active savings goals
        total_current_savings = await self._calculate_total_current_savings(user_id)
        
        # Get user's monthly target achievement this month
        monthly_progress = await self._calculate_monthly_savings_progress(user_id)
        
        # Update user financial settings
        update_data = {
            "financial_settings.current_savings": total_current_savings,
            "updated_at": now_for_db()
        }
        
        result = self.db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        
        return {
            "success": result.modified_count > 0,
            "total_current_savings": total_current_savings,
            "monthly_progress": monthly_progress,
            "updated": result.modified_count > 0
        }
    
    async def _calculate_total_current_savings(self, user_id: str) -> float:
        """Hitung total tabungan aktual dari semua savings goals"""
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
        """Hitung progress tabungan bulanan"""
        now = IndonesiaDatetime.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_of_month_utc = IndonesiaDatetime.to_utc(start_of_month).replace(tzinfo=None)
        
        # Get user's monthly target
        user_doc = self.db.users.find_one({"_id": ObjectId(user_id)})
        if not user_doc or not user_doc.get("financial_settings"):
            return {"monthly_target": 0, "achieved_this_month": 0, "progress_percentage": 0}
        
        monthly_target = user_doc["financial_settings"].get("monthly_savings_target", 0)
        
        # Calculate savings added this month (income - expense)
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
        income_this_month = 0
        expense_this_month = 0
        
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
            "remaining_to_target": max(monthly_target - net_savings_this_month, 0)
        }
    
    async def create_monthly_savings_goal(self, user_id: str) -> Optional[SavingsGoal]:
        """Buat atau update target tabungan bulanan otomatis"""
        user_doc = self.db.users.find_one({"_id": ObjectId(user_id)})
        if not user_doc or not user_doc.get("financial_settings"):
            return None
        
        financial_settings = user_doc["financial_settings"]
        monthly_target = financial_settings.get("monthly_savings_target")
        
        if not monthly_target or monthly_target <= 0:
            return None
        
        now = IndonesiaDatetime.now()
        month_year = now.strftime("%B %Y")
        goal_name = f"Target Tabungan {month_year}"
        
        # Check if goal for this month already exists
        existing_goal = self.db.savings_goals.find_one({
            "user_id": user_id,
            "item_name": goal_name,
            "source": "auto_monthly"
        })
        
        if existing_goal:
            return SavingsGoal.from_mongo(existing_goal)
        
        # Create new monthly goal
        goal_data = {
            "item_name": goal_name,
            "target_amount": monthly_target,
            "description": f"Target tabungan bulanan untuk {month_year}",
            "monthly_target": monthly_target,
            "target_date": now.replace(day=28) + timedelta(days=4)  # End of month
        }
        
        return await self.create_savings_goal(
            user_id,
            goal_data,
            {"source": "auto_monthly"}
        )
    
    # === Enhanced Transaction Management ===
    
    async def create_transaction(self, user_id: str, transaction_data: Dict[str, Any], 
                               chat_context: Dict[str, Any] = None) -> Transaction:
        """Membuat transaksi baru dengan auto-sync financial settings"""
        now = now_for_db()
        
        # Prepare transaction data
        trans_data = {
            "user_id": user_id,
            "type": transaction_data["type"],
            "amount": transaction_data["amount"],
            "category": transaction_data["category"],
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
        """Konfirmasi transaksi dengan auto-sync financial settings"""
        result = self.db.transactions.update_one(
            {"_id": ObjectId(transaction_id), "user_id": user_id},
            {"$set": {
                "status": TransactionStatus.CONFIRMED.value,
                "confirmed_at": now_for_db(),
                "updated_at": now_for_db()
            }}
        )
        
        # Sync financial settings after transaction confirmation
        if result.modified_count > 0:
            await self.sync_user_financial_settings(user_id)
        
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
    
    # === Enhanced Savings Goal Management ===
    
    async def create_savings_goal(self, user_id: str, goal_data: Dict[str, Any],
                                chat_context: Dict[str, Any] = None) -> SavingsGoal:
        """Membuat target tabungan baru dengan auto-sync financial settings"""
        now = now_for_db()
        
        # Prepare goal data
        goal_data_prepared = {
            "user_id": user_id,
            "item_name": goal_data["item_name"],
            "target_amount": goal_data["target_amount"],
            "current_amount": 0.0,
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
        
        # Sync financial settings after creating goal
        await self.sync_user_financial_settings(user_id)
        
        # Return goal object
        goal_data_prepared["_id"] = goal_id
        return SavingsGoal.from_mongo(goal_data_prepared)
    
    async def add_savings_to_goal(self, goal_id: str, user_id: str, amount: float) -> bool:
        """Menambah tabungan ke target dengan auto-sync financial settings"""
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
        
        # Sync financial settings after updating savings
        if result.modified_count > 0:
            await self.sync_user_financial_settings(user_id)
        
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
    
    # === Financial Dashboard & Analytics ===
    
    async def get_financial_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Mendapatkan data dashboard keuangan lengkap"""
        # Get user financial settings
        user_doc = self.db.users.find_one({"_id": ObjectId(user_id)})
        financial_settings = user_doc.get("financial_settings", {}) if user_doc else {}
        
        # Get monthly progress
        monthly_progress = await self._calculate_monthly_savings_progress(user_id)
        
        # Get current savings total
        total_current_savings = await self._calculate_total_current_savings(user_id)
        
        # Get active goals summary
        active_goals = await self.get_user_savings_goals(user_id, "active")
        
        # Get recent transactions
        recent_transactions = await self.get_user_transactions(user_id, {"status": "confirmed"}, 5, 0)
        
        # Get monthly summary
        monthly_summary = await self.get_financial_summary(user_id, "monthly")
        
        return {
            "user_financial_settings": {
                "current_savings": financial_settings.get("current_savings", 0),
                "monthly_savings_target": financial_settings.get("monthly_savings_target", 0),
                "primary_bank": financial_settings.get("primary_bank", "")
            },
            "calculated_totals": {
                "actual_current_savings": total_current_savings,
                "savings_difference": total_current_savings - financial_settings.get("current_savings", 0)
            },
            "monthly_progress": monthly_progress,
            "active_goals": {
                "count": len(active_goals),
                "goals": [goal.dict() for goal in active_goals[:3]],  # Top 3 goals
                "total_target": sum(goal.target_amount for goal in active_goals),
                "total_current": sum(goal.current_amount for goal in active_goals)
            },
            "recent_activity": {
                "transactions": [trans.dict() for trans in recent_transactions],
                "monthly_summary": monthly_summary.dict()
            },
            "sync_status": {
                "last_synced": now_for_db(),
                "needs_sync": abs(total_current_savings - financial_settings.get("current_savings", 0)) > 1000
            }
        }
    
    # === Pending Data Management ===
    
    async def create_pending_financial_data(self, user_id: str, conversation_id: str,
                                          message_id: str, parsed_data: Dict[str, Any],
                                          original_message: str, luna_response: str) -> PendingFinancialData:
        """Membuat data keuangan yang menunggu konfirmasi"""
        now = now_for_db()
        expires_at = now + timedelta(hours=24)  # Expired dalam 24 jam
        
        pending_data = {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "chat_message_id": message_id,
            "data_type": parsed_data["data_type"],
            "parsed_data": parsed_data["parsed_data"],
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
    
    async def confirm_pending_data(self, pending_id: str, user_id: str, 
                                 confirmed: bool, modifications: Dict[str, Any] = None) -> Dict[str, Any]:
        """Konfirmasi atau batalkan data keuangan yang pending"""
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
            
            # Save to appropriate collection
            if pending.data_type == "transaction":
                transaction = await self.create_transaction(
                    user_id, 
                    data_to_save,
                    {
                        "source": "chat",
                        "message_id": pending.chat_message_id,
                        "conversation_id": pending.conversation_id
                    }
                )
                # Auto-confirm transaction from chat
                await self.confirm_transaction(transaction.id, user_id)
                created_object = transaction
                
            elif pending.data_type == "savings_goal":
                goal = await self.create_savings_goal(
                    user_id,
                    data_to_save,
                    {
                        "source": "chat",
                        "message_id": pending.chat_message_id,
                        "conversation_id": pending.conversation_id
                    }
                )
                created_object = goal
            
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
                "data": created_object
            }
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