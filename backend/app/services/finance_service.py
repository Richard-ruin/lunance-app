# app/services/finance_service.py - COMPLETE Backend Finance Service (No Chatbot Dependencies)

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from bson import ObjectId
import statistics
from collections import defaultdict

from ..config.database import get_database
from ..models.finance import Transaction, SavingsGoal, TransactionType, TransactionStatus, SavingsGoalStatus
from ..models.user import User
from ..utils.timezone_utils import IndonesiaDatetime, now_for_db
from .financial_categories import IndonesianStudentCategories

logger = logging.getLogger(__name__)

class FinanceService:
    """Complete Finance Service for Finance Routes - NO Chatbot Dependencies"""
    
    def __init__(self):
        self.db = get_database()
        logger.info("✅ FinanceService initialized (Finance Routes Only)")
    
    def format_currency(self, amount: float) -> str:
        """Format currency to Rupiah"""
        return f"Rp {amount:,.0f}".replace(',', '.')
    
    # ==========================================
    # TRANSACTION METHODS
    # ==========================================
    
    async def create_transaction(self, user_id: str, transaction_data: Dict[str, Any]) -> Transaction:
        """Create new transaction"""
        try:
            now = now_for_db()
            
            # Create transaction document
            transaction_doc = {
                "user_id": user_id,
                "type": transaction_data["type"],
                "amount": transaction_data["amount"],
                "category": transaction_data["category"],
                "description": transaction_data.get("description", ""),
                "date": transaction_data.get("date", now),
                "status": TransactionStatus.CONFIRMED.value,
                "source": transaction_data.get("source", "manual"),
                "tags": transaction_data.get("tags", []),
                "notes": transaction_data.get("notes"),
                "created_at": now,
                "updated_at": now,
                "confirmed_at": now
            }
            
            result = self.db.transactions.insert_one(transaction_doc)
            transaction_id = str(result.inserted_id)
            
            # Create Transaction object
            transaction = Transaction(
                id=transaction_id,
                user_id=user_id,
                type=TransactionType(transaction_data["type"]),
                amount=transaction_data["amount"],
                category=transaction_data["category"],
                description=transaction_data.get("description", ""),
                date=transaction_data.get("date", now),
                status=TransactionStatus.CONFIRMED,
                source=transaction_data.get("source", "manual"),
                tags=transaction_data.get("tags", []),
                notes=transaction_data.get("notes"),
                created_at=now,
                updated_at=now,
                confirmed_at=now
            )
            
            logger.info(f"✅ Transaction created: {transaction_id}")
            return transaction
            
        except Exception as e:
            logger.error(f"❌ Error creating transaction: {e}")
            raise
    
    async def get_user_transactions(self, user_id: str, filters: Dict = None, 
                                   limit: int = 50, offset: int = 0) -> List[Transaction]:
        """Get user transactions with filters"""
        try:
            query = {"user_id": user_id}
            
            if filters:
                if "type" in filters:
                    query["type"] = filters["type"]
                if "category" in filters:
                    query["category"] = filters["category"]
                if "status" in filters:
                    query["status"] = filters["status"]
                if "date" in filters:
                    query["date"] = filters["date"]
                if "budget_type" in filters:
                    # Filter by budget type requires category lookup
                    budget_type_categories = self._get_categories_by_budget_type(filters["budget_type"])
                    query["category"] = {"$in": budget_type_categories}
            
            cursor = self.db.transactions.find(query).sort("date", -1).skip(offset).limit(limit)
            
            transactions = []
            for doc in cursor:
                transaction = Transaction.from_mongo(doc)
                transactions.append(transaction)
            
            logger.info(f"📋 Retrieved {len(transactions)} transactions")
            return transactions
            
        except Exception as e:
            logger.error(f"❌ Error getting user transactions: {e}")
            return []
    
    async def get_transaction_by_id(self, transaction_id: str, user_id: str) -> Optional[Transaction]:
        """Get transaction by ID"""
        try:
            doc = self.db.transactions.find_one({
                "_id": ObjectId(transaction_id),
                "user_id": user_id
            })
            
            if doc:
                return Transaction.from_mongo(doc)
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting transaction: {e}")
            return None
    
    async def update_transaction(self, transaction_id: str, user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update transaction"""
        try:
            update_data["updated_at"] = now_for_db()
            
            result = self.db.transactions.update_one(
                {"_id": ObjectId(transaction_id), "user_id": user_id},
                {"$set": update_data}
            )
            
            success = result.modified_count > 0
            if success:
                logger.info(f"✅ Transaction updated: {transaction_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error updating transaction: {e}")
            return False
    
    async def delete_transaction(self, transaction_id: str, user_id: str) -> bool:
        """Delete transaction"""
        try:
            result = self.db.transactions.delete_one({
                "_id": ObjectId(transaction_id),
                "user_id": user_id
            })
            
            success = result.deleted_count > 0
            if success:
                logger.info(f"✅ Transaction deleted: {transaction_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error deleting transaction: {e}")
            return False
    
    # ==========================================
    # SAVINGS GOALS METHODS
    # ==========================================
    
    async def create_savings_goal(self, user_id: str, goal_data: Dict[str, Any]) -> SavingsGoal:
        """Create new savings goal"""
        try:
            now = now_for_db()
            
            goal_doc = {
                "user_id": user_id,
                "item_name": goal_data["item_name"],
                "target_amount": goal_data["target_amount"],
                "current_amount": goal_data.get("current_amount", 0.0),
                "description": goal_data.get("description"),
                "target_date": goal_data.get("target_date"),
                "status": SavingsGoalStatus.ACTIVE.value,
                "monthly_target": goal_data.get("monthly_target"),
                "source": goal_data.get("source", "manual"),
                "tags": goal_data.get("tags", []),
                "notes": goal_data.get("notes"),
                "created_at": now,
                "updated_at": now
            }
            
            result = self.db.savings_goals.insert_one(goal_doc)
            goal_id = str(result.inserted_id)
            
            # Create SavingsGoal object
            goal = SavingsGoal(
                id=goal_id,
                user_id=user_id,
                item_name=goal_data["item_name"],
                target_amount=goal_data["target_amount"],
                current_amount=goal_data.get("current_amount", 0.0),
                description=goal_data.get("description"),
                target_date=goal_data.get("target_date"),
                status=SavingsGoalStatus.ACTIVE,
                monthly_target=goal_data.get("monthly_target"),
                source=goal_data.get("source", "manual"),
                tags=goal_data.get("tags", []),
                notes=goal_data.get("notes"),
                created_at=now,
                updated_at=now
            )
            
            logger.info(f"✅ Savings goal created: {goal_id}")
            return goal
            
        except Exception as e:
            logger.error(f"❌ Error creating savings goal: {e}")
            raise
    
    async def get_user_savings_goals(self, user_id: str, status: str = None) -> List[SavingsGoal]:
        """Get user savings goals"""
        try:
            query = {"user_id": user_id}
            
            if status:
                query["status"] = status
            else:
                query["status"] = {"$in": ["active", "paused", "completed"]}
            
            cursor = self.db.savings_goals.find(query).sort("created_at", -1)
            
            goals = []
            for doc in cursor:
                goal = SavingsGoal.from_mongo(doc)
                goals.append(goal)
            
            logger.info(f"🎯 Retrieved {len(goals)} savings goals")
            return goals
            
        except Exception as e:
            logger.error(f"❌ Error getting savings goals: {e}")
            return []
    
    async def get_savings_goal_by_id(self, goal_id: str, user_id: str) -> Optional[SavingsGoal]:
        """Get savings goal by ID"""
        try:
            doc = self.db.savings_goals.find_one({
                "_id": ObjectId(goal_id),
                "user_id": user_id
            })
            
            if doc:
                return SavingsGoal.from_mongo(doc)
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting savings goal: {e}")
            return None
    
    async def update_savings_goal(self, goal_id: str, user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update savings goal"""
        try:
            update_data["updated_at"] = now_for_db()
            
            result = self.db.savings_goals.update_one(
                {"_id": ObjectId(goal_id), "user_id": user_id},
                {"$set": update_data}
            )
            
            success = result.modified_count > 0
            if success:
                logger.info(f"✅ Savings goal updated: {goal_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error updating savings goal: {e}")
            return False
    
    async def delete_savings_goal(self, goal_id: str, user_id: str) -> bool:
        """Delete savings goal"""
        try:
            result = self.db.savings_goals.delete_one({
                "_id": ObjectId(goal_id),
                "user_id": user_id
            })
            
            success = result.deleted_count > 0
            if success:
                logger.info(f"✅ Savings goal deleted: {goal_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error deleting savings goal: {e}")
            return False
    
    async def add_savings_to_goal(self, goal_id: str, user_id: str, amount: float) -> bool:
        """Add savings to goal"""
        try:
            goal = await self.get_savings_goal_by_id(goal_id, user_id)
            if not goal:
                return False
            
            new_amount = goal.current_amount + amount
            status = goal.status
            
            # Check if goal completed
            if new_amount >= goal.target_amount and status == SavingsGoalStatus.ACTIVE:
                status = SavingsGoalStatus.COMPLETED
                completed_at = now_for_db()
                update_data = {
                    "current_amount": new_amount,
                    "status": status.value,
                    "completed_at": completed_at,
                    "updated_at": now_for_db()
                }
            else:
                update_data = {
                    "current_amount": new_amount,
                    "updated_at": now_for_db()
                }
            
            result = self.db.savings_goals.update_one(
                {"_id": ObjectId(goal_id), "user_id": user_id},
                {"$set": update_data}
            )
            
            success = result.modified_count > 0
            if success:
                logger.info(f"✅ Added {amount} to savings goal: {goal_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error adding savings to goal: {e}")
            return False
    
    # ==========================================
    # FINANCIAL ANALYTICS METHODS
    # ==========================================
    
    async def get_financial_summary(self, user_id: str, period: str = "monthly", 
                                   start_date: Optional[datetime] = None, 
                                   end_date: Optional[datetime] = None):
        """Get financial summary for a period"""
        try:
            # Set date range based on period
            if not start_date or not end_date:
                now = datetime.now()
                if period == "daily":
                    start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                    end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)
                elif period == "weekly":
                    start_date = now - timedelta(days=7)
                    end_date = now
                elif period == "monthly":
                    start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                    end_date = now
                elif period == "yearly":
                    start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
                    end_date = now
            
            # Query transactions
            query = {
                "user_id": user_id,
                "status": TransactionStatus.CONFIRMED.value,
                "date": {"$gte": start_date, "$lte": end_date}
            }
            
            transactions = list(self.db.transactions.find(query))
            
            # Calculate summary
            total_income = 0.0
            total_expense = 0.0
            income_count = 0
            expense_count = 0
            expense_categories = defaultdict(float)
            income_categories = defaultdict(float)
            
            for trans in transactions:
                amount = trans["amount"]
                category = trans["category"]
                trans_type = trans["type"]
                
                if trans_type == "income":
                    total_income += amount
                    income_count += 1
                    income_categories[category] += amount
                elif trans_type == "expense":
                    total_expense += amount
                    expense_count += 1
                    expense_categories[category] += amount
            
            # Create summary object
            class FinancialSummary:
                def __init__(self):
                    self.user_id = user_id
                    self.period = period
                    self.total_income = total_income
                    self.total_expense = total_expense
                    self.net_balance = total_income - total_expense
                    self.income_count = income_count
                    self.expense_count = expense_count
                    self.income_categories = dict(income_categories)
                    self.expense_categories = dict(expense_categories)
                    self.start_date = start_date
                    self.end_date = end_date
                    self.generated_at = now_for_db()
            
            summary = FinancialSummary()
            logger.info(f"📈 Financial summary generated for period: {period}")
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error generating financial summary: {e}")
            return None
    
    async def get_monthly_budget_performance(self, user_id: str) -> Dict[str, Any]:
        """Get 50/30/20 budget performance for current month"""
        try:
            # Get user's monthly income
            user_doc = self.db.users.find_one({"_id": ObjectId(user_id)})
            if not user_doc or not user_doc.get("financial_settings"):
                return {"has_budget": False, "error": "No financial settings found"}
            
            monthly_income = user_doc["financial_settings"].get("monthly_income", 0)
            if monthly_income <= 0:
                return {"has_budget": False, "error": "No monthly income set"}
            
            # Calculate budget allocations (50/30/20)
            needs_budget = monthly_income * 0.5
            wants_budget = monthly_income * 0.3
            savings_budget = monthly_income * 0.2
            
            # Get current month spending by budget type
            spending = await self.get_current_month_spending_by_budget_type(user_id)
            
            needs_spent = spending.get("needs", 0)
            wants_spent = spending.get("wants", 0)
            savings_spent = spending.get("savings", 0)
            
            # Calculate performance metrics
            def calculate_performance(budget: float, spent: float) -> Dict[str, Any]:
                remaining = budget - spent
                percentage_used = (spent / budget * 100) if budget > 0 else 0
                
                if percentage_used > 100:
                    status = "over_budget"
                elif percentage_used > 80:
                    status = "warning"
                elif percentage_used > 50:
                    status = "good"
                else:
                    status = "excellent"
                
                return {
                    "budget": budget,
                    "spent": spent,
                    "remaining": remaining,
                    "percentage_used": percentage_used,
                    "status": status,
                    "formatted_budget": self.format_currency(budget),
                    "formatted_spent": self.format_currency(spent),
                    "formatted_remaining": self.format_currency(remaining)
                }
            
            performance = {
                "needs": calculate_performance(needs_budget, needs_spent),
                "wants": calculate_performance(wants_budget, wants_spent),
                "savings": calculate_performance(savings_budget, savings_spent)
            }
            
            # Overall budget health
            total_spent = needs_spent + wants_spent + savings_spent
            total_budget = monthly_income
            overall_percentage = (total_spent / total_budget * 100) if total_budget > 0 else 0
            
            if overall_percentage > 100:
                budget_health = "critical"
            elif overall_percentage > 90:
                budget_health = "warning"
            elif overall_percentage > 70:
                budget_health = "good"
            else:
                budget_health = "excellent"
            
            # Generate recommendations
            recommendations = []
            if performance["needs"]["status"] == "over_budget":
                recommendations.append("⚠️ Pengeluaran NEEDS melebihi 50% - review kebutuhan pokok")
            if performance["wants"]["status"] == "over_budget":
                recommendations.append("🔍 Pengeluaran WANTS melebihi 30% - kurangi lifestyle spending")
            if performance["savings"]["percentage_used"] < 50:
                recommendations.append("📈 Peluang menabung lebih besar - tingkatkan savings")
            
            if not recommendations:
                recommendations.append("✅ Budget performance baik - pertahankan pola ini!")
            
            budget_data = {
                "has_budget": True,
                "method": "50/30/20 Elizabeth Warren",
                "base_income": monthly_income,
                "current_month": datetime.now().strftime("%B %Y"),
                "performance": performance,
                "overall": {
                    "total_spent": total_spent,
                    "total_budget": total_budget,
                    "percentage_used": overall_percentage,
                    "budget_health": budget_health,
                    "formatted_total_spent": self.format_currency(total_spent),
                    "formatted_total_budget": self.format_currency(total_budget)
                },
                "recommendations": recommendations
            }
            
            logger.info(f"📊 Budget performance calculated")
            return budget_data
            
        except Exception as e:
            logger.error(f"❌ Error calculating budget performance: {e}")
            return {
                "has_budget": False,
                "error": str(e)
            }
    
    async def get_current_month_spending_by_budget_type(self, user_id: str) -> Dict[str, float]:
        """Get current month spending categorized by budget type (needs/wants/savings)"""
        try:
            # Get current month date range
            now = datetime.now()
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = now
            
            # Query current month expenses
            query = {
                "user_id": user_id,
                "type": "expense",
                "status": TransactionStatus.CONFIRMED.value,
                "date": {"$gte": start_date, "$lte": end_date}
            }
            
            transactions = list(self.db.transactions.find(query))
            
            # Initialize spending by budget type
            spending = {
                "needs": 0.0,
                "wants": 0.0,
                "savings": 0.0
            }
            
            # Categorize transactions by budget type
            for trans in transactions:
                category = trans["category"]
                amount = trans["amount"]
                
                # Get budget type for this category
                budget_type = self._get_budget_type_from_category(category)
                spending[budget_type] += amount
            
            logger.info(f"💳 Current month spending calculated: {spending}")
            return spending
            
        except Exception as e:
            logger.error(f"❌ Error calculating current month spending: {e}")
            return {"needs": 0.0, "wants": 0.0, "savings": 0.0}
    
    def _get_budget_type_from_category(self, category: str) -> str:
        """Get budget type using IndonesianStudentCategories"""
        try:
            return IndonesianStudentCategories.get_budget_type(category)
            
        except Exception as e:
            logger.error(f"❌ Error getting budget type for category '{category}': {e}")
            
            # Fallback categorization
            category_lower = category.lower()
            
            # NEEDS keywords
            needs_keywords = [
                'kos', 'kost', 'sewa', 'listrik', 'air', 'tempat tinggal',
                'makan', 'makanan', 'nasi', 'lauk', 'groceries', 'masak',
                'transport', 'transportasi', 'angkot', 'bus', 'bensin', 'parkir',
                'buku', 'alat tulis', 'print', 'ukt', 'spp', 'kuliah', 'pendidikan',
                'internet', 'wifi', 'pulsa', 'kuota', 'komunikasi',
                'obat', 'dokter', 'shampo', 'sabun', 'pasta gigi', 'kesehatan'
            ]
            
            # SAVINGS keywords
            savings_keywords = [
                'tabungan', 'saving', 'simpan', 'deposito', 'menabung',
                'dana darurat', 'emergency', 'darurat', 'cadangan',
                'investasi', 'reksadana', 'saham', 'obligasi', 'crypto',
                'modal usaha', 'masa depan', 'pensiun'
            ]
            
            # Check NEEDS first
            for keyword in needs_keywords:
                if keyword in category_lower:
                    return "needs"
            
            # Check SAVINGS second
            for keyword in savings_keywords:
                if keyword in category_lower:
                    return "savings"
            
            # Default to WANTS
            return "wants"
    
    async def _calculate_real_total_savings(self, user_id: str) -> float:
        """Calculate real total savings (income - expenses + initial savings)"""
        try:
            # Get user's initial savings
            user_doc = self.db.users.find_one({"_id": ObjectId(user_id)})
            initial_savings = 0.0
            if user_doc and user_doc.get("financial_settings"):
                initial_savings = user_doc["financial_settings"].get("current_savings", 0.0)
            
            # Get all confirmed transactions
            query = {
                "user_id": user_id,
                "status": TransactionStatus.CONFIRMED.value
            }
            
            transactions = list(self.db.transactions.find(query))
            
            total_income = 0.0
            total_expense = 0.0
            
            for trans in transactions:
                amount = trans["amount"]
                if trans["type"] == "income":
                    total_income += amount
                elif trans["type"] == "expense":
                    total_expense += amount
            
            # Calculate real savings
            real_savings = initial_savings + total_income - total_expense
            
            logger.info(f"💰 Real total savings calculated: {self.format_currency(real_savings)}")
            return real_savings
            
        except Exception as e:
            logger.error(f"❌ Error calculating real total savings: {e}")
            return 0.0
    
    # ==========================================
    # DASHBOARD METHODS
    # ==========================================
    
    async def get_financial_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive financial dashboard"""
        try:
            # Get user financial settings
            user_doc = self.db.users.find_one({"_id": ObjectId(user_id)})
            if not user_doc:
                return {"error": "User not found"}
            
            financial_settings = user_doc.get("financial_settings", {})
            
            # Get real total savings
            real_total_savings = await self._calculate_real_total_savings(user_id)
            
            # Get recent transactions
            recent_transactions = await self.get_user_transactions(user_id, limit=10)
            
            # Get active savings goals
            active_goals = await self.get_user_savings_goals(user_id, status="active")
            
            # Get budget performance
            budget_performance = await self.get_monthly_budget_performance(user_id)
            
            dashboard_data = {
                "user_id": user_id,
                "real_total_savings": real_total_savings,
                "user_financial_settings": {
                    "monthly_income": financial_settings.get("monthly_income", 0.0),
                    "initial_savings": financial_settings.get("current_savings", 0.0),
                    "primary_bank": financial_settings.get("primary_bank", ""),
                    "last_budget_reset": financial_settings.get("last_budget_reset")
                },
                "calculated_totals": {
                    "actual_current_savings": real_total_savings
                },
                "budget_performance": budget_performance,
                "active_goals": {
                    "count": len(active_goals),
                    "goals": [
                        {
                            "id": goal.id,
                            "item_name": goal.item_name,
                            "target_amount": goal.target_amount,
                            "current_amount": goal.current_amount,
                            "progress_percentage": goal.progress_percentage,
                            "status": goal.status.value
                        }
                        for goal in active_goals[:5]  # Top 5 goals
                    ]
                },
                "recent_activity": {
                    "transactions": [
                        {
                            "id": trans.id,
                            "type": trans.type.value,
                            "amount": trans.amount,
                            "category": trans.category,
                            "description": trans.description,
                            "date": trans.date,
                            "relative_time": self._calculate_relative_time(trans.date)
                        }
                        for trans in recent_transactions
                    ],
                    "transaction_count": len(recent_transactions)
                },
                "sync_status": {
                    "needs_sync": False,
                    "last_sync": now_for_db()
                }
            }
            
            logger.info(f"📊 Financial dashboard generated")
            return dashboard_data
            
        except Exception as e:
            logger.error(f"❌ Error generating financial dashboard: {e}")
            return {
                "error": str(e)
            }
    
    async def get_financial_dashboard_50_30_20(self, user_id: str) -> Dict[str, Any]:
        """Get 50/30/20 specific dashboard"""
        try:
            # Get base dashboard
            dashboard_data = await self.get_financial_dashboard(user_id)
            
            if "error" in dashboard_data:
                return dashboard_data
            
            # Add 50/30/20 specific analysis
            budget_performance = dashboard_data.get("budget_performance", {})
            
            # Enhanced insights for 50/30/20
            insights = {
                "strongest_category": "unknown",
                "needs_attention": "none"
            }
            
            if budget_performance.get("has_budget"):
                performance = budget_performance.get("performance", {})
                
                # Find strongest performing category
                best_performance = min(
                    performance.get("needs", {}).get("percentage_used", 100),
                    performance.get("wants", {}).get("percentage_used", 100),
                    performance.get("savings", {}).get("percentage_used", 100)
                )
                
                for category, perf in performance.items():
                    if perf.get("percentage_used", 100) == best_performance:
                        insights["strongest_category"] = category
                        break
                
                # Find category that needs attention
                for category, perf in performance.items():
                    if perf.get("status") in ["over_budget", "warning"]:
                        insights["needs_attention"] = category
                        break
            
            # Add 50/30/20 specific data
            dashboard_data.update({
                "method": "50/30/20 Elizabeth Warren",
                "insights": insights,
                "wants_budget_goals": {
                    "goals": dashboard_data["active_goals"]["goals"],
                    "total_goals": dashboard_data["active_goals"]["count"],
                    "total_allocated": sum(goal["current_amount"] for goal in dashboard_data["active_goals"]["goals"]),
                    "total_target": sum(goal["target_amount"] for goal in dashboard_data["active_goals"]["goals"])
                }
            })
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"❌ Error generating 50/30/20 dashboard: {e}")
            return {
                "error": str(e)
            }
    
    # ==========================================
    # UTILITY METHODS
    # ==========================================
    
    def _get_categories_by_budget_type(self, budget_type: str) -> List[str]:
        """Get categories that belong to a budget type"""
        try:
            if budget_type == "needs":
                return IndonesianStudentCategories.get_all_needs_categories()
            elif budget_type == "wants":
                return IndonesianStudentCategories.get_all_wants_categories()
            elif budget_type == "savings":
                return IndonesianStudentCategories.get_all_savings_categories()
            else:
                return []
        except:
            # Fallback
            return []
    
    def _parse_datetime_from_string(self, date_str: Any) -> datetime:
        """Parse datetime from string or return current time"""
        if not date_str:
            return now_for_db()
        
        if isinstance(date_str, datetime):
            return date_str
        
        if isinstance(date_str, str):
            try:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except:
                return now_for_db()
        
        return now_for_db()
    
    def _calculate_relative_time(self, date_obj: datetime) -> str:
        """Calculate relative time string"""
        try:
            now = datetime.now()
            if date_obj.tzinfo is not None:
                date_obj = date_obj.replace(tzinfo=None)
            
            difference = now - date_obj
            
            if difference.days > 0:
                if difference.days == 1:
                    return '1 hari lalu'
                elif difference.days < 7:
                    return f'{difference.days} hari lalu'
                elif difference.days < 30:
                    weeks = difference.days // 7
                    return f'{weeks} minggu lalu'
                else:
                    months = difference.days // 30
                    return f'{months} bulan lalu'
            
            hours = difference.seconds // 3600
            if hours > 0:
                return f'{hours} jam lalu'
            
            minutes = difference.seconds // 60
            if minutes > 0:
                return f'{minutes} menit lalu'
            
            return 'Baru saja'
        except Exception:
            return 'Unknown'