# app/services/finance_service.py - FIXED missing imports dan error handling
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from bson import ObjectId
import traceback

from ..config.database import get_database
from ..models.finance import (
    Transaction, SavingsGoal, FinancialSummary, PendingFinancialData,
    TransactionType, TransactionStatus, SavingsGoalStatus
)
from ..models.user import User, FinancialSettings
from ..utils.timezone_utils import IndonesiaDatetime, now_for_db

# FIXED: Import yang hilang
try:
    from .enhanced_financial_parser import EnhancedFinancialParser
except ImportError:
    print("⚠️ Warning: EnhancedFinancialParser not found, using fallback")
    EnhancedFinancialParser = None

try:
    from .financial_categories import IndonesianStudentCategories
except ImportError:
    print("⚠️ Warning: IndonesianStudentCategories not found, using fallback")
    IndonesianStudentCategories = None

class FinanceService:
    """Enhanced Finance Service dengan metode 50/30/20 untuk mahasiswa Indonesia"""
    
    def __init__(self):
        self.db = get_database()
        
        # Initialize parser with fallback
        if EnhancedFinancialParser:
            self.parser = EnhancedFinancialParser()
        else:
            self.parser = None
            print("⚠️ Using fallback parser")
    
    # === ENHANCED: 50/30/20 Budget Integration ===
    
    async def get_current_month_spending_by_budget_type(self, user_id: str) -> Dict[str, float]:
        """
        Hitung pengeluaran bulan ini berdasarkan budget type (needs/wants/savings)
        untuk tracking budget 50/30/20 - FIXED with better error handling
        """
        try:
            # Get start of current month
            now = IndonesiaDatetime.now()
            start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            start_of_month_utc = IndonesiaDatetime.to_utc(start_of_month).replace(tzinfo=None)
            
            # Get all confirmed transactions this month
            transactions = self.db.transactions.find({
                "user_id": user_id,
                "status": TransactionStatus.CONFIRMED.value,
                "date": {"$gte": start_of_month_utc},
                "type": TransactionType.EXPENSE.value  # Only expenses for budget tracking
            })
            
            spending_by_type = {
                "needs": 0.0,
                "wants": 0.0, 
                "savings": 0.0,
                "unknown": 0.0
            }
            
            for trans in transactions:
                try:
                    category = trans.get("category", "")
                    amount = trans.get("amount", 0.0)
                    
                    # Determine budget type from category with fallback
                    budget_type = self._get_budget_type_fallback(category)
                    
                    if budget_type in spending_by_type:
                        spending_by_type[budget_type] += amount
                    else:
                        spending_by_type["unknown"] += amount
                except Exception as e:
                    print(f"Error processing transaction: {e}")
                    continue
            
            return spending_by_type
            
        except Exception as e:
            print(f"Error calculating current month spending by budget type: {e}")
            traceback.print_exc()
            return {"needs": 0.0, "wants": 0.0, "savings": 0.0, "unknown": 0.0}
    
    def _get_budget_type_fallback(self, category: str) -> str:
        """Fallback method untuk kategori budget type jika IndonesianStudentCategories tidak tersedia"""
        try:
            if IndonesianStudentCategories:
                return IndonesianStudentCategories.get_budget_type(category)
            else:
                # Simple fallback categorization
                category_lower = category.lower()
                
                # NEEDS keywords
                needs_keywords = ['makan', 'makanan', 'kos', 'sewa', 'transport', 'transportasi', 
                                'pendidikan', 'buku', 'kuliah', 'kampus', 'listrik', 'air', 
                                'internet', 'pulsa', 'kesehatan', 'obat']
                for keyword in needs_keywords:
                    if keyword in category_lower:
                        return "needs"
                
                # SAVINGS keywords
                savings_keywords = ['tabungan', 'saving', 'investasi', 'deposito', 'darurat', 
                                  'masa depan', 'reksadana', 'saham']
                for keyword in savings_keywords:
                    if keyword in category_lower:
                        return "savings"
                
                # Default to wants
                return "wants"
        except Exception as e:
            print(f"Error in _get_budget_type_fallback: {e}")
            return "wants"
    
    def _get_expense_category_fallback(self, text: str) -> str:
        """Fallback method untuk kategori expense jika IndonesianStudentCategories tidak tersedia"""
        try:
            if IndonesianStudentCategories:
                return IndonesianStudentCategories.get_expense_category(text)
            else:
                # Simple fallback categorization
                text_lower = text.lower()
                
                if any(word in text_lower for word in ['makan', 'makanan', 'nasi', 'lauk']):
                    return "Makanan Pokok"
                elif any(word in text_lower for word in ['kos', 'sewa', 'kamar']):
                    return "Kos/Tempat Tinggal"
                elif any(word in text_lower for word in ['transport', 'angkot', 'bus', 'ojol']):
                    return "Transportasi Wajib"
                elif any(word in text_lower for word in ['buku', 'kuliah', 'kampus', 'tugas']):
                    return "Pendidikan"
                elif any(word in text_lower for word in ['jajan', 'snack', 'cafe', 'kopi']):
                    return "Jajan & Snack"
                elif any(word in text_lower for word in ['tabungan', 'saving', 'nabung']):
                    return "Tabungan Umum"
                else:
                    return "Lainnya (Wants)"
        except Exception as e:
            print(f"Error in _get_expense_category_fallback: {e}")
            return "Lainnya (Wants)"
    
    def _get_income_category_fallback(self, text: str) -> str:
        """Fallback method untuk kategori income jika IndonesianStudentCategories tidak tersedia"""
        try:
            if IndonesianStudentCategories:
                return IndonesianStudentCategories.get_income_category(text)
            else:
                # Simple fallback categorization
                text_lower = text.lower()
                
                if any(word in text_lower for word in ['uang saku', 'kiriman', 'ortu', 'orang tua']):
                    return "Uang Saku/Kiriman Ortu"
                elif any(word in text_lower for word in ['part time', 'kerja', 'jual']):
                    return "Part-time Job"
                elif any(word in text_lower for word in ['freelance', 'project', 'tugas']):
                    return "Freelance/Project"
                elif any(word in text_lower for word in ['beasiswa', 'bidikmisi', 'bantuan']):
                    return "Beasiswa"
                elif any(word in text_lower for word in ['hadiah', 'bonus', 'kado']):
                    return "Hadiah/Bonus"
                else:
                    return "Lainnya"
        except Exception as e:
            print(f"Error in _get_income_category_fallback: {e}")
            return "Lainnya"
    
    async def get_monthly_budget_performance(self, user_id: str) -> Dict[str, Any]:
        """
        Analisis performa budget 50/30/20 untuk bulan ini - FIXED with better error handling
        """
        try:
            # Get user's budget allocation
            user_doc = self.db.users.find_one({"_id": ObjectId(user_id)})
            if not user_doc or not user_doc.get("financial_settings"):
                return {
                    "has_budget": False,
                    "message": "Budget 50/30/20 belum di-setup"
                }
            
            financial_settings = user_doc["financial_settings"]
            monthly_income = financial_settings.get("monthly_income", 0)
            
            if monthly_income <= 0:
                return {
                    "has_budget": False,
                    "message": "Monthly income belum di-set"
                }
            
            # Calculate budget allocation
            needs_budget = monthly_income * 0.50
            wants_budget = monthly_income * 0.30
            savings_budget = monthly_income * 0.20
            
            # Get actual spending this month
            actual_spending = await self.get_current_month_spending_by_budget_type(user_id)
            
            # Calculate performance metrics
            performance = {
                "needs": {
                    "budget": needs_budget,
                    "spent": actual_spending.get("needs", 0),
                    "remaining": max(needs_budget - actual_spending.get("needs", 0), 0),
                    "percentage_used": (actual_spending.get("needs", 0) / needs_budget * 100) if needs_budget > 0 else 0,
                    "status": "over" if actual_spending.get("needs", 0) > needs_budget else "under"
                },
                "wants": {
                    "budget": wants_budget,
                    "spent": actual_spending.get("wants", 0),
                    "remaining": max(wants_budget - actual_spending.get("wants", 0), 0),
                    "percentage_used": (actual_spending.get("wants", 0) / wants_budget * 100) if wants_budget > 0 else 0,
                    "status": "over" if actual_spending.get("wants", 0) > wants_budget else "under"
                },
                "savings": {
                    "budget": savings_budget,
                    "spent": actual_spending.get("savings", 0),
                    "remaining": max(savings_budget - actual_spending.get("savings", 0), 0),
                    "percentage_used": (actual_spending.get("savings", 0) / savings_budget * 100) if savings_budget > 0 else 0,
                    "status": "over" if actual_spending.get("savings", 0) > savings_budget else "under"
                }
            }
            
            # Overall budget health assessment
            total_budget = monthly_income
            total_spent = sum(actual_spending.values())
            overall_percentage = (total_spent / total_budget * 100) if total_budget > 0 else 0
            
            if overall_percentage <= 70:
                budget_health = "excellent"
            elif overall_percentage <= 90:
                budget_health = "good"
            elif overall_percentage <= 100:
                budget_health = "warning"
            else:
                budget_health = "over_budget"
            
            return {
                "has_budget": True,
                "method": "50/30/20 Elizabeth Warren",
                "period": datetime.now().strftime("%B %Y"),
                "monthly_income": monthly_income,
                "budget_allocation": {
                    "needs_budget": needs_budget,
                    "wants_budget": wants_budget, 
                    "savings_budget": savings_budget
                },
                "performance": performance,
                "overall": {
                    "total_budget": total_budget,
                    "total_spent": total_spent,
                    "total_remaining": max(total_budget - total_spent, 0),
                    "percentage_used": overall_percentage,
                    "budget_health": budget_health
                }
            }
            
        except Exception as e:
            print(f"Error getting monthly budget performance: {e}")
            traceback.print_exc()
            return {
                "has_budget": False,
                "error": str(e)
            }
    
    async def _calculate_real_total_savings(self, user_id: str) -> float:
        """
        Hitung total tabungan real-time - FIXED with better error handling
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
            traceback.print_exc()
            return 0.0
    
    # === ENHANCED Transaction Management ===
    
    async def create_transaction(self, user_id: str, transaction_data: Dict[str, Any], 
                               chat_context: Dict[str, Any] = None) -> Transaction:
        """Membuat transaksi baru - FIXED with better error handling"""
        try:
            now = now_for_db()
            
            # Enhanced category detection
            category = transaction_data.get("category")
            
            if not category or category == "lainnya":
                if transaction_data["type"] == "income":
                    category = self._get_income_category_fallback(
                        transaction_data.get("description", "")
                    )
                else:
                    category = self._get_expense_category_fallback(
                        transaction_data.get("description", "")
                    )
            
            # Prepare transaction data
            trans_data = {
                "user_id": user_id,
                "type": transaction_data["type"],
                "amount": transaction_data["amount"],
                "category": category,
                "description": transaction_data.get("description", ""),
                "date": transaction_data.get("date", now),
                "status": TransactionStatus.PENDING.value,
                "source": chat_context.get("source", "manual") if chat_context else "manual",
                "tags": transaction_data.get("tags", []),
                "notes": transaction_data.get("notes"),
                "created_at": now,
                "updated_at": now
            }
            
            # Add budget type for expenses
            if transaction_data["type"] == "expense":
                trans_data["budget_type"] = self._get_budget_type_fallback(category)
            
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
            
        except Exception as e:
            print(f"Error creating transaction: {e}")
            traceback.print_exc()
            raise
    
    async def confirm_transaction(self, transaction_id: str, user_id: str) -> bool:
        """Konfirmasi transaksi - FIXED with better error handling"""
        try:
            result = self.db.transactions.update_one(
                {"_id": ObjectId(transaction_id), "user_id": user_id},
                {"$set": {
                    "status": TransactionStatus.CONFIRMED.value,
                    "confirmed_at": now_for_db(),
                    "updated_at": now_for_db()
                }}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"Error confirming transaction: {e}")
            traceback.print_exc()
            return False
    
    async def get_user_transactions(self, user_id: str, filters: Dict[str, Any] = None,
                                  limit: int = 50, offset: int = 0) -> List[Transaction]:
        """Mengambil transaksi user - FIXED with better error handling"""
        try:
            query = {"user_id": user_id}
            
            if filters:
                if filters.get("type"):
                    query["type"] = filters["type"]
                if filters.get("category"):
                    query["category"] = filters["category"]
                if filters.get("budget_type"):
                    query["budget_type"] = filters["budget_type"]
                if filters.get("status"):
                    query["status"] = filters["status"]
                if filters.get("date"):
                    query["date"] = filters["date"]
            
            cursor = self.db.transactions.find(query).sort("date", -1).skip(offset).limit(limit)
            
            transactions = []
            for doc in cursor:
                try:
                    transactions.append(Transaction.from_mongo(doc))
                except Exception as e:
                    print(f"Error converting transaction: {e}")
                    continue
            
            return transactions
            
        except Exception as e:
            print(f"Error getting user transactions: {e}")
            traceback.print_exc()
            return []
    
    # === ENHANCED Savings Goal Management ===
    
    async def create_savings_goal_from_wants_budget(self, user_id: str, goal_data: Dict[str, Any],
                                                  chat_context: Dict[str, Any] = None) -> SavingsGoal:
        """Membuat target tabungan baru - FIXED with better error handling"""
        try:
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
                "budget_source": "wants",
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
            
        except Exception as e:
            print(f"Error creating savings goal: {e}")
            traceback.print_exc()
            raise
    
    async def get_user_savings_goals(self, user_id: str, status: str = None) -> List[SavingsGoal]:
        """Mengambil target tabungan user - FIXED with better error handling"""
        try:
            query = {"user_id": user_id}
            if status:
                query["status"] = status
            
            cursor = self.db.savings_goals.find(query).sort("created_at", -1)
            
            goals = []
            for doc in cursor:
                try:
                    goals.append(SavingsGoal.from_mongo(doc))
                except Exception as e:
                    print(f"Error converting savings goal: {e}")
                    continue
            
            return goals
            
        except Exception as e:
            print(f"Error getting user savings goals: {e}")
            traceback.print_exc()
            return []
    
    # === ENHANCED Financial Dashboard ===
    
    async def get_financial_dashboard_50_30_20(self, user_id: str) -> Dict[str, Any]:
        """Mendapatkan dashboard keuangan - FIXED with better error handling"""
        try:
            # Get user financial settings
            user_doc = self.db.users.find_one({"_id": ObjectId(user_id)})
            financial_settings = user_doc.get("financial_settings", {}) if user_doc else {}
            
            if not financial_settings.get("monthly_income"):
                return {
                    "error": "Monthly income belum di-set untuk budget 50/30/20"
                }
            
            # Get budget performance
            budget_performance = await self.get_monthly_budget_performance(user_id)
            
            # Get real total savings
            real_total_savings = await self._calculate_real_total_savings(user_id)
            
            # Get savings goals
            wants_based_goals = await self.get_user_savings_goals(user_id, "active")
            
            # Get recent transactions
            recent_transactions = await self.get_user_transactions(
                user_id, {"status": "confirmed"}, 10, 0
            )
            
            recent_with_budget_type = []
            for trans in recent_transactions:
                try:
                    trans_dict = trans.dict()
                    if trans.type == "expense":
                        trans_dict["budget_type"] = self._get_budget_type_fallback(trans.category)
                    recent_with_budget_type.append(trans_dict)
                except Exception as e:
                    print(f"Error processing recent transaction: {e}")
                    continue
            
            return {
                "method": "50/30/20 Elizabeth Warren",
                "user_financial_settings": {
                    "monthly_income": financial_settings.get("monthly_income", 0),
                    "initial_savings": financial_settings.get("current_savings", 0),
                    "primary_bank": financial_settings.get("primary_bank", ""),
                },
                "budget_performance": budget_performance,
                "real_total_savings": real_total_savings,
                "wants_budget_goals": {
                    "total_goals": len(wants_based_goals),
                    "goals": wants_based_goals[:5],
                    "total_allocated": sum(goal.current_amount for goal in wants_based_goals),
                    "total_target": sum(goal.target_amount for goal in wants_based_goals)
                },
                "recent_activity": {
                    "transactions": recent_with_budget_type,
                    "transaction_count": len(recent_transactions)
                }
            }
            
        except Exception as e:
            print(f"Error getting financial dashboard 50/30/20: {e}")
            traceback.print_exc()
            return {
                "error": f"Gagal mengambil dashboard: {str(e)}",
                "method": "50/30/20 Elizabeth Warren"
            }
    
    # === Financial Summary ===
    
    async def get_financial_summary(self, user_id: str, period: str = "monthly",
                                  start_date: datetime = None, end_date: datetime = None) -> FinancialSummary:
        """Generate ringkasan keuangan - FIXED with better error handling"""
        try:
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
                try:
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
                except Exception as e:
                    print(f"Error processing transaction in summary: {e}")
                    continue
            
            # Get savings goals summary
            active_goals = 0
            total_savings_target = 0.0
            total_savings_current = 0.0
            
            try:
                active_goals = self.db.savings_goals.count_documents({
                    "user_id": user_id,
                    "status": SavingsGoalStatus.ACTIVE.value
                })
                
                goals_cursor = self.db.savings_goals.find({
                    "user_id": user_id,
                    "status": {"$ne": SavingsGoalStatus.CANCELLED.value}
                })
                
                for goal in goals_cursor:
                    total_savings_target += goal.get("target_amount", 0)
                    total_savings_current += goal.get("current_amount", 0)
                    
            except Exception as e:
                print(f"Error getting savings goals summary: {e}")
            
            # Create summary object
            summary = FinancialSummary(
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
            
            return summary
            
        except Exception as e:
            print(f"Error getting financial summary: {e}")
            traceback.print_exc()
            raise
    
    # === Chat Integration ===
    
    def parse_financial_message(self, message: str) -> Dict[str, Any]:
        """Parse pesan chat - FIXED with fallback"""
        try:
            if self.parser:
                result = self.parser.parse_financial_data(message)
                
                # Enhance result dengan budget type info
                if result.get("is_financial_data") and result.get("parsed_data"):
                    if result["data_type"] in ["expense"]:
                        category = result["parsed_data"]["category"]
                        budget_type = self._get_budget_type_fallback(category)
                        result["parsed_data"]["budget_type"] = budget_type
                        result["budget_guidance"] = {
                            "needs": "50% budget - Kebutuhan pokok yang wajib",
                            "wants": "30% budget - Keinginan dan target tabungan barang",
                            "savings": "20% budget - Tabungan masa depan"
                        }.get(budget_type, "Kategori tidak dikenali")
                
                return result
            else:
                # Fallback parsing
                return {
                    "is_financial_data": False,
                    "message": "Parser tidak tersedia"
                }
                
        except Exception as e:
            print(f"Error parsing financial message: {e}")
            return {
                "is_financial_data": False,
                "error": str(e)
            }
    
    # === Data Confirmation ===
    
    def confirm_pending_data(self, pending_id: str, user_id: str, 
                           confirmed: bool, modifications: Dict[str, Any] = None) -> Dict[str, Any]:
        """Konfirmasi data pending - FIXED with better error handling"""
        try:
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
                        # Create transaction
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
                        
                        now = now_for_db()
                        
                        # Enhanced category detection
                        category = transaction_data.get("category")
                        budget_type = None
                        
                        if not category or category == "lainnya":
                            if transaction_data["type"] == "income":
                                category = self._get_income_category_fallback(
                                    transaction_data.get("description", "")
                                )
                            else:
                                category = self._get_expense_category_fallback(
                                    transaction_data.get("description", "")
                                )
                        
                        budget_type = self._get_budget_type_fallback(category)
                        
                        # Prepare transaction data for database
                        trans_data = {
                            "user_id": user_id,
                            "type": transaction_data["type"],
                            "amount": transaction_data["amount"],
                            "category": category,
                            "description": transaction_data["description"],
                            "date": transaction_data["date"],
                            "status": "confirmed",
                            "source": "chat",
                            "tags": [],
                            "notes": "Dibuat melalui chat Luna AI",
                            "chat_message_id": pending.chat_message_id,
                            "conversation_id": pending.conversation_id,
                            "created_at": now,
                            "updated_at": now,
                            "confirmed_at": now
                        }
                        
                        # Add budget type for expenses
                        if transaction_data["type"] == "expense":
                            trans_data["budget_type"] = budget_type
                        
                        # Insert to database
                        result = self.db.transactions.insert_one(trans_data)
                        transaction_id = str(result.inserted_id)
                        
                        created_object = {
                            "id": transaction_id,
                            "type": trans_data["type"],
                            "amount": trans_data["amount"],
                            "category": trans_data["category"],
                            "description": trans_data["description"],
                            "date": trans_data["date"],
                            "status": trans_data["status"],
                            "budget_type": trans_data.get("budget_type")
                        }
                        
                    elif pending.data_type == "savings_goal":
                        # Create savings goal
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
                            "budget_source": "wants",
                            "chat_message_id": pending.chat_message_id,
                            "conversation_id": pending.conversation_id,
                            "created_at": now,
                            "updated_at": now
                        }
                        
                        # Insert to database
                        result = self.db.savings_goals.insert_one(goal_data_prepared)
                        goal_id = str(result.inserted_id)
                        
                        created_object = {
                            "id": goal_id,
                            "item_name": goal_data_prepared["item_name"],
                            "target_amount": goal_data_prepared["target_amount"],
                            "current_amount": goal_data_prepared["current_amount"],
                            "target_date": goal_data_prepared["target_date"],
                            "status": goal_data_prepared["status"],
                            "budget_source": "wants"
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
                    traceback.print_exc()
                    return {"success": False, "message": f"Gagal menyimpan data: {str(e)}"}
            else:
                # Mark as cancelled (delete)
                self.db.pending_financial_data.delete_one({"_id": ObjectId(pending_id)})
                return {"success": True, "message": "Data dibatalkan"}
                
        except Exception as e:
            print(f"Error confirming pending data: {e}")
            traceback.print_exc()
            return {"success": False, "message": f"Gagal memproses data: {str(e)}"}
    
    async def get_user_pending_data(self, user_id: str) -> List[PendingFinancialData]:
        """Mengambil data pending user - FIXED with better error handling"""
        try:
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
                try:
                    pending_data.append(PendingFinancialData.from_mongo(doc))
                except Exception as e:
                    print(f"Error converting pending data: {e}")
                    continue
            
            return pending_data
            
        except Exception as e:
            print(f"Error getting user pending data: {e}")
            traceback.print_exc()
            return []