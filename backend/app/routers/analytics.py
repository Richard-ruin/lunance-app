# app/routers/analytics.py (enhanced version)
from fastapi import APIRouter, Depends, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from bson import ObjectId
import calendar

from ..middleware.auth_middleware import get_current_verified_user
from ..database import get_database
from ..utils.analytics_helpers import (
    calculate_trend_analysis, get_spending_patterns,
    generate_financial_insights, calculate_category_variance,
    # New dashboard analytics helpers
    calculate_dashboard_metrics, get_quick_stats, get_monthly_comparison,
    get_income_expense_trend, get_category_breakdown, get_daily_spending_pattern,
    get_weekly_summary, get_yearly_overview, analyze_spending_habits, get_peak_spending_times
)
from ..utils.exceptions import CustomHTTPException

router = APIRouter(prefix="/analytics", tags=["Analytics"])

# Keep all your existing endpoints
@router.get("/overview", response_model=Dict[str, Any])
async def get_analytics_overview(
    period: str = Query("monthly", pattern="^(weekly|monthly|quarterly|yearly)$"),
    current_user: Dict[str, Any] = Depends(get_current_verified_user),
    db = Depends(get_database)
):
    """Overview pemasukan/pengeluaran dengan insights"""
    # Your existing implementation...
    pass

@router.get("/by-category", response_model=Dict[str, Any])
async def get_analytics_by_category(
    type: str = Query("pengeluaran", pattern="^(pemasukan|pengeluaran|both)$"),
    period: str = Query("monthly", pattern="^(weekly|monthly|quarterly|yearly)$"),
    limit: int = Query(10, ge=1, le=50),
    current_user: Dict[str, Any] = Depends(get_current_verified_user),
    db = Depends(get_database)
):
    """Breakdown by category dengan detailed analysis"""
    
    date_ranges = calculate_period_ranges(period, datetime.utcnow())
    
    # Build aggregation pipeline
    match_stage = {
        "user_id": ObjectId(current_user["id"]),
        "date": {
            "$gte": date_ranges["current_start"],
            "$lte": date_ranges["current_end"]
        }
    }
    
    if type != "both":
        match_stage["type"] = type
    
    pipeline = [
        {"$match": match_stage},
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
            "$group": {
                "_id": {
                    "category_id": "$category_id",
                    "category_name": "$category.nama_kategori",
                    "category_icon": "$category.icon",
                    "category_color": "$category.color",
                    "type": "$type"
                },
                "total_amount": {"$sum": "$amount"},
                "transaction_count": {"$sum": 1},
                "avg_amount": {"$avg": "$amount"},
                "min_amount": {"$min": "$amount"},
                "max_amount": {"$max": "$amount"}
            }
        },
        {"$sort": {"total_amount": -1}},
        {"$limit": limit}
    ]
    
    results = await db.transactions.aggregate(pipeline).to_list(length=limit)
    
    # Calculate totals for percentage calculation
    total_amount = sum(result["total_amount"] for result in results)
    
    # Format results
    categories = []
    for result in results:
        percentage = (result["total_amount"] / total_amount * 100) if total_amount > 0 else 0
        
        categories.append({
            "category": {
                "id": str(result["_id"]["category_id"]),
                "nama": result["_id"]["category_name"],
                "icon": result["_id"]["category_icon"],
                "color": result["_id"]["category_color"]
            },
            "type": result["_id"]["type"],
            "total_amount": result["total_amount"],
            "percentage": round(percentage, 2),
            "transaction_count": result["transaction_count"],
            "avg_amount": round(result["avg_amount"], 2),
            "min_amount": result["min_amount"],
            "max_amount": result["max_amount"]
        })
    
    # Get previous period for comparison
    previous_data = await get_category_comparison_data(
        current_user["id"], date_ranges["previous_start"], date_ranges["previous_end"], type, db
    )
    
    return {
        "period": period,
        "type": type,
        "total_amount": total_amount,
        "categories": categories,
        "comparison": previous_data,
        "insights": {
            "top_category": categories[0]["category"]["nama"] if categories else None,
            "most_frequent": max(categories, key=lambda x: x["transaction_count"])["category"]["nama"] if categories else None,
            "highest_avg": max(categories, key=lambda x: x["avg_amount"])["category"]["nama"] if categories else None
        }
    }

@router.get("/trends", response_model=Dict[str, Any])
async def get_trends_analysis(
    period: str = Query("monthly", pattern="^(daily|weekly|monthly)$"),
    duration: int = Query(12, ge=3, le=24),  # months/weeks/days
    type: str = Query("both", pattern="^(pemasukan|pengeluaran|both)$"),
    current_user: Dict[str, Any] = Depends(get_current_verified_user),
    db = Depends(get_database)
):
    """Trend analysis dengan forecasting"""
    
    # Calculate date range
    now = datetime.utcnow()
    if period == "daily":
        start_date = now - timedelta(days=duration)
        group_format = "%Y-%m-%d"
    elif period == "weekly":
        start_date = now - timedelta(weeks=duration)
        group_format = "%Y-W%U"
    else:  # monthly
        start_date = now - timedelta(days=duration * 30)
        group_format = "%Y-%m"
    
    # Build aggregation pipeline
    match_stage = {
        "user_id": ObjectId(current_user["id"]),
        "date": {"$gte": start_date, "$lte": now}
    }
    
    if type != "both":
        match_stage["type"] = type
    
    pipeline = [
        {"$match": match_stage},
        {
            "$group": {
                "_id": {
                    "period": {"$dateToString": {"format": group_format, "date": "$date"}},
                    "type": "$type"
                },
                "total_amount": {"$sum": "$amount"},
                "transaction_count": {"$sum": 1},
                "avg_amount": {"$avg": "$amount"}
            }
        },
        {"$sort": {"_id.period": 1}}
    ]
    
    results = await db.transactions.aggregate(pipeline).to_list(length=None)
    
    # Process results into time series
    trends = {}
    for result in results:
        period_key = result["_id"]["period"]
        trans_type = result["_id"]["type"]
        
        if period_key not in trends:
            trends[period_key] = {
                "period": period_key,
                "pemasukan": 0,
                "pengeluaran": 0,
                "balance": 0,
                "transaction_count": 0
            }
        
        trends[period_key][trans_type] = result["total_amount"]
        trends[period_key]["transaction_count"] += result["transaction_count"]
    
    # Calculate balances
    for trend in trends.values():
        trend["balance"] = trend["pemasukan"] - trend["pengeluaran"]
    
    trend_list = list(trends.values())
    
    # Calculate trend statistics
    trend_stats = calculate_trend_analysis(trend_list, type)
    
    return {
        "period": period,
        "duration": duration,
        "type": type,
        "trends": trend_list,
        "statistics": trend_stats,
        "forecast": generate_simple_forecast(trend_list, 3)  # 3 periods ahead
    }

@router.get("/comparison", response_model=Dict[str, Any])
async def get_period_comparison(
    compare_type: str = Query("month", pattern="^(month|quarter|year)$"),
    periods: int = Query(2, ge=2, le=12),
    current_user: Dict[str, Any] = Depends(get_current_verified_user),
    db = Depends(get_database)
):
    """Period comparison analysis"""
    
    now = datetime.utcnow()
    comparisons = []
    
    for i in range(periods):
        if compare_type == "month":
            if now.month - i <= 0:
                period_date = now.replace(year=now.year - 1, month=12 + (now.month - i))
            else:
                period_date = now.replace(month=now.month - i)
            
            start_date = period_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if period_date.month == 12:
                end_date = start_date.replace(year=period_date.year + 1, month=1)
            else:
                end_date = start_date.replace(month=period_date.month + 1)
            
            period_label = period_date.strftime("%B %Y")
            
        elif compare_type == "quarter":
            quarter = ((now.month - 1) // 3) - i
            year = now.year
            if quarter < 0:
                quarter = 3 + quarter + 1  # Adjust for previous year
                year -= 1
            
            start_month = quarter * 3 + 1
            start_date = datetime(year, start_month, 1)
            end_date = datetime(year, start_month + 3, 1) if start_month + 3 <= 12 else datetime(year + 1, 1, 1)
            period_label = f"Q{quarter + 1} {year}"
            
        else:  # year
            year = now.year - i
            start_date = datetime(year, 1, 1)
            end_date = datetime(year + 1, 1, 1)
            period_label = str(year)
        
        # Get period data
        period_data = await get_period_financial_data(
            current_user["id"], start_date, end_date, db
        )
        
        comparisons.append({
            "period": period_label,
            "start_date": start_date,
            "end_date": end_date,
            "total_pemasukan": period_data["total_pemasukan"],
            "total_pengeluaran": period_data["total_pengeluaran"],
            "balance": period_data["total_pemasukan"] - period_data["total_pengeluaran"],
            "transaction_count": period_data["transaction_count"],
            "avg_transaction": period_data["avg_amount"],
            "savings_rate": calculate_savings_rate(period_data)
        })
    
    # Calculate period-over-period changes
    for i in range(1, len(comparisons)):
        current = comparisons[i-1]
        previous = comparisons[i]
        
        current["income_change"] = calculate_growth_rate(current["total_pemasukan"], previous["total_pemasukan"])
        current["expense_change"] = calculate_growth_rate(current["total_pengeluaran"], previous["total_pengeluaran"])
        current["balance_change"] = current["balance"] - previous["balance"]
    
    return {
        "compare_type": compare_type,
        "periods": periods,
        "comparisons": comparisons,
        "summary": {
            "best_period": max(comparisons, key=lambda x: x["balance"])["period"],
            "highest_income": max(comparisons, key=lambda x: x["total_pemasukan"])["period"],
            "lowest_expense": min(comparisons, key=lambda x: x["total_pengeluaran"])["period"],
            "avg_monthly_income": sum(c["total_pemasukan"] for c in comparisons) / len(comparisons),
            "avg_monthly_expense": sum(c["total_pengeluaran"] for c in comparisons) / len(comparisons)
        }
    }

@router.get("/top-spending", response_model=Dict[str, Any])
async def get_top_spending_analysis(
    period: str = Query("monthly", pattern="^(weekly|monthly|quarterly)$"),
    limit: int = Query(10, ge=5, le=50),
    group_by: str = Query("category", pattern="^(category|merchant|day|payment_method)$"),
    current_user: Dict[str, Any] = Depends(get_current_verified_user),
    db = Depends(get_database)
):
    """Top spending analysis dengan multiple grouping options"""
    
    date_ranges = calculate_period_ranges(period, datetime.utcnow())
    
    # Build aggregation based on group_by
    if group_by == "category":
        pipeline = [
            {
                "$match": {
                    "user_id": ObjectId(current_user["id"]),
                    "type": "pengeluaran",
                    "date": {
                        "$gte": date_ranges["current_start"],
                        "$lte": date_ranges["current_end"]
                    }
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
                "$group": {
                    "_id": {
                        "category_id": "$category_id",
                        "category_name": "$category.nama_kategori",
                        "category_icon": "$category.icon",
                        "category_color": "$category.color"
                    },
                    "total_amount": {"$sum": "$amount"},
                    "transaction_count": {"$sum": 1},
                    "avg_amount": {"$avg": "$amount"},
                    "transactions": {"$push": "$$ROOT"}
                }
            }
        ]
    elif group_by == "payment_method":
        pipeline = [
            {
                "$match": {
                    "user_id": ObjectId(current_user["id"]),
                    "type": "pengeluaran",
                    "date": {
                        "$gte": date_ranges["current_start"],
                        "$lte": date_ranges["current_end"]
                    }
                }
            },
            {
                "$group": {
                    "_id": "$payment_method",
                    "total_amount": {"$sum": "$amount"},
                    "transaction_count": {"$sum": 1},
                    "avg_amount": {"$avg": "$amount"}
                }
            }
        ]
    elif group_by == "day":
        pipeline = [
            {
                "$match": {
                    "user_id": ObjectId(current_user["id"]),
                    "type": "pengeluaran",
                    "date": {
                        "$gte": date_ranges["current_start"],
                        "$lte": date_ranges["current_end"]
                    }
                }
            },
            {
                "$group": {
                    "_id": {"$dayOfWeek": "$date"},
                    "total_amount": {"$sum": "$amount"},
                    "transaction_count": {"$sum": 1},
                    "avg_amount": {"$avg": "$amount"}
                }
            }
        ]
    else:  # merchant (based on description patterns)
        pipeline = [
            {
                "$match": {
                    "user_id": ObjectId(current_user["id"]),
                    "type": "pengeluaran",
                    "date": {
                        "$gte": date_ranges["current_start"],
                        "$lte": date_ranges["current_end"]
                    }
                }
            },
            {
                "$group": {
                    "_id": "$description",
                    "total_amount": {"$sum": "$amount"},
                    "transaction_count": {"$sum": 1},
                    "avg_amount": {"$avg": "$amount"}
                }
            }
        ]
    
    pipeline.extend([
        {"$sort": {"total_amount": -1}},
        {"$limit": limit}
    ])
    
    results = await db.transactions.aggregate(pipeline).to_list(length=limit)
    
    # Calculate total for percentages
    total_spending = sum(result["total_amount"] for result in results)
    
    # Format results based on group_by
    formatted_results = []
    for result in results:
        percentage = (result["total_amount"] / total_spending * 100) if total_spending > 0 else 0
        
        if group_by == "category":
            formatted_results.append({
                "category": {
                    "id": str(result["_id"]["category_id"]),
                    "nama": result["_id"]["category_name"],
                    "icon": result["_id"]["category_icon"],
                    "color": result["_id"]["category_color"]
                },
                "total_amount": result["total_amount"],
                "percentage": round(percentage, 2),
                "transaction_count": result["transaction_count"],
                "avg_amount": round(result["avg_amount"], 2)
            })
        elif group_by == "day":
            day_names = ["", "Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]
            formatted_results.append({
                "day": day_names[result["_id"]],
                "day_number": result["_id"],
                "total_amount": result["total_amount"],
                "percentage": round(percentage, 2),
                "transaction_count": result["transaction_count"],
                "avg_amount": round(result["avg_amount"], 2)
            })
        else:
            formatted_results.append({
                "name": result["_id"],
                "total_amount": result["total_amount"],
                "percentage": round(percentage, 2),
                "transaction_count": result["transaction_count"],
                "avg_amount": round(result["avg_amount"], 2)
            })
    
    return {
        "period": period,
        "group_by": group_by,
        "total_spending": total_spending,
        "top_spending": formatted_results,
        "insights": {
            "highest_spending": formatted_results[0] if formatted_results else None,
            "most_frequent": max(formatted_results, key=lambda x: x["transaction_count"]) if formatted_results else None,
            "concentration_ratio": sum(r["percentage"] for r in formatted_results[:3])  # Top 3 concentration
        }
    }

@router.get("/dashboard-summary")
async def get_dashboard_analytics_summary(
    current_user: Dict[str, Any] = Depends(get_current_verified_user)
):
    """Get comprehensive dashboard analytics summary"""
    try:
        db = await get_database()
        user_id = ObjectId(current_user["id"])
        
        # Get comprehensive dashboard data
        dashboard_data = await calculate_dashboard_metrics(db, user_id)
        
        return {
            "status": "success",
            "data": dashboard_data,
            "metadata": {
                "generated_at": datetime.utcnow(),
                "user_id": current_user["id"]
            }
        }
        
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Failed to fetch dashboard summary: {str(e)}",
            error_code="DASHBOARD_ANALYTICS_ERROR"
        )

@router.get("/income-expense-trend")
async def get_income_expense_trend_data(
    period: str = Query("6months", regex="^(3months|6months|1year|2years)$"),
    current_user: Dict[str, Any] = Depends(get_current_verified_user)
):
    """Get income vs expense trend with chart data"""
    try:
        db = await get_database()
        user_id = ObjectId(current_user["id"])
        
        trend_data = await get_income_expense_trend(db, user_id, period)
        
        return {
            "chart_type": "line",
            "data": {
                "labels": trend_data["labels"],
                "datasets": [
                    {
                        "label": "Pemasukan",
                        "data": trend_data["income_data"],
                        "borderColor": "#10B981",
                        "backgroundColor": "rgba(16, 185, 129, 0.1)",
                        "tension": 0.4
                    },
                    {
                        "label": "Pengeluaran",
                        "data": trend_data["expense_data"],
                        "borderColor": "#EF4444",
                        "backgroundColor": "rgba(239, 68, 68, 0.1)",
                        "tension": 0.4
                    }
                ]
            },
            "summary": {
                "avg_income": trend_data["avg_income"],
                "avg_expense": trend_data["avg_expense"],
                "trend_direction": trend_data["trend_direction"],
                "highest_income_month": trend_data["highest_income_month"],
                "highest_expense_month": trend_data["highest_expense_month"]
            }
        }
        
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Failed to fetch trend data: {str(e)}",
            error_code="TREND_DATA_ERROR"
        )

@router.get("/category-breakdown")
async def get_category_breakdown_data(
    period: str = Query("month", regex="^(week|month|quarter|year)$"),
    jenis: str = Query("pengeluaran", regex="^(pemasukan|pengeluaran|both)$"),
    current_user: Dict[str, Any] = Depends(get_current_verified_user)
):
    """Get category breakdown with pie chart data"""
    try:
        db = await get_database()
        user_id = ObjectId(current_user["id"])
        
        breakdown_data = await get_category_breakdown(db, user_id, period, jenis)
        
        return {
            "chart_type": "pie",
            "data": {
                "labels": breakdown_data["labels"],
                "datasets": [{
                    "data": breakdown_data["amounts"],
                    "backgroundColor": breakdown_data["colors"],
                    "borderWidth": 2,
                    "borderColor": "#ffffff"
                }]
            },
            "summary": {
                "total_amount": breakdown_data["total_amount"],
                "top_category": breakdown_data["top_category"],
                "top_percentage": breakdown_data["top_percentage"],
                "category_count": len(breakdown_data["labels"])
            },
            "details": breakdown_data["category_details"]
        }
        
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Failed to fetch category breakdown: {str(e)}",
            error_code="CATEGORY_BREAKDOWN_ERROR"
        )

@router.get("/daily-spending")
async def get_daily_spending_pattern(
    days: int = Query(30, ge=7, le=90),
    current_user: Dict[str, Any] = Depends(get_current_verified_user)
):
    """Get daily spending pattern analysis"""
    try:
        db = await get_database()
        user_id = ObjectId(current_user["id"])
        
        spending_data = await get_daily_spending_pattern(db, user_id, days)
        
        return {
            "chart_type": "bar",
            "data": {
                "labels": spending_data["dates"],
                "datasets": [{
                    "label": "Daily Spending",
                    "data": spending_data["amounts"],
                    "backgroundColor": "rgba(59, 130, 246, 0.6)",
                    "borderColor": "#3B82F6",
                    "borderWidth": 1
                }]
            },
            "analysis": {
                "avg_daily_spending": spending_data["avg_daily"],
                "highest_spending_day": spending_data["highest_day"],
                "lowest_spending_day": spending_data["lowest_day"],
                "spending_trend": spending_data["trend"],
                "weekday_vs_weekend": spending_data["weekday_weekend_comparison"]
            }
        }
        
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Failed to fetch daily spending: {str(e)}",
            error_code="DAILY_SPENDING_ERROR"
        )

@router.get("/weekly-summary")
async def get_weekly_financial_summary(
    weeks: int = Query(12, ge=4, le=52),
    current_user: Dict[str, Any] = Depends(get_current_verified_user)
):
    """Get weekly financial summary"""
    try:
        db = await get_database()
        user_id = ObjectId(current_user["id"])
        
        weekly_data = await get_weekly_summary(db, user_id, weeks)
        
        return {
            "chart_type": "line",
            "data": {
                "labels": weekly_data["week_labels"],
                "datasets": [
                    {
                        "label": "Weekly Income",
                        "data": weekly_data["weekly_income"],
                        "borderColor": "#10B981",
                        "backgroundColor": "rgba(16, 185, 129, 0.1)"
                    },
                    {
                        "label": "Weekly Expense",
                        "data": weekly_data["weekly_expense"],
                        "borderColor": "#EF4444",
                        "backgroundColor": "rgba(239, 68, 68, 0.1)"
                    },
                    {
                        "label": "Net Savings",
                        "data": weekly_data["weekly_savings"],
                        "borderColor": "#8B5CF6",
                        "backgroundColor": "rgba(139, 92, 246, 0.1)"
                    }
                ]
            },
            "summary": {
                "avg_weekly_income": weekly_data["avg_weekly_income"],
                "avg_weekly_expense": weekly_data["avg_weekly_expense"],
                "avg_weekly_savings": weekly_data["avg_weekly_savings"],
                "best_savings_week": weekly_data["best_week"],
                "worst_savings_week": weekly_data["worst_week"]
            }
        }
        
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Failed to fetch weekly summary: {str(e)}",
            error_code="WEEKLY_SUMMARY_ERROR"
        )

@router.get("/yearly-overview")
async def get_yearly_financial_overview(
    current_user: Dict[str, Any] = Depends(get_current_verified_user)
):
    """Get yearly financial overview"""
    try:
        db = await get_database()
        user_id = ObjectId(current_user["id"])
        
        yearly_data = await get_yearly_overview(db, user_id)
        
        return {
            "monthly_breakdown": {
                "chart_type": "bar",
                "data": {
                    "labels": yearly_data["months"],
                    "datasets": [
                        {
                            "label": "Income",
                            "data": yearly_data["monthly_income"],
                            "backgroundColor": "#10B981"
                        },
                        {
                            "label": "Expense",
                            "data": yearly_data["monthly_expense"],
                            "backgroundColor": "#EF4444"
                        }
                    ]
                }
            },
            "summary": {
                "total_income": yearly_data["total_income"],
                "total_expense": yearly_data["total_expense"],
                "net_savings": yearly_data["net_savings"],
                "savings_rate": yearly_data["savings_rate"],
                "best_month": yearly_data["best_month"],
                "worst_month": yearly_data["worst_month"],
                "total_transactions": yearly_data["transaction_count"]
            },
            "quarterly_analysis": yearly_data["quarterly_breakdown"]
        }
        
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Failed to fetch yearly overview: {str(e)}",
            error_code="YEARLY_OVERVIEW_ERROR"
        )

@router.get("/spending-habits")
async def analyze_user_spending_habits(
    current_user: Dict[str, Any] = Depends(get_current_verified_user)
):
    """Analyze user spending habits and patterns"""
    try:
        db = await get_database()
        user_id = ObjectId(current_user["id"])
        
        habits_data = await analyze_spending_habits(db, user_id)
        
        return {
            "spending_personality": habits_data["personality_type"],
            "top_categories": habits_data["preferred_categories"],
            "spending_frequency": habits_data["frequency_analysis"],
            "time_patterns": habits_data["time_patterns"],
            "recommendations": habits_data["recommendations"],
            "financial_health_score": habits_data["health_score"],
            "alerts": habits_data["alerts"]
        }
        
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Failed to analyze spending habits: {str(e)}",
            error_code="SPENDING_HABITS_ERROR"
        )

@router.get("/peak-spending-times")
async def get_peak_spending_analysis(
    current_user: Dict[str, Any] = Depends(get_current_verified_user)
):
    """Analyze peak spending times and patterns"""
    try:
        db = await get_database()
        user_id = ObjectId(current_user["id"])
        
        peak_data = await get_peak_spending_times(db, user_id)
        
        return {
            "hourly_pattern": {
                "chart_type": "bar",
                "data": {
                    "labels": peak_data["hours"],
                    "datasets": [{
                        "label": "Spending by Hour",
                        "data": peak_data["hourly_amounts"],
                        "backgroundColor": "rgba(99, 102, 241, 0.6)"
                    }]
                }
            },
            "daily_pattern": {
                "chart_type": "radar",
                "data": {
                    "labels": peak_data["days_of_week"],
                    "datasets": [{
                        "label": "Spending by Day",
                        "data": peak_data["daily_amounts"],
                        "backgroundColor": "rgba(16, 185, 129, 0.2)",
                        "borderColor": "#10B981"
                    }]
                }
            },
            "insights": {
                "peak_hour": peak_data["peak_hour"],
                "peak_day": peak_data["peak_day"],
                "lowest_activity": peak_data["lowest_activity"],
                "weekend_vs_weekday": peak_data["weekend_comparison"]
            }
        }
        
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Failed to analyze peak spending times: {str(e)}",
            error_code="PEAK_SPENDING_ERROR"
        )

# Helper functions for existing endpoints
async def calculate_period_ranges(period: str, now: datetime) -> Dict[str, datetime]:
    """Calculate date ranges for different periods"""
    if period == "weekly":
        current_start = now - timedelta(days=7)
        current_end = now
        previous_start = current_start - timedelta(days=7)
        previous_end = current_start
    elif period == "monthly":
        current_start = datetime(now.year, now.month, 1)
        if now.month == 12:
            current_end = datetime(now.year + 1, 1, 1)
        else:
            current_end = datetime(now.year, now.month + 1, 1)
        
        if current_start.month == 1:
            previous_start = datetime(current_start.year - 1, 12, 1)
            previous_end = current_start
        else:
            previous_start = datetime(current_start.year, current_start.month - 1, 1)
            previous_end = current_start
    elif period == "quarterly":
        quarter = (now.month - 1) // 3
        current_start = datetime(now.year, quarter * 3 + 1, 1)
        current_end = datetime(now.year, (quarter + 1) * 3 + 1, 1) if quarter < 3 else datetime(now.year + 1, 1, 1)
        
        prev_quarter = quarter - 1 if quarter > 0 else 3
        prev_year = now.year if quarter > 0 else now.year - 1
        previous_start = datetime(prev_year, prev_quarter * 3 + 1, 1)
        previous_end = current_start
    else:  # yearly
        current_start = datetime(now.year, 1, 1)
        current_end = datetime(now.year + 1, 1, 1)
        previous_start = datetime(now.year - 1, 1, 1)
        previous_end = current_start
    
    return {
        "current_start": current_start,
        "current_end": current_end,
        "previous_start": previous_start,
        "previous_end": previous_end
    }

async def get_period_financial_data(user_id: str, start_date: datetime, end_date: datetime, db) -> Dict[str, Any]:
    """Get financial data for a specific period"""
    pipeline = [
        {
            "$match": {
                "user_id": ObjectId(user_id),
                "date": {"$gte": start_date, "$lt": end_date}
            }
        },
        {
            "$group": {
                "_id": "$jenis",
                "total": {"$sum": "$amount"},
                "count": {"$sum": 1},
                "avg": {"$avg": "$amount"}
            }
        }
    ]
    
    result = await db.transactions.aggregate(pipeline).to_list(10)
    
    pemasukan_data = next((r for r in result if r["_id"] == "pemasukan"), {"total": 0, "count": 0, "avg": 0})
    pengeluaran_data = next((r for r in result if r["_id"] == "pengeluaran"), {"total": 0, "count": 0, "avg": 0})
    
    return {
        "total_pemasukan": pemasukan_data["total"],
        "total_pengeluaran": pengeluaran_data["total"],
        "transaction_count": pemasukan_data["count"] + pengeluaran_data["count"],
        "avg_amount": (pemasukan_data["avg"] + pengeluaran_data["avg"]) / 2 if (pemasukan_data["avg"] + pengeluaran_data["avg"]) > 0 else 0
    }

def calculate_growth_rate(current: float, previous: float) -> float:
    """Calculate growth rate percentage"""
    if previous == 0:
        return 0.0
    return round(((current - previous) / previous) * 100, 2)

def calculate_financial_health_score(data: Dict[str, Any], balance: float) -> int:
    """Calculate financial health score (0-100)"""
    score = 50  # Base score
    
    # Positive balance
    if balance > 0:
        score += 20
    elif balance < 0:
        score -= 20
    
    # Income vs expense ratio
    if data["total_pemasukan"] > 0:
        expense_ratio = data["total_pengeluaran"] / data["total_pemasukan"]
        if expense_ratio < 0.5:
            score += 20
        elif expense_ratio < 0.8:
            score += 10
        elif expense_ratio > 1.2:
            score -= 20
    
    # Transaction frequency (activity)
    if data["transaction_count"] > 10:
        score += 10
    elif data["transaction_count"] < 3:
        score -= 10
    
    return max(0, min(100, score))

def calculate_savings_rate(data: Dict[str, Any]) -> float:
    """Calculate savings rate percentage"""
    if data["total_pemasukan"] == 0:
        return 0.0
    
    savings = data["total_pemasukan"] - data["total_pengeluaran"]
    return round((savings / data["total_pemasukan"]) * 100, 2)

async def get_category_comparison_data(user_id: str, start_date: datetime, end_date: datetime, jenis: str, db) -> Dict[str, Any]:
    """Get category comparison data for previous period"""
    # Implementation for category comparison
    return {"message": "Previous period comparison data"}

def generate_simple_forecast(trend_list: List[Dict[str, Any]], periods: int) -> List[Dict[str, Any]]:
    """Generate simple forecast based on trend data"""
    if len(trend_list) < 2:
        return []
    
    # Simple linear trend calculation
    last_periods = trend_list[-3:] if len(trend_list) >= 3 else trend_list
    
    # Calculate average change
    income_changes = []
    expense_changes = []
    
    for i in range(1, len(last_periods)):
        income_changes.append(last_periods[i]["pemasukan"] - last_periods[i-1]["pemasukan"])
        expense_changes.append(last_periods[i]["pengeluaran"] - last_periods[i-1]["pengeluaran"])
    
    avg_income_change = sum(income_changes) / len(income_changes) if income_changes else 0
    avg_expense_change = sum(expense_changes) / len(expense_changes) if expense_changes else 0
    
    # Generate forecast
    forecasts = []
    last_data = trend_list[-1]
    
    for i in range(1, periods + 1):
        forecast_income = last_data["pemasukan"] + (avg_income_change * i)
        forecast_expense = last_data["pengeluaran"] + (avg_expense_change * i)
        
        forecasts.append({
            "period": f"Forecast +{i}",
            "pemasukan": max(0, forecast_income),
            "pengeluaran": max(0, forecast_expense),
            "balance": forecast_income - forecast_expense,
            "is_forecast": True
        })
    
    return forecasts