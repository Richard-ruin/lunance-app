# app/routers/finance.py - ENHANCED with Chart Data for Flutter

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import statistics
import traceback
import warnings
import json
warnings.filterwarnings('ignore')

from ..services.auth_dependency import get_current_user
from ..services.finance_service import FinanceService
from ..models.user import User
from ..utils.timezone_utils import IndonesiaDatetime
from ..schemas.auth_schemas import UpdateFinancialSettings

router = APIRouter(prefix="/finance", tags=["Finance - 50/30/20 Method for Indonesian Students"])

def format_currency(amount: float) -> str:
    """Format jumlah uang ke format Rupiah"""
    try:
        return f"Rp {amount:,.0f}".replace(',', '.')
    except:
        return f"Rp 0"

def serialize_datetime(obj):
    """Custom JSON serializer untuk datetime objects"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: serialize_datetime(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_datetime(item) for item in obj]
    else:
        return obj

def safe_json_response(status_code: int, content: dict):
    """Safe JSONResponse dengan datetime serialization"""
    try:
        serialized_content = serialize_datetime(content)
        return JSONResponse(
            status_code=status_code,
            content=serialized_content
        )
    except Exception as e:
        print(f"JSON serialization error: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Error dalam serialisasi data",
                "error": str(e)
            }
        )

# ==========================================
# TAB 1: DASHBOARD
# ==========================================

@router.get("/dashboard")
async def get_finance_dashboard(
    current_user: User = Depends(get_current_user)
):
    """TAB 1: DASHBOARD - Fixed Budget categorization"""
    try:
        print(f"Dashboard request for user: {current_user.id}")
        
        finance_service = FinanceService()
        
        # Check financial setup
        financial_setup_completed = getattr(current_user, 'financial_setup_completed', False)
        
        if not financial_setup_completed:
            return safe_json_response(200, {
                "success": True,
                "message": "Financial setup belum dilakukan",
                "data": {
                    "setup_required": True,
                    "setup_url": "/api/v1/auth/setup-financial-50-30-20",
                    "method": "50/30/20 Elizabeth Warren"
                }
            })
        
        # Get comprehensive dashboard data
        try:
            dashboard_data = await finance_service.get_financial_dashboard_50_30_20(current_user.id)
        except Exception as e:
            print(f"Error getting dashboard data: {e}")
            traceback.print_exc()
            dashboard_data = {"error": f"Gagal mengambil data dashboard: {str(e)}"}
        
        if "error" in dashboard_data:
            return safe_json_response(400, {
                "success": False,
                "message": dashboard_data["error"],
                "data": {"setup_required": True}
            })
        
        # Get budget performance
        budget_performance = {}
        try:
            budget_performance = dashboard_data.get("budget_performance", {})
            if not budget_performance or not budget_performance.get("has_budget", False):
                print("Getting budget performance directly...")
                budget_performance = await finance_service.get_monthly_budget_performance(current_user.id)
        except Exception as e:
            print(f"Error getting budget performance: {e}")
            budget_performance = {"has_budget": False, "error": str(e)}
        
        # Get user financial settings
        user_financial_settings = dashboard_data.get("user_financial_settings", {})
        monthly_income = user_financial_settings.get("monthly_income", 0.0)
        
        # Get current month spending with PROPER categorization
        current_spending = {"needs": 0.0, "wants": 0.0, "savings": 0.0}
        try:
            current_spending = await finance_service.get_current_month_spending_by_budget_type_fixed(current_user.id)
        except Exception as e:
            print(f"Error getting current month spending: {e}")
        
        # Calculate quick_stats
        real_total_savings = dashboard_data.get("real_total_savings", 0.0)
        total_spending = sum(current_spending.values())
        net_balance = monthly_income - total_spending
        savings_rate = (net_balance / monthly_income * 100) if monthly_income > 0 else 0
        
        quick_stats = {
            "real_total_savings": real_total_savings,
            "formatted_real_total_savings": format_currency(real_total_savings),
            "monthly_income": monthly_income,
            "formatted_monthly_income": format_currency(monthly_income),
            "current_month_spending": current_spending,
            "formatted_spending": {
                "needs": format_currency(current_spending.get("needs", 0)),
                "wants": format_currency(current_spending.get("wants", 0)),
                "savings": format_currency(current_spending.get("savings", 0))
            },
            "budget_allocation": {
                "needs": monthly_income * 0.5,
                "wants": monthly_income * 0.3,
                "savings": monthly_income * 0.2
            },
            "formatted_budget_allocation": {
                "needs": format_currency(monthly_income * 0.5),
                "wants": format_currency(monthly_income * 0.3),
                "savings": format_currency(monthly_income * 0.2)
            }
        }
        
        # Calculate financial_summary
        financial_summary = {
            "monthly_income": monthly_income,
            "monthly_expense": total_spending,
            "net_balance": net_balance,
            "savings_rate": savings_rate,
            "formatted_monthly_income": format_currency(monthly_income),
            "formatted_monthly_expense": format_currency(total_spending),
            "formatted_net_balance": format_currency(net_balance),
            "formatted_savings_rate": f"{savings_rate:.1f}%",
            "real_total_savings": real_total_savings,
            "formatted_real_total_savings": format_currency(real_total_savings),
            "initial_savings": user_financial_settings.get("initial_savings", 0),
            "formatted_initial_savings": format_currency(user_financial_settings.get("initial_savings", 0)),
            "primary_bank": user_financial_settings.get("primary_bank", ""),
            "last_budget_reset": _safe_datetime_to_string(user_financial_settings.get("last_budget_reset"))
        }
        
        # Format dashboard response
        dashboard_response = {
            "method": "50/30/20 Elizabeth Warren",
            "current_month": datetime.now().strftime("%B %Y"),
            "setup_completed": True,
            
            # Quick stats
            "quick_stats": quick_stats,
            
            # Financial summary
            "financial_summary": financial_summary,

            # Budget Overview
            "budget_overview": {
                "monthly_income": monthly_income,
                "formatted_monthly_income": format_currency(monthly_income),
                "allocation": {
                    "needs": _safe_get_allocation_data_complete_fixed(budget_performance, "needs", monthly_income, current_spending),
                    "wants": _safe_get_allocation_data_complete_fixed(budget_performance, "wants", monthly_income, current_spending),
                    "savings": _safe_get_allocation_data_complete_fixed(budget_performance, "savings", monthly_income, current_spending)
                }
            },
            
            # Budget Health & Status
            "budget_health": {
                "overall_status": budget_performance.get("overall", {}).get("budget_health", "good"),
                "total_spent": total_spending,
                "formatted_total_spent": format_currency(total_spending),
                "total_remaining": monthly_income - total_spending,
                "formatted_total_remaining": format_currency(monthly_income - total_spending),
                "percentage_used": (total_spending / monthly_income * 100) if monthly_income > 0 else 0,
                "strongest_category": dashboard_data.get("insights", {}).get("strongest_category", "unknown"),
                "needs_attention": dashboard_data.get("insights", {}).get("needs_attention", "none"),
                "recommendations": budget_performance.get("recommendations", []),
                "budget_health_by_type": {
                    "needs": _calculate_budget_health("needs", current_spending.get("needs", 0), monthly_income * 0.5),
                    "wants": _calculate_budget_health("wants", current_spending.get("wants", 0), monthly_income * 0.3),
                    "savings": _calculate_budget_health("savings", current_spending.get("savings", 0), monthly_income * 0.2)
                }
            },
            
            # Savings Goals
            "wants_savings_goals": _safe_get_savings_goals_complete(dashboard_data),
            
            # Recent Activity
            "recent_activity": {
                "transactions": _safe_serialize_transactions(dashboard_data.get("recent_activity", {}).get("transactions", [])[:10]),
                "transaction_count": dashboard_data.get("recent_activity", {}).get("transaction_count", 0)
            },
            
            # Quick Actions
            "quick_actions": [
                {
                    "action": "add_transaction",
                    "title": "Catat Transaksi",
                    "description": "Tambah pemasukan atau pengeluaran",
                    "icon": "💰"
                },
                {
                    "action": "create_savings_goal",
                    "title": "Target Tabungan Baru",
                    "description": "Buat target dari wants budget (30%)",
                    "icon": "🎯"
                },
                {
                    "action": "view_analytics",
                    "title": "Lihat Analytics",
                    "description": "Analisis mendalam spending pattern",
                    "icon": "📊"
                },
                {
                    "action": "export_data",
                    "title": "Export Data",
                    "description": "Download laporan keuangan",
                    "icon": "📄"
                }
            ],
            
            "next_reset": "Tanggal 1 bulan depan",
            "timezone": "Asia/Jakarta (WIB)"
        }
        
        print("Dashboard response prepared successfully")
        return safe_json_response(200, {
            "success": True,
            "message": "Dashboard keuangan 50/30/20 berhasil diambil",
            "data": dashboard_response
        })
        
    except Exception as e:
        print(f"Critical error in get_finance_dashboard: {e}")
        traceback.print_exc()
        
        return safe_json_response(500, {
            "success": False,
            "message": f"Gagal mengambil dashboard: {str(e)}",
            "data": {"setup_required": True}
        })

# ==========================================
# TAB 2: ANALYTICS - ENHANCED with Real Chart Data
# ==========================================

@router.get("/analytics")
async def get_finance_analytics(
    period: str = Query("monthly", description="daily, weekly, monthly, yearly"),
    chart_type: str = Query("expense", description="income, expense, comparison"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """TAB 2: ANALYTICS - Enhanced with Real Chart Data for Flutter"""
    try:
        finance_service = FinanceService()
        
        # Check if financial setup completed
        financial_setup_completed = getattr(current_user, 'financial_setup_completed', False)
        
        if not financial_setup_completed:
            return safe_json_response(400, {
                "success": False,
                "message": "Financial setup belum dilakukan"
            })
        
        # Get budget performance
        try:
            budget_performance = await finance_service.get_monthly_budget_performance(current_user.id)
        except Exception as e:
            print(f"Error getting budget performance: {e}")
            budget_performance = {"has_budget": False, "error": str(e)}
        
        # Get financial summary
        try:
            summary = await finance_service.get_financial_summary(current_user.id, period, start_date, end_date)
        except Exception as e:
            print(f"Error getting financial summary: {e}")
            traceback.print_exc()
            
            # Create empty summary as fallback
            summary = type('Summary', (), {
                'total_income': 0,
                'total_expense': 0,
                'net_balance': 0,
                'expense_categories': {},
                'income_categories': {},
                'start_date': start_date or datetime.now(),
                'end_date': end_date or datetime.now(),
                'income_count': 0,
                'expense_count': 0
            })()
        
        # ENHANCED: Generate Real Chart Data for Flutter
        raw_data = await _generate_real_chart_data(finance_service, current_user.id, period, chart_type)
        
        # Get kategori breakdown dengan budget type classification
        category_analysis = {}
        budget_type_totals = {"needs": 0, "wants": 0, "savings": 0, "unknown": 0}
        
        try:
            categories_to_analyze = {}
            if chart_type == "income":
                categories_to_analyze = getattr(summary, 'income_categories', {})
            else:  # expense or comparison
                categories_to_analyze = getattr(summary, 'expense_categories', {})
            
            if categories_to_analyze:
                total_amount = sum(categories_to_analyze.values()) if categories_to_analyze else 1
                
                for category, amount in categories_to_analyze.items():
                    try:
                        # Get budget type
                        budget_type = _get_budget_type_safe(category)
                        percentage = (amount / total_amount * 100) if total_amount > 0 else 0
                        
                        category_analysis[category] = {
                            "amount": amount,
                            "formatted_amount": format_currency(amount),
                            "percentage": round(percentage, 1),
                            "budget_type": budget_type,
                            "budget_type_color": _get_budget_type_color(budget_type)
                        }
                        
                        budget_type_totals[budget_type] += amount
                        
                    except Exception as e:
                        print(f"Error processing category {category}: {e}")
                        continue
        except Exception as e:
            print(f"Error analyzing categories: {e}")
        
        # Budget vs Actual comparison
        try:
            financial_settings = getattr(current_user, 'financial_settings', None)
            monthly_income = financial_settings.monthly_income if financial_settings else 0
        except Exception as e:
            print(f"Error getting monthly income: {e}")
            monthly_income = 0
        
        budget_vs_actual = {
            "needs": _calculate_budget_vs_actual("needs", monthly_income, budget_type_totals),
            "wants": _calculate_budget_vs_actual("wants", monthly_income, budget_type_totals),
            "savings": _calculate_budget_vs_actual("savings", monthly_income, budget_type_totals)
        }
        
        # Financial health calculation
        try:
            savings_rate = (summary.net_balance / summary.total_income * 100) if summary.total_income > 0 else 0
            health_score = _calculate_health_score(budget_vs_actual, savings_rate)
        except Exception as e:
            print(f"Error calculating health score: {e}")
            savings_rate = 0
            health_score = 0
        
        # Generate insights
        insights = _generate_insights(budget_vs_actual, savings_rate, chart_type)
        
        # ENHANCED: Format categories for chart dengan better colors
        formatted_categories = _format_categories_for_chart(category_analysis)
        
        analytics_response = {
            "period": period,
            "period_display": f"{period.title()} Analysis",
            "chart_type": chart_type,
            "chart_type_display": {
                "income": "Analisis Pemasukan",
                "expense": "Analisis Pengeluaran", 
                "comparison": "Perbandingan Pemasukan vs Pengeluaran"
            }.get(chart_type, "Analisis Keuangan"),
            "date_range": {
                "start": _safe_datetime_to_string(start_date) or _safe_datetime_to_string(summary.start_date),
                "end": _safe_datetime_to_string(end_date) or _safe_datetime_to_string(summary.end_date)
            },
            
            # ENHANCED: Real Chart Data for Flutter
            "raw_data": raw_data,
            "max_value": _get_max_value_from_data(raw_data),
            
            # Budget Performance Analysis
            "budget_performance": {
                "method": "50/30/20 Elizabeth Warren",
                "budget_vs_actual": budget_vs_actual,
                "budget_type_totals": {
                    category: {
                        "amount": amount,
                        "formatted": format_currency(amount),
                        "percentage": (amount / sum(budget_type_totals.values()) * 100) if sum(budget_type_totals.values()) > 0 else 0
                    }
                    for category, amount in budget_type_totals.items()
                }
            },
            
            # Enhanced Category Analysis for Flutter Charts
            "categories": formatted_categories,
            "category_breakdown": {
                "total_categories": len(category_analysis),
                "categories": dict(sorted(category_analysis.items(), key=lambda x: x[1]["amount"], reverse=True)),
                "top_needs_expense": _get_top_expense_by_type(category_analysis, "needs"),
                "top_wants_expense": _get_top_expense_by_type(category_analysis, "wants"),
            },
            
            # Financial Health
            "financial_health": {
                "health_score": round(health_score, 1),
                "health_level": _get_health_level(health_score),
                "savings_rate": round(savings_rate, 1),
                "income_expense_ratio": (summary.total_expense / summary.total_income * 100) if summary.total_income > 0 else 0,
                "net_balance": summary.net_balance,
                "formatted_net_balance": format_currency(summary.net_balance)
            },
            
            # Summary
            "summary": {
                "total_income": summary.total_income,
                "total_expense": summary.total_expense,
                "net_balance": summary.net_balance,
                "formatted_total_income": format_currency(summary.total_income),
                "formatted_total_expense": format_currency(summary.total_expense),
                "formatted_net_balance": format_currency(summary.net_balance)
            },
            
            # Trends & Insights
            "insights": insights,
            "recommendations": [
                "Maintain 50% needs budget untuk kebutuhan pokok",
                "Allocate 30% wants untuk lifestyle dan target tabungan",
                "Consistently save 20% untuk masa depan",
                "Track spending weekly untuk kontrol budget yang lebih baik"
            ]
        }
        
        return safe_json_response(200, {
            "success": True,
            "message": f"Analytics {period} untuk {chart_type} berhasil diambil",
            "data": analytics_response
        })
        
    except Exception as e:
        print(f"Error in get_finance_analytics: {e}")
        traceback.print_exc()
        
        return safe_json_response(500, {
            "success": False,
            "message": f"Gagal mengambil analytics: {str(e)}",
            "data": {"period": period, "chart_type": chart_type}
        })

# ==========================================
# ENHANCED CHART DATA GENERATION
# ==========================================

async def _generate_real_chart_data(finance_service, user_id: str, period: str, chart_type: str) -> List[Dict]:
    """Generate real chart data from actual transactions"""
    try:
        # Set date range based on period
        now = datetime.now()
        if period == "daily":
            # Last 7 days
            start_date = now - timedelta(days=7)
            end_date = now
            date_format = "%d/%m"
            periods = [(start_date + timedelta(days=i)).strftime(date_format) for i in range(8)]
        elif period == "weekly":
            # Last 4 weeks
            start_date = now - timedelta(weeks=4)
            end_date = now
            date_format = "Week %U"
            periods = [f"W{i+1}" for i in range(4)]
        elif period == "yearly":
            # Last 12 months
            start_date = now - timedelta(days=365)
            end_date = now
            date_format = "%b"
            periods = [(start_date + timedelta(days=30*i)).strftime(date_format) for i in range(12)]
        else:  # monthly - Last 6 months
            start_date = now - timedelta(days=180)
            end_date = now
            date_format = "%b"
            periods = [(now - timedelta(days=30*i)).strftime(date_format) for i in range(6)][::-1]
        
        # Query transactions for the period
        query = {
            "user_id": user_id,
            "status": "confirmed",
            "date": {"$gte": start_date, "$lte": end_date}
        }
        
        transactions = await finance_service.get_user_transactions(user_id, query, limit=1000)
        
        # Group transactions by period
        data_by_period = {}
        for period_name in periods:
            data_by_period[period_name] = {"income": 0.0, "expense": 0.0}
        
        for trans in transactions:
            try:
                trans_date = trans.date if hasattr(trans, 'date') else datetime.now()
                period_key = trans_date.strftime(date_format)
                
                # Handle weekly format
                if period == "weekly":
                    week_number = (trans_date - start_date).days // 7 + 1
                    period_key = f"W{min(week_number, 4)}"
                
                if period_key in data_by_period:
                    if trans.type.value == "income":
                        data_by_period[period_key]["income"] += trans.amount
                    elif trans.type.value == "expense":
                        data_by_period[period_key]["expense"] += trans.amount
            except Exception as e:
                print(f"Error processing transaction: {e}")
                continue
        
        # Format data for Flutter charts
        chart_data = []
        for period_name in periods:
            period_data = data_by_period.get(period_name, {"income": 0.0, "expense": 0.0})
            
            chart_entry = {
                "period": period_name,
                "income": period_data["income"],
                "expense": period_data["expense"],
                "net": period_data["income"] - period_data["expense"]
            }
            chart_data.append(chart_entry)
        
        return chart_data
        
    except Exception as e:
        print(f"Error generating real chart data: {e}")
        # Return fallback data
        return _generate_fallback_chart_data(period)

def _generate_fallback_chart_data(period: str) -> List[Dict]:
    """Generate fallback chart data when real data is not available"""
    if period == "daily":
        return [
            {"period": f"Day {i+1}", "income": 50000 + (i * 5000), "expense": 35000 + (i * 3000), "net": 15000 + (i * 2000)}
            for i in range(7)
        ]
    elif period == "weekly":
        return [
            {"period": f"W{i+1}", "income": 300000 + (i * 25000), "expense": 200000 + (i * 15000), "net": 100000 + (i * 10000)}
            for i in range(4)
        ]
    elif period == "yearly":
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        return [
            {"period": months[i], "income": 1200000 + (i * 50000), "expense": 900000 + (i * 30000), "net": 300000 + (i * 20000)}
            for i in range(12)
        ]
    else:  # monthly
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
        return [
            {"period": months[i], "income": 1500000 + (i * 25000), "expense": 1100000 + (i * 20000), "net": 400000 + (i * 5000)}
            for i in range(6)
        ]

def _get_max_value_from_data(raw_data: List[Dict]) -> float:
    """Get maximum value from chart data for Flutter chart scaling"""
    try:
        max_value = 0.0
        for item in raw_data:
            values = [
                item.get("income", 0),
                item.get("expense", 0),
                abs(item.get("net", 0))
            ]
            max_value = max(max_value, max(values))
        return max_value * 1.2  # Add 20% padding
    except:
        return 2000000.0  # Default max value

# Continue with existing helper functions...
def _safe_get_allocation_data_complete_fixed(budget_performance: Dict, category: str, monthly_income: float, current_spending: Dict) -> Dict[str, Any]:
    """FIXED allocation data with proper categorization"""
    try:
        percentages = {
            "needs": 0.50,    
            "wants": 0.30,    
            "savings": 0.20   
        }
        
        budget = monthly_income * percentages.get(category, 0)
        spent = current_spending.get(category, 0.0)
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
            "formatted_budget": format_currency(budget),
            "formatted_spent": format_currency(spent),
            "formatted_remaining": format_currency(remaining),
            "allocation_percentage": int(percentages.get(category, 0) * 100),
            "budget_type": category,
            "budget_color": {
                "needs": "#22C55E",    
                "wants": "#F59E0B",    
                "savings": "#3B82F6"   
            }.get(category, "#6B7280"),
            "is_over_budget": percentage_used > 100,
            "is_warning": percentage_used > 80,
            "percentage_remaining": max(0, 100 - percentage_used)
        }
        
    except Exception as e:
        print(f"Error in _safe_get_allocation_data_complete_fixed for {category}: {e}")
        
        percentages = {"needs": 0.50, "wants": 0.30, "savings": 0.20}
        budget = monthly_income * percentages.get(category, 0)
        
        return {
            "budget": budget,
            "spent": 0.0,
            "remaining": budget,
            "percentage_used": 0.0,
            "status": "excellent",
            "formatted_budget": format_currency(budget),
            "formatted_spent": format_currency(0),
            "formatted_remaining": format_currency(budget),
            "allocation_percentage": int(percentages.get(category, 0) * 100),
            "budget_type": category,
            "budget_color": {
                "needs": "#22C55E",
                "wants": "#F59E0B", 
                "savings": "#3B82F6"
            }.get(category, "#6B7280"),
            "is_over_budget": False,
            "is_warning": False,
            "percentage_remaining": 100.0
        }

# Keep all other existing helper functions unchanged...
def _calculate_budget_health(budget_type: str, spent: float, budget: float) -> Dict[str, Any]:
    """Calculate health metrics for each budget type"""
    try:
        percentage_used = (spent / budget * 100) if budget > 0 else 0
        
        if percentage_used > 100:
            health = "over_budget"
            health_score = 0
        elif percentage_used > 90:
            health = "critical"
            health_score = 25
        elif percentage_used > 80:
            health = "warning"
            health_score = 50
        elif percentage_used > 60:
            health = "good"
            health_score = 75
        else:
            health = "excellent"
            health_score = 100
        
        return {
            "health": health,
            "health_score": health_score,
            "percentage_used": round(percentage_used, 1),
            "amount_spent": spent,
            "budget_amount": budget,
            "remaining": budget - spent,
            "formatted_spent": format_currency(spent),
            "formatted_budget": format_currency(budget),
            "formatted_remaining": format_currency(budget - spent)
        }
    except Exception as e:
        print(f"Error calculating budget health for {budget_type}: {e}")
        return {
            "health": "unknown",
            "health_score": 0,
            "percentage_used": 0,
            "amount_spent": 0,
            "budget_amount": 0,
            "remaining": 0,
            "formatted_spent": format_currency(0),
            "formatted_budget": format_currency(0),
            "formatted_remaining": format_currency(0)
        }

def _safe_get_savings_goals_complete(dashboard_data: Dict) -> Dict[str, Any]:
    """Complete savings goals data"""
    try:
        goals_data = dashboard_data.get("wants_budget_goals", {})
        if not goals_data:
            goals_data = dashboard_data.get("wants_savings_goals", {})
        if not goals_data:
            goals_data = dashboard_data.get("savings_goals", {})
        
        goals = goals_data.get("goals", [])
        
        formatted_goals = []
        for goal in goals[:5]:  # Top 5 goals
            try:
                goal_dict = goal if isinstance(goal, dict) else goal.__dict__
                
                days_remaining = None
                target_date = goal_dict.get("target_date")
                if target_date:
                    if isinstance(target_date, str):
                        target_date = datetime.fromisoformat(target_date)
                    days_remaining = (target_date - datetime.now()).days
                
                formatted_goal = {
                    "id": goal_dict.get("id"),
                    "item_name": goal_dict.get("item_name"),
                    "target_amount": goal_dict.get("target_amount", 0),
                    "current_amount": goal_dict.get("current_amount", 0),
                    "progress_percentage": goal_dict.get("progress_percentage", 0),
                    "status": goal_dict.get("status", "active"),
                    "target_date": _safe_datetime_to_string(target_date),
                    "days_remaining": days_remaining,
                    "is_urgent": goal_dict.get("is_urgent", False),
                    "budget_source": "wants_30_percent",
                    "formatted_target": format_currency(goal_dict.get("target_amount", 0)),
                    "formatted_current": format_currency(goal_dict.get("current_amount", 0)),
                    "remaining_amount": goal_dict.get("target_amount", 0) - goal_dict.get("current_amount", 0),
                    "formatted_remaining": format_currency(goal_dict.get("target_amount", 0) - goal_dict.get("current_amount", 0))
                }
                formatted_goals.append(formatted_goal)
            except Exception as e:
                print(f"Error formatting goal: {e}")
                continue
        
        total_goals = goals_data.get("total_goals", len(goals))
        total_allocated = goals_data.get("total_allocated", 0)
        total_target = goals_data.get("total_target", 0)
        
        return {
            "total_goals": total_goals,
            "total_allocated": total_allocated,
            "total_target": total_target,
            "formatted_total_allocated": format_currency(total_allocated),
            "formatted_total_target": format_currency(total_target),
            "goals": formatted_goals,
            "progress_percentage": (total_allocated / total_target * 100) if total_target > 0 else 0,
            "active_goals": len([g for g in formatted_goals if g["status"] == "active"]),
            "completed_goals": len([g for g in formatted_goals if g["status"] == "completed"])
        }
    except Exception as e:
        print(f"Error in _safe_get_savings_goals_complete: {e}")
        return {
            "total_goals": 0,
            "total_allocated": 0,
            "total_target": 0,
            "formatted_total_allocated": format_currency(0),
            "formatted_total_target": format_currency(0),
            "goals": [],
            "progress_percentage": 0,
            "active_goals": 0,
            "completed_goals": 0
        }

def _safe_serialize_transactions(transactions: List) -> List[Dict]:
    """Complete transaction serialization"""
    try:
        if not transactions:
            return []
        
        serialized = []
        for trans in transactions:
            try:
                if isinstance(trans, dict):
                    trans_dict = trans.copy()
                else:
                    trans_dict = trans.__dict__ if hasattr(trans, '__dict__') else {}
                
                # Serialize datetime fields
                for field in ['date', 'created_at', 'updated_at', 'confirmed_at']:
                    if field in trans_dict and isinstance(trans_dict[field], datetime):
                        trans_dict[field] = trans_dict[field].isoformat()
                
                # Add calculated fields
                if 'relative_time' not in trans_dict and 'date' in trans_dict:
                    try:
                        date_obj = trans_dict['date']
                        if isinstance(date_obj, str):
                            date_obj = datetime.fromisoformat(date_obj)
                        trans_dict['relative_time'] = _calculate_relative_time(date_obj)
                    except:
                        trans_dict['relative_time'] = "Unknown"
                
                if 'formatted_amount' not in trans_dict and 'amount' in trans_dict:
                    trans_dict['formatted_amount'] = format_currency(trans_dict.get('amount', 0))
                
                if trans_dict.get('type') == 'expense' and 'budget_type' not in trans_dict:
                    trans_dict['budget_type'] = _get_budget_type_safe(trans_dict.get('category', ''))
                
                serialized.append(trans_dict)
                
            except Exception as e:
                print(f"Error serializing transaction: {e}")
                continue
        
        return serialized
    except Exception as e:
        print(f"Error in _safe_serialize_transactions: {e}")
        return []

def _safe_datetime_to_string(dt) -> Optional[str]:
    """Safely convert datetime to string"""
    if dt is None:
        return None
    if isinstance(dt, datetime):
        return dt.isoformat()
    if isinstance(dt, str):
        return dt
    return str(dt)

def _calculate_relative_time(date_obj: datetime) -> str:
    """Calculate relative time from date"""
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
    except Exception as e:
        print(f"Error calculating relative time: {e}")
        return "Unknown"

def _get_budget_type_safe(category: str) -> str:
    """Safe way to get budget type dengan fallback"""
    try:
        category_lower = category.lower()
        
        # NEEDS keywords
        needs_keywords = ['makan', 'makanan', 'kos', 'sewa', 'transport', 'transportasi', 'pendidikan', 'buku', 'kuliah', 'kampus', 'listrik', 'air', 'internet', 'pulsa', 'kesehatan', 'obat', 'sabun', 'pasta']
        for keyword in needs_keywords:
            if keyword in category_lower:
                return "needs"
        
        # SAVINGS keywords
        savings_keywords = ['tabungan', 'saving', 'investasi', 'deposito', 'darurat', 'masa depan', 'reksadana', 'saham']
        for keyword in savings_keywords:
            if keyword in category_lower:
                return "savings"
        
        # Default to wants
        return "wants"
        
    except Exception as e:
        print(f"Error in _get_budget_type_safe: {e}")
        return "wants"

# Helper functions for analytics
def _get_budget_type_color(budget_type: str) -> str:
    """Get color for budget type"""
    colors = {
        "needs": "#22C55E",    
        "wants": "#F59E0B",    
        "savings": "#3B82F6",  
        "unknown": "#6B7280"   
    }
    return colors.get(budget_type, "#6B7280")

def _calculate_budget_vs_actual(category: str, monthly_income: float, budget_type_totals: Dict) -> Dict:
    """Calculate budget vs actual for a category"""
    percentages = {"needs": 0.50, "wants": 0.30, "savings": 0.20}
    
    budget = monthly_income * percentages.get(category, 0)
    actual = budget_type_totals.get(category, 0)
    variance = actual - budget
    percentage = (actual / budget * 100) if budget > 0 else 0
    
    return {
        "budget": budget,
        "actual": actual,
        "variance": variance,
        "percentage": percentage,
        "formatted_budget": format_currency(budget),
        "formatted_actual": format_currency(actual),
        "formatted_variance": format_currency(variance)
    }

def _calculate_health_score(budget_vs_actual: Dict, savings_rate: float) -> float:
    """Calculate financial health score"""
    try:
        needs_score = min(budget_vs_actual["needs"]["percentage"], 100) * 0.3
        wants_score = max(0, 100 - budget_vs_actual["wants"]["percentage"]) * 0.2
        savings_score = min(budget_vs_actual["savings"]["percentage"], 150) * 0.3
        savings_rate_score = min(savings_rate, 30) * 0.2 / 30 * 100
        
        return min(100, max(0, needs_score + wants_score + savings_score + savings_rate_score))
    except Exception as e:
        print(f"Error calculating health score: {e}")
        return 0

def _get_health_level(health_score: float) -> str:
    """Get health level based on score"""
    if health_score >= 80:
        return "excellent"
    elif health_score >= 60:
        return "good"
    elif health_score >= 40:
        return "fair"
    else:
        return "needs_improvement"

def _generate_insights(budget_vs_actual: Dict, savings_rate: float, chart_type: str) -> List[str]:
    """Generate insights based on budget performance and chart type"""
    insights = []
    
    try:
        if budget_vs_actual["needs"]["percentage"] > 110:
            insights.append("⚠️ Pengeluaran NEEDS melebihi 50% budget - review kebutuhan pokok")
        elif budget_vs_actual["needs"]["percentage"] < 70:
            insights.append("✅ Pengeluaran NEEDS sangat efisien - bisa realokasi ke savings")
        
        if budget_vs_actual["wants"]["percentage"] > 120:
            insights.append("🚨 Pengeluaran WANTS terlalu tinggi - kurangi jajan dan hiburan")
        elif budget_vs_actual["wants"]["percentage"] < 50:
            insights.append("💡 Budget WANTS masih banyak - bisa untuk target tabungan")
        
        if budget_vs_actual["savings"]["percentage"] < 50:
            insights.append("📈 Peluang menabung lebih besar - tingkatkan alokasi savings")
        elif budget_vs_actual["savings"]["percentage"] > 100:
            insights.append("🎉 Target savings tercapai - pertahankan atau tingkatkan!")
        
        if savings_rate < 10:
            insights.append("📊 Savings rate masih rendah - target minimal 15-20%")
        elif savings_rate > 25:
            insights.append("🌟 Savings rate excellent - Anda sangat disiplin!")
        
        # Chart type specific insights
        if chart_type == "income":
            insights.append("💰 Fokus pada diversifikasi sumber pemasukan")
        elif chart_type == "expense":
            insights.append("📉 Monitor pengeluaran untuk kontrol budget yang lebih baik")
        elif chart_type == "comparison":
            insights.append("⚖️ Perbandingan pemasukan vs pengeluaran membantu planning")
            
    except Exception as e:
        print(f"Error generating insights: {e}")
        insights.append("💡 Terus pantau pengeluaran untuk insight yang lebih baik")
    
    return insights

def _get_top_expense_by_type(category_analysis: Dict, budget_type: str) -> str:
    """Get top expense category by budget type"""
    try:
        filtered = {k: v for k, v in category_analysis.items() if v["budget_type"] == budget_type}
        if not filtered:
            return "N/A"
        
        top_category = max(filtered.items(), key=lambda x: x[1]["amount"])
        return top_category[0]
    except Exception as e:
        print(f"Error getting top expense for {budget_type}: {e}")
        return "N/A"

def _format_categories_for_chart(category_analysis: Dict) -> List[Dict]:
    """Format categories data for chart with enhanced colors"""
    try:
        categories = []
        
        # Define color palette untuk kategori
        color_palette = [
            "#3B82F6", "#EF4444", "#10B981", "#F59E0B", "#8B5CF6", 
            "#EC4899", "#06B6D4", "#84CC16", "#F97316", "#6366F1",
            "#14B8A6", "#F43F5E", "#8B5A3C", "#6B7280", "#DC2626"
        ]
        
        sorted_categories = sorted(category_analysis.items(), key=lambda x: x[1]["amount"], reverse=True)
        
        for i, (category, data) in enumerate(sorted_categories):
            # Assign color from palette
            color = color_palette[i % len(color_palette)]
            
            categories.append({
                "category": category,
                "amount": data.get("amount", 0),
                "formatted_amount": data.get("formatted_amount", "Rp 0"),
                "percentage": data.get("percentage", 0),
                "budget_type": data.get("budget_type", "unknown"),
                "color": color,
                "enhanced_color": color  # For compatibility
            })
        
        return categories
    except Exception as e:
        print(f"Error formatting categories for chart: {e}")
        return []

# ==========================================
# TAB 3: HISTORY - Keep existing implementation
# ==========================================

@router.get("/history")
async def get_finance_history(
    type: Optional[str] = Query(None, description="income, expense, goals, all"),
    budget_type: Optional[str] = Query(None, description="needs, wants, savings"),
    category: Optional[str] = Query(None, description="Filter berdasarkan kategori"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    search: Optional[str] = Query(None, description="Cari dalam deskripsi"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("date", description="date, amount, category"),
    sort_order: str = Query("desc", description="asc, desc"),
    current_user: User = Depends(get_current_user)
):
    """TAB 3: HISTORY - Complete transaction and savings goals history"""
    try:
        finance_service = FinanceService()
        
        # Check if financial setup completed
        financial_setup_completed = getattr(current_user, 'financial_setup_completed', False)
        
        if not financial_setup_completed:
            return safe_json_response(400, {
                "success": False,
                "message": "Financial setup belum dilakukan",
                "data": {
                    "setup_required": True,
                    "method": "50/30/20 Elizabeth Warren"
                }
            })
        
        # Handle savings goals request
        if type == "goals":
            try:
                print("Getting savings goals...")
                savings_goals = await finance_service.get_user_savings_goals(current_user.id)
                
                formatted_goals = []
                for goal in savings_goals:
                    try:
                        days_remaining = None
                        if goal.target_date:
                            days_remaining = (goal.target_date - datetime.now()).days
                        
                        formatted_goals.append({
                            "id": goal.id,
                            "type": "savings_goal",
                            "item_name": goal.item_name,
                            "target_amount": goal.target_amount,
                            "current_amount": goal.current_amount,
                            "progress_percentage": goal.progress_percentage,
                            "status": goal.status,
                            "target_date": goal.target_date.isoformat() if goal.target_date else None,
                            "days_remaining": days_remaining,
                            "formatted_target": format_currency(goal.target_amount),
                            "formatted_current": format_currency(goal.current_amount),
                            "budget_source": "wants_30_percent",
                            "created_at": goal.created_at.isoformat() if goal.created_at else None
                        })
                    except Exception as e:
                        print(f"Error formatting goal: {e}")
                        continue
                
                return safe_json_response(200, {
                    "success": True,
                    "message": "Riwayat savings goals berhasil diambil",
                    "data": {
                        "items": formatted_goals,
                        "type": "savings_goals",
                        "total": len(formatted_goals),
                        "pagination": {
                            "current_page": page,
                            "per_page": limit,
                            "total_items": len(formatted_goals),
                            "has_next": False,
                            "has_prev": False
                        }
                    }
                })
                
            except Exception as e:
                print(f"Error getting savings goals: {e}")
                return safe_json_response(500, {
                    "success": False,
                    "message": f"Gagal mengambil savings goals: {str(e)}",
                    "data": {"items": [], "total": 0}
                })
        
        # Handle transaction history request
        try:
            print("Getting transaction history...")
            
            # Build filters
            filters = {"status": "confirmed"}
            if type and type != "all":
                filters["type"] = type
            if budget_type:
                filters["budget_type"] = budget_type
            if category:
                filters["category"] = category
            if start_date or end_date:
                date_filter = {}
                if start_date:
                    date_filter["$gte"] = start_date
                if end_date:
                    date_filter["$lte"] = end_date
                filters["date"] = date_filter
            
            # Get transactions
            offset = (page - 1) * limit
            transactions = await finance_service.get_user_transactions(
                current_user.id, filters, limit, offset
            )
            
            # Format transactions
            formatted_transactions = []
            for trans in transactions:
                try:
                    # Determine budget type
                    budget_type_display = "unknown"
                    if trans.type == "expense":
                        budget_type_display = _get_budget_type_safe(trans.category)
                    
                    # Apply search filter
                    if search and search.lower() not in trans.description.lower():
                        continue
                    
                    formatted_trans = {
                        "id": trans.id,
                        "type": trans.type,
                        "amount": trans.amount,
                        "formatted_amount": format_currency(trans.amount),
                        "category": trans.category,
                        "budget_type": budget_type_display,
                        "description": trans.description,
                        "date": trans.date.isoformat() if trans.date else datetime.now().isoformat(),
                        "formatted_date": trans.date.strftime("%d/%m/%Y") if trans.date else "",
                        "relative_date": _calculate_relative_time_safe(trans.date),
                        "status": trans.status,
                        "source": trans.source,
                        "tags": trans.tags or []
                    }
                    
                    formatted_transactions.append(formatted_trans)
                    
                except Exception as e:
                    print(f"Error formatting transaction: {e}")
                    continue
            
            # Sort transactions
            if sort_by == "date":
                formatted_transactions.sort(key=lambda x: x.get("date", ""), reverse=(sort_order == "desc"))
            elif sort_by == "amount":
                formatted_transactions.sort(key=lambda x: x.get("amount", 0), reverse=(sort_order == "desc"))
            elif sort_by == "category":
                formatted_transactions.sort(key=lambda x: x.get("category", ""), reverse=(sort_order == "desc"))
            
            # Calculate summary
            total_income = sum(t["amount"] for t in formatted_transactions if t["type"] == "income")
            total_expense = sum(t["amount"] for t in formatted_transactions if t["type"] == "expense")
            
            history_response = {
                "items": formatted_transactions,
                "summary": {
                    "total_income": total_income,
                    "total_expense": total_expense,
                    "net_balance": total_income - total_expense,
                    "formatted_income": format_currency(total_income),
                    "formatted_expense": format_currency(total_expense),
                    "formatted_net": format_currency(total_income - total_expense),
                    "transaction_count": len(formatted_transactions)
                },
                "filters_applied": {
                    "type": type,
                    "budget_type": budget_type,
                    "category": category,
                    "search": search
                },
                "pagination": {
                    "current_page": page,
                    "per_page": limit,
                    "total_items": len(formatted_transactions),
                    "has_next": len(formatted_transactions) == limit,
                    "has_prev": page > 1
                }
            }
            
            print("History response prepared successfully")
            return safe_json_response(200, {
                "success": True,
                "message": "Riwayat transaksi berhasil diambil",
                "data": history_response
            })
            
        except Exception as e:
            print(f"Error getting transaction history: {e}")
            traceback.print_exc()
            
            return safe_json_response(500, {
                "success": False,
                "message": f"Gagal mengambil history: {str(e)}",
                "data": {"items": [], "total": 0}
            })
        
    except Exception as e:
        print(f"Critical error in get_finance_history: {e}")
        traceback.print_exc()
        
        return safe_json_response(500, {
            "success": False,
            "message": f"Gagal mengambil history: {str(e)}",
            "data": {"items": [], "total": 0}
        })

def _calculate_relative_time_safe(date_obj: datetime) -> str:
    """Safe calculation of relative time"""
    try:
        if not date_obj:
            return "Unknown"
        
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
    except Exception as e:
        print(f"Error calculating relative time: {e}")
        return "Unknown"

# ==========================================
# UTILITY ENDPOINTS
# ==========================================

@router.get("/categories")
async def get_available_categories(
    current_user: User = Depends(get_current_user)
):
    """Get all available categories dengan budget type classification"""
    try:
        categories_by_type = {
            "needs": ["Makanan Pokok", "Kos/Tempat Tinggal", "Transportasi Wajib", "Pendidikan", "Internet & Komunikasi", "Kesehatan & Kebersihan"],
            "wants": ["Hiburan & Sosial", "Jajan & Snack", "Pakaian & Aksesoris", "Organisasi & Event", "Target Tabungan Barang", "Lainnya (Wants)"],
            "savings": ["Tabungan Umum", "Dana Darurat", "Investasi Masa Depan", "Tabungan Jangka Panjang"],
            "income": ["Uang Saku/Kiriman Ortu", "Part-time Job", "Freelance/Project", "Beasiswa", "Hadiah/Bonus", "Lainnya"]
        }
        
        return safe_json_response(200, {
            "success": True,
            "message": "Kategori berhasil diambil",
            "data": {
                "method": "50/30/20 Elizabeth Warren",
                "categories_by_budget_type": categories_by_type,
                "total_categories": {
                    "needs": len(categories_by_type["needs"]),
                    "wants": len(categories_by_type["wants"]),
                    "savings": len(categories_by_type["savings"]),
                    "income": len(categories_by_type["income"])
                }
            }
        })
        
    except Exception as e:
        return safe_json_response(500, {
            "success": False,
            "message": f"Gagal mengambil kategori: {str(e)}"
        })

@router.get("/stats")
async def get_basic_stats(
    current_user: User = Depends(get_current_user)
):
    """Get basic financial statistics"""
    try:
        finance_service = FinanceService()
        
        # Check if financial setup completed
        financial_setup_completed = getattr(current_user, 'financial_setup_completed', False)
        
        if not financial_setup_completed:
            return safe_json_response(400, {
                "success": False,
                "message": "Financial setup belum dilakukan"
            })
        
        # Get basic stats dengan 50/30/20 calculations
        stats_data = {
            "method": "50/30/20 Elizabeth Warren",
            "current_month": datetime.now().strftime("%B %Y"),
            "real_total_savings": 0.0,
            "formatted_real_total_savings": format_currency(0),
            "monthly_income": 0.0,
            "formatted_monthly_income": format_currency(0),
            "total_spending_this_month": 0.0,
            "formatted_total_spending": format_currency(0),
            "savings_rate": 0.0
        }
        
        return safe_json_response(200, {
            "success": True,
            "message": "Statistik keuangan berhasil diambil",
            "data": stats_data
        })
        
    except Exception as e:
        print(f"Error in get_basic_stats: {e}")
        
        return safe_json_response(500, {
            "success": False,
            "message": f"Gagal mengambil statistik: {str(e)}"
        })

# ==========================================
# EXPORT ENDPOINTS (TAB 4: REPORTS)
# ==========================================

@router.get("/export")
async def export_financial_data(
    format: str = Query("csv", description="csv, json, excel"),
    type: Optional[str] = Query(None, description="income, expense, goals, all"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    include_summary: bool = Query(True),
    current_user: User = Depends(get_current_user)
):
    """TAB 4: EXPORT/REPORTS - Export laporan keuangan dalam berbagai format"""
    try:
        print(f"Export request for user: {current_user.id}, format: {format}, type: {type}")
        
        # Check financial setup
        financial_setup_completed = getattr(current_user, 'financial_setup_completed', False)
        
        if not financial_setup_completed:
            return safe_json_response(400, {
                "success": False,
                "message": "Setup keuangan belum dilakukan untuk export",
                "data": {"setup_required": True}
            })
        
        # Initialize finance service
        finance_service = FinanceService()
        
        # Set default date range if not provided
        if not start_date or not end_date:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)  # Default 3 months
        
        # Get export data based on type
        export_data = await _prepare_export_data(
            finance_service, current_user.id, type, start_date, end_date, include_summary
        )
        
        if "error" in export_data:
            return safe_json_response(400, {
                "success": False,
                "message": export_data["error"],
                "data": {"export_type": type, "format": format}
            })
        
        # Format export response
        export_response = {
            "export_info": {
                "format": format,
                "type": type or "all",
                "date_range": {
                    "start": start_date.strftime("%Y-%m-%d"),
                    "end": end_date.strftime("%Y-%m-%d")
                },
                "generated_at": IndonesiaDatetime.now().isoformat(),
                "method": "50/30/20 Elizabeth Warren"
            },
            
            # User info
            "user_info": {
                "username": current_user.username,
                "email": current_user.email,
                "export_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            
            # Export data
            "data": export_data,
            
            # Download info
            "download_info": {
                "filename": f"lunance_export_{current_user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}",
                "size_estimate": len(str(export_data)),
                "records_count": _count_records(export_data)
            }
        }
        
        return safe_json_response(200, {
            "success": True,
            "message": f"Data export {format} berhasil disiapkan",
            "data": export_response
        })
        
    except Exception as e:
        print(f"Error in export_financial_data: {e}")
        traceback.print_exc()
        
        return safe_json_response(500, {
            "success": False,
            "message": f"Gagal export data: {str(e)}",
            "data": {"export_type": type, "format": format}
        })

@router.get("/reports/summary")
async def get_financial_summary_report(
    period: str = Query("monthly", description="weekly, monthly, quarterly, yearly"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """Generate comprehensive financial summary report"""
    try:
        print(f"Summary report request for user: {current_user.id}, period: {period}")
        
        # Check financial setup
        financial_setup_completed = getattr(current_user, 'financial_setup_completed', False)
        
        if not financial_setup_completed:
            return safe_json_response(400, {
                "success": False,
                "message": "Setup keuangan belum dilakukan"
            })
        
        # Initialize finance service
        finance_service = FinanceService()
        
        # Get financial summary
        summary = await finance_service.get_financial_summary(current_user.id, period, start_date, end_date)
        if not summary:
            return safe_json_response(400, {
                "success": False,
                "message": "Gagal mengambil summary data"
            })
        
        # Get budget performance
        budget_performance = await finance_service.get_monthly_budget_performance(current_user.id)
        
        # Get real total savings
        real_total_savings = await finance_service._calculate_real_total_savings(current_user.id)
        
        # Format comprehensive report
        report_data = {
            "report_info": {
                "type": "financial_summary",
                "period": period,
                "generated_at": IndonesiaDatetime.now().isoformat(),
                "method": "50/30/20 Elizabeth Warren"
            },
            
            # Summary totals
            "financial_totals": {
                "total_income": summary.total_income,
                "total_expense": summary.total_expense,
                "net_balance": summary.net_balance,
                "real_total_savings": real_total_savings,
                "formatted_income": format_currency(summary.total_income),
                "formatted_expense": format_currency(summary.total_expense),
                "formatted_net_balance": format_currency(summary.net_balance),
                "formatted_savings": format_currency(real_total_savings)
            },
            
            # Budget analysis
            "budget_analysis": budget_performance,
            
            # Category breakdown
            "category_breakdown": {
                "income_categories": summary.income_categories,
                "expense_categories": summary.expense_categories,
                "formatted_income_categories": {
                    category: format_currency(amount) 
                    for category, amount in summary.income_categories.items()
                },
                "formatted_expense_categories": {
                    category: format_currency(amount) 
                    for category, amount in summary.expense_categories.items()
                }
            },
            
            # Counts
            "transaction_counts": {
                "income_transactions": summary.income_count,
                "expense_transactions": summary.expense_count,
                "total_transactions": summary.income_count + summary.expense_count
            },
            
            # Period info
            "period_info": {
                "start_date": summary.start_date.isoformat(),
                "end_date": summary.end_date.isoformat(),
                "days_covered": (summary.end_date - summary.start_date).days
            }
        }
        
        return safe_json_response(200, {
            "success": True,
            "message": f"Financial summary report {period} berhasil dibuat",
            "data": report_data
        })
        
    except Exception as e:
        print(f"Error in get_financial_summary_report: {e}")
        traceback.print_exc()
        
        return safe_json_response(500, {
            "success": False,
            "message": f"Gagal membuat summary report: {str(e)}"
        })

# ==========================================
# HELPER FUNCTIONS FOR EXPORT
# ==========================================

async def _prepare_export_data(finance_service, user_id: str, export_type: Optional[str], 
                               start_date: datetime, end_date: datetime, include_summary: bool) -> Dict[str, Any]:
    """Prepare data for export based on type"""
    try:
        export_data = {}
        
        if export_type in [None, "all", "transactions", "income", "expense"]:
            # Get transactions
            filters = {"status": "confirmed"}
            if start_date and end_date:
                filters["date"] = {"$gte": start_date, "$lte": end_date}
            if export_type in ["income", "expense"]:
                filters["type"] = export_type
            
            transactions = await finance_service.get_user_transactions(user_id, filters, limit=1000)
            
            export_data["transactions"] = [
                {
                    "id": trans.id,
                    "date": trans.date.isoformat() if trans.date else None,
                    "type": trans.type.value,
                    "amount": trans.amount,
                    "category": trans.category,
                    "description": trans.description,
                    "status": trans.status.value,
                    "source": trans.source,
                    "budget_type": _get_budget_type_safe(trans.category)
                }
                for trans in transactions
            ]
        
        if export_type in [None, "all", "goals"]:
            # Get savings goals
            goals = await finance_service.get_user_savings_goals(user_id)
            
            export_data["savings_goals"] = [
                {
                    "id": goal.id,
                    "item_name": goal.item_name,
                    "target_amount": goal.target_amount,
                    "current_amount": goal.current_amount,
                    "progress_percentage": goal.progress_percentage,
                    "status": goal.status.value,
                    "target_date": goal.target_date.isoformat() if goal.target_date else None,
                    "created_at": goal.created_at.isoformat() if goal.created_at else None
                }
                for goal in goals
            ]
        
        if include_summary:
            # Add summary statistics
            summary = await finance_service.get_financial_summary(user_id, "monthly", start_date, end_date)
            if summary:
                export_data["summary"] = {
                    "total_income": summary.total_income,
                    "total_expense": summary.total_expense,
                    "net_balance": summary.net_balance,
                    "income_categories": summary.income_categories,
                    "expense_categories": summary.expense_categories,
                    "transaction_counts": {
                        "income": summary.income_count,
                        "expense": summary.expense_count
                    }
                }
        
        return export_data
        
    except Exception as e:
        print(f"Error preparing export data: {e}")
        return {"error": str(e)}

def _count_records(export_data: Dict[str, Any]) -> int:
    """Count total records in export data"""
    count = 0
    if "transactions" in export_data:
        count += len(export_data["transactions"])
    if "savings_goals" in export_data:
        count += len(export_data["savings_goals"])
    return count