# app/api/v1/dashboard/routes.py
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId

from app.api.deps import get_verified_user, get_db
from app.models.student import Student
from app.models.transaction import Transaction, TransactionSummary, CategoryBreakdown
from app.models.category import Category
from app.services.analytics.student_insights import StudentInsightsService
from app.services.analytics.prediction_service import PredictionService

router = APIRouter()

# Initialize services
insights_service = StudentInsightsService()
prediction_service = PredictionService()

@router.get("/financial-summary")
async def get_financial_summary(
    period: str = Query("monthly", description="daily, weekly, monthly, yearly"),
    current_student: Student = Depends(get_verified_user),
    db = Depends(get_db)
):
    """Get financial summary for dashboard"""
    try:
        # Calculate date range based on period
        now = datetime.utcnow()
        if period == "daily":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "weekly":
            start_date = now - timedelta(days=7)
        elif period == "monthly":
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == "yearly":
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            raise HTTPException(status_code=400, detail="Invalid period")

        # Get transactions for the period
        transactions_collection = db.transactions
        transactions_cursor = transactions_collection.find({
            "student_id": current_student.id,
            "transaction_date": {"$gte": start_date, "$lte": now}
        }).sort("transaction_date", -1)
        
        transactions = await transactions_cursor.to_list(length=None)
        
        # Calculate summary
        total_income = sum(t["amount"] for t in transactions if t["type"] == "income")
        total_expense = sum(t["amount"] for t in transactions if t["type"] == "expense")
        net_balance = total_income - total_expense
        transaction_count = len(transactions)
        
        # Calculate daily average for the period
        days_in_period = max(1, (now - start_date).days or 1)
        daily_average = total_expense / days_in_period if days_in_period > 0 else 0
        
        # Get previous period for comparison
        prev_start = start_date - (now - start_date)
        prev_transactions_cursor = transactions_collection.find({
            "student_id": current_student.id,
            "transaction_date": {"$gte": prev_start, "$lt": start_date}
        })
        prev_transactions = await prev_transactions_cursor.to_list(length=None)
        
        prev_total_expense = sum(t["amount"] for t in prev_transactions if t["type"] == "expense")
        expense_change = ((total_expense - prev_total_expense) / prev_total_expense * 100) if prev_total_expense > 0 else 0
        
        # Get last transaction
        last_transaction = transactions[0] if transactions else None
        
        return {
            "period": period,
            "date_range": {
                "start": start_date,
                "end": now
            },
            "summary": {
                "total_income": total_income,
                "total_expense": total_expense,
                "net_balance": net_balance,
                "transaction_count": transaction_count,
                "daily_average": daily_average,
                "expense_vs_previous_period": round(expense_change, 1)
            },
            "last_transaction": {
                "id": str(last_transaction["_id"]) if last_transaction else None,
                "type": last_transaction.get("type") if last_transaction else None,
                "amount": last_transaction.get("amount") if last_transaction else None,
                "title": last_transaction.get("title") if last_transaction else None,
                "date": last_transaction.get("transaction_date") if last_transaction else None
            } if last_transaction else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting financial summary: {str(e)}")

@router.get("/quick-stats")
async def get_quick_stats(
    current_student: Student = Depends(get_verified_user),
    db = Depends(get_db)
):
    """Get quick statistics for dashboard widgets"""
    try:
        # Get current month transactions
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        transactions_collection = db.transactions
        
        # Total transactions this month
        total_transactions = await transactions_collection.count_documents({
            "student_id": current_student.id,
            "transaction_date": {"$gte": month_start}
        })
        
        # Active categories (used in last 30 days)
        active_categories = await transactions_collection.distinct(
            "category_id",
            {
                "student_id": current_student.id,
                "transaction_date": {"$gte": now - timedelta(days=30)}
            }
        )
        
        # Average transaction amount this month
        pipeline = [
            {
                "$match": {
                    "student_id": current_student.id,
                    "transaction_date": {"$gte": month_start}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "avg_amount": {"$avg": "$amount"},
                    "total_amount": {"$sum": "$amount"}
                }
            }
        ]
        
        avg_result = await transactions_collection.aggregate(pipeline).to_list(length=1)
        avg_amount = avg_result[0]["avg_amount"] if avg_result else 0
        
        # Spending streak (consecutive days with transactions)
        spending_streak = await calculate_spending_streak(db, current_student.id)
        
        # Budget adherence (if student has budget goals)
        monthly_allowance = current_student.profile.monthly_allowance
        budget_adherence = None
        if monthly_allowance > 0:
            month_expenses = await transactions_collection.aggregate([
                {
                    "$match": {
                        "student_id": current_student.id,
                        "type": "expense",
                        "transaction_date": {"$gte": month_start}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total": {"$sum": "$amount"}
                    }
                }
            ]).to_list(length=1)
            
            total_expenses = month_expenses[0]["total"] if month_expenses else 0
            budget_adherence = {
                "spent": total_expenses,
                "budget": monthly_allowance,
                "percentage": round((total_expenses / monthly_allowance * 100), 1) if monthly_allowance > 0 else 0,
                "remaining": monthly_allowance - total_expenses
            }
        
        return {
            "total_transactions_this_month": total_transactions,
            "active_categories_count": len(active_categories),
            "average_transaction_amount": round(avg_amount, 2),
            "spending_streak_days": spending_streak,
            "budget_adherence": budget_adherence
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting quick stats: {str(e)}")

@router.get("/category-breakdown")
async def get_category_breakdown(
    period: str = Query("monthly", description="weekly, monthly, yearly"),
    limit: int = Query(5, le=10),
    current_student: Student = Depends(get_verified_user),
    db = Depends(get_db)
):
    """Get spending breakdown by category"""
    try:
        # Calculate date range
        now = datetime.utcnow()
        if period == "weekly":
            start_date = now - timedelta(days=7)
        elif period == "monthly":
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == "yearly":
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            raise HTTPException(status_code=400, detail="Invalid period")
        
        # Aggregate expenses by category
        pipeline = [
            {
                "$match": {
                    "student_id": current_student.id,
                    "type": "expense",
                    "transaction_date": {"$gte": start_date, "$lte": now}
                }
            },
            {
                "$group": {
                    "_id": "$category_id",
                    "total_amount": {"$sum": "$amount"},
                    "transaction_count": {"$sum": 1},
                    "avg_amount": {"$avg": "$amount"}
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
        
        # Get category details
        categories_collection = db.categories
        breakdown = []
        total_expense = sum(stat["total_amount"] for stat in category_stats)
        
        for stat in category_stats:
            category = await categories_collection.find_one({"_id": stat["_id"]})
            if category:
                percentage = (stat["total_amount"] / total_expense * 100) if total_expense > 0 else 0
                breakdown.append({
                    "category_id": str(stat["_id"]),
                    "category_name": category["name"],
                    "category_icon": category.get("icon", "💰"),
                    "category_color": category.get("color", "#3498db"),
                    "total_amount": stat["total_amount"],
                    "transaction_count": stat["transaction_count"],
                    "average_amount": round(stat["avg_amount"], 2),
                    "percentage": round(percentage, 1)
                })
        
        return {
            "period": period,
            "total_expense": total_expense,
            "breakdown": breakdown
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting category breakdown: {str(e)}")

@router.get("/recent-transactions")
async def get_recent_transactions(
    limit: int = Query(5, le=20),
    current_student: Student = Depends(get_verified_user),
    db = Depends(get_db)
):
    """Get recent transactions with category info"""
    try:
        # Get recent transactions
        transactions_cursor = db.transactions.find({
            "student_id": current_student.id
        }).sort("transaction_date", -1).limit(limit)
        
        transactions = await transactions_cursor.to_list(length=None)
        
        # Get category info for each transaction
        categories_collection = db.categories
        enriched_transactions = []
        
        for transaction in transactions:
            category = await categories_collection.find_one({"_id": transaction["category_id"]})
            
            enriched_transactions.append({
                "id": str(transaction["_id"]),
                "type": transaction["type"],
                "amount": transaction["amount"],
                "title": transaction["title"],
                "transaction_date": transaction["transaction_date"],
                "payment_method": transaction.get("payment_method", "cash"),
                "category": {
                    "id": str(transaction["category_id"]),
                    "name": category["name"] if category else "Unknown",
                    "icon": category.get("icon", "💰") if category else "💰",
                    "color": category.get("color", "#3498db") if category else "#3498db"
                },
                "location": transaction.get("location"),
                "notes": transaction.get("notes")
            })
        
        return {
            "transactions": enriched_transactions,
            "count": len(enriched_transactions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting recent transactions: {str(e)}")

@router.get("/predictions")
async def get_financial_predictions(
    prediction_type: str = Query("expense", description="income, expense, balance"),
    days_ahead: int = Query(30, le=90),
    current_student: Student = Depends(get_verified_user),
    db = Depends(get_db)
):
    """Get financial predictions using simplified prediction service"""
    try:
        # Use simplified prediction service
        prediction = await prediction_service.get_or_generate_prediction(
            db, current_student.id, prediction_type, days_ahead
        )
        
        if not prediction:
            raise HTTPException(
                status_code=404, 
                detail="Insufficient data for prediction. Need at least 7 days of transaction history."
            )
        
        return prediction
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting predictions: {str(e)}")

@router.get("/insights")
async def get_financial_insights(
    current_student: Student = Depends(get_verified_user),
    db = Depends(get_db)
):
    """Get AI-generated financial insights for students"""
    try:
        # Use insights service to generate student-specific insights
        insights = await insights_service.generate_student_insights(
            db, current_student.id
        )
        
        return {
            "insights": insights,
            "generated_at": datetime.utcnow(),
            "student_context": {
                "semester": current_student.profile.semester,
                "university": current_student.profile.university,
                "monthly_allowance": current_student.profile.monthly_allowance
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting insights: {str(e)}")

@router.get("/academic-context")
async def get_academic_context(
    current_student: Student = Depends(get_verified_user),
    db = Depends(get_db)
):
    """Get academic calendar context affecting finances"""
    try:
        now = datetime.utcnow()
        academic_info = current_student.profile.academic_info
        
        # Check current academic events
        current_events = []
        upcoming_events = []
        
        # Check exam periods
        for exam in academic_info.exam_periods:
            if exam.start_date <= now <= exam.end_date:
                current_events.append({
                    "type": "exam",
                    "name": f"{exam.type.title()} Exam",
                    "start_date": exam.start_date,
                    "end_date": exam.end_date,
                    "financial_impact": "Reduced entertainment spending, increased study materials cost"
                })
            elif exam.start_date > now and exam.start_date <= now + timedelta(days=14):
                upcoming_events.append({
                    "type": "exam",
                    "name": f"{exam.type.title()} Exam",
                    "start_date": exam.start_date,
                    "end_date": exam.end_date,
                    "days_until": (exam.start_date - now).days,
                    "financial_impact": "Prepare for reduced entertainment spending"
                })
        
        # Check holiday periods
        for holiday in academic_info.holiday_periods:
            if holiday.start_date <= now <= holiday.end_date:
                current_events.append({
                    "type": "holiday",
                    "name": holiday.name,
                    "start_date": holiday.start_date,
                    "end_date": holiday.end_date,
                    "financial_impact": "Potential travel costs, reduced daily expenses"
                })
            elif holiday.start_date > now and holiday.start_date <= now + timedelta(days=30):
                upcoming_events.append({
                    "type": "holiday",
                    "name": holiday.name,
                    "start_date": holiday.start_date,
                    "end_date": holiday.end_date,
                    "days_until": (holiday.start_date - now).days,
                    "financial_impact": "Plan for potential travel costs"
                })
        
        # Calculate semester progress
        semester_progress = calculate_semester_progress(academic_info, now)
        
        return {
            "current_events": current_events,
            "upcoming_events": upcoming_events,
            "semester_progress": semester_progress,
            "academic_calendar": {
                "semester_start": academic_info.semester_start,
                "semester_end": academic_info.semester_end,
                "current_week": calculate_academic_week(academic_info, now)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting academic context: {str(e)}")

@router.get("/spending-trends")
async def get_spending_trends(
    days: int = Query(30, le=90, description="Number of days to analyze"),
    current_student: Student = Depends(get_verified_user),
    db = Depends(get_db)
):
    """Get daily spending trends for visualization"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Aggregate daily spending
        pipeline = [
            {
                "$match": {
                    "student_id": current_student.id,
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
                "transaction_count": day_data["transaction_count"],
                "day_of_week": current_date.strftime("%A")
            })
            
            current_date += timedelta(days=1)
        
        # Calculate statistics
        amounts = [t["amount"] for t in trends if t["amount"] > 0]
        stats = {
            "average_daily": sum(amounts) / len(amounts) if amounts else 0,
            "highest_day": max(trends, key=lambda x: x["amount"]) if trends else None,
            "lowest_day": min([t for t in trends if t["amount"] > 0], key=lambda x: x["amount"]) if amounts else None,
            "total_days_with_spending": len(amounts),
            "spending_days_percentage": (len(amounts) / len(trends) * 100) if trends else 0
        }
        
        return {
            "period": {
                "start_date": start_date,
                "end_date": end_date,
                "days": days
            },
            "trends": trends,
            "statistics": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting spending trends: {str(e)}")

# Helper functions
async def calculate_spending_streak(db, student_id: ObjectId) -> int:
    """Calculate consecutive days with transactions"""
    now = datetime.utcnow()
    streak = 0
    current_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    for i in range(30):  # Check last 30 days max
        day_start = current_date - timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        
        has_transaction = await db.transactions.count_documents({
            "student_id": student_id,
            "transaction_date": {"$gte": day_start, "$lt": day_end}
        }) > 0
        
        if has_transaction:
            streak += 1
        else:
            break
    
    return streak

def calculate_semester_progress(academic_info, current_date: datetime) -> Dict:
    """Calculate semester progress percentage"""
    total_days = (academic_info.semester_end - academic_info.semester_start).days
    days_passed = (current_date - academic_info.semester_start).days
    
    progress_percentage = min(100, max(0, (days_passed / total_days) * 100)) if total_days > 0 else 0
    
    return {
        "percentage": round(progress_percentage, 1),
        "days_passed": max(0, days_passed),
        "days_remaining": max(0, (academic_info.semester_end - current_date).days),
        "total_days": total_days
    }

def calculate_academic_week(academic_info, current_date: datetime) -> int:
    """Calculate current academic week (1-16)"""
    days_since_start = (current_date - academic_info.semester_start).days
    week = min(16, max(1, (days_since_start // 7) + 1))
    return week