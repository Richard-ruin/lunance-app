# app/services/financial_actions.py
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from bson import ObjectId
import logging
from ..database import get_database

logger = logging.getLogger(__name__)

class FinancialActionsService:
    """Service to handle financial actions triggered by AI intents"""
    
    async def get_user_summary(self, user_id: str) -> Dict[str, Any]:
        """Get user financial summary"""
        try:
            db = await get_database()
            
            # Get user info
            user = await db.users.find_one({"_id": ObjectId(user_id)})
            if not user:
                return {}
            
            # Get recent transaction count
            recent_transactions = await db.transactions.count_documents({
                "user_id": ObjectId(user_id),
                "date": {"$gte": datetime.now() - timedelta(days=7)}
            })
            
            return {
                "name": user.get("nama_lengkap", ""),
                "recent_activity": recent_transactions,
                "is_active": recent_transactions > 0
            }
            
        except Exception as e:
            logger.error(f"Error getting user summary: {e}")
            return {}
    
    async def create_transaction(
        self, 
        user_id: str, 
        amount: float, 
        category: str, 
        transaction_type: str,
        date: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new transaction"""
        try:
            db = await get_database()
            
            # Get or create category
            category_doc = await db.categories.find_one({
                "$or": [
                    {"user_id": ObjectId(user_id), "name": category},
                    {"user_id": None, "name": category}  # Global category
                ]
            })
            
            if not category_doc:
                # Create personal category
                category_doc = {
                    "name": category,
                    "user_id": ObjectId(user_id),
                    "color": "#4CAF50",
                    "icon": "category",
                    "is_active": True,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                result = await db.categories.insert_one(category_doc)
                category_doc["_id"] = result.inserted_id
            
            # Parse date
            transaction_date = datetime.now()
            if date:
                try:
                    transaction_date = datetime.fromisoformat(date.replace('Z', '+00:00'))
                except:
                    pass
            
            # Create transaction
            transaction = {
                "user_id": ObjectId(user_id),
                "jumlah": amount,
                "jenis": transaction_type,
                "kategori": category,
                "category_id": category_doc["_id"],
                "deskripsi": description or f"Auto-input via Luna: {category}",
                "date": transaction_date,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = await db.transactions.insert_one(transaction)
            
            # Check budget status if expense
            budget_alert = None
            spending_insight = None
            suggestions = []
            
            if transaction_type == "expense":
                budget_status = await self._check_budget_after_transaction(
                    user_id, category_doc["_id"], amount
                )
                budget_alert = budget_status.get("alert")
                spending_insight = budget_status.get("insight")
                suggestions = budget_status.get("suggestions", [])
            
            return {
                "success": True,
                "transaction_id": str(result.inserted_id),
                "budget_alert": budget_alert,
                "spending_insight": spending_insight,
                "suggestions": suggestions
            }
            
        except Exception as e:
            logger.error(f"Error creating transaction: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_current_balance(self, user_id: str) -> Dict[str, Any]:
        """Get current balance and recent spending"""
        try:
            db = await get_database()
            
            # Calculate balance
            pipeline = [
                {"$match": {"user_id": ObjectId(user_id)}},
                {"$group": {
                    "_id": "$jenis",
                    "total": {"$sum": "$jumlah"}
                }}
            ]
            
            results = await db.transactions.aggregate(pipeline).to_list(None)
            
            income = 0
            expense = 0
            for result in results:
                if result["_id"] == "income":
                    income = result["total"]
                elif result["_id"] == "expense":
                    expense = result["total"]
            
            # Get user's initial balance
            user = await db.users.find_one({"_id": ObjectId(user_id)})
            initial_balance = user.get("tabungan_awal", 0) if user else 0
            
            current_balance = initial_balance + income - expense
            
            # Get recent spending (last 7 days)
            recent_spending = await db.transactions.aggregate([
                {
                    "$match": {
                        "user_id": ObjectId(user_id),
                        "jenis": "expense",
                        "date": {"$gte": datetime.now() - timedelta(days=7)}
                    }
                },
                {"$group": {"_id": None, "total": {"$sum": "$jumlah"}}}
            ]).to_list(1)
            
            recent_spending_amount = recent_spending[0]["total"] if recent_spending else 0
            
            return {
                "balance": current_balance,
                "recent_spending": recent_spending_amount,
                "income_total": income,
                "expense_total": expense
            }
            
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            return {"balance": 0, "recent_spending": 0}
    
    async def analyze_spending(self, user_id: str) -> Dict[str, Any]:
        """Analyze user spending patterns"""
        try:
            db = await get_database()
            
            # Current month spending by category
            current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            pipeline = [
                {
                    "$match": {
                        "user_id": ObjectId(user_id),
                        "jenis": "expense",
                        "date": {"$gte": current_month_start}
                    }
                },
                {
                    "$group": {
                        "_id": "$kategori",
                        "total": {"$sum": "$jumlah"},
                        "count": {"$sum": 1}
                    }
                },
                {"$sort": {"total": -1}}
            ]
            
            category_spending = await db.transactions.aggregate(pipeline).to_list(None)
            
            total_spending = sum(cat["total"] for cat in category_spending)
            
            # Previous month comparison
            prev_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
            prev_month_end = current_month_start
            
            prev_month_total = await db.transactions.aggregate([
                {
                    "$match": {
                        "user_id": ObjectId(user_id),
                        "jenis": "expense",
                        "date": {"$gte": prev_month_start, "$lt": prev_month_end}
                    }
                },
                {"$group": {"_id": None, "total": {"$sum": "$jumlah"}}}
            ]).to_list(1)
            
            prev_total = prev_month_total[0]["total"] if prev_month_total else 0
            
            # Calculate change percentage
            change_pct = 0
            if prev_total > 0:
                change_pct = ((total_spending - prev_total) / prev_total) * 100
            
            # Generate recommendations
            recommendations = []
            if category_spending:
                top_category = category_spending[0]
                if top_category["total"] > total_spending * 0.4:
                    recommendations.append(f"Pengeluaran {top_category['_id']} dominan, coba kurangi 20%")
            
            if change_pct > 20:
                recommendations.append("Pengeluaran naik signifikan, review kembali kebutuhan vs keinginan")
            
            return {
                "total_spending": total_spending,
                "top_categories": [
                    {"name": cat["_id"], "amount": cat["total"], "count": cat["count"]}
                    for cat in category_spending[:3]
                ],
                "comparison": {
                    "previous_month": prev_total,
                    "change": change_pct
                },
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Error analyzing spending: {e}")
            return {"total_spending": 0, "top_categories": [], "comparison": {}}
    
    async def get_budget_status(self, user_id: str) -> Dict[str, Any]:
        """Get current budget status"""
        try:
            db = await get_database()
            
            # Get active budgets
            budgets = await db.budgets.find({
                "user_id": ObjectId(user_id),
                "is_active": True
            }).to_list(None)
            
            budget_status = []
            current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            for budget in budgets:
                # Calculate current spending for this budget
                spent = await db.transactions.aggregate([
                    {
                        "$match": {
                            "user_id": ObjectId(user_id),
                            "category_id": budget["category_id"],
                            "jenis": "expense",
                            "date": {"$gte": current_month_start}
                        }
                    },
                    {"$group": {"_id": None, "total": {"$sum": "$jumlah"}}}
                ]).to_list(1)
                
                spent_amount = spent[0]["total"] if spent else 0
                
                # Get category name
                category = await db.categories.find_one({"_id": budget["category_id"]})
                category_name = category["name"] if category else "Unknown"
                
                budget_status.append({
                    "category": category_name,
                    "amount": budget["jumlah"],
                    "used": spent_amount,
                    "remaining": budget["jumlah"] - spent_amount
                })
            
            return {"budgets": budget_status}
            
        except Exception as e:
            logger.error(f"Error getting budget status: {e}")
            return {"budgets": []}
    
    async def _check_budget_after_transaction(
        self, user_id: str, category_id: ObjectId, amount: float
    ) -> Dict[str, Any]:
        """Check budget status after adding a transaction"""
        try:
            db = await get_database()
            
            # Find budget for this category
            budget = await db.budgets.find_one({
                "user_id": ObjectId(user_id),
                "category_id": category_id,
                "is_active": True
            })
            
            if not budget:
                return {}
            
            # Calculate current month spending
            current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            spent = await db.transactions.aggregate([
                {
                    "$match": {
                        "user_id": ObjectId(user_id),
                        "category_id": category_id,
                        "jenis": "expense",
                        "date": {"$gte": current_month_start}
                    }
                },
                {"$group": {"_id": None, "total": {"$sum": "$jumlah"}}}
            ]).to_list(1)
            
            total_spent = spent[0]["total"] if spent else 0
            usage_pct = (total_spent / budget["jumlah"]) * 100
            
            alert = None
            suggestions = []
            
            if usage_pct >= 100:
                alert = f"Budget exceeded! {usage_pct:.1f}% of budget used"
                suggestions.append("Review pengeluaran kategori ini")
                suggestions.append("Pertimbangkan adjust budget")
            elif usage_pct >= 80:
                alert = f"Budget warning: {usage_pct:.1f}% used"
                suggestions.append("Perhatikan pengeluaran kategori ini")
            elif usage_pct >= 60:
                insight = f"Budget usage: {usage_pct:.1f}%"
            
            return {
                "alert": alert,
                "insight": insight if usage_pct < 80 else None,
                "suggestions": suggestions
            }
            
        except Exception as e:
            logger.error(f"Error checking budget: {e}")
            return {}

# Global instance
financial_actions_service = FinancialActionsService()