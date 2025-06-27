# app/api/v1/dashboard/crud.py
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

class DashboardCRUD:
    """CRUD operations for dashboard data"""
    
    async def get_financial_summary_data(
        self, 
        db: AsyncIOMotorDatabase, 
        student_id: ObjectId, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get aggregated financial data for summary"""
        
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
                    "total_amount": {"$sum": "$amount"},
                    "count": {"$sum": 1},
                    "avg_amount": {"$avg": "$amount"}
                }
            }
        ]
        
        results = await db.transactions.aggregate(pipeline).to_list(length=None)
        
        # Format results
        summary = {
            "income": {"total": 0, "count": 0, "average": 0},
            "expense": {"total": 0, "count": 0, "average": 0}
        }
        
        for result in results:
            transaction_type = result["_id"]
            if transaction_type in summary:
                summary[transaction_type] = {
                    "total": result["total_amount"],
                    "count": result["count"],
                    "average": result["avg_amount"]
                }
        
        # Calculate net balance
        net_balance = summary["income"]["total"] - summary["expense"]["total"]
        
        return {
            "income": summary["income"],
            "expense": summary["expense"],
            "net_balance": net_balance,
            "total_transactions": summary["income"]["count"] + summary["expense"]["count"]
        }
    
    async def get_category_breakdown_data(
        self, 
        db: AsyncIOMotorDatabase, 
        student_id: ObjectId, 
        start_date: datetime, 
        end_date: datetime,
        transaction_type: str = "expense",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get spending/income breakdown by category"""
        
        pipeline = [
            {
                "$match": {
                    "student_id": student_id,
                    "type": transaction_type,
                    "transaction_date": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$group": {
                    "_id": "$category_id",
                    "total_amount": {"$sum": "$amount"},
                    "transaction_count": {"$sum": 1},
                    "avg_amount": {"$avg": "$amount"},
                    "latest_transaction": {"$max": "$transaction_date"}
                }
            },
            {
                "$sort": {"total_amount": -1}
            },
            {
                "$limit": limit
            }
        ]
        
        category_stats = await db.transactions.aggregate(pipeline).to_list(length=None)
        
        # Get total for percentage calculation
        total_amount = sum(stat["total_amount"] for stat in category_stats)
        
        # Enrich with category information
        breakdown = []
        for stat in category_stats:
            category = await db.categories.find_one({"_id": stat["_id"]})
            
            if category:
                percentage = (stat["total_amount"] / total_amount * 100) if total_amount > 0 else 0
                breakdown.append({
                    "category_id": str(stat["_id"]),
                    "category_name": category["name"],
                    "category_icon": category.get("icon", "💰"),
                    "category_color": category.get("color", "#3498db"),
                    "total_amount": stat["total_amount"],
                    "transaction_count": stat["transaction_count"],
                    "average_amount": stat["avg_amount"],
                    "percentage": round(percentage, 1),
                    "latest_transaction": stat["latest_transaction"]
                })
        
        return breakdown
    
    async def get_spending_trends_data(
        self, 
        db: AsyncIOMotorDatabase, 
        student_id: ObjectId, 
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get daily spending trends for the last N days"""
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        pipeline = [
            {
                "$match": {
                    "student_id": student_id,
                    "type": "expense",
                    "transaction_date": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$transaction_date"},
                        "month": {"$month": "$transaction_date"},
                        "day": {"$dayOfMonth": "$transaction_date"}
                    },
                    "daily_total": {"$sum": "$amount"},
                    "transaction_count": {"$sum": 1}
                }
            },
            {
                "$sort": {"_id": 1}
            }
        ]
        
        daily_data = await db.transactions.aggregate(pipeline).to_list(length=None)
        
        # Fill in missing days with zero values
        trends = []
        current_date = start_date
        daily_lookup = {
            f"{d['_id']['year']}-{d['_id']['month']}-{d['_id']['day']}": d 
            for d in daily_data
        }
        
        while current_date <= end_date:
            date_key = f"{current_date.year}-{current_date.month}-{current_date.day}"
            day_data = daily_lookup.get(date_key, {
                "daily_total": 0,
                "transaction_count": 0
            })
            
            trends.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "amount": day_data["daily_total"],
                "transaction_count": day_data["transaction_count"]
            })
            
            current_date += timedelta(days=1)
        
        return trends
    
    async def get_recent_transactions_data(
        self, 
        db: AsyncIOMotorDatabase, 
        student_id: ObjectId, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent transactions with category information"""
        
        pipeline = [
            {
                "$match": {"student_id": student_id}
            },
            {
                "$sort": {"transaction_date": -1}
            },
            {
                "$limit": limit
            },
            {
                "$lookup": {
                    "from": "categories",
                    "localField": "category_id",
                    "foreignField": "_id",
                    "as": "category_info"
                }
            },
            {
                "$unwind": {
                    "path": "$category_info",
                    "preserveNullAndEmptyArrays": True
                }
            }
        ]
        
        transactions = await db.transactions.aggregate(pipeline).to_list(length=None)
        
        # Format response
        formatted_transactions = []
        for tx in transactions:
            category_info = tx.get("category_info", {})
            
            formatted_transactions.append({
                "id": str(tx["_id"]),
                "type": tx["type"],
                "amount": tx["amount"],
                "title": tx["title"],
                "notes": tx.get("notes"),
                "transaction_date": tx["transaction_date"],
                "payment_method": tx.get("payment_method", "cash"),
                "account_name": tx.get("account_name", ""),
                "category": {
                    "id": str(tx["category_id"]) if tx.get("category_id") else None,
                    "name": category_info.get("name", "Uncategorized"),
                    "icon": category_info.get("icon", "💰"),
                    "color": category_info.get("color", "#3498db")
                },
                "location": tx.get("location"),
                "metadata": tx.get("metadata", {})
            })
        
        return formatted_transactions
    
    async def get_budget_analysis_data(
        self, 
        db: AsyncIOMotorDatabase, 
        student_id: ObjectId,
        monthly_allowance: float
    ) -> Dict[str, Any]:
        """Get budget analysis for current month"""
        
        # Current month date range
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Get current month expenses
        pipeline = [
            {
                "$match": {
                    "student_id": student_id,
                    "type": "expense",
                    "transaction_date": {"$gte": month_start, "$lte": now}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_spent": {"$sum": "$amount"},
                    "transaction_count": {"$sum": 1},
                    "daily_average": {"$avg": "$amount"}
                }
            }
        ]
        
        expense_result = await db.transactions.aggregate(pipeline).to_list(length=1)
        total_spent = expense_result[0]["total_spent"] if expense_result else 0
        
        # Calculate budget metrics
        days_in_month = (now.replace(month=now.month+1, day=1) - timedelta(days=1)).day
        days_passed = now.day
        days_remaining = days_in_month - days_passed
        
        budget_used_percentage = (total_spent / monthly_allowance * 100) if monthly_allowance > 0 else 0
        daily_budget = monthly_allowance / days_in_month if days_in_month > 0 else 0
        daily_spent_avg = total_spent / days_passed if days_passed > 0 else 0
        projected_monthly_spend = daily_spent_avg * days_in_month
        
        # Budget status
        status = "good"
        if budget_used_percentage > 90:
            status = "critical"
        elif budget_used_percentage > 75:
            status = "warning"
        elif budget_used_percentage > 50:
            status = "caution"
        
        return {
            "monthly_allowance": monthly_allowance,
            "total_spent": total_spent,
            "remaining_budget": monthly_allowance - total_spent,
            "budget_used_percentage": round(budget_used_percentage, 1),
            "daily_budget": daily_budget,
            "daily_spent_average": daily_spent_avg,
            "projected_monthly_spend": projected_monthly_spend,
            "days_remaining": days_remaining,
            "status": status,
            "on_track": projected_monthly_spend <= monthly_allowance
        }
    
    async def get_comparison_data(
        self, 
        db: AsyncIOMotorDatabase, 
        student_id: ObjectId,
        current_start: datetime,
        current_end: datetime
    ) -> Dict[str, Any]:
        """Get comparison data vs previous period"""
        
        period_length = current_end - current_start
        prev_start = current_start - period_length
        prev_end = current_start
        
        # Current period data
        current_data = await self.get_financial_summary_data(
            db, student_id, current_start, current_end
        )
        
        # Previous period data
        prev_data = await self.get_financial_summary_data(
            db, student_id, prev_start, prev_end
        )
        
        # Calculate changes
        income_change = calculate_percentage_change(
            prev_data["income"]["total"], 
            current_data["income"]["total"]
        )
        expense_change = calculate_percentage_change(
            prev_data["expense"]["total"], 
            current_data["expense"]["total"]
        )
        balance_change = calculate_percentage_change(
            prev_data["net_balance"], 
            current_data["net_balance"]
        )
        
        return {
            "current_period": current_data,
            "previous_period": prev_data,
            "changes": {
                "income_change": income_change,
                "expense_change": expense_change,
                "balance_change": balance_change
            }
        }

# Helper functions
def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """Calculate percentage change between two values"""
    if old_value == 0:
        return 100.0 if new_value > 0 else 0.0
    return round(((new_value - old_value) / old_value) * 100, 1)