# app/utils/analytics_helpers.py
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from bson import ObjectId
import calendar

async def calculate_dashboard_metrics(db, user_id: ObjectId) -> Dict[str, Any]:
    """Calculate comprehensive dashboard metrics using aggregation pipeline"""
    
    # Current month date range
    now = datetime.now()
    start_of_month = datetime(now.year, now.month, 1)
    next_month = start_of_month.replace(month=start_of_month.month + 1) if start_of_month.month < 12 else start_of_month.replace(year=start_of_month.year + 1, month=1)
    
    # Previous month for comparison
    prev_month_start = (start_of_month - timedelta(days=1)).replace(day=1)
    prev_month_end = start_of_month - timedelta(days=1)
    
    # Main aggregation pipeline for current month metrics
    current_month_pipeline = [
        {
            "$match": {
                "user_id": user_id,
                "date": {"$gte": start_of_month, "$lt": next_month}
            }
        },
        {
            "$group": {
                "_id": "$jenis",
                "total": {"$sum": "$amount"},
                "count": {"$sum": 1}
            }
        }
    ]
    
    # Previous month pipeline for comparison
    prev_month_pipeline = [
        {
            "$match": {
                "user_id": user_id,
                "date": {"$gte": prev_month_start, "$lte": prev_month_end}
            }
        },
        {
            "$group": {
                "_id": "$jenis",
                "total": {"$sum": "$amount"}
            }
        }
    ]
    
    # Execute aggregations concurrently
    current_results = await db.transactions.aggregate(current_month_pipeline).to_list(10)
    prev_results = await db.transactions.aggregate(prev_month_pipeline).to_list(10)
    
    # Process current month results
    current_income = next((r["total"] for r in current_results if r["_id"] == "pemasukan"), 0)
    current_expense = next((r["total"] for r in current_results if r["_id"] == "pengeluaran"), 0)
    total_transactions = sum(r["count"] for r in current_results)
    
    # Process previous month results
    prev_income = next((r["total"] for r in prev_results if r["_id"] == "pemasukan"), 0)
    prev_expense = next((r["total"] for r in prev_results if r["_id"] == "pengeluaran"), 0)
    
    # Calculate metrics
    current_balance = current_income - current_expense
    monthly_savings = current_balance
    savings_rate = (monthly_savings / current_income * 100) if current_income > 0 else 0
    
    # Calculate changes vs last month
    income_change = ((current_income - prev_income) / prev_income * 100) if prev_income > 0 else 0
    expense_change = ((current_expense - prev_expense) / prev_expense * 100) if prev_expense > 0 else 0
    prev_savings = prev_income - prev_expense
    savings_change = ((monthly_savings - prev_savings) / abs(prev_savings) * 100) if prev_savings != 0 else 0
    
    # Get active goals count
    active_goals = await db.savings_goals.count_documents({
        "user_id": user_id,
        "is_achieved": False
    })
    
    # Get total saved in goals
    goals_pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": None, "total_saved": {"$sum": "$current_amount"}}}
    ]
    
    goals_result = await db.savings_goals.aggregate(goals_pipeline).to_list(1)
    total_saved_goals = goals_result[0]["total_saved"] if goals_result else 0
    
    return {
        "current_balance": current_balance,
        "monthly_income": current_income,
        "monthly_expense": current_expense,
        "monthly_savings": monthly_savings,
        "savings_rate": round(savings_rate, 2),
        "vs_last_month": {
            "income_change": round(income_change, 2),
            "expense_change": round(expense_change, 2),
            "savings_change": round(savings_change, 2)
        },
        "total_transactions": total_transactions,
        "active_goals": active_goals,
        "total_saved_goals": total_saved_goals
    }

async def get_quick_stats(db, user_id: ObjectId) -> Dict[str, Any]:
    """Get quick stats for dashboard fast menu"""
    
    now = datetime.now()
    today_start = datetime(now.year, now.month, now.day)
    week_start = today_start - timedelta(days=now.weekday())
    month_start = datetime(now.year, now.month, 1)
    
    # Aggregation pipeline for time-based stats
    pipeline = [
        {"$match": {"user_id": user_id}},
        {
            "$group": {
                "_id": None,
                "today_income": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$gte": ["$date", today_start]},
                                    {"$eq": ["$jenis", "pemasukan"]}
                                ]
                            },
                            "$amount", 0
                        ]
                    }
                },
                "today_expense": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$gte": ["$date", today_start]},
                                    {"$eq": ["$jenis", "pengeluaran"]}
                                ]
                            },
                            "$amount", 0
                        ]
                    }
                },
                "week_income": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$gte": ["$date", week_start]},
                                    {"$eq": ["$jenis", "pemasukan"]}
                                ]
                            },
                            "$amount", 0
                        ]
                    }
                },
                "week_expense": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$gte": ["$date", week_start]},
                                    {"$eq": ["$jenis", "pengeluaran"]}
                                ]
                            },
                            "$amount", 0
                        ]
                    }
                },
                "month_income": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$gte": ["$date", month_start]},
                                    {"$eq": ["$jenis", "pemasukan"]}
                                ]
                            },
                            "$amount", 0
                        ]
                    }
                },
                "month_expense": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$gte": ["$date", month_start]},
                                    {"$eq": ["$jenis", "pengeluaran"]}
                                ]
                            },
                            "$amount", 0
                        ]
                    }
                }
            }
        }
    ]
    
    result = await db.transactions.aggregate(pipeline).to_list(1)
    
    if result:
        stats = result[0]
        # Determine balance trend
        today_balance = stats["today_income"] - stats["today_expense"]
        week_balance = stats["week_income"] - stats["week_expense"]
        
        if today_balance > 0:
            balance_trend = "up"
        elif today_balance < 0:
            balance_trend = "down"
        else:
            balance_trend = "stable"
        
        return {
            "today_income": stats["today_income"],
            "today_expense": stats["today_expense"],
            "week_income": stats["week_income"],
            "week_expense": stats["week_expense"],
            "month_income": stats["month_income"],
            "month_expense": stats["month_expense"],
            "balance_trend": balance_trend
        }
    else:
        return {
            "today_income": 0,
            "today_expense": 0,
            "week_income": 0,
            "week_expense": 0,
            "month_income": 0,
            "month_expense": 0,
            "balance_trend": "stable"
        }

async def get_monthly_comparison(db, user_id: ObjectId) -> Dict[str, Any]:
    """Get detailed monthly comparison data"""
    
    now = datetime.now()
    current_month_start = datetime(now.year, now.month, 1)
    
    # Previous month calculation
    if now.month == 1:
        prev_month_start = datetime(now.year - 1, 12, 1)
        prev_month_end = datetime(now.year, 1, 1) - timedelta(days=1)
    else:
        prev_month_start = datetime(now.year, now.month - 1, 1)
        prev_month_end = current_month_start - timedelta(days=1)
    
    # Aggregation pipeline using $facet for parallel processing
    pipeline = [
        {"$match": {"user_id": user_id}},
        {
            "$facet": {
                "current_month": [
                    {"$match": {"date": {"$gte": current_month_start}}},
                    {
                        "$group": {
                            "_id": "$jenis",
                            "total": {"$sum": "$amount"},
                            "count": {"$sum": 1},
                            "avg": {"$avg": "$amount"}
                        }
                    }
                ],
                "previous_month": [
                    {"$match": {"date": {"$gte": prev_month_start, "$lte": prev_month_end}}},
                    {
                        "$group": {
                            "_id": "$jenis",
                            "total": {"$sum": "$amount"},
                            "count": {"$sum": 1},
                            "avg": {"$avg": "$amount"}
                        }
                    }
                ]
            }
        }
    ]
    
    result = await db.transactions.aggregate(pipeline).to_list(1)
    
    if result:
        data = result[0]
        
        # Process current month
        current_income = next((r["total"] for r in data["current_month"] if r["_id"] == "pemasukan"), 0)
        current_expense = next((r["total"] for r in data["current_month"] if r["_id"] == "pengeluaran"), 0)
        current_transactions = sum(r["count"] for r in data["current_month"])
        
        # Process previous month
        prev_income = next((r["total"] for r in data["previous_month"] if r["_id"] == "pemasukan"), 0)
        prev_expense = next((r["total"] for r in data["previous_month"] if r["_id"] == "pengeluaran"), 0)
        prev_transactions = sum(r["count"] for r in data["previous_month"])
        
        # Calculate percentage changes
        income_change = ((current_income - prev_income) / prev_income * 100) if prev_income > 0 else 0
        expense_change = ((current_expense - prev_expense) / prev_expense * 100) if prev_expense > 0 else 0
        
        current_savings = current_income - current_expense
        prev_savings = prev_income - prev_expense
        savings_change = ((current_savings - prev_savings) / abs(prev_savings) * 100) if prev_savings != 0 else 0
        
        return {
            "current_month": {
                "income": current_income,
                "expense": current_expense,
                "savings": current_savings,
                "transactions": current_transactions,
                "name": calendar.month_name[now.month]
            },
            "previous_month": {
                "income": prev_income,
                "expense": prev_expense,
                "savings": prev_savings,
                "transactions": prev_transactions,
                "name": calendar.month_name[prev_month_start.month]
            },
            "income_change": round(income_change, 2),
            "expense_change": round(expense_change, 2),
            "savings_change": round(savings_change, 2)
        }
    else:
        return {
            "current_month": {"income": 0, "expense": 0, "savings": 0, "transactions": 0, "name": calendar.month_name[now.month]},
            "previous_month": {"income": 0, "expense": 0, "savings": 0, "transactions": 0, "name": ""},
            "income_change": 0,
            "expense_change": 0,
            "savings_change": 0
        }

async def get_income_expense_trend(db, user_id: ObjectId, period: str) -> Dict[str, Any]:
    """Get income vs expense trend data for charts"""
    
    now = datetime.now()
    
    # Determine date range based on period
    if period == "3months":
        start_date = now - timedelta(days=90)
        group_format = "%Y-%m"
    elif period == "6months":
        start_date = now - timedelta(days=180)
        group_format = "%Y-%m"
    elif period == "1year":
        start_date = now - timedelta(days=365)
        group_format = "%Y-%m"
    else:  # 2years
        start_date = now - timedelta(days=730)
        group_format = "%Y-%m"
    
    # Aggregation pipeline for trend analysis 
    pipeline = [
        {"$match": {"user_id": user_id, "date": {"$gte": start_date}}},
        {
            "$group": {
                "_id": {
                    "period": {"$dateToString": {"format": group_format, "date": "$date"}},
                    "jenis": "$jenis"
                },
                "total": {"$sum": "$amount"}
            }
        },
        {"$sort": {"_id.period": 1}}
    ]
    
    result = await db.transactions.aggregate(pipeline).to_list(100)
    
    # Process results into chart format
    periods = {}
    for item in result:
        period_key = item["_id"]["period"]
        jenis = item["_id"]["jenis"]
        
        if period_key not in periods:
            periods[period_key] = {"pemasukan": 0, "pengeluaran": 0}
        
        periods[period_key][jenis] = item["total"]
    
    # Sort periods and create arrays
    sorted_periods = sorted(periods.keys())
    labels = []
    income_data = []
    expense_data = []
    
    for period in sorted_periods:
        if group_format == "%Y-%m":
            # Convert YYYY-MM to readable format
            year, month = period.split("-")
            month_name = calendar.month_abbr[int(month)]
            labels.append(f"{month_name} {year}")
        else:
            labels.append(period)
        
        income_data.append(periods[period]["pemasukan"])
        expense_data.append(periods[period]["pengeluaran"])
    
    # Calculate summary statistics
    avg_income = sum(income_data) / len(income_data) if income_data else 0
    avg_expense = sum(expense_data) / len(expense_data) if expense_data else 0
    
    # Determine trend direction
    if len(income_data) >= 2:
        income_trend = "up" if income_data[-1] > income_data[0] else "down"
    else:
        income_trend = "stable"
    
    # Find highest months
    highest_income_idx = income_data.index(max(income_data)) if income_data else 0
    highest_expense_idx = expense_data.index(max(expense_data)) if expense_data else 0
    
    return {
        "labels": labels,
        "income_data": income_data,
        "expense_data": expense_data,
        "avg_income": round(avg_income, 2),
        "avg_expense": round(avg_expense, 2),
       "trend_direction": income_trend,
       "highest_income_month": labels[highest_income_idx] if labels else "",
       "highest_expense_month": labels[highest_expense_idx] if labels else ""
   }

async def get_category_breakdown(db, user_id: ObjectId, period: str, jenis: str) -> Dict[str, Any]:
   """Get category breakdown with colors for pie charts"""
   
   now = datetime.now()
   
   # Determine date range
   if period == "week":
       start_date = now - timedelta(days=7)
   elif period == "month":
       start_date = datetime(now.year, now.month, 1)
   elif period == "quarter":
       quarter_start_month = ((now.month - 1) // 3) * 3 + 1
       start_date = datetime(now.year, quarter_start_month, 1)
   else:  # year
       start_date = datetime(now.year, 1, 1)
   
   # Build match criteria
   match_criteria = {
       "user_id": user_id,
       "date": {"$gte": start_date}
   }
   
   if jenis != "both":
       match_criteria["jenis"] = jenis
   
   # Aggregation pipeline with category lookup
   pipeline = [
       {"$match": match_criteria},
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
                   "jenis": "$jenis"
               },
               "total": {"$sum": "$amount"},
               "count": {"$sum": 1}
           }
       },
       {"$sort": {"total": -1}},
       {"$limit": 10}
   ]
   
   result = await db.transactions.aggregate(pipeline).to_list(10)
   
   # Define color palette for categories
   colors = [
       "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7",
       "#DDA0DD", "#98D8C8", "#F7DC6F", "#BB8FCE", "#85C1E9"
   ]
   
   labels = []
   amounts = []
   category_colors = []
   category_details = []
   total_amount = 0
   
   for i, item in enumerate(result):
       labels.append(item["_id"]["category_name"])
       amounts.append(item["total"])
       category_colors.append(colors[i % len(colors)])
       total_amount += item["total"]
       
       category_details.append({
           "category": item["_id"]["category_name"],
           "amount": item["total"],
           "count": item["count"],
           "percentage": 0  # Will be calculated below
       })
   
   # Calculate percentages
   for detail in category_details:
       detail["percentage"] = round((detail["amount"] / total_amount * 100), 2) if total_amount > 0 else 0
   
   # Top category info
   top_category = labels[0] if labels else ""
   top_percentage = category_details[0]["percentage"] if category_details else 0
   
   return {
       "labels": labels,
       "amounts": amounts,
       "colors": category_colors,
       "total_amount": total_amount,
       "top_category": top_category,
       "top_percentage": top_percentage,
       "category_details": category_details
   }

async def get_daily_spending_pattern(db, user_id: ObjectId, days: int) -> Dict[str, Any]:
   """Analyze daily spending patterns"""
   
   end_date = datetime.now()
   start_date = end_date - timedelta(days=days)
   
   # Aggregation pipeline for daily spending
   pipeline = [
       {
           "$match": {
               "user_id": user_id,
               "jenis": "pengeluaran",
               "date": {"$gte": start_date, "$lte": end_date}
           }
       },
       {
           "$group": {
               "_id": {
                   "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$date"}},
                   "dayOfWeek": {"$dayOfWeek": "$date"}
               },
               "total": {"$sum": "$amount"},
               "count": {"$sum": 1}
           }
       },
       {"$sort": {"_id.date": 1}}
   ]
   
   result = await db.transactions.aggregate(pipeline).to_list(100)
   
   # Process results
   dates = []
   amounts = []
   weekday_amounts = []
   weekend_amounts = []
   
   for item in result:
       date_str = item["_id"]["date"]
       amount = item["total"]
       day_of_week = item["_id"]["dayOfWeek"]
       
       dates.append(date_str)
       amounts.append(amount)
       
       # 1=Sunday, 7=Saturday in MongoDB
       if day_of_week in [1, 7]:  # Weekend
           weekend_amounts.append(amount)
       else:  # Weekday
           weekday_amounts.append(amount)
   
   # Calculate statistics
   avg_daily = sum(amounts) / len(amounts) if amounts else 0
   highest_day = dates[amounts.index(max(amounts))] if amounts else ""
   lowest_day = dates[amounts.index(min(amounts))] if amounts else ""
   
   # Determine trend
   if len(amounts) >= 7:
       first_week_avg = sum(amounts[:7]) / 7
       last_week_avg = sum(amounts[-7:]) / 7
       trend = "increasing" if last_week_avg > first_week_avg else "decreasing"
   else:
       trend = "stable"
   
   # Weekend vs weekday comparison
   avg_weekday = sum(weekday_amounts) / len(weekday_amounts) if weekday_amounts else 0
   avg_weekend = sum(weekend_amounts) / len(weekend_amounts) if weekend_amounts else 0
   
   return {
       "dates": dates,
       "amounts": amounts,
       "avg_daily": round(avg_daily, 2),
       "highest_day": highest_day,
       "lowest_day": lowest_day,
       "trend": trend,
       "weekday_weekend_comparison": {
           "avg_weekday": round(avg_weekday, 2),
           "avg_weekend": round(avg_weekend, 2),
           "weekend_higher": avg_weekend > avg_weekday
       }
   }

async def get_weekly_summary(db, user_id: ObjectId, weeks: int) -> Dict[str, Any]:
   """Get weekly financial summary data"""
   
   end_date = datetime.now()
   start_date = end_date - timedelta(weeks=weeks)
   
   # Complex aggregation pipeline for weekly grouping
   pipeline = [
       {"$match": {"user_id": user_id, "date": {"$gte": start_date, "$lte": end_date}}},
       {
           "$group": {
               "_id": {
                   "year": {"$year": "$date"},
                   "week": {"$week": "$date"},
                   "jenis": "$jenis"
               },
               "total": {"$sum": "$amount"}
           }
       },
       {
           "$group": {
               "_id": {
                   "year": "$_id.year",
                   "week": "$_id.week"
               },
               "income": {
                   "$sum": {
                       "$cond": [{"$eq": ["$_id.jenis", "pemasukan"]}, "$total", 0]
                   }
               },
               "expense": {
                   "$sum": {
                       "$cond": [{"$eq": ["$_id.jenis", "pengeluaran"]}, "$total", 0]
                   }
               }
           }
       },
       {"$sort": {"_id.year": 1, "_id.week": 1}}
   ]
   
   result = await db.transactions.aggregate(pipeline).to_list(100)
   
   # Process results
   week_labels = []
   weekly_income = []
   weekly_expense = []
   weekly_savings = []
   
   for item in result:
       year = item["_id"]["year"]
       week = item["_id"]["week"]
       income = item["income"]
       expense = item["expense"]
       savings = income - expense
       
       week_labels.append(f"W{week} {year}")
       weekly_income.append(income)
       weekly_expense.append(expense)
       weekly_savings.append(savings)
   
   # Calculate averages
   avg_weekly_income = sum(weekly_income) / len(weekly_income) if weekly_income else 0
   avg_weekly_expense = sum(weekly_expense) / len(weekly_expense) if weekly_expense else 0
   avg_weekly_savings = sum(weekly_savings) / len(weekly_savings) if weekly_savings else 0
   
   # Find best and worst weeks
   best_week_idx = weekly_savings.index(max(weekly_savings)) if weekly_savings else 0
   worst_week_idx = weekly_savings.index(min(weekly_savings)) if weekly_savings else 0
   
   return {
       "week_labels": week_labels,
       "weekly_income": weekly_income,
       "weekly_expense": weekly_expense,
       "weekly_savings": weekly_savings,
       "avg_weekly_income": round(avg_weekly_income, 2),
       "avg_weekly_expense": round(avg_weekly_expense, 2),
       "avg_weekly_savings": round(avg_weekly_savings, 2),
       "best_week": week_labels[best_week_idx] if week_labels else "",
       "worst_week": week_labels[worst_week_idx] if week_labels else ""
   }

async def get_yearly_overview(db, user_id: ObjectId) -> Dict[str, Any]:
   """Get comprehensive yearly financial overview"""
   
   current_year = datetime.now().year
   start_of_year = datetime(current_year, 1, 1)
   
   # Monthly breakdown pipeline
   monthly_pipeline = [
       {"$match": {"user_id": user_id, "date": {"$gte": start_of_year}}},
       {
           "$group": {
               "_id": {
                   "month": {"$month": "$date"},
                   "jenis": "$jenis"
               },
               "total": {"$sum": "$amount"},
               "count": {"$sum": 1}
           }
       },
       {
           "$group": {
               "_id": "$_id.month",
               "income": {
                   "$sum": {
                       "$cond": [{"$eq": ["$_id.jenis", "pemasukan"]}, "$total", 0]
                   }
               },
               "expense": {
                   "$sum": {
                       "$cond": [{"$eq": ["$_id.jenis", "pengeluaran"]}, "$total", 0]
                   }
               },
               "transaction_count": {"$sum": "$count"}
           }
       },
       {"$sort": {"_id": 1}}
   ]
   
   result = await db.transactions.aggregate(monthly_pipeline).to_list(12)
   
   # Initialize arrays for all 12 months
   months = [calendar.month_abbr[i] for i in range(1, 13)]
   monthly_income = [0] * 12
   monthly_expense = [0] * 12
   monthly_savings = [0] * 12
   
   # Fill in actual data
   for item in result:
       month_idx = item["_id"] - 1  # Convert to 0-based index
       monthly_income[month_idx] = item["income"]
       monthly_expense[month_idx] = item["expense"]
       monthly_savings[month_idx] = item["income"] - item["expense"]
   
   # Calculate totals and summary
   total_income = sum(monthly_income)
   total_expense = sum(monthly_expense)
   net_savings = total_income - total_expense
   savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0
   
   # Find best and worst months
   best_month_idx = monthly_savings.index(max(monthly_savings))
   worst_month_idx = monthly_savings.index(min(monthly_savings))
   
   # Quarterly breakdown
   quarterly_breakdown = []
   for quarter in range(4):
       start_month = quarter * 3
       end_month = start_month + 3
       quarter_income = sum(monthly_income[start_month:end_month])
       quarter_expense = sum(monthly_expense[start_month:end_month])
       quarter_savings = quarter_income - quarter_expense
       
       quarterly_breakdown.append({
           "quarter": f"Q{quarter + 1}",
           "income": quarter_income,
           "expense": quarter_expense,
           "savings": quarter_savings
       })
   
   # Get total transaction count
   transaction_count = await db.transactions.count_documents({
       "user_id": user_id,
       "date": {"$gte": start_of_year}
   })
   
   return {
       "months": months,
       "monthly_income": monthly_income,
       "monthly_expense": monthly_expense,
       "total_income": total_income,
       "total_expense": total_expense,
       "net_savings": net_savings,
       "savings_rate": round(savings_rate, 2),
       "best_month": months[best_month_idx],
       "worst_month": months[worst_month_idx],
       "transaction_count": transaction_count,
       "quarterly_breakdown": quarterly_breakdown
   }

async def analyze_spending_habits(db, user_id: ObjectId) -> Dict[str, Any]:
   """Analyze user spending habits and provide insights"""
   
   # Complex analysis pipeline
   habits_pipeline = [
       {"$match": {"user_id": user_id, "jenis": "pengeluaran"}},
       {
           "$facet": {
               "category_analysis": [
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
                           "_id": "$category.nama_kategori",
                           "total": {"$sum": "$amount"},
                           "count": {"$sum": 1},
                           "avg": {"$avg": "$amount"}
                       }
                   },
                   {"$sort": {"total": -1}}
               ],
               "time_analysis": [
                   {
                       "$group": {
                           "_id": {"$hour": "$date"},
                           "total": {"$sum": "$amount"},
                           "count": {"$sum": 1}
                       }
                   },
                   {"$sort": {"_id": 1}}
               ],
               "frequency_analysis": [
                   {
                       "$group": {
                           "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$date"}},
                           "count": {"$sum": 1},
                           "total": {"$sum": "$amount"}
                       }
                   },
                   {
                       "$group": {
                           "_id": null,
                           "avg_daily_transactions": {"$avg": "$count"},
                           "avg_daily_amount": {"$avg": "$total"},
                           "total_days": {"$sum": 1}
                       }
                   }
               ]
           }
       }
   ]
   
   result = await db.transactions.aggregate(habits_pipeline).to_list(1)
   
   if not result:
       return {
           "personality_type": "New User",
           "preferred_categories": [],
           "frequency_analysis": {},
           "time_patterns": {},
           "recommendations": ["Start tracking your expenses to get personalized insights"],
           "health_score": 50,
           "alerts": []
       }
   
   data = result[0]
   
   # Analyze spending personality
   category_data = data["category_analysis"]
   if category_data:
       top_category = category_data[0]["_id"]
       top_category_percentage = (category_data[0]["total"] / sum(cat["total"] for cat in category_data)) * 100
       
       if top_category_percentage > 50:
           personality_type = f"Heavy {top_category} Spender"
       elif len(category_data) > 5 and top_category_percentage < 30:
           personality_type = "Diversified Spender"
       else:
           personality_type = "Moderate Spender"
   else:
       personality_type = "New User"
   
   # Time patterns analysis
   time_data = data["time_analysis"]
   peak_hour = max(time_data, key=lambda x: x["total"])["_id"] if time_data else 12
   
   # Frequency analysis
   freq_data = data["frequency_analysis"][0] if data["frequency_analysis"] else {}
   avg_daily_transactions = freq_data.get("avg_daily_transactions", 0)
   
   # Generate recommendations
   recommendations = []
   if avg_daily_transactions > 5:
       recommendations.append("Consider consolidating small purchases to reduce transaction fees")
   if category_data and len(category_data) > 0:
       top_spending = category_data[0]
       recommendations.append(f"Your top spending category is {top_spending['_id']}. Consider setting a budget for this category.")
   
   # Calculate financial health score (0-100)
   health_score = 75  # Base score
   if len(category_data) > 3:
       health_score += 10  # Diversified spending
   if avg_daily_transactions < 3:
       health_score += 10  # Controlled spending frequency
   
   health_score = min(100, max(0, health_score))
   
   # Generate alerts
   alerts = []
   if category_data and category_data[0]["total"] > 1000000:  # > 1M IDR
       alerts.append(f"High spending detected in {category_data[0]['_id']} category")
   
   return {
       "personality_type": personality_type,
       "preferred_categories": [cat["_id"] for cat in category_data[:3]],
       "frequency_analysis": {
           "avg_daily_transactions": round(avg_daily_transactions, 2),
           "total_active_days": freq_data.get("total_days", 0)
       },
       "time_patterns": {
           "peak_spending_hour": peak_hour,
           "hourly_distribution": {str(item["_id"]): item["total"] for item in time_data}
       },
       "recommendations": recommendations,
       "health_score": health_score,
       "alerts": alerts
   }

async def get_peak_spending_times(db, user_id: ObjectId) -> Dict[str, Any]:
   """Analyze peak spending times and patterns"""
   
   # Aggregation pipeline for time analysis
   pipeline = [
       {"$match": {"user_id": user_id, "jenis": "pengeluaran"}},
       {
           "$facet": {
               "hourly_pattern": [
                   {
                       "$group": {
                           "_id": {"$hour": "$date"},
                           "total": {"$sum": "$amount"},
                           "count": {"$sum": 1}
                       }
                   },
                   {"$sort": {"_id": 1}}
               ],
               "daily_pattern": [
                   {
                       "$group": {
                           "_id": {"$dayOfWeek": "$date"},
                           "total": {"$sum": "$amount"},
                           "count": {"$sum": 1}
                       }
                   },
                   {"$sort": {"_id": 1}}
               ]
           }
       }
   ]
   
   result = await db.transactions.aggregate(pipeline).to_list(1)
   
   if not result:
       return {
           "hours": list(range(24)),
           "hourly_amounts": [0] * 24,
           "days_of_week": ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
           "daily_amounts": [0] * 7,
           "peak_hour": 12,
           "peak_day": "Monday",
           "lowest_activity": "3 AM",
           "weekend_comparison": {"weekend_higher": False}
       }
   
   data = result[0]
   
   # Process hourly data
   hourly_data = {item["_id"]: item["total"] for item in data["hourly_pattern"]}
   hours = list(range(24))
   hourly_amounts = [hourly_data.get(hour, 0) for hour in hours]
   
   # Process daily data (1=Sunday, 2=Monday, etc.)
   daily_data = {item["_id"]: item["total"] for item in data["daily_pattern"]}
   days_of_week = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
   daily_amounts = [daily_data.get(i + 1, 0) for i in range(7)]
   
   # Find peak times
   peak_hour = hours[hourly_amounts.index(max(hourly_amounts))] if hourly_amounts else 12
   peak_day = days_of_week[daily_amounts.index(max(daily_amounts))] if daily_amounts else "Monday"
   
   # Find lowest activity
   lowest_hour = hours[hourly_amounts.index(min(hourly_amounts))] if hourly_amounts else 3
   lowest_activity = f"{lowest_hour}:00"
   
   # Weekend vs weekday comparison
   weekend_total = daily_amounts