# app/routers/finance.py (No Prophet Dependencies - Windows Compatible)
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import statistics
import warnings
warnings.filterwarnings('ignore')

from ..services.auth_dependency import get_current_user
from ..services.finance_service import FinanceService
from ..models.user import User
from ..utils.timezone_utils import IndonesiaDatetime

router = APIRouter(prefix="/finance", tags=["Finance Analytics"])
finance_service = FinanceService()

def format_currency(amount: float) -> str:
    """Format jumlah uang ke format Rupiah"""
    return f"Rp {amount:,.0f}".replace(',', '.')

class SimplePredictionEngine:
    """Simple prediction engine without external dependencies"""
    
    @staticmethod
    def moving_average_prediction(data_points: List[float], days_ahead: int, window_size: int = 7) -> List[float]:
        """Moving average prediction"""
        if len(data_points) < window_size:
            window_size = max(1, len(data_points))
        
        # Calculate moving average for the last window
        recent_data = data_points[-window_size:]
        avg = sum(recent_data) / len(recent_data)
        
        # Add some trend calculation
        if len(data_points) >= 2:
            trend = (data_points[-1] - data_points[0]) / len(data_points)
        else:
            trend = 0
        
        predictions = []
        for i in range(days_ahead):
            # Apply slight trend and some randomness based on historical variance
            if len(data_points) > 1:
                variance = statistics.variance(recent_data) if len(recent_data) > 1 else 0
                prediction = max(0, avg + (trend * i) + (variance * 0.1))
            else:
                prediction = max(0, avg)
            predictions.append(prediction)
        
        return predictions
    
    @staticmethod
    def linear_regression_prediction(data_points: List[Dict], days_ahead: int) -> List[Dict]:
        """Simple linear regression prediction"""
        if len(data_points) < 2:
            # Fallback to average
            avg_income = sum(p.get('income', 0) for p in data_points) / max(len(data_points), 1)
            avg_expense = sum(p.get('expense', 0) for p in data_points) / max(len(data_points), 1)
            
            predictions = []
            base_date = datetime.now()
            
            for i in range(days_ahead):
                pred_date = base_date + timedelta(days=i+1)
                predictions.append({
                    "date": pred_date.strftime("%Y-%m-%d"),
                    "formatted_date": pred_date.strftime("%d %b %Y"),
                    "predicted_income": max(0, avg_income),
                    "predicted_expense": max(0, avg_expense),
                    "predicted_net": avg_income - avg_expense,
                    "confidence": "low"
                })
            
            return predictions
        
        # Extract time series data
        incomes = [p.get('income', 0) for p in data_points]
        expenses = [p.get('expense', 0) for p in data_points]
        
        # Simple linear trend calculation
        n = len(data_points)
        x_values = list(range(n))
        
        def calculate_trend(y_values):
            if n < 2:
                return 0, sum(y_values) / n if y_values else 0
            
            sum_x = sum(x_values)
            sum_y = sum(y_values)
            sum_xy = sum(x * y for x, y in zip(x_values, y_values))
            sum_x2 = sum(x * x for x in x_values)
            
            # Calculate slope and intercept
            denominator = n * sum_x2 - sum_x * sum_x
            if denominator == 0:
                slope = 0
            else:
                slope = (n * sum_xy - sum_x * sum_y) / denominator
            
            intercept = (sum_y - slope * sum_x) / n
            return slope, intercept
        
        income_slope, income_intercept = calculate_trend(incomes)
        expense_slope, expense_intercept = calculate_trend(expenses)
        
        # Generate predictions
        predictions = []
        base_date = datetime.now()
        
        for i in range(days_ahead):
            pred_date = base_date + timedelta(days=i+1)
            x_pred = n + i
            
            pred_income = max(0, income_slope * x_pred + income_intercept)
            pred_expense = max(0, expense_slope * x_pred + expense_intercept)
            pred_net = pred_income - pred_expense
            
            predictions.append({
                "date": pred_date.strftime("%Y-%m-%d"),
                "formatted_date": pred_date.strftime("%d %b %Y"),
                "predicted_income": pred_income,
                "predicted_expense": pred_expense,
                "predicted_net": pred_net,
                "confidence": "medium" if n > 10 else "low"
            })
        
        return predictions

# === 1. DASHBOARD SUMMARY ===

@router.get("/dashboard-summary")
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user)
):
    """Mendapatkan ringkasan total pemasukan, pengeluaran, dan tabungan"""
    try:
        # Get monthly summary
        monthly_summary = await finance_service.get_financial_summary(
            current_user.id, "monthly"
        )
        
        # Get total current savings
        total_savings = await finance_service._calculate_total_current_savings(current_user.id)
        
        # Get user's financial settings
        user_settings = current_user.financial_settings.dict() if current_user.financial_settings else {}
        
        # Calculate monthly progress
        monthly_progress = await finance_service._calculate_monthly_savings_progress(current_user.id)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Dashboard summary berhasil diambil",
                "data": {
                    "monthly_totals": {
                        "total_income": monthly_summary.total_income,
                        "total_expense": monthly_summary.total_expense,
                        "net_balance": monthly_summary.net_balance,
                        "formatted_income": format_currency(monthly_summary.total_income),
                        "formatted_expense": format_currency(monthly_summary.total_expense),
                        "formatted_balance": format_currency(monthly_summary.net_balance)
                    },
                    "savings_summary": {
                        "current_total_savings": total_savings,
                        "monthly_target": user_settings.get("monthly_savings_target", 0),
                        "monthly_progress": monthly_progress,
                        "formatted_total_savings": format_currency(total_savings),
                        "formatted_monthly_target": format_currency(user_settings.get("monthly_savings_target", 0))
                    },
                    "period": {
                        "start_date": monthly_summary.start_date.isoformat(),
                        "end_date": monthly_summary.end_date.isoformat(),
                        "month_year": IndonesiaDatetime.now().strftime("%B %Y")
                    }
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil dashboard summary: {str(e)}")

# === 2. TRANSACTION HISTORY WITH FILTERS ===

@router.get("/history")
async def get_transaction_history(
    type: Optional[str] = Query(None, description="income, expense, atau all"),
    category: Optional[str] = Query(None, description="Filter berdasarkan kategori"),
    start_date: Optional[datetime] = Query(None, description="Tanggal mulai"),
    end_date: Optional[datetime] = Query(None, description="Tanggal akhir"),
    min_amount: Optional[float] = Query(None, description="Jumlah minimum"),
    max_amount: Optional[float] = Query(None, description="Jumlah maksimum"),
    search: Optional[str] = Query(None, description="Cari dalam deskripsi"),
    page: int = Query(1, ge=1, description="Halaman"),
    limit: int = Query(20, ge=1, le=100, description="Items per halaman"),
    sort_by: str = Query("date", description="Urutkan berdasarkan: date, amount, category"),
    sort_order: str = Query("desc", description="asc atau desc"),
    current_user: User = Depends(get_current_user)
):
    """Mendapatkan history transaksi dengan filter lengkap"""
    try:
        # Build filters
        filters = {"status": "confirmed"}
        
        if type and type != "all":
            filters["type"] = type
        if category:
            filters["category"] = category
        if start_date:
            filters["start_date"] = start_date
        if end_date:
            filters["end_date"] = end_date
        
        # Get transactions
        offset = (page - 1) * limit
        transactions = await finance_service.get_user_transactions(
            current_user.id, filters, limit, offset
        )
        
        # Apply additional filters (amount, search)
        filtered_transactions = []
        for trans in transactions:
            # Amount filter
            if min_amount and trans.amount < min_amount:
                continue
            if max_amount and trans.amount > max_amount:
                continue
            
            # Search filter
            if search and search.lower() not in trans.description.lower():
                continue
                
            filtered_transactions.append(trans)
        
        # Format response
        formatted_transactions = []
        for trans in filtered_transactions:
            formatted_transactions.append({
                "id": trans.id,
                "type": trans.type,
                "amount": trans.amount,
                "formatted_amount": format_currency(trans.amount),
                "category": trans.category,
                "description": trans.description,
                "date": trans.date.isoformat(),
                "formatted_date": IndonesiaDatetime.format_date_only(trans.date),
                "relative_date": IndonesiaDatetime.format_relative(trans.date),
                "source": trans.source,
                "tags": trans.tags
            })
        
        # Get savings goals history
        savings_goals = await finance_service.get_user_savings_goals(current_user.id)
        formatted_goals = []
        for goal in savings_goals:
            formatted_goals.append({
                "id": goal.id,
                "item_name": goal.item_name,
                "target_amount": goal.target_amount,
                "current_amount": goal.current_amount,
                "formatted_target": format_currency(goal.target_amount),
                "formatted_current": format_currency(goal.current_amount),
                "progress_percentage": goal.progress_percentage,
                "status": goal.status,
                "created_date": goal.created_at.isoformat(),
                "formatted_created": IndonesiaDatetime.format_date_only(goal.created_at)
            })
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "History berhasil diambil",
                "data": {
                    "transactions": formatted_transactions,
                    "savings_goals": formatted_goals,
                    "pagination": {
                        "current_page": page,
                        "per_page": limit,
                        "total_transactions": len(formatted_transactions),
                        "total_goals": len(formatted_goals)
                    },
                    "filters_applied": {
                        "type": type,
                        "category": category,
                        "date_range": f"{start_date} - {end_date}" if start_date and end_date else None,
                        "amount_range": f"{min_amount} - {max_amount}" if min_amount and max_amount else None,
                        "search": search
                    }
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil history: {str(e)}")

# === 3. CHARTS DATA - INCOME/EXPENSE BY TIME ===

@router.get("/charts/time-series")
async def get_time_series_chart_data(
    period: str = Query("monthly", description="daily, weekly, monthly"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """Mendapatkan data chart pemasukan/pengeluaran berdasarkan waktu"""
    try:
        # Set default date range if not provided
        if not start_date or not end_date:
            now = IndonesiaDatetime.now()
            if period == "daily":
                start_date = now - timedelta(days=30)  # Last 30 days
                end_date = now
            elif period == "weekly":
                start_date = now - timedelta(weeks=12)  # Last 12 weeks
                end_date = now
            elif period == "monthly":
                start_date = now - timedelta(days=365)  # Last 12 months
                end_date = now
        
        # Get all transactions in period
        filters = {
            "status": "confirmed",
            "start_date": start_date,
            "end_date": end_date
        }
        
        transactions = await finance_service.get_user_transactions(
            current_user.id, filters, 1000, 0  # Get all transactions
        )
        
        # Group by period
        data_points = {}
        
        for trans in transactions:
            # Determine grouping key based on period
            if period == "daily":
                key = trans.date.strftime("%Y-%m-%d")
                display_key = IndonesiaDatetime.format_date_only(trans.date)
            elif period == "weekly":
                # Start of week (Monday)
                start_of_week = trans.date - timedelta(days=trans.date.weekday())
                key = start_of_week.strftime("%Y-%m-%d")
                display_key = f"Week of {IndonesiaDatetime.format_date_only(start_of_week)}"
            elif period == "monthly":
                key = trans.date.strftime("%Y-%m")
                display_key = trans.date.strftime("%B %Y")
            
            if key not in data_points:
                data_points[key] = {
                    "period": display_key,
                    "date_key": key,
                    "income": 0,
                    "expense": 0,
                    "net": 0
                }
            
            if trans.type == "income":
                data_points[key]["income"] += trans.amount
            else:
                data_points[key]["expense"] += trans.amount
            
            data_points[key]["net"] = data_points[key]["income"] - data_points[key]["expense"]
        
        # Sort by date
        sorted_data = sorted(data_points.values(), key=lambda x: x["date_key"])
        
        # Format for chart
        chart_data = {
            "labels": [point["period"] for point in sorted_data],
            "datasets": [
                {
                    "label": "Pemasukan",
                    "data": [point["income"] for point in sorted_data],
                    "backgroundColor": "rgba(34, 197, 94, 0.8)",
                    "borderColor": "rgba(34, 197, 94, 1)"
                },
                {
                    "label": "Pengeluaran", 
                    "data": [point["expense"] for point in sorted_data],
                    "backgroundColor": "rgba(239, 68, 68, 0.8)",
                    "borderColor": "rgba(239, 68, 68, 1)"
                },
                {
                    "label": "Net Balance",
                    "data": [point["net"] for point in sorted_data],
                    "backgroundColor": "rgba(59, 130, 246, 0.8)",
                    "borderColor": "rgba(59, 130, 246, 1)"
                }
            ]
        }
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": f"Chart data {period} berhasil diambil",
                "data": {
                    "chart_data": chart_data,
                    "raw_data": sorted_data,
                    "summary": {
                        "total_income": sum(point["income"] for point in sorted_data),
                        "total_expense": sum(point["expense"] for point in sorted_data),
                        "average_monthly": sum(point["net"] for point in sorted_data) / len(sorted_data) if sorted_data else 0
                    },
                    "period_info": {
                        "type": period,
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat(),
                        "data_points": len(sorted_data)
                    }
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil chart data: {str(e)}")

# === 4. CHARTS DATA - BY CATEGORY ===

@router.get("/charts/by-category")
async def get_category_chart_data(
    type: str = Query("expense", description="income atau expense"),
    period: str = Query("monthly", description="daily, weekly, monthly, yearly"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """Mendapatkan data chart berdasarkan kategori"""
    try:
        # Get summary for the period
        summary = await finance_service.get_financial_summary(
            current_user.id, period, start_date, end_date
        )
        
        # Get category data based on type
        if type == "income":
            categories_data = summary.income_categories
            total_amount = summary.total_income
        else:
            categories_data = summary.expense_categories
            total_amount = summary.total_expense
        
        if not categories_data:
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": f"Tidak ada data {type} untuk periode ini",
                    "data": {
                        "chart_data": {"labels": [], "datasets": []},
                        "categories": [],
                        "summary": {
                            "total_amount": 0,
                            "formatted_total": "Rp 0",
                            "total_categories": 0,
                            "type": type,
                            "period": period
                        }
                    }
                }
            )
        
        # Sort categories by amount (descending)
        sorted_categories = sorted(categories_data.items(), key=lambda x: x[1], reverse=True)
        
        # Prepare chart data
        labels = [cat[0].title() for cat in sorted_categories]
        amounts = [cat[1] for cat in sorted_categories]
        percentages = [(amount/total_amount)*100 if total_amount > 0 else 0 for amount in amounts]
        
        # Colors for categories
        colors = [
            "#EF4444",  # Red
            "#22C55E",  # Green  
            "#3B82F6",  # Blue
            "#F59E0B",  # Yellow
            "#A855F7",  # Purple
            "#EC4899",  # Pink
            "#14B8A6",  # Teal
            "#FB923C",  # Orange
        ]
        
        chart_data = {
            "labels": labels,
            "datasets": [{
                "label": f"{type.title()} by Category",
                "data": amounts,
                "backgroundColor": colors[:len(labels)],
                "borderWidth": 2
            }]
        }
        
        # Detailed breakdown
        categories_breakdown = []
        for i, (category, amount) in enumerate(sorted_categories):
            categories_breakdown.append({
                "category": category.title(),
                "amount": amount,
                "formatted_amount": format_currency(amount),
                "percentage": round(percentages[i], 1),
                "color": colors[i % len(colors)]
            })
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": f"Chart data kategori {type} berhasil diambil",
                "data": {
                    "chart_data": chart_data,
                    "categories": categories_breakdown,
                    "summary": {
                        "total_amount": total_amount,
                        "formatted_total": format_currency(total_amount),
                        "total_categories": len(categories_breakdown),
                        "type": type,
                        "period": period
                    }
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil chart kategori: {str(e)}")

# === 5. PROGRESS BARS DATA ===

@router.get("/progress")
async def get_progress_data(
    current_user: User = Depends(get_current_user)
):
    """Mendapatkan data progress untuk target tabungan"""
    try:
        # Get monthly progress
        monthly_progress = await finance_service._calculate_monthly_savings_progress(current_user.id)
        
        # Get all active savings goals
        active_goals = await finance_service.get_user_savings_goals(current_user.id, "active")
        
        # Format savings goals progress
        goals_progress = []
        for goal in active_goals:
            # Calculate time progress if target_date exists
            time_progress = None
            if goal.target_date:
                now = IndonesiaDatetime.now().replace(tzinfo=None)
                total_days = (goal.target_date - goal.created_at).days
                elapsed_days = (now - goal.created_at).days
                time_progress = min((elapsed_days / total_days) * 100, 100) if total_days > 0 else 100
            
            goals_progress.append({
                "id": goal.id,
                "item_name": goal.item_name,
                "target_amount": goal.target_amount,
                "current_amount": goal.current_amount,
                "formatted_target": format_currency(goal.target_amount),
                "formatted_current": format_currency(goal.current_amount),
                "formatted_remaining": format_currency(goal.remaining_amount),
                "progress_percentage": round(goal.progress_percentage, 1),
                "time_progress_percentage": round(time_progress, 1) if time_progress else None,
                "status": goal.status,
                "target_date": goal.target_date.isoformat() if goal.target_date else None,
                "formatted_target_date": IndonesiaDatetime.format_date_only(goal.target_date) if goal.target_date else None,
                "is_completed": goal.progress_percentage >= 100,
                "days_remaining": (goal.target_date - IndonesiaDatetime.now().replace(tzinfo=None)).days if goal.target_date else None
            })
        
        # Sort by progress percentage (highest first)
        goals_progress.sort(key=lambda x: x["progress_percentage"], reverse=True)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Progress data berhasil diambil",
                "data": {
                    "monthly_savings_progress": {
                        "target": monthly_progress["monthly_target"],
                        "achieved": monthly_progress["net_savings_this_month"],
                        "remaining": monthly_progress["remaining_to_target"],
                        "progress_percentage": round(monthly_progress["progress_percentage"], 1),
                        "formatted_target": format_currency(monthly_progress["monthly_target"]),
                        "formatted_achieved": format_currency(monthly_progress["net_savings_this_month"]),
                        "formatted_remaining": format_currency(monthly_progress["remaining_to_target"]),
                        "is_completed": monthly_progress["progress_percentage"] >= 100,
                        "month_year": IndonesiaDatetime.now().strftime("%B %Y")
                    },
                    "savings_goals_progress": goals_progress,
                    "summary": {
                        "total_active_goals": len(goals_progress),
                        "completed_goals": len([g for g in goals_progress if g["is_completed"]]),
                        "total_target_amount": sum(g["target_amount"] for g in goals_progress),
                        "total_saved_amount": sum(g["current_amount"] for g in goals_progress),
                        "overall_progress": round((sum(g["current_amount"] for g in goals_progress) / sum(g["target_amount"] for g in goals_progress)) * 100, 1) if goals_progress else 0
                    }
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil progress data: {str(e)}")

# === 6. SIMPLE PREDICTION WITHOUT PROPHET ===

@router.get("/predictions")
async def get_financial_predictions(
    days_ahead: int = Query(30, ge=7, le=365, description="Jumlah hari prediksi ke depan"),
    type: str = Query("both", description="income, expense, atau both"),
    current_user: User = Depends(get_current_user)
):
    """Mendapatkan prediksi pemasukan/pengeluaran menggunakan simple prediction"""
    try:
        # Get historical data (last 6 months minimum for better prediction)
        end_date = IndonesiaDatetime.now()
        start_date = end_date - timedelta(days=180)  # 6 months history
        
        filters = {
            "status": "confirmed",
            "start_date": start_date,
            "end_date": end_date
        }
        
        transactions = await finance_service.get_user_transactions(
            current_user.id, filters, 1000, 0
        )
        
        if len(transactions) < 5:  # Need minimum data for prediction
            return JSONResponse(
                status_code=200,
                content={
                    "success": False,
                    "message": "Data transaksi tidak cukup untuk prediksi (minimum 5 transaksi dalam 6 bulan terakhir)",
                    "data": {
                        "predictions": {},
                        "net_balance_predictions": [],
                        "confidence": "insufficient_data",
                        "data_points": len(transactions),
                        "suggestion": "Tambahkan lebih banyak transaksi untuk mendapatkan prediksi yang akurat"
                    }
                }
            )
        
        # Prepare daily aggregated data
        daily_data = {}
        for trans in transactions:
            date_key = trans.date.strftime("%Y-%m-%d")
            if date_key not in daily_data:
                daily_data[date_key] = {"income": 0, "expense": 0, "net": 0}
            
            if trans.type == "income":
                daily_data[date_key]["income"] += trans.amount
            else:
                daily_data[date_key]["expense"] += trans.amount
            
            daily_data[date_key]["net"] = daily_data[date_key]["income"] - daily_data[date_key]["expense"]
        
        # Convert to sorted list
        sorted_data = [
            {"date": k, **v} 
            for k, v in sorted(daily_data.items())
        ]
        
        # Use simple prediction engine
        prediction_engine = SimplePredictionEngine()
        predictions = {}
        
        try:
            # Generate predictions based on type
            if type in ["income", "both"]:
                income_data = [item["income"] for item in sorted_data]
                income_predictions = prediction_engine.moving_average_prediction(income_data, days_ahead)
                
                base_date = datetime.now()
                predictions["income"] = {
                    "predictions": [
                        {
                            "date": (base_date + timedelta(days=i+1)).strftime("%Y-%m-%d"),
                            "formatted_date": (base_date + timedelta(days=i+1)).strftime("%d %b %Y"),
                            "predicted_amount": max(0, pred),
                            "formatted_predicted": format_currency(max(0, pred)),
                            "lower_bound": max(0, pred * 0.7),
                            "upper_bound": pred * 1.3,
                            "confidence": "medium" if len(sorted_data) > 20 else "low"
                        }
                        for i, pred in enumerate(income_predictions)
                    ],
                    "total_predicted": sum(income_predictions),
                    "average_daily": sum(income_predictions) / days_ahead,
                    "data_points_used": len(sorted_data),
                    "method": "moving_average"
                }
            
            if type in ["expense", "both"]:
                expense_data = [item["expense"] for item in sorted_data]
                expense_predictions = prediction_engine.moving_average_prediction(expense_data, days_ahead)
                
                base_date = datetime.now()
                predictions["expense"] = {
                    "predictions": [
                        {
                            "date": (base_date + timedelta(days=i+1)).strftime("%Y-%m-%d"),
                            "formatted_date": (base_date + timedelta(days=i+1)).strftime("%d %b %Y"),
                            "predicted_amount": max(0, pred),
                            "formatted_predicted": format_currency(max(0, pred)),
                            "lower_bound": max(0, pred * 0.7),
                            "upper_bound": pred * 1.3,
                            "confidence": "medium" if len(sorted_data) > 20 else "low"
                        }
                        for i, pred in enumerate(expense_predictions)
                    ],
                    "total_predicted": sum(expense_predictions),
                    "average_daily": sum(expense_predictions) / days_ahead,
                    "data_points_used": len(sorted_data),
                    "method": "moving_average"
                }
            
            # Calculate net balance predictions if both are available
            net_predictions = []
            if "income" in predictions and "expense" in predictions:
                for i in range(days_ahead):
                    income_pred = predictions["income"]["predictions"][i]["predicted_amount"]
                    expense_pred = predictions["expense"]["predictions"][i]["predicted_amount"]
                    net_amount = income_pred - expense_pred
                    
                    net_predictions.append({
                        "date": predictions["income"]["predictions"][i]["date"],
                        "formatted_date": predictions["income"]["predictions"][i]["formatted_date"],
                        "predicted_net": net_amount,
                        "formatted_predicted_net": format_currency(net_amount),
                        "income_predicted": income_pred,
                        "expense_predicted": expense_pred
                    })
            
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": f"Prediksi {days_ahead} hari berhasil dibuat",
                    "data": {
                        "predictions": predictions,
                        "net_balance_predictions": net_predictions,
                        "summary": {
                            "prediction_period": f"{days_ahead} days",
                            "start_date": end_date.strftime("%Y-%m-%d"),
                            "end_date": (end_date + timedelta(days=days_ahead)).strftime("%Y-%m-%d"),
                            "historical_data_period": f"{(end_date - start_date).days} days",
                            "total_transactions_analyzed": len(transactions),
                            "model_confidence": "medium" if len(sorted_data) > 20 else "basic",
                            "method_used": "moving_average_with_trend"
                        },
                        "disclaimer": "Prediksi ini menggunakan analisis tren historis sederhana. Gunakan sebagai referensi dan pertimbangan tambahan dalam perencanaan keuangan."
                    }
                }
            )
            
        except Exception as prediction_error:
            print(f"Prediction error: {prediction_error}")
            return JSONResponse(
                status_code=200,
                content={
                    "success": False,
                    "message": "Gagal membuat prediksi karena data tidak memadai",
                    "data": {
                        "predictions": {},
                        "net_balance_predictions": [],
                        "error_details": str(prediction_error),
                        "suggestion": "Pastikan Anda memiliki transaksi yang konsisten untuk prediksi yang lebih akurat"
                    }
                }
            )
        
    except Exception as e:
        return JSONResponse(
            status_code=200,
            content={
                "success": False,
                "message": "Gagal memproses permintaan prediksi",
                "data": {
                    "predictions": {},
                    "net_balance_predictions": [],
                    "error_details": str(e),
                    "suggestion": "Silakan coba lagi atau hubungi support jika masalah berlanjut"
                }
            }
        )

# === HELPER ENDPOINTS ===

@router.get("/categories")
async def get_available_categories(
    current_user: User = Depends(get_current_user)
):
    """Mendapatkan daftar kategori yang tersedia"""
    try:
        # Get categories from actual transaction data
        filters = {"status": "confirmed"}
        transactions = await finance_service.get_user_transactions(
            current_user.id, filters, 1000, 0
        )
        
        income_categories = set()
        expense_categories = set()
        
        for trans in transactions:
            if trans.type == "income":
                income_categories.add(trans.category)
            else:
                expense_categories.add(trans.category)
        
        # Add default categories if no transactions exist
        if not income_categories:
            income_categories = {"Gaji", "Freelance", "Bisnis", "Investasi", "Bonus", "Lainnya"}
        
        if not expense_categories:
            expense_categories = {"Makanan", "Transportasi", "Belanja", "Hiburan", "Kesehatan", "Pendidikan", "Tagihan", "Lainnya"}
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Kategori berhasil diambil",
                "data": {
                    "income_categories": sorted(list(income_categories)),
                    "expense_categories": sorted(list(expense_categories)),
                    "all_categories": sorted(list(income_categories.union(expense_categories)))
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil kategori: {str(e)}")

@router.get("/stats")
async def get_basic_stats(
    current_user: User = Depends(get_current_user)
):
    """Mendapatkan statistik dasar untuk dashboard"""
    try:
        # Get various periods
        now = IndonesiaDatetime.now()
        
        # Current month
        monthly_summary = await finance_service.get_financial_summary(current_user.id, "monthly")
        
        # Previous month for comparison
        prev_month_start = now.replace(day=1) - timedelta(days=1)
        prev_month_start = prev_month_start.replace(day=1)
        prev_month_end = now.replace(day=1)
        
        prev_monthly_summary = await finance_service.get_financial_summary(
            current_user.id, "monthly", prev_month_start, prev_month_end
        )
        
        # Calculate changes
        income_change = ((monthly_summary.total_income - prev_monthly_summary.total_income) / prev_monthly_summary.total_income * 100) if prev_monthly_summary.total_income > 0 else 0
        expense_change = ((monthly_summary.total_expense - prev_monthly_summary.total_expense) / prev_monthly_summary.total_expense * 100) if prev_monthly_summary.total_expense > 0 else 0
        
        # Get goal stats
        active_goals = await finance_service.get_user_savings_goals(current_user.id, "active")
        completed_goals = await finance_service.get_user_savings_goals(current_user.id, "completed")
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Statistik dasar berhasil diambil",
                "data": {
                    "current_month": {
                        "income": monthly_summary.total_income,
                        "expense": monthly_summary.total_expense,
                        "net": monthly_summary.net_balance,
                        "transactions": monthly_summary.income_count + monthly_summary.expense_count
                    },
                    "month_over_month_change": {
                        "income_change_percent": round(income_change, 1),
                        "expense_change_percent": round(expense_change, 1),
                        "income_trend": "up" if income_change > 0 else "down" if income_change < 0 else "stable",
                        "expense_trend": "up" if expense_change > 0 else "down" if expense_change < 0 else "stable"
                    },
                    "savings_goals": {
                        "active_count": len(active_goals),
                        "completed_count": len(completed_goals),
                        "total_target": sum(goal.target_amount for goal in active_goals),
                        "total_saved": sum(goal.current_amount for goal in active_goals)
                    }
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil statistik: {str(e)}")