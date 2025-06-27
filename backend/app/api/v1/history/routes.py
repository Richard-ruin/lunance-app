# app/api/v1/history/routes.py
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
import io
import csv
from calendar import monthrange

from app.models.transaction import (
    TransactionResponse, TransactionFilter, TransactionSort,
    TransactionListResponse, TransactionSummary, CategoryBreakdown,
    PeriodSummary, MonthlyTransactionSummary
)
from app.api.deps import get_current_student, get_database
from app.api.v1.transactions.crud import TransactionCRUD
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter(tags=["history"])

# Helper function to convert Transaction to TransactionResponse
def to_transaction_response(transaction) -> TransactionResponse:
    return TransactionResponse(
        _id=transaction.id or "",
        type=transaction.type,
        amount=transaction.amount,
        currency=transaction.currency,
        category_id=transaction.category_id,
        subcategory=transaction.subcategory,
        title=transaction.title,
        notes=transaction.notes,
        transaction_date=transaction.transaction_date,
        created_at=transaction.created_at,
        payment_method=transaction.payment_method,
        account_name=transaction.account_name,
        location=transaction.location,
        receipt_photo=transaction.receipt_photo,
        metadata=transaction.metadata,
        budget_impact=transaction.budget_impact
    )

@router.get("/history", response_model=TransactionListResponse)
async def get_transaction_history(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    type: Optional[str] = Query(None, description="Filter by transaction type"),
    category_id: Optional[str] = Query(None, description="Filter by category"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    search: Optional[str] = Query(None, description="Search term"),
    sort: TransactionSort = Query(TransactionSort.DATE_DESC, description="Sort order"),
    current_student: dict = Depends(get_current_student),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get transaction history with advanced filtering"""
    crud = TransactionCRUD(db)
    
    filters = TransactionFilter(
        type=type,
        category_id=category_id,
        start_date=start_date,
        end_date=end_date,
        search=search
    )
    
    skip = (page - 1) * limit
    result = await crud.get_transactions(
        student_id=str(current_student["_id"]),
        skip=skip,
        limit=limit,
        filters=filters,
        sort=sort
    )
    
    return TransactionListResponse(
        transactions=[to_transaction_response(t) for t in result["transactions"]],
        total=result["total"],
        page=result["page"],
        limit=result["limit"],
        total_pages=result["total_pages"]
    )

@router.get("/history/summary/daily")
async def get_daily_summary(
    date: Optional[datetime] = Query(None, description="Specific date (defaults to today)"),
    current_student: dict = Depends(get_current_student),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get daily transaction summary"""
    if not date:
        date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + timedelta(days=1) - timedelta(microseconds=1)
    
    crud = TransactionCRUD(db)
    
    summary = await crud.get_transaction_summary(
        student_id=str(current_student["_id"]),
        start_date=start_date,
        end_date=end_date
    )
    
    category_breakdown = await crud.get_category_breakdown(
        student_id=str(current_student["_id"]),
        start_date=start_date,
        end_date=end_date,
        transaction_type="expense"
    )
    
    return {
        "date": date.date(),
        "summary": summary,
        "category_breakdown": category_breakdown
    }

@router.get("/history/summary/weekly")
async def get_weekly_summary(
    week_start: Optional[datetime] = Query(None, description="Week start date"),
    current_student: dict = Depends(get_current_student),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get weekly transaction summary"""
    if not week_start:
        today = datetime.utcnow()
        week_start = today - timedelta(days=today.weekday())
    
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    week_end = week_start + timedelta(days=7) - timedelta(microseconds=1)
    
    crud = TransactionCRUD(db)
    
    summary = await crud.get_transaction_summary(
        student_id=str(current_student["_id"]),
        start_date=week_start,
        end_date=week_end
    )
    
    category_breakdown = await crud.get_category_breakdown(
        student_id=str(current_student["_id"]),
        start_date=week_start,
        end_date=week_end,
        transaction_type="expense"
    )
    
    # Get daily breakdown for the week
    daily_breakdown = []
    for i in range(7):
        day_start = week_start + timedelta(days=i)
        day_end = day_start + timedelta(days=1) - timedelta(microseconds=1)
        
        day_summary = await crud.get_transaction_summary(
            student_id=str(current_student["_id"]),
            start_date=day_start,
            end_date=day_end
        )
        
        daily_breakdown.append({
            "date": day_start.date(),
            "day_name": day_start.strftime("%A"),
            "summary": day_summary
        })
    
    return {
        "week_start": week_start.date(),
        "week_end": week_end.date(),
        "summary": summary,
        "category_breakdown": category_breakdown,
        "daily_breakdown": daily_breakdown
    }

@router.get("/history/summary/monthly", response_model=MonthlyTransactionSummary)
async def get_monthly_summary(
    month: Optional[int] = Query(None, ge=1, le=12, description="Month (1-12)"),
    year: Optional[int] = Query(None, ge=2020, description="Year"),
    current_student: dict = Depends(get_current_student),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get monthly transaction summary with weekly breakdown"""
    today = datetime.utcnow()
    if not month:
        month = today.month
    if not year:
        year = today.year
    
    # Get month boundaries
    start_date = datetime(year, month, 1)
    _, last_day = monthrange(year, month)
    end_date = datetime(year, month, last_day, 23, 59, 59, 999999)
    
    crud = TransactionCRUD(db)
    
    # Get monthly summary
    summary = await crud.get_transaction_summary(
        student_id=str(current_student["_id"]),
        start_date=start_date,
        end_date=end_date
    )
    
    # Get category breakdown
    category_breakdown = await crud.get_category_breakdown(
        student_id=str(current_student["_id"]),
        start_date=start_date,
        end_date=end_date,
        transaction_type="expense"
    )
    
    # Get weekly breakdown
    weekly_breakdown = []
    current_week_start = start_date
    week_number = 1
    
    while current_week_start <= end_date:
        # Calculate week end (Sunday or end of month)
        current_week_end = min(
            current_week_start + timedelta(days=6),
            end_date
        )
        
        week_summary = await crud.get_transaction_summary(
            student_id=str(current_student["_id"]),
            start_date=current_week_start,
            end_date=current_week_end
        )
        
        weekly_breakdown.append(PeriodSummary(
            period=f"Week {week_number}",
            start_date=current_week_start,
            end_date=current_week_end,
            summary=week_summary,
            category_breakdown=[]  # Simplified for now
        ))
        
        current_week_start = current_week_end + timedelta(days=1)
        week_number += 1
    
    return MonthlyTransactionSummary(
        month=month,
        year=year,
        summary=summary,
        category_breakdown=category_breakdown,
        weekly_breakdown=weekly_breakdown
    )

@router.get("/history/analytics/trends")
async def get_spending_trends(
    months: int = Query(6, ge=1, le=24, description="Number of months to analyze"),
    current_student: dict = Depends(get_current_student),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get spending trends over time"""
    crud = TransactionCRUD(db)
    end_date = datetime.utcnow()
    
    monthly_data = []
    
    for i in range(months):
        # Calculate month boundaries
        if i == 0:
            month_end = end_date
            month_start = month_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            month_end = month_start - timedelta(days=1)
            month_start = month_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        summary = await crud.get_transaction_summary(
            student_id=str(current_student["_id"]),
            start_date=month_start,
            end_date=month_end
        )
        
        monthly_data.append({
            "month": month_start.strftime("%Y-%m"),
            "month_name": month_start.strftime("%B %Y"),
            "total_income": summary.total_income,
            "total_expense": summary.total_expense,
            "net_balance": summary.net_balance,
            "transaction_count": summary.transaction_count,
            "daily_average": summary.daily_average
        })
    
    # Reverse to get chronological order
    monthly_data.reverse()
    
    return {
        "period": f"Last {months} months",
        "monthly_data": monthly_data
    }

@router.get("/history/analytics/patterns")
async def get_spending_patterns(
    current_student: dict = Depends(get_current_student),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Analyze spending patterns (day of week, time of day, etc.)"""
    crud = TransactionCRUD(db)
    
    # Get last 3 months of data
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=90)
    
    # Aggregate by day of week
    pipeline = [
        {
            "$match": {
                "student_id": str(current_student["_id"]),
                "type": "expense",
                "transaction_date": {"$gte": start_date, "$lte": end_date}
            }
        },
        {
            "$group": {
                "_id": {"$dayOfWeek": "$transaction_date"},
                "total_amount": {"$sum": "$amount"},
                "avg_amount": {"$avg": "$amount"},
                "transaction_count": {"$sum": 1}
            }
        },
        {"$sort": {"_id": 1}}
    ]
    
    day_of_week_results = await db.transactions.aggregate(pipeline).to_list(length=None)
    
    # Convert day numbers to names
    day_names = ["", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    day_patterns = []
    
    for result in day_of_week_results:
        day_patterns.append({
            "day": day_names[result["_id"]],
            "day_number": result["_id"],
            "total_amount": result["total_amount"],
            "avg_amount": result["avg_amount"],
            "transaction_count": result["transaction_count"]
        })
    
    # Aggregate by hour of day
    pipeline[1]["$group"]["_id"] = {"$hour": "$transaction_date"}
    hour_results = await db.transactions.aggregate(pipeline).to_list(length=None)
    
    hour_patterns = []
    for result in hour_results:
        hour_patterns.append({
            "hour": result["_id"],
            "hour_label": f"{result['_id']:02d}:00",
            "total_amount": result["total_amount"],
            "avg_amount": result["avg_amount"],
            "transaction_count": result["transaction_count"]
        })
    
    return {
        "analysis_period": {
            "start_date": start_date,
            "end_date": end_date,
            "days": 90
        },
        "day_of_week_patterns": day_patterns,
        "hour_of_day_patterns": sorted(hour_patterns, key=lambda x: x["hour"])
    }

@router.get("/history/export/csv")
async def export_transactions_csv(
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    category_id: Optional[str] = Query(None, description="Filter by category"),
    type: Optional[str] = Query(None, description="Filter by type"),
    current_student: dict = Depends(get_current_student),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Export transactions to CSV"""
    crud = TransactionCRUD(db)
    
    # Default to last 3 months if no dates provided
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=90)
    if not end_date:
        end_date = datetime.utcnow()
    
    filters = TransactionFilter(
        type=type,
        category_id=category_id,
        start_date=start_date,
        end_date=end_date
    )
    
    # Get all transactions (no pagination for export)
    result = await crud.get_transactions(
        student_id=str(current_student["_id"]),
        skip=0,
        limit=10000,  # Large limit for export
        filters=filters,
        sort=TransactionSort.DATE_DESC
    )
    
    # Create CSV content
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        "Date", "Type", "Amount", "Currency", "Title", "Category",
        "Payment Method", "Account", "Notes", "Location"
    ])
    
    # Write data
    for transaction in result["transactions"]:
        writer.writerow([
            transaction.transaction_date.strftime("%Y-%m-%d %H:%M:%S"),
            transaction.type,
            transaction.amount,
            transaction.currency,
            transaction.title,
            transaction.category_id,  # Could be improved to show category name
            transaction.payment_method,
            transaction.account_name,
            transaction.notes or "",
            transaction.location.name if transaction.location else ""
        ])
    
    # Create response
    output.seek(0)
    
    return StreamingResponse(
        io.StringIO(output.getvalue()),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=transactions_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"
        }
    )

@router.get("/history/statistics")
async def get_statistics(
    current_student: dict = Depends(get_current_student),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get overall statistics and insights"""
    crud = TransactionCRUD(db)
    
    # Get various time periods
    now = datetime.utcnow()
    
    # This month
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_summary = await crud.get_transaction_summary(
        student_id=str(current_student["_id"]),
        start_date=month_start,
        end_date=now
    )
    
    # Last month
    if month_start.month == 1:
        last_month_start = month_start.replace(year=month_start.year - 1, month=12)
    else:
        last_month_start = month_start.replace(month=month_start.month - 1)
    
    last_month_end = month_start - timedelta(days=1)
    last_month_summary = await crud.get_transaction_summary(
        student_id=str(current_student["_id"]),
        start_date=last_month_start,
        end_date=last_month_end
    )
    
    # Calculate changes
    expense_change = 0
    if last_month_summary.total_expense > 0:
        expense_change = ((month_summary.total_expense - last_month_summary.total_expense) / 
                         last_month_summary.total_expense) * 100
    
    income_change = 0
    if last_month_summary.total_income > 0:
        income_change = ((month_summary.total_income - last_month_summary.total_income) / 
                        last_month_summary.total_income) * 100
    
    # Get top categories this month
    top_categories = await crud.get_category_breakdown(
        student_id=str(current_student["_id"]),
        start_date=month_start,
        end_date=now,
        transaction_type="expense"
    )
    
    # Get all-time stats
    all_time_summary = await crud.get_transaction_summary(
        student_id=str(current_student["_id"])
    )
    
    return {
        "current_month": {
            "summary": month_summary,
            "vs_last_month": {
                "expense_change_percent": round(expense_change, 2),
                "income_change_percent": round(income_change, 2)
            }
        },
        "last_month": {
            "summary": last_month_summary
        },
        "all_time": {
            "summary": all_time_summary
        },
        "top_categories": top_categories[:5],  # Top 5 categories
        "insights": {
            "days_tracked": (now - month_start).days + 1,
            "avg_daily_expense": month_summary.daily_average,
            "most_active_category": top_categories[0].category_name if top_categories else None
        }
    }