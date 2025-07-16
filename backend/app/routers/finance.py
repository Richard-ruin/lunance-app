# app/routers/finance.py - FIXED JSON serialization untuk datetime
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
    return f"Rp {amount:,.0f}".replace(',', '.')

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
        # Serialize datetime objects
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
# TAB 1: DASHBOARD - Overview Keuangan 50/30/20
# ==========================================

@router.get("/dashboard")
async def get_finance_dashboard(
    current_user: User = Depends(get_current_user)
):
    """
    TAB 1: DASHBOARD - Overview lengkap keuangan dengan metode 50/30/20
    """
    try:
        # Initialize finance service
        finance_service = FinanceService()
        
        # Cek apakah user ada financial_setup_completed attribute
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
        
        # Get comprehensive dashboard data with error handling
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
        
        # Get budget performance dengan error handling
        try:
            budget_performance = dashboard_data.get("budget_performance", {})
        except Exception as e:
            print(f"Error getting budget performance: {e}")
            budget_performance = {}
        
        # Format dashboard response dengan safe access dan datetime serialization
        dashboard_response = {
            "method": "50/30/20 Elizabeth Warren",
            "current_month": datetime.now().strftime("%B %Y"),
            "setup_completed": True,
            
            # Budget Overview dengan safe access
            "budget_overview": {
                "monthly_income": dashboard_data.get("user_financial_settings", {}).get("monthly_income", 0),
                "formatted_monthly_income": format_currency(dashboard_data.get("user_financial_settings", {}).get("monthly_income", 0)),
                "allocation": {
                    "needs": _safe_get_allocation_data(budget_performance, "needs"),
                    "wants": _safe_get_allocation_data(budget_performance, "wants"),
                    "savings": _safe_get_allocation_data(budget_performance, "savings")
                }
            },
            
            # Financial Summary dengan safe access
            "financial_summary": {
                "real_total_savings": dashboard_data.get("real_total_savings", 0),
                "formatted_real_total_savings": format_currency(dashboard_data.get("real_total_savings", 0)),
                "initial_savings": dashboard_data.get("user_financial_settings", {}).get("initial_savings", 0),
                "formatted_initial_savings": format_currency(dashboard_data.get("user_financial_settings", {}).get("initial_savings", 0)),
                "primary_bank": dashboard_data.get("user_financial_settings", {}).get("primary_bank", ""),
                "last_budget_reset": _safe_datetime_to_string(dashboard_data.get("user_financial_settings", {}).get("last_budget_reset"))
            },
            
            # Budget Health & Status dengan safe access
            "budget_health": {
                "overall_status": budget_performance.get("overall", {}).get("budget_health", "unknown"),
                "total_spent": budget_performance.get("overall", {}).get("total_spent", 0),
                "total_remaining": budget_performance.get("overall", {}).get("total_remaining", 0),
                "percentage_used": budget_performance.get("overall", {}).get("percentage_used", 0),
                "formatted_total_spent": format_currency(budget_performance.get("overall", {}).get("total_spent", 0)),
                "formatted_total_remaining": format_currency(budget_performance.get("overall", {}).get("total_remaining", 0)),
                "strongest_category": dashboard_data.get("insights", {}).get("strongest_category", "unknown"),
                "needs_attention": dashboard_data.get("insights", {}).get("needs_attention", "none"),
                "recommendations": budget_performance.get("recommendations", [])
            },
            
            # Savings Goals dengan safe access
            "wants_savings_goals": _safe_get_savings_goals(dashboard_data),
            
            # Recent Activity dengan safe access dan datetime serialization
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
        
        return safe_json_response(200, {
            "success": True,
            "message": "Dashboard keuangan 50/30/20 berhasil diambil",
            "data": dashboard_response
        })
        
    except Exception as e:
        print(f"Error in get_finance_dashboard: {e}")
        traceback.print_exc()
        
        return safe_json_response(500, {
            "success": False,
            "message": f"Gagal mengambil dashboard: {str(e)}",
            "data": {"setup_required": True}
        })

def _safe_datetime_to_string(dt) -> Optional[str]:
    """Safely convert datetime to string"""
    if dt is None:
        return None
    if isinstance(dt, datetime):
        return dt.isoformat()
    if isinstance(dt, str):
        return dt
    return str(dt)

def _safe_serialize_transactions(transactions: List) -> List:
    """Safely serialize transactions list dengan datetime handling"""
    serialized = []
    for trans in transactions:
        try:
            if isinstance(trans, dict):
                serialized_trans = {}
                for key, value in trans.items():
                    if isinstance(value, datetime):
                        serialized_trans[key] = value.isoformat()
                    else:
                        serialized_trans[key] = value
                serialized.append(serialized_trans)
            else:
                # If it's an object, convert to dict first
                trans_dict = trans.__dict__ if hasattr(trans, '__dict__') else {}
                serialized_trans = {}
                for key, value in trans_dict.items():
                    if isinstance(value, datetime):
                        serialized_trans[key] = value.isoformat()
                    else:
                        serialized_trans[key] = value
                serialized.append(serialized_trans)
        except Exception as e:
            print(f"Error serializing transaction: {e}")
            continue
    return serialized

def _safe_get_allocation_data(budget_performance: Dict, category: str) -> Dict:
    """Helper function untuk safely get allocation data"""
    try:
        performance = budget_performance.get("performance", {}).get(category, {})
        budget_allocation = budget_performance.get("budget_allocation", {})
        
        budget_key = f"{category}_budget"
        budget = budget_allocation.get(budget_key, 0)
        spent = performance.get("spent", 0)
        remaining = performance.get("remaining", 0)
        percentage_used = performance.get("percentage_used", 0)
        status = performance.get("status", "unknown")
        
        return {
            "budget": budget,
            "spent": spent,
            "remaining": remaining,
            "percentage_used": percentage_used,
            "status": status,
            "formatted_budget": format_currency(budget),
            "formatted_spent": format_currency(spent),
            "formatted_remaining": format_currency(remaining),
        }
    except Exception as e:
        print(f"Error getting allocation data for {category}: {e}")
        return {
            "budget": 0,
            "spent": 0,
            "remaining": 0,
            "percentage_used": 0,
            "status": "unknown",
            "formatted_budget": format_currency(0),
            "formatted_spent": format_currency(0),
            "formatted_remaining": format_currency(0),
        }

def _safe_get_savings_goals(dashboard_data: Dict) -> Dict:
    """Helper function untuk safely get savings goals data dengan datetime serialization"""
    try:
        goals_data = dashboard_data.get("wants_budget_goals", {})
        goals = goals_data.get("goals", [])
        
        formatted_goals = []
        for goal in goals[:5]:  # Top 5 goals
            try:
                formatted_goal = {
                    "id": goal.get("id"),
                    "item_name": goal.get("item_name"),
                    "target_amount": goal.get("target_amount", 0),
                    "current_amount": goal.get("current_amount", 0),
                    "progress_percentage": goal.get("progress_percentage", 0),
                    "target_date": _safe_datetime_to_string(goal.get("target_date")),
                    "days_remaining": goal.get("days_remaining"),
                    "is_urgent": goal.get("is_urgent", False),
                    "budget_source": "wants_30_percent"
                }
                formatted_goals.append(formatted_goal)
            except Exception as e:
                print(f"Error formatting goal: {e}")
                continue
        
        return {
            "total_goals": goals_data.get("total_goals", 0),
            "total_allocated": goals_data.get("total_allocated", 0),
            "total_target": goals_data.get("total_target", 0),
            "formatted_total_allocated": format_currency(goals_data.get("total_allocated", 0)),
            "formatted_total_target": format_currency(goals_data.get("total_target", 0)),
            "goals": formatted_goals,
            "progress_percentage": (goals_data.get("total_allocated", 0) / goals_data.get("total_target", 1) * 100) if goals_data.get("total_target", 0) > 0 else 0
        }
    except Exception as e:
        print(f"Error getting savings goals: {e}")
        return {
            "total_goals": 0,
            "total_allocated": 0,
            "total_target": 0,
            "formatted_total_allocated": format_currency(0),
            "formatted_total_target": format_currency(0),
            "goals": [],
            "progress_percentage": 0
        }

@router.get("/dashboard/quick-stats")
async def get_dashboard_quick_stats(
    current_user: User = Depends(get_current_user)
):
    """Quick stats untuk dashboard widgets"""
    try:
        finance_service = FinanceService()
        
        # Check if financial setup completed
        financial_setup_completed = getattr(current_user, 'financial_setup_completed', False)
        
        if not financial_setup_completed:
            return safe_json_response(200, {
                "success": True,
                "data": {"setup_required": True}
            })
        
        # Get real total savings dengan error handling
        try:
            real_total_savings = await finance_service._calculate_real_total_savings(current_user.id)
        except Exception as e:
            print(f"Error calculating real total savings: {e}")
            real_total_savings = 0
        
        # Get current month spending dengan error handling
        try:
            current_spending = await finance_service.get_current_month_spending_by_budget_type(current_user.id)
        except Exception as e:
            print(f"Error getting current month spending: {e}")
            current_spending = {"needs": 0, "wants": 0, "savings": 0}
        
        # Get monthly income dengan safe access
        try:
            financial_settings = getattr(current_user, 'financial_settings', None)
            monthly_income = financial_settings.monthly_income if financial_settings else 0
        except Exception as e:
            print(f"Error getting monthly income: {e}")
            monthly_income = 0
        
        return safe_json_response(200, {
            "success": True,
            "data": {
                "real_total_savings": real_total_savings,
                "formatted_savings": format_currency(real_total_savings),
                "monthly_income": monthly_income,
                "formatted_income": format_currency(monthly_income),
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
                }
            }
        })
        
    except Exception as e:
        print(f"Error in get_dashboard_quick_stats: {e}")
        traceback.print_exc()
        
        return safe_json_response(500, {
            "success": False,
            "message": f"Gagal mengambil quick stats: {str(e)}",
            "data": {"setup_required": True}
        })

# ==========================================
# TAB 2: ANALYTICS - Analisis Mendalam 50/30/20
# ==========================================

@router.get("/analytics")
async def get_finance_analytics(
    period: str = Query("monthly", description="daily, weekly, monthly, yearly"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """
    TAB 2: ANALYTICS - Analisis mendalam keuangan dengan metode 50/30/20
    """
    try:
        finance_service = FinanceService()
        
        # Check if financial setup completed
        financial_setup_completed = getattr(current_user, 'financial_setup_completed', False)
        
        if not financial_setup_completed:
            return safe_json_response(400, {
                "success": False,
                "message": "Financial setup belum dilakukan"
            })
        
        # Get budget performance dengan error handling
        try:
            budget_performance = await finance_service.get_monthly_budget_performance(current_user.id)
        except Exception as e:
            print(f"Error getting budget performance: {e}")
            budget_performance = {"has_budget": False, "error": str(e)}
        
        # Get financial summary dengan error handling
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
                'start_date': start_date or datetime.now(),
                'end_date': end_date or datetime.now(),
                'income_count': 0,
                'expense_count': 0
            })()
        
        # Get kategori breakdown dengan budget type classification
        category_analysis = {}
        budget_type_totals = {"needs": 0, "wants": 0, "savings": 0, "unknown": 0}
        
        try:
            if hasattr(summary, 'expense_categories') and summary.expense_categories:
                for category, amount in summary.expense_categories.items():
                    try:
                        # Try to get budget type, fallback to unknown
                        budget_type = _get_budget_type_safe(category)
                        percentage = (amount / summary.total_expense * 100) if summary.total_expense > 0 else 0
                        
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
        
        # Budget vs Actual comparison dengan safe access
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
        
        # Financial health calculation dengan safe values
        try:
            savings_rate = (summary.net_balance / summary.total_income * 100) if summary.total_income > 0 else 0
            health_score = _calculate_health_score(budget_vs_actual, savings_rate)
        except Exception as e:
            print(f"Error calculating health score: {e}")
            savings_rate = 0
            health_score = 0
        
        # Generate insights
        insights = _generate_insights(budget_vs_actual, savings_rate)
        
        analytics_response = {
            "period": period,
            "period_display": f"{period.title()} Analysis",
            "date_range": {
                "start": _safe_datetime_to_string(start_date) or _safe_datetime_to_string(summary.start_date),
                "end": _safe_datetime_to_string(end_date) or _safe_datetime_to_string(summary.end_date)
            },
            
            # Budget Performance Analysis
            "budget_performance": {
                "method": "50/30/20 Elizabeth Warren",
                "budget_vs_actual": budget_vs_actual,
                "budget_type_totals": {
                    category: {
                        "amount": amount,
                        "formatted": format_currency(amount),
                        "percentage": (amount / summary.total_expense * 100) if summary.total_expense > 0 else 0
                    }
                    for category, amount in budget_type_totals.items()
                }
            },
            
            # Category Analysis
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
            
            # Trends & Insights
            "insights": insights,
            "recommendations": [
                "Maintain 50% needs budget untuk kebutuhan pokok",
                "Allocate 30% wants untuk lifestyle dan target tabungan",
                "Consistently save 20% untuk masa depan",
                "Track spending weekly untuk kontrol budget yang lebih baik"
            ],
            
            # Summary Totals
            "summary": {
                "total_income": summary.total_income,
                "total_expense": summary.total_expense,
                "net_balance": summary.net_balance,
                "formatted_income": format_currency(summary.total_income),
                "formatted_expense": format_currency(summary.total_expense),
                "formatted_net": format_currency(summary.net_balance),
                "transaction_count": summary.income_count + summary.expense_count
            }
        }
        
        return safe_json_response(200, {
            "success": True,
            "message": f"Analytics {period} berhasil diambil",
            "data": analytics_response
        })
        
    except Exception as e:
        print(f"Error in get_finance_analytics: {e}")
        traceback.print_exc()
        
        return safe_json_response(500, {
            "success": False,
            "message": f"Gagal mengambil analytics: {str(e)}",
            "data": {"period": period}
        })

# Helper functions untuk analytics
def _get_budget_type_safe(category: str) -> str:
    """Safe way to get budget type"""
    try:
        # Try to import and use IndonesianStudentCategories
        from ..services.financial_categories import IndonesianStudentCategories
        return IndonesianStudentCategories.get_budget_type(category)
    except ImportError:
        # Fallback categorization
        needs_keywords = ['makan', 'transport', 'kos', 'listrik', 'air', 'internet', 'kesehatan', 'obat']
        wants_keywords = ['jajan', 'cafe', 'nonton', 'game', 'baju', 'sepatu', 'hiburan', 'travel']
        savings_keywords = ['tabungan', 'investasi', 'deposito', 'saham', 'reksadana']
        
        category_lower = category.lower()
        
        for keyword in needs_keywords:
            if keyword in category_lower:
                return "needs"
        
        for keyword in wants_keywords:
            if keyword in category_lower:
                return "wants"
        
        for keyword in savings_keywords:
            if keyword in category_lower:
                return "savings"
        
        return "unknown"

def _get_budget_type_color(budget_type: str) -> str:
    """Get color for budget type"""
    colors = {
        "needs": "#22C55E",    # Green
        "wants": "#F59E0B",    # Orange
        "savings": "#3B82F6",  # Blue
        "unknown": "#6B7280"   # Gray
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
        "percentage": percentage
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

def _generate_insights(budget_vs_actual: Dict, savings_rate: float) -> List[str]:
    """Generate insights based on budget performance"""
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

# ==========================================
# UTILITY ENDPOINTS - Budget & Settings
# ==========================================

@router.get("/budget-status")
async def get_budget_status(
    current_user: User = Depends(get_current_user)
):
    """Get current budget status 50/30/20"""
    try:
        from ..services.auth_service import AuthService
        auth_service = AuthService()
        
        budget_status = await auth_service.get_budget_status(current_user.id)
        
        return safe_json_response(200, {
            "success": True,
            "message": "Budget status berhasil diambil",
            "data": budget_status
        })
        
    except Exception as e:
        return safe_json_response(500, {
            "success": False,
            "message": f"Gagal mengambil budget status: {str(e)}"
        })

@router.get("/categories")
async def get_available_categories(
    current_user: User = Depends(get_current_user)
):
    """Get all available categories dengan budget type classification"""
    try:
        from ..services.financial_categories import IndonesianStudentCategories
        categories_by_type = IndonesianStudentCategories.get_categories_by_budget_type()
        
        return safe_json_response(200, {
            "success": True,
            "message": "Kategori berhasil diambil",
            "data": {
                "method": "50/30/20 Elizabeth Warren",
                "categories_by_budget_type": categories_by_type,
                "budget_allocation_guide": IndonesianStudentCategories.get_budget_allocation_guide(),
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
        
        # Get real total savings
        try:
            real_total_savings = await finance_service._calculate_real_total_savings(current_user.id)
        except Exception as e:
            print(f"Error calculating real total savings: {e}")
            real_total_savings = 0
        
        # Get current month spending
        try:
            current_spending = await finance_service.get_current_month_spending_by_budget_type(current_user.id)
        except Exception as e:
            print(f"Error getting current month spending: {e}")
            current_spending = {"needs": 0, "wants": 0, "savings": 0}
        
        # Get monthly income
        try:
            financial_settings = getattr(current_user, 'financial_settings', None)
            monthly_income = financial_settings.monthly_income if financial_settings else 0
        except Exception as e:
            print(f"Error getting monthly income: {e}")
            monthly_income = 0
        
        # Calculate basic stats
        total_spending = sum(current_spending.values())
        savings_rate = ((monthly_income - total_spending) / monthly_income * 100) if monthly_income > 0 else 0
        
        stats_data = {
            "method": "50/30/20 Elizabeth Warren",
            "current_month": datetime.now().strftime("%B %Y"),
            "real_total_savings": real_total_savings,
            "formatted_real_total_savings": format_currency(real_total_savings),
            "monthly_income": monthly_income,
            "formatted_monthly_income": format_currency(monthly_income),
            "total_spending_this_month": total_spending,
            "formatted_total_spending": format_currency(total_spending),
            "savings_rate": round(savings_rate, 1),
            "spending_by_type": {
                "needs": current_spending["needs"],
                "wants": current_spending["wants"],
                "savings": current_spending["savings"],
                "formatted_needs": format_currency(current_spending["needs"]),
                "formatted_wants": format_currency(current_spending["wants"]),
                "formatted_savings": format_currency(current_spending["savings"])
            },
            "budget_utilization": {
                "needs_percentage": (current_spending["needs"] / (monthly_income * 0.5) * 100) if monthly_income > 0 else 0,
                "wants_percentage": (current_spending["wants"] / (monthly_income * 0.3) * 100) if monthly_income > 0 else 0,
                "savings_percentage": (current_spending["savings"] / (monthly_income * 0.2) * 100) if monthly_income > 0 else 0
            }
        }
        
        return safe_json_response(200, {
            "success": True,
            "message": "Statistik keuangan berhasil diambil",
            "data": stats_data
        })
        
    except Exception as e:
        print(f"Error in get_basic_stats: {e}")
        traceback.print_exc()
        
        return safe_json_response(500, {
            "success": False,
            "message": f"Gagal mengambil statistik: {str(e)}"
        })

@router.get("/progress")
async def get_progress_data(
    current_user: User = Depends(get_current_user)
):
    """Get financial progress data"""
    try:
        finance_service = FinanceService()
        
        # Check if financial setup completed
        financial_setup_completed = getattr(current_user, 'financial_setup_completed', False)
        
        if not financial_setup_completed:
            return safe_json_response(400, {
                "success": False,
                "message": "Financial setup belum dilakukan"
            })
        
        # Get savings goals
        try:
            savings_goals = await finance_service.get_user_savings_goals(current_user.id)
        except Exception as e:
            print(f"Error getting savings goals: {e}")
            savings_goals = []
        
        # Get budget performance
        try:
            budget_performance = await finance_service.get_monthly_budget_performance(current_user.id)
        except Exception as e:
            print(f"Error getting budget performance: {e}")
            budget_performance = {"has_budget": False}
        
        # Get real total savings
        try:
            real_total_savings = await finance_service._calculate_real_total_savings(current_user.id)
        except Exception as e:
            print(f"Error calculating real total savings: {e}")
            real_total_savings = 0
        
        # Get initial savings
        try:
            financial_settings = getattr(current_user, 'financial_settings', None)
            initial_savings = financial_settings.current_savings if financial_settings else 0
        except Exception as e:
            print(f"Error getting initial savings: {e}")
            initial_savings = 0
        
        # Format savings goals
        formatted_goals = []
        for goal in savings_goals:
            try:
                formatted_goal = {
                    "id": goal.id,
                    "item_name": goal.item_name,
                    "target_amount": goal.target_amount,
                    "current_amount": goal.current_amount,
                    "progress_percentage": goal.progress_percentage,
                    "status": goal.status,
                    "target_date": _safe_datetime_to_string(goal.target_date),
                    "formatted_target": format_currency(goal.target_amount),
                    "formatted_current": format_currency(goal.current_amount),
                    "remaining_amount": goal.remaining_amount,
                    "formatted_remaining": format_currency(goal.remaining_amount),
                    "budget_source": "wants_30_percent"
                }
                formatted_goals.append(formatted_goal)
            except Exception as e:
                print(f"Error formatting goal: {e}")
                continue
        
        # Calculate progress metrics
        total_goals = len(savings_goals)
        completed_goals = len([g for g in savings_goals if g.status == "completed"])
        active_goals = len([g for g in savings_goals if g.status == "active"])
        
        # Calculate savings progress
        savings_growth = real_total_savings - initial_savings
        
        progress_data = {
            "method": "50/30/20 Elizabeth Warren",
            "current_month": datetime.now().strftime("%B %Y"),
            "savings_progress": {
                "initial_savings": initial_savings,
                "current_savings": real_total_savings,
                "growth": savings_growth,
                "formatted_initial": format_currency(initial_savings),
                "formatted_current": format_currency(real_total_savings),
                "formatted_growth": format_currency(savings_growth),
                "growth_percentage": (savings_growth / initial_savings * 100) if initial_savings > 0 else 0
            },
            "goals_progress": {
                "total_goals": total_goals,
                "completed_goals": completed_goals,
                "active_goals": active_goals,
                "completion_rate": (completed_goals / total_goals * 100) if total_goals > 0 else 0,
                "goals": formatted_goals
            },
            "budget_progress": {
                "has_budget": budget_performance.get("has_budget", False),
                "budget_health": budget_performance.get("overall", {}).get("budget_health", "unknown"),
                "monthly_income": budget_performance.get("monthly_income", 0),
                "formatted_monthly_income": format_currency(budget_performance.get("monthly_income", 0)),
                "budget_allocation": budget_performance.get("budget_allocation", {}),
                "performance": budget_performance.get("performance", {})
            },
            "insights": [
                f"Total {total_goals} savings goals created",
                f"{completed_goals} goals completed ({(completed_goals/total_goals*100):.1f}%)" if total_goals > 0 else "No goals completed yet",
                f"Savings growth: {format_currency(savings_growth)}" if savings_growth > 0 else "Focus on increasing savings",
                f"Budget health: {budget_performance.get('overall', {}).get('budget_health', 'unknown')}"
            ]
        }
        
        return safe_json_response(200, {
            "success": True,
            "message": "Progress data berhasil diambil",
            "data": progress_data
        })
        
    except Exception as e:
        print(f"Error in get_progress_data: {e}")
        traceback.print_exc()
        
        return safe_json_response(500, {
            "success": False,
            "message": f"Gagal mengambil progress data: {str(e)}"
        })
    

# ==========================================
# TAB 3: HISTORY - Riwayat Transaksi & Goals
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
    """
    TAB 3: HISTORY - Riwayat lengkap transaksi dan savings goals
    
    Features:
    - Filter by transaction type, budget type (50/30/20), category
    - Search dalam deskripsi
    - Date range filtering
    - Pagination dengan sorting
    - Export capabilities
    - Bulk actions
    """
    try:
        if not current_user.financial_setup_completed:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": "Financial setup belum dilakukan"
                }
            )
        
        # Build filters
        filters = {"status": "confirmed"}
        
        if type and type != "all":
            if type == "goals":
                # Handle savings goals separately
                savings_goals = await finance_service.get_user_savings_goals(current_user.id)
                
                formatted_goals = []
                for goal in savings_goals:
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
                        "created_at": goal.created_at.isoformat()
                    })
                
                return JSONResponse(
                    status_code=200,
                    content={
                        "success": True,
                        "message": "Riwayat savings goals berhasil diambil",
                        "data": {
                            "items": formatted_goals,
                            "type": "savings_goals",
                            "total": len(formatted_goals),
                            "pagination": {
                                "current_page": page,
                                "per_page": limit,
                                "total_items": len(formatted_goals)
                            }
                        }
                    }
                )
            else:
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
        
        # Apply search filter dan format
        filtered_transactions = []
        for trans in transactions:
            # Search filter
            if search and search.lower() not in trans.description.lower():
                continue
            
            # Determine budget type if not present
            budget_type_display = "unknown"
            if trans.type == "expense":
                budget_type_display = IndonesianStudentCategories.get_budget_type(trans.category)
            
            # Format transaction
            formatted_trans = {
                "id": trans.id,
                "type": trans.type,
                "amount": trans.amount,
                "formatted_amount": format_currency(trans.amount),
                "category": trans.category,
                "budget_type": budget_type_display,
                "budget_type_color": {
                    "needs": "#22C55E",
                    "wants": "#F59E0B", 
                    "savings": "#3B82F6",
                    "unknown": "#6B7280"
                }.get(budget_type_display, "#6B7280"),
                "description": trans.description,
                "date": trans.date.isoformat(),
                "formatted_date": IndonesiaDatetime.format_date_only(trans.date),
                "formatted_time": IndonesiaDatetime.format_time_only(trans.date),
                "relative_date": IndonesiaDatetime.format_relative(trans.date),
                "status": trans.status,
                "source": trans.source,
                "tags": trans.tags
            }
            
            filtered_transactions.append(formatted_trans)
        
        # Sort transactions
        if sort_by == "date":
            filtered_transactions.sort(key=lambda x: x["date"], reverse=(sort_order == "desc"))
        elif sort_by == "amount":
            filtered_transactions.sort(key=lambda x: x["amount"], reverse=(sort_order == "desc"))
        elif sort_by == "category":
            filtered_transactions.sort(key=lambda x: x["category"], reverse=(sort_order == "desc"))
        
        # Calculate summary for filtered data
        total_income = sum(t["amount"] for t in filtered_transactions if t["type"] == "income")
        total_expense = sum(t["amount"] for t in filtered_transactions if t["type"] == "expense")
        
        # Budget type breakdown
        budget_breakdown = {"needs": 0, "wants": 0, "savings": 0, "unknown": 0}
        for trans in filtered_transactions:
            if trans["type"] == "expense":
                budget_breakdown[trans["budget_type"]] += trans["amount"]
        
        history_response = {
            "items": filtered_transactions,
            "summary": {
                "total_income": total_income,
                "total_expense": total_expense,
                "net_balance": total_income - total_expense,
                "formatted_income": format_currency(total_income),
                "formatted_expense": format_currency(total_expense),
                "formatted_net": format_currency(total_income - total_expense),
                "transaction_count": len(filtered_transactions),
                "budget_breakdown": {
                    category: {
                        "amount": amount,
                        "formatted": format_currency(amount),
                        "percentage": (amount / total_expense * 100) if total_expense > 0 else 0
                    }
                    for category, amount in budget_breakdown.items()
                }
            },
            "filters_applied": {
                "type": type,
                "budget_type": budget_type,
                "category": category,
                "date_range": f"{start_date} - {end_date}" if start_date and end_date else None,
                "search": search
            },
            "pagination": {
                "current_page": page,
                "per_page": limit,
                "total_items": len(filtered_transactions),
                "has_next": len(filtered_transactions) == limit,  # Simplified check
                "has_prev": page > 1
            },
            "available_filters": {
                "types": ["income", "expense", "goals", "all"],
                "budget_types": ["needs", "wants", "savings"],
                "categories": {
                    "needs": IndonesianStudentCategories.get_all_needs_categories(),
                    "wants": IndonesianStudentCategories.get_all_wants_categories(),
                    "savings": IndonesianStudentCategories.get_all_savings_categories(),
                    "income": IndonesianStudentCategories.get_all_income_categories()
                }
            }
        }
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Riwayat transaksi berhasil diambil",
                "data": history_response
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil history: {str(e)}")

@router.get("/history/export")
async def export_finance_history(
    format: str = Query("csv", description="csv, json, excel"),
    type: Optional[str] = Query(None, description="income, expense, goals, all"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """Export history data dalam berbagai format"""
    try:
        # Get all matching transactions for export
        filters = {"status": "confirmed"}
        if type and type != "all":
            filters["type"] = type
        if start_date or end_date:
            date_filter = {}
            if start_date:
                date_filter["$gte"] = start_date
            if end_date:
                date_filter["$lte"] = end_date
            filters["date"] = date_filter
        
        transactions = await finance_service.get_user_transactions(
            current_user.id, filters, 10000, 0  # Get all for export
        )
        
        # Prepare export data
        export_data = {
            "user_info": {
                "username": current_user.username,
                "email": current_user.email,
                "university": current_user.profile.university if current_user.profile else "",
                "export_date": IndonesiaDatetime.now().isoformat(),
                "method": "50/30/20 Elizabeth Warren",
                "date_range": f"{start_date} to {end_date}" if start_date and end_date else "All time"
            },
            "transactions": [
                {
                    "date": t.date.isoformat(),
                    "type": t.type,
                    "amount": t.amount,
                    "formatted_amount": format_currency(t.amount),
                    "category": t.category,
                    "budget_type": IndonesianStudentCategories.get_budget_type(t.category) if t.type == "expense" else "income",
                    "description": t.description,
                    "source": t.source,
                    "status": t.status
                }
                for t in transactions
            ],
            "summary": {
                "total_transactions": len(transactions),
                "total_income": sum(t.amount for t in transactions if t.type == "income"),
                "total_expense": sum(t.amount for t in transactions if t.type == "expense"),
                "format": format
            }
        }
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": f"Data export dalam format {format} berhasil disiapkan",
                "data": export_data,
                "download_info": {
                    "filename": f"lunance_finance_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}",
                    "total_records": len(transactions),
                    "file_size_estimate": f"{len(str(export_data)) / 1024:.1f} KB"
                }
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal export data: {str(e)}")
