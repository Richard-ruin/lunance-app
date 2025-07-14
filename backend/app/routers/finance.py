# app/routers/finance.py - Complete routes untuk mahasiswa Indonesia
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import statistics
import warnings
warnings.filterwarnings('ignore')

from ..services.auth_dependency import get_current_user
from ..services.finance_service import FinanceService
from ..services.financial_categories import IndonesianStudentCategories
from ..models.user import User
from ..utils.timezone_utils import IndonesiaDatetime

router = APIRouter(prefix="/finance", tags=["Finance Analytics - Indonesian Students"])
finance_service = FinanceService()

def format_currency(amount: float) -> str:
    """Format jumlah uang ke format Rupiah"""
    return f"Rp {amount:,.0f}".replace(',', '.')

class StudentFinanceCalculator:
    """Calculator khusus untuk keuangan mahasiswa Indonesia"""
    
    @staticmethod
    async def calculate_real_total_savings(user_id: str, finance_service) -> float:
        """
        Hitung total tabungan real-time:
        Total tabungan = Tabungan awal (dari setup) + Total pemasukan - Total pengeluaran
        """
        try:
            # Get user's initial savings from financial setup
            from ..services.auth_service import AuthService
            auth_service = AuthService()
            user = await auth_service.get_user_by_id(user_id)
            
            initial_savings = 0.0
            if user and user.financial_settings:
                initial_savings = user.financial_settings.current_savings or 0.0
            
            # Get all confirmed transactions
            all_transactions = await finance_service.get_user_transactions(
                user_id, {"status": "confirmed"}, 10000, 0
            )
            
            total_income = sum(t.amount for t in all_transactions if t.type == "income")
            total_expense = sum(t.amount for t in all_transactions if t.type == "expense")
            
            # Real total savings = initial + income - expense
            real_total_savings = initial_savings + total_income - total_expense
            
            return max(real_total_savings, 0.0)  # Cannot be negative
            
        except Exception as e:
            print(f"Error calculating real total savings: {e}")
            return 0.0
    
    @staticmethod
    async def calculate_monthly_savings_capacity(user_id: str, finance_service) -> Dict[str, float]:
        """
        Hitung kapasitas tabungan bulanan:
        Target tabungan per bulan = Total pemasukan bulan ini - Total pengeluaran bulan ini
        Reset setiap tanggal 1
        """
        try:
            # Get current month transactions
            now = IndonesiaDatetime.now()
            start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            monthly_summary = await finance_service.get_financial_summary(
                user_id, "monthly", start_of_month, None
            )
            
            monthly_income = monthly_summary.total_income
            monthly_expense = monthly_summary.total_expense
            monthly_net_savings = monthly_income - monthly_expense
            
            # Get user's target from financial settings
            from ..services.auth_service import AuthService
            auth_service = AuthService()
            user = await auth_service.get_user_by_id(user_id)
            
            target_savings = 0.0
            if user and user.financial_settings:
                target_savings = user.financial_settings.monthly_savings_target or 0.0
            
            return {
                "monthly_income": monthly_income,
                "monthly_expense": monthly_expense,
                "actual_monthly_savings": monthly_net_savings,
                "target_monthly_savings": target_savings,
                "savings_difference": monthly_net_savings - target_savings,
                "achievement_percentage": (monthly_net_savings / target_savings * 100) if target_savings > 0 else 0
            }
            
        except Exception as e:
            print(f"Error calculating monthly savings capacity: {e}")
            return {
                "monthly_income": 0.0,
                "monthly_expense": 0.0,
                "actual_monthly_savings": 0.0,
                "target_monthly_savings": 0.0,
                "savings_difference": 0.0,
                "achievement_percentage": 0.0
            }
    
    @staticmethod
    async def calculate_available_for_goals(user_id: str, finance_service) -> Dict[str, Any]:
        """
        Hitung dana yang tersedia untuk target tabungan:
        Available = Total tabungan - rata-rata pemasukan per bulan - dana darurat
        Jika masih ada lebih, bisa dialokasikan ke target tabungan dengan prioritas waktu
        """
        try:
            # Get real total savings
            total_savings = await StudentFinanceCalculator.calculate_real_total_savings(user_id, finance_service)
            
            # Get average monthly income (last 6 months)
            end_date = IndonesiaDatetime.now()
            start_date = end_date - timedelta(days=180)  # 6 months
            
            transactions = await finance_service.get_user_transactions(
                user_id, 
                {"status": "confirmed", "start_date": start_date, "end_date": end_date},
                10000, 0
            )
            
            monthly_incomes = {}
            for trans in transactions:
                if trans.type == "income":
                    month_key = trans.date.strftime("%Y-%m")
                    monthly_incomes[month_key] = monthly_incomes.get(month_key, 0) + trans.amount
            
            avg_monthly_income = sum(monthly_incomes.values()) / max(len(monthly_incomes), 1)
            
            # Get emergency fund
            from ..services.auth_service import AuthService
            auth_service = AuthService()
            user = await auth_service.get_user_by_id(user_id)
            
            emergency_fund = 0.0
            if user and user.financial_settings:
                emergency_fund = user.financial_settings.emergency_fund or 0.0
            
            # Calculate available amount
            reserved_amount = avg_monthly_income + emergency_fund
            available_for_goals = max(total_savings - reserved_amount, 0.0)
            
            # Get active savings goals sorted by target date
            active_goals = await finance_service.get_user_savings_goals(user_id, "active")
            
            # Sort by target date (earliest first), then by priority
            goals_with_priority = []
            for goal in active_goals:
                priority_score = 0
                if goal.target_date:
                    days_until_target = (goal.target_date - datetime.now()).days
                    priority_score = 1000 - days_until_target  # Earlier dates get higher priority
                else:
                    priority_score = 0  # No date = lowest priority
                
                goals_with_priority.append({
                    "goal": goal,
                    "priority_score": priority_score,
                    "remaining_needed": goal.remaining_amount
                })
            
            goals_with_priority.sort(key=lambda x: x["priority_score"], reverse=True)
            
            # Allocate available funds to goals
            allocation_suggestions = []
            remaining_available = available_for_goals
            
            for goal_data in goals_with_priority:
                goal = goal_data["goal"]
                needed = goal_data["remaining_needed"]
                
                if remaining_available <= 0:
                    break
                
                can_allocate = min(remaining_available, needed)
                if can_allocate > 0:
                    allocation_suggestions.append({
                        "goal_id": goal.id,
                        "goal_name": goal.item_name,
                        "suggested_allocation": can_allocate,
                        "remaining_after_allocation": needed - can_allocate,
                        "target_date": goal.target_date.isoformat() if goal.target_date else None
                    })
                    remaining_available -= can_allocate
            
            return {
                "total_savings": total_savings,
                "avg_monthly_income": avg_monthly_income,
                "emergency_fund": emergency_fund,
                "reserved_amount": reserved_amount,
                "available_for_goals": available_for_goals,
                "remaining_after_allocation": remaining_available,
                "allocation_suggestions": allocation_suggestions,
                "total_active_goals": len(active_goals)
            }
            
        except Exception as e:
            print(f"Error calculating available for goals: {e}")
            return {
                "total_savings": 0.0,
                "avg_monthly_income": 0.0,
                "emergency_fund": 0.0,
                "reserved_amount": 0.0,
                "available_for_goals": 0.0,
                "remaining_after_allocation": 0.0,
                "allocation_suggestions": [],
                "total_active_goals": 0
            }

# === 1. ENHANCED DASHBOARD SUMMARY dengan logika yang diperbaiki ===

@router.get("/student-dashboard")
async def get_student_dashboard_summary(
    current_user: User = Depends(get_current_user)
):
    """Dashboard ringkasan keuangan khusus mahasiswa Indonesia dengan logika yang diperbaiki"""
    try:
        # Calculate real total savings
        real_total_savings = await StudentFinanceCalculator.calculate_real_total_savings(
            current_user.id, finance_service
        )
        
        # Calculate monthly savings capacity
        monthly_capacity = await StudentFinanceCalculator.calculate_monthly_savings_capacity(
            current_user.id, finance_service
        )
        
        # Calculate allocation for goals
        goal_allocation = await StudentFinanceCalculator.calculate_available_for_goals(
            current_user.id, finance_service
        )
        
        # Get monthly summary
        monthly_summary = await finance_service.get_financial_summary(
            current_user.id, "monthly"
        )
        
        # Get user's financial settings
        user_settings = current_user.financial_settings.dict() if current_user.financial_settings else {}
        
        # Get all transactions for total calculation
        all_transactions = await finance_service.get_user_transactions(
            current_user.id, {"status": "confirmed"}, 10000, 0
        )
        
        total_income_ever = sum(t.amount for t in all_transactions if t.type == "income")
        total_expense_ever = sum(t.amount for t in all_transactions if t.type == "expense")
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Dashboard mahasiswa berhasil diambil",
                "data": {
                    "real_financial_totals": {
                        "real_total_savings": real_total_savings,
                        "initial_savings": user_settings.get("current_savings", 0),
                        "total_income_ever": total_income_ever,
                        "total_expense_ever": total_expense_ever,
                        "formatted_real_total": format_currency(real_total_savings),
                        "formatted_initial": format_currency(user_settings.get("current_savings", 0)),
                        "formatted_total_income": format_currency(total_income_ever),
                        "formatted_total_expense": format_currency(total_expense_ever)
                    },
                    "monthly_financial_capacity": {
                        "current_month": IndonesiaDatetime.now().strftime("%B %Y"),
                        "monthly_income": monthly_capacity["monthly_income"],
                        "monthly_expense": monthly_capacity["monthly_expense"],
                        "actual_monthly_savings": monthly_capacity["actual_monthly_savings"],
                        "target_monthly_savings": monthly_capacity["target_monthly_savings"],
                        "achievement_percentage": monthly_capacity["achievement_percentage"],
                        "formatted_income": format_currency(monthly_capacity["monthly_income"]),
                        "formatted_expense": format_currency(monthly_capacity["monthly_expense"]),
                        "formatted_actual_savings": format_currency(monthly_capacity["actual_monthly_savings"]),
                        "formatted_target_savings": format_currency(monthly_capacity["target_monthly_savings"]),
                        "status": "exceeds_target" if monthly_capacity["achievement_percentage"] > 100 else "on_track" if monthly_capacity["achievement_percentage"] >= 75 else "needs_improvement"
                    },
                    "savings_goal_allocation": {
                        "available_for_new_goals": goal_allocation["available_for_goals"],
                        "emergency_fund": goal_allocation["emergency_fund"],
                        "avg_monthly_income": goal_allocation["avg_monthly_income"],
                        "allocation_suggestions": goal_allocation["allocation_suggestions"],
                        "formatted_available": format_currency(goal_allocation["available_for_goals"]),
                        "formatted_emergency": format_currency(goal_allocation["emergency_fund"]),
                        "formatted_avg_income": format_currency(goal_allocation["avg_monthly_income"]),
                        "can_add_new_goals": goal_allocation["available_for_goals"] > 100000  # Minimal 100k untuk goal baru
                    },
                    "student_insights": {
                        "financial_health_score": min(100, max(0, 
                            (monthly_capacity["achievement_percentage"] * 0.4) +
                            (min(real_total_savings / 1000000, 1) * 30) +  # Max 30 points for 1M savings
                            (min(total_income_ever / 2000000, 1) * 20) +  # Max 20 points for 2M income
                            (10 if monthly_summary.expense_categories else 0)  # 10 points for having expense tracking
                        )),
                        "recommendation": "excellent" if monthly_capacity["achievement_percentage"] > 100 and real_total_savings > 2000000 else "good" if monthly_capacity["achievement_percentage"] > 75 else "needs_improvement",
                        "next_milestone": "1 juta" if real_total_savings < 1000000 else "5 juta" if real_total_savings < 5000000 else "10 juta",
                        "days_to_next_milestone": max(1, int((1000000 - real_total_savings) / max(monthly_capacity["actual_monthly_savings"], 50000))) if real_total_savings < 1000000 else None,
                        "student_level": "Pemula" if real_total_savings < 500000 else "Berkembang" if real_total_savings < 2000000 else "Mahir" if real_total_savings < 5000000 else "Expert"
                    }
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil dashboard mahasiswa: {str(e)}")

@router.get("/student-categories")
async def get_student_categories(
    current_user: User = Depends(get_current_user)
):
    """Mendapatkan kategori keuangan khusus mahasiswa Indonesia"""
    try:
        income_categories = IndonesianStudentCategories.get_all_income_categories()
        expense_categories = IndonesianStudentCategories.get_all_expense_categories()
        
        # Get usage statistics from user's actual data
        user_transactions = await finance_service.get_user_transactions(
            current_user.id, {"status": "confirmed"}, 1000, 0
        )
        
        category_usage = {"income": {}, "expense": {}}
        category_amounts = {"income": {}, "expense": {}}
        
        for trans in user_transactions:
            trans_type = "income" if trans.type == "income" else "expense"
            category = trans.category
            category_usage[trans_type][category] = category_usage[trans_type].get(category, 0) + 1
            category_amounts[trans_type][category] = category_amounts[trans_type].get(category, 0) + trans.amount
        
        # Get top categories by amount
        top_income_category = max(category_amounts["income"], key=category_amounts["income"].get) if category_amounts["income"] else None
        top_expense_category = max(category_amounts["expense"], key=category_amounts["expense"].get) if category_amounts["expense"] else None
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Kategori mahasiswa berhasil diambil",
                "data": {
                    "income_categories": income_categories,
                    "expense_categories": expense_categories,
                    "category_suggestions": {
                        "income": IndonesianStudentCategories.get_category_suggestions("income"),
                        "expense": IndonesianStudentCategories.get_category_suggestions("expense")
                    },
                    "user_category_usage": {
                        "income_usage": category_usage["income"],
                        "expense_usage": category_usage["expense"],
                        "income_amounts": {k: format_currency(v) for k, v in category_amounts["income"].items()},
                        "expense_amounts": {k: format_currency(v) for k, v in category_amounts["expense"].items()}
                    },
                    "top_categories": {
                        "most_used_income": max(category_usage["income"], key=category_usage["income"].get) if category_usage["income"] else None,
                        "most_used_expense": max(category_usage["expense"], key=category_usage["expense"].get) if category_usage["expense"] else None,
                        "highest_income_amount": top_income_category,
                        "highest_expense_amount": top_expense_category,
                        "top_income_amount": format_currency(category_amounts["income"].get(top_income_category, 0)) if top_income_category else "Rp 0",
                        "top_expense_amount": format_currency(category_amounts["expense"].get(top_expense_category, 0)) if top_expense_category else "Rp 0"
                    },
                    "total_categories": {
                        "income": len(income_categories),
                        "expense": len(expense_categories)
                    }
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil kategori: {str(e)}")

# === 2. ENHANCED TRANSACTION HISTORY dengan kategori mahasiswa ===

@router.get("/student-history")
async def get_student_transaction_history(
    type: Optional[str] = Query(None, description="income, expense, atau all"),
    category: Optional[str] = Query(None, description="Filter berdasarkan kategori mahasiswa"),
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
    """History transaksi dengan kategori yang disesuaikan untuk mahasiswa Indonesia"""
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
            current_user.id, filters, limit * 2, offset  # Get more to allow filtering
        )
        
        # Apply additional filters and format
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
            
            # Categorize based on student life context
            student_context = ""
            priority_level = "normal"
            
            if trans.category == "Makanan & Minuman":
                student_context = "🍜 Kebutuhan makan sehari-hari"
                priority_level = "high" if trans.amount > 50000 else "normal"
            elif trans.category == "Transportasi":
                student_context = "🚌 Biaya transport kuliah"
                priority_level = "high" if trans.amount > 100000 else "normal"
            elif trans.category == "Pendidikan":
                student_context = "📚 Keperluan kuliah"
                priority_level = "high"
            elif trans.category == "Kos/Tempat Tinggal":
                student_context = "🏠 Biaya tempat tinggal"
                priority_level = "high"
            elif trans.category == "Uang Saku/Kiriman Ortu":
                student_context = "💝 Support keluarga"
                priority_level = "high"
            elif trans.category == "Part-time Job":
                student_context = "💼 Penghasilan sampingan"
                priority_level = "high"
            elif trans.category == "Beasiswa":
                student_context = "🎓 Dana beasiswa"
                priority_level = "high"
            elif trans.category == "Hiburan & Sosial":
                student_context = "🎉 Kegiatan sosial"
                priority_level = "low" if trans.amount > 200000 else "normal"
            
            filtered_transactions.append({
                "id": trans.id,
                "type": trans.type,
                "amount": trans.amount,
                "formatted_amount": format_currency(trans.amount),
                "category": trans.category,
                "student_context": student_context,
                "priority_level": priority_level,
                "description": trans.description,
                "date": trans.date.isoformat(),
                "formatted_date": IndonesiaDatetime.format_date_only(trans.date),
                "relative_date": IndonesiaDatetime.format_relative(trans.date),
                "source": trans.source,
                "tags": trans.tags,
                "is_recurring": "bulanan" in trans.description.lower() or "rutin" in trans.description.lower(),
                "is_large_amount": trans.amount > 500000,  # > 500k considered large for students
                "percentage_of_monthly_budget": 0  # Will be calculated if needed
            })
        
        # Sort and limit
        if sort_by == "date":
            filtered_transactions.sort(key=lambda x: x["date"], reverse=(sort_order == "desc"))
        elif sort_by == "amount":
            filtered_transactions.sort(key=lambda x: x["amount"], reverse=(sort_order == "desc"))
        elif sort_by == "category":
            filtered_transactions.sort(key=lambda x: x["category"], reverse=(sort_order == "desc"))
        
        final_transactions = filtered_transactions[:limit]
        
        # Calculate summary for filtered data
        total_filtered_income = sum(t["amount"] for t in filtered_transactions if t["type"] == "income")
        total_filtered_expense = sum(t["amount"] for t in filtered_transactions if t["type"] == "expense")
        
        # Get savings goals for context
        savings_goals = await finance_service.get_user_savings_goals(current_user.id, "active")
        formatted_goals = []
        for goal in savings_goals[:5]:  # Show top 5
            days_remaining = None
            is_urgent = False
            
            if goal.target_date:
                days_remaining = (goal.target_date - datetime.now()).days
                is_urgent = days_remaining <= 30 and days_remaining > 0
            
            formatted_goals.append({
                "id": goal.id,
                "item_name": goal.item_name,
                "target_amount": goal.target_amount,
                "current_amount": goal.current_amount,
                "formatted_target": format_currency(goal.target_amount),
                "formatted_current": format_currency(goal.current_amount),
                "progress_percentage": goal.progress_percentage,
                "status": goal.status,
                "target_date": goal.target_date.isoformat() if goal.target_date else None,
                "formatted_target_date": IndonesiaDatetime.format_date_only(goal.target_date) if goal.target_date else "Belum ditentukan",
                "days_remaining": days_remaining,
                "is_urgent": is_urgent,
                "monthly_needed": goal.remaining_amount / max(days_remaining / 30, 1) if days_remaining and days_remaining > 0 else 0
            })
        
        # Get category breakdown
        category_breakdown = {}
        for trans in final_transactions:
            cat = trans["category"]
            if cat not in category_breakdown:
                category_breakdown[cat] = {"count": 0, "total": 0, "type": trans["type"]}
            category_breakdown[cat]["count"] += 1
            category_breakdown[cat]["total"] += trans["amount"]
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "History mahasiswa berhasil diambil",
                "data": {
                    "transactions": final_transactions,
                    "savings_goals": formatted_goals,
                    "category_breakdown": {
                        cat: {
                            **data,
                            "formatted_total": format_currency(data["total"]),
                            "avg_amount": data["total"] / data["count"],
                            "formatted_avg": format_currency(data["total"] / data["count"])
                        }
                        for cat, data in category_breakdown.items()
                    },
                    "summary": {
                        "filtered_income": total_filtered_income,
                        "filtered_expense": total_filtered_expense,
                        "filtered_net": total_filtered_income - total_filtered_expense,
                        "formatted_income": format_currency(total_filtered_income),
                        "formatted_expense": format_currency(total_filtered_expense),
                        "formatted_net": format_currency(total_filtered_income - total_filtered_expense),
                        "transaction_count": len(final_transactions),
                        "avg_transaction": (total_filtered_income + total_filtered_expense) / max(len(final_transactions), 1),
                        "biggest_expense": max((t["amount"] for t in final_transactions if t["type"] == "expense"), default=0),
                        "biggest_income": max((t["amount"] for t in final_transactions if t["type"] == "income"), default=0),
                        "formatted_avg": format_currency((total_filtered_income + total_filtered_expense) / max(len(final_transactions), 1)),
                        "formatted_biggest_expense": format_currency(max((t["amount"] for t in final_transactions if t["type"] == "expense"), default=0)),
                        "formatted_biggest_income": format_currency(max((t["amount"] for t in final_transactions if t["type"] == "income"), default=0))
                    },
                    "pagination": {
                        "current_page": page,
                        "per_page": limit,
                        "total_transactions": len(filtered_transactions),
                        "total_goals": len(formatted_goals),
                        "has_next": len(filtered_transactions) > page * limit,
                        "has_prev": page > 1
                    },
                    "filters_applied": {
                        "type": type,
                        "category": category,
                        "date_range": f"{start_date} - {end_date}" if start_date and end_date else None,
                        "amount_range": f"{min_amount} - {max_amount}" if min_amount and max_amount else None,
                        "search": search
                    },
                    "student_insights": {
                        "most_spent_category": max(
                            (data["category"] for data in final_transactions if data["type"] == "expense"),
                            key=lambda cat: sum(t["amount"] for t in final_transactions if t["category"] == cat and t["type"] == "expense"),
                            default="Tidak ada data"
                        ) if any(t["type"] == "expense" for t in final_transactions) else "Tidak ada data",
                        "avg_daily_expense": total_filtered_expense / max(30, 1),  # Assume 30 days
                        "formatted_avg_daily": format_currency(total_filtered_expense / max(30, 1)),
                        "high_priority_expenses": len([t for t in final_transactions if t["priority_level"] == "high" and t["type"] == "expense"]),
                        "large_transactions": len([t for t in final_transactions if t["is_large_amount"]]),
                        "recurring_transactions": len([t for t in final_transactions if t["is_recurring"]])
                    }
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil history mahasiswa: {str(e)}")

# === 3. STUDENT FINANCIAL INSIGHTS ===

@router.get("/student-insights")
async def get_student_financial_insights(
    period: str = Query("monthly", description="weekly, monthly, semester"),
    current_user: User = Depends(get_current_user)
):
    """Insight keuangan khusus untuk mahasiswa Indonesia"""
    try:
        # Get real totals
        real_total_savings = await StudentFinanceCalculator.calculate_real_total_savings(
            current_user.id, finance_service
        )
        
        monthly_capacity = await StudentFinanceCalculator.calculate_monthly_savings_capacity(
            current_user.id, finance_service
        )
        
        # Get period-specific data
        if period == "semester":
            # 6 months period for semester
            start_date = IndonesiaDatetime.now() - timedelta(days=180)
        elif period == "weekly":
            start_date = IndonesiaDatetime.now() - timedelta(days=7)
        else:  # monthly
            start_date = IndonesiaDatetime.now().replace(day=1)
        
        period_summary = await finance_service.get_financial_summary(
            current_user.id, period, start_date, None
        )
        
        # Calculate student-specific insights
        insights = {
            "financial_health": {
                "score": min(100, max(0, 
                    (monthly_capacity["achievement_percentage"] * 0.4) +
                    (min(real_total_savings / 1000000, 1) * 30) +  # Max 30 points for 1M savings
                    (min(period_summary.total_income / 2000000, 1) * 20) +  # Max 20 points for 2M income
                    (10 if period_summary.expense_categories else 0)  # 10 points for having expense tracking
                )),
                "level": "",
                "description": "",
                "areas_for_improvement": []
            },
            "spending_patterns": {
                "top_expense_categories": [],
                "spending_trend": "stable",
                "avg_daily_expense": period_summary.total_expense / 30,
                "biggest_single_expense": 0,
                "most_frequent_category": "",
                "student_specific_analysis": {}
            },
            "savings_performance": {
                "monthly_savings_rate": (monthly_capacity["actual_monthly_savings"] / max(monthly_capacity["monthly_income"], 1)) * 100,
                "savings_consistency": "good",  # Would need historical data to calculate
                "emergency_fund_months": 0,
                "goal_achievement_rate": 0,
                "recommended_savings_rate": 20  # 20% for students
            },
            "recommendations": []
        }
        
        # Calculate health level and areas for improvement
        score = insights["financial_health"]["score"]
        if score >= 80:
            insights["financial_health"]["level"] = "Excellent"
            insights["financial_health"]["description"] = "Keuangan Anda sangat sehat untuk ukuran mahasiswa! Pertahankan kebiasaan baik ini."
        elif score >= 60:
            insights["financial_health"]["level"] = "Good"
            insights["financial_health"]["description"] = "Keuangan Anda cukup baik, ada beberapa area yang bisa diperbaiki."
            insights["financial_health"]["areas_for_improvement"] = ["Tingkatkan dana darurat", "Optimalkan pengeluaran bulanan"]
        elif score >= 40:
            insights["financial_health"]["level"] = "Fair"
            insights["financial_health"]["description"] = "Keuangan Anda perlu perhatian lebih untuk mencapai stabilitas sebagai mahasiswa."
            insights["financial_health"]["areas_for_improvement"] = ["Buat budget bulanan", "Kurangi pengeluaran tidak perlu", "Tingkatkan tabungan"]
        else:
            insights["financial_health"]["level"] = "Needs Improvement"
            insights["financial_health"]["description"] = "Saatnya untuk lebih serius mengelola keuangan mahasiswa."
            insights["financial_health"]["areas_for_improvement"] = ["Mulai tracking pengeluaran", "Buat dana darurat", "Cari sumber penghasilan tambahan"]
        
        # Top expense categories with student context
        if period_summary.expense_categories:
            sorted_expenses = sorted(period_summary.expense_categories.items(), key=lambda x: x[1], reverse=True)
            insights["spending_patterns"]["top_expense_categories"] = []
            
            for cat, amount in sorted_expenses[:5]:
                percentage = (amount / period_summary.total_expense) * 100 if period_summary.total_expense > 0 else 0
                
                # Student-specific analysis
                analysis = ""
                recommendation = ""
                
                if cat == "Makanan & Minuman":
                    if percentage > 40:
                        analysis = "Pengeluaran makan terlalu tinggi untuk mahasiswa"
                        recommendation = "Coba masak sendiri atau cari tempat makan yang lebih hemat"
                    elif percentage > 30:
                        analysis = "Pengeluaran makan dalam batas wajar"
                        recommendation = "Pertahankan, tapi bisa lebih dioptimalkan"
                    else:
                        analysis = "Pengeluaran makan sudah sangat efisien"
                        recommendation = "Sangat baik! Pertahankan pola ini"
                
                elif cat == "Transportasi":
                    if percentage > 25:
                        analysis = "Ongkos transport cukup tinggi"
                        recommendation = "Pertimbangkan transport umum atau berbagi ongkos"
                    else:
                        analysis = "Ongkos transport dalam batas wajar"
                        recommendation = "Sudah efisien"
                
                elif cat == "Hiburan & Sosial":
                    if percentage > 20:
                        analysis = "Pengeluaran hiburan terlalu tinggi untuk mahasiswa"
                        recommendation = "Kurangi ke 10-15% dari total pengeluaran"
                    else:
                        analysis = "Pengeluaran hiburan dalam batas sehat"
                        recommendation = "Balance yang baik antara kebutuhan dan hiburan"
                
                insights["spending_patterns"]["top_expense_categories"].append({
                    "category": cat,
                    "amount": amount,
                    "formatted_amount": format_currency(amount),
                    "percentage": round(percentage, 1),
                    "student_analysis": analysis,
                    "recommendation": recommendation
                })
            
            insights["spending_patterns"]["most_frequent_category"] = sorted_expenses[0][0] if sorted_expenses else ""
        
        # Emergency fund calculation
        if monthly_capacity["monthly_expense"] > 0:
            insights["savings_performance"]["emergency_fund_months"] = real_total_savings / monthly_capacity["monthly_expense"]
        
        # Get user profile for personalized recommendations
        user_profile = current_user.profile
        university = user_profile.university if user_profile else ""
        city = user_profile.city if user_profile else ""
        
        # Generate personalized recommendations
        recommendations = []
        
        # Emergency fund recommendation
        if real_total_savings < 500000:
            recommendations.append({
                "type": "emergency_fund",
                "priority": "high",
                "title": "Bangun Dana Darurat",
                "description": "Mahasiswa perlu dana darurat minimal Rp 500.000 untuk situasi mendesak seperti biaya kesehatan atau keperluan kuliah mendadak.",
                "action": "Sisihkan Rp 25.000 per minggu sampai mencapai Rp 500.000",
                "target_amount": 500000,
                "current_amount": real_total_savings,
                "weekly_target": 25000,
                "time_needed_weeks": max(1, (500000 - real_total_savings) / 25000)
            })
        
        # Savings rate recommendation
        if monthly_capacity["achievement_percentage"] < 50:
            recommendations.append({
                "type": "savings_rate",
                "priority": "medium",
                "title": "Tingkatkan Tingkat Tabungan",
                "description": f"Target tabungan bulanan Anda baru tercapai {monthly_capacity['achievement_percentage']:.1f}%. Ideal untuk mahasiswa adalah 15-20% dari pemasukan.",
                "action": "Review pengeluaran harian dan kurangi kategori hiburan atau jajan",
                "current_rate": monthly_capacity["achievement_percentage"],
                "target_rate": 20
            })
        
        # Food expense optimization
        food_expense = period_summary.expense_categories.get("Makanan & Minuman", 0)
        if food_expense > monthly_capacity["monthly_income"] * 0.4:  # More than 40%
            recommendations.append({
                "type": "expense_optimization",
                "priority": "medium",
                "title": "Optimalkan Pengeluaran Makan",
                "description": f"Pengeluaran makan Anda {(food_expense / monthly_capacity['monthly_income']) * 100:.1f}% dari pemasukan. Ideal untuk mahasiswa adalah 30-35%.",
                "action": "Coba masak sendiri, beli bahan makanan bareng teman kos, atau cari tempat makan dengan harga mahasiswa",
                "current_percentage": (food_expense / monthly_capacity["monthly_income"]) * 100,
                "target_percentage": 35,
                "potential_savings": format_currency(food_expense - (monthly_capacity["monthly_income"] * 0.35))
            })
        
        # Part-time job recommendation
        if monthly_capacity["monthly_income"] < 1000000 and not period_summary.income_categories.get("Part-time Job"):
            recommendations.append({
                "type": "income_increase",
                "priority": "low",
                "title": "Pertimbangkan Kerja Sampingan",
                "description": "Pemasukan bulanan bisa ditingkatkan dengan pekerjaan paruh waktu yang fleksibel dengan jadwal kuliah.",
                "action": "Cari part-time job online seperti freelance writing, design, atau les private",
                "current_income": monthly_capacity["monthly_income"],
                "potential_additional": 500000,
                "suitable_jobs": ["Les private", "Freelance design", "Content writing", "Virtual assistant", "Jual online"]
            })
        
        # Savings goal recommendation
        active_goals = await finance_service.get_user_savings_goals(current_user.id, "active")
        if len(active_goals) == 0 and real_total_savings > 1000000:
            recommendations.append({
                "type": "savings_goal",
                "priority": "low",
                "title": "Buat Target Tabungan Spesifik",
                "description": "Anda sudah punya tabungan yang cukup. Saatnya membuat target untuk barang atau keperluan spesifik.",
                "action": "Buat target tabungan untuk laptop, HP baru, atau liburan. Contoh: 'Mau nabung buat beli laptop 10 juta pada tanggal 22 januari 2026'",
                "suggested_targets": ["Laptop untuk kuliah (8-15 juta)", "Smartphone baru (3-8 juta)", "Dana liburan (2-5 juta)", "Kursus online (500rb-2 juta)"]
            })
        
        # City-specific recommendations
        if city:
            city_lower = city.lower()
            if "jakarta" in city_lower:
                recommendations.append({
                    "type": "location_specific",
                    "priority": "low",
                    "title": "Tips Hemat Jakarta",
                    "description": "Jakarta mahal, tapi ada cara hemat untuk mahasiswa.",
                    "action": "Manfaatkan TransJakarta, KRL, dan cari kos dekat kampus untuk hemat transport",
                    "specific_tips": ["Gunakan TransJakarta dan KRL", "Makan di warteg atau kantin kampus", "Cari kos dekat kampus", "Manfaatkan diskon mahasiswa"]
                })
            elif "bandung" in city_lower:
                recommendations.append({
                    "type": "location_specific",
                    "priority": "low",
                    "title": "Tips Hemat Bandung",
                    "description": "Bandung ramah mahasiswa dengan banyak pilihan hemat.",
                    "action": "Eksplorasi tempat makan murah di sekitar ITB/Unpad dan gunakan angkot",
                    "specific_tips": ["Makan di tempat kuliner mahasiswa", "Gunakan angkot untuk transport", "Manfaatkan udara sejuk untuk jalan kaki", "Cari clothing murah di distro lokal"]
                })
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": f"Insight keuangan mahasiswa periode {period} berhasil diambil",
                "data": {
                    "period_info": {
                        "type": period,
                        "start_date": start_date.isoformat(),
                        "end_date": IndonesiaDatetime.now().isoformat(),
                        "formatted_period": f"{period.title()} - {IndonesiaDatetime.format_date_only(start_date)} sampai {IndonesiaDatetime.format_date_only(IndonesiaDatetime.now())}"
                    },
                    "insights": insights,
                    "recommendations": recommendations,
                    "real_totals": {
                        "total_savings": real_total_savings,
                        "formatted_savings": format_currency(real_total_savings),
                        "monthly_capacity": monthly_capacity,
                        "period_income": period_summary.total_income,
                        "period_expense": period_summary.total_expense,
                        "formatted_period_income": format_currency(period_summary.total_income),
                        "formatted_period_expense": format_currency(period_summary.total_expense)
                    },
                    "student_context": {
                        "university": university,
                        "city": city,
                        "financial_level": current_user._calculate_financial_health_level() if hasattr(current_user, '_calculate_financial_health_level') else "unknown"
                    }
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil insight mahasiswa: {str(e)}")

# === 4. CHARTS DATA - INCOME/EXPENSE BY TIME ===

@router.get("/charts/time-series")
async def get_time_series_chart_data(
    period: str = Query("monthly", description="daily, weekly, monthly"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """Mendapatkan data chart pemasukan/pengeluaran berdasarkan waktu untuk mahasiswa"""
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
                display_key = f"Minggu {IndonesiaDatetime.format_date_only(start_of_week)}"
            elif period == "monthly":
                key = trans.date.strftime("%Y-%m")
                display_key = trans.date.strftime("%B %Y")
            
            if key not in data_points:
                data_points[key] = {
                    "period": display_key,
                    "date_key": key,
                    "income": 0,
                    "expense": 0,
                    "net": 0,
                    "income_count": 0,
                    "expense_count": 0
                }
            
            if trans.type == "income":
                data_points[key]["income"] += trans.amount
                data_points[key]["income_count"] += 1
            else:
                data_points[key]["expense"] += trans.amount
                data_points[key]["expense_count"] += 1
            
            data_points[key]["net"] = data_points[key]["income"] - data_points[key]["expense"]
        
        # Sort by date
        sorted_data = sorted(data_points.values(), key=lambda x: x["date_key"])
        
        # Calculate moving averages for smoother charts
        if len(sorted_data) > 3:
            window_size = min(3, len(sorted_data))
            for i in range(len(sorted_data)):
                start_idx = max(0, i - window_size + 1)
                end_idx = i + 1
                
                window_data = sorted_data[start_idx:end_idx]
                sorted_data[i]["income_avg"] = sum(d["income"] for d in window_data) / len(window_data)
                sorted_data[i]["expense_avg"] = sum(d["expense"] for d in window_data) / len(window_data)
                sorted_data[i]["net_avg"] = sum(d["net"] for d in window_data) / len(window_data)
        
        # Format for chart dengan student-friendly colors
        chart_data = {
            "labels": [point["period"] for point in sorted_data],
            "datasets": [
                {
                    "label": "Pemasukan",
                    "data": [point["income"] for point in sorted_data],
                    "backgroundColor": "rgba(34, 197, 94, 0.8)",  # Green
                    "borderColor": "rgba(34, 197, 94, 1)",
                    "tension": 0.3
                },
                {
                    "label": "Pengeluaran", 
                    "data": [point["expense"] for point in sorted_data],
                    "backgroundColor": "rgba(239, 68, 68, 0.8)",  # Red
                    "borderColor": "rgba(239, 68, 68, 1)",
                    "tension": 0.3
                },
                {
                    "label": "Net Savings",
                    "data": [point["net"] for point in sorted_data],
                    "backgroundColor": "rgba(59, 130, 246, 0.8)",  # Blue
                    "borderColor": "rgba(59, 130, 246, 1)",
                    "tension": 0.3
                }
            ]
        }
        
        # Add moving averages if enough data
        if len(sorted_data) > 3:
            chart_data["datasets"].extend([
                {
                    "label": "Trend Pemasukan",
                    "data": [point.get("income_avg", point["income"]) for point in sorted_data],
                    "backgroundColor": "rgba(34, 197, 94, 0.3)",
                    "borderColor": "rgba(34, 197, 94, 0.7)",
                    "borderDash": [5, 5],
                    "tension": 0.4
                },
                {
                    "label": "Trend Pengeluaran",
                    "data": [point.get("expense_avg", point["expense"]) for point in sorted_data],
                    "backgroundColor": "rgba(239, 68, 68, 0.3)",
                    "borderColor": "rgba(239, 68, 68, 0.7)",
                    "borderDash": [5, 5],
                    "tension": 0.4
                }
            ])
        
        # Calculate additional insights
        total_income = sum(point["income"] for point in sorted_data)
        total_expense = sum(point["expense"] for point in sorted_data)
        avg_monthly_net = sum(point["net"] for point in sorted_data) / len(sorted_data) if sorted_data else 0
        
        # Find best and worst periods
        best_period = max(sorted_data, key=lambda x: x["net"]) if sorted_data else None
        worst_period = min(sorted_data, key=lambda x: x["net"]) if sorted_data else None
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": f"Chart data {period} berhasil diambil",
                "data": {
                    "chart_data": chart_data,
                    "raw_data": sorted_data,
                    "summary": {
                        "total_income": total_income,
                        "total_expense": total_expense,
                        "average_net_savings": avg_monthly_net,
                        "formatted_total_income": format_currency(total_income),
                        "formatted_total_expense": format_currency(total_expense),
                        "formatted_avg_net": format_currency(avg_monthly_net),
                        "savings_rate": (avg_monthly_net / (total_income / len(sorted_data)) * 100) if sorted_data and total_income > 0 else 0
                    },
                    "insights": {
                        "best_period": {
                            "period": best_period["period"] if best_period else "N/A",
                            "net_savings": best_period["net"] if best_period else 0,
                            "formatted_net": format_currency(best_period["net"]) if best_period else "Rp 0"
                        },
                        "worst_period": {
                            "period": worst_period["period"] if worst_period else "N/A",
                            "net_savings": worst_period["net"] if worst_period else 0,
                            "formatted_net": format_currency(worst_period["net"]) if worst_period else "Rp 0"
                        },
                        "trend": "improving" if len(sorted_data) > 1 and sorted_data[-1]["net"] > sorted_data[0]["net"] else "declining" if len(sorted_data) > 1 else "stable",
                        "consistency_score": 100 - (statistics.stdev([p["net"] for p in sorted_data]) / max(abs(avg_monthly_net), 1) * 100) if len(sorted_data) > 1 else 100
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

# === 5. LEGACY ENDPOINTS (untuk backward compatibility) ===

@router.get("/dashboard-summary")
async def get_dashboard_summary(current_user: User = Depends(get_current_user)):
    """Legacy dashboard endpoint - redirects to student dashboard"""
    return await get_student_dashboard_summary(current_user)

@router.get("/categories")
async def get_available_categories(current_user: User = Depends(get_current_user)):
    """Legacy categories endpoint - returns student categories"""
    return await get_student_categories(current_user)

@router.get("/history")
async def get_transaction_history(
    type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    """Legacy history endpoint - redirects to student history"""
    return await get_student_transaction_history(
        type=type, category=category, page=page, limit=limit, current_user=current_user
    )

# === 6. ADDITIONAL UTILITY ENDPOINTS ===

@router.get("/stats")
async def get_basic_stats(
    current_user: User = Depends(get_current_user)
):
    """Mendapatkan statistik dasar untuk dashboard mahasiswa"""
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
        
        # Get real total savings
        real_total_savings = await StudentFinanceCalculator.calculate_real_total_savings(
            current_user.id, finance_service
        )
        
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
                        "transactions": monthly_summary.income_count + monthly_summary.expense_count,
                        "formatted_income": format_currency(monthly_summary.total_income),
                        "formatted_expense": format_currency(monthly_summary.total_expense),
                        "formatted_net": format_currency(monthly_summary.net_balance)
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
                        "total_saved": sum(goal.current_amount for goal in active_goals),
                        "formatted_total_target": format_currency(sum(goal.target_amount for goal in active_goals)),
                        "formatted_total_saved": format_currency(sum(goal.current_amount for goal in active_goals))
                    },
                    "overall_financial_health": {
                        "real_total_savings": real_total_savings,
                        "formatted_real_total": format_currency(real_total_savings),
                        "monthly_savings_rate": (monthly_summary.net_balance / monthly_summary.total_income * 100) if monthly_summary.total_income > 0 else 0,
                        "emergency_fund_coverage": real_total_savings / max(monthly_summary.total_expense, 1),
                        "student_level": "Pemula" if real_total_savings < 500000 else "Berkembang" if real_total_savings < 2000000 else "Mahir" if real_total_savings < 5000000 else "Expert"
                    }
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil statistik: {str(e)}")

@router.get("/export")
async def export_financial_data(
    format: str = Query("csv", description="csv, json, atau excel"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """Export data keuangan mahasiswa"""
    try:
        # Get all transactions in date range
        filters = {"status": "confirmed"}
        if start_date:
            filters["start_date"] = start_date
        if end_date:
            filters["end_date"] = end_date
        
        transactions = await finance_service.get_user_transactions(
            current_user.id, filters, 10000, 0
        )
        
        # Get savings goals
        savings_goals = await finance_service.get_user_savings_goals(current_user.id)
        
        # Get real total savings
        real_total_savings = await StudentFinanceCalculator.calculate_real_total_savings(
            current_user.id, finance_service
        )
        
        # Prepare export data
        export_data = {
            "user_info": {
                "username": current_user.username,
                "email": current_user.email,
                "university": current_user.profile.university if current_user.profile else "",
                "export_date": IndonesiaDatetime.now().isoformat(),
                "date_range": f"{start_date} to {end_date}" if start_date and end_date else "All time"
            },
            "financial_summary": {
                "real_total_savings": real_total_savings,
                "formatted_real_total": format_currency(real_total_savings),
                "total_transactions": len(transactions),
                "total_income": sum(t.amount for t in transactions if t.type == "income"),
                "total_expense": sum(t.amount for t in transactions if t.type == "expense"),
                "active_goals": len([g for g in savings_goals if g.status == "active"])
            },
            "transactions": [
                {
                    "date": t.date.isoformat(),
                    "type": t.type,
                    "amount": t.amount,
                    "category": t.category,
                    "description": t.description,
                    "source": t.source
                }
                for t in transactions
            ],
            "savings_goals": [
                {
                    "item_name": g.item_name,
                    "target_amount": g.target_amount,
                    "current_amount": g.current_amount,
                    "progress_percentage": g.progress_percentage,
                    "status": g.status,
                    "target_date": g.target_date.isoformat() if g.target_date else None,
                    "created_at": g.created_at.isoformat()
                }
                for g in savings_goals
            ]
        }
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": f"Data export dalam format {format} berhasil disiapkan",
                "data": export_data,
                "export_info": {
                    "format": format,
                    "total_transactions": len(transactions),
                    "total_goals": len(savings_goals),
                    "file_size_estimate": f"{len(str(export_data)) / 1024:.1f} KB"
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal export data: {str(e)}")

# === 7. PROGRESS BARS DATA ===

@router.get("/progress")
async def get_progress_data(
    current_user: User = Depends(get_current_user)
):
    """Mendapatkan data progress untuk target tabungan mahasiswa"""
    try:
        # Get monthly progress dengan logika yang diperbaiki
        monthly_capacity = await StudentFinanceCalculator.calculate_monthly_savings_capacity(
            current_user.id, finance_service
        )
        
        # Get all active savings goals
        active_goals = await finance_service.get_user_savings_goals(current_user.id, "active")
        
        # Format savings goals progress dengan enhanced data
        goals_progress = []
        for goal in active_goals:
            # Calculate time progress if target_date exists
            time_progress = None
            days_remaining = None
            is_urgent = False
            monthly_needed = 0
            
            if goal.target_date:
                now = IndonesiaDatetime.now().replace(tzinfo=None)
                total_days = (goal.target_date - goal.created_at).days
                elapsed_days = (now - goal.created_at).days
                days_remaining = (goal.target_date - now).days
                
                time_progress = min((elapsed_days / total_days) * 100, 100) if total_days > 0 else 100
                is_urgent = days_remaining <= 30 and days_remaining > 0
                
                # Calculate monthly needed to reach goal
                months_remaining = max(days_remaining / 30, 0.5)
                monthly_needed = goal.remaining_amount / months_remaining if months_remaining > 0 else 0
            
            # Determine goal category for better insights
            goal_category = "electronics" if any(word in goal.item_name.lower() for word in ["laptop", "hp", "phone", "gadget"]) else \
                          "transport" if any(word in goal.item_name.lower() for word in ["motor", "mobil", "sepeda"]) else \
                          "education" if any(word in goal.item_name.lower() for word in ["kursus", "course", "buku", "kuliah"]) else \
                          "lifestyle" if any(word in goal.item_name.lower() for word in ["liburan", "vacation", "travel"]) else \
                          "other"
            
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
                "formatted_target_date": IndonesiaDatetime.format_date_only(goal.target_date) if goal.target_date else "Belum ditentukan",
                "is_completed": goal.progress_percentage >= 100,
                "is_urgent": is_urgent,
                "days_remaining": days_remaining,
                "monthly_needed": monthly_needed,
                "formatted_monthly_needed": format_currency(monthly_needed),
                "goal_category": goal_category,
                "affordability": "easy" if monthly_needed < monthly_capacity["actual_monthly_savings"] * 0.3 else \
                               "moderate" if monthly_needed < monthly_capacity["actual_monthly_savings"] * 0.6 else \
                               "challenging" if monthly_needed < monthly_capacity["actual_monthly_savings"] else "difficult",
                "created_at": goal.created_at.isoformat()
            })
        
        # Sort by urgency and progress
        goals_progress.sort(key=lambda x: (
            x["is_urgent"],  # Urgent goals first
            -x["progress_percentage"],  # Higher progress first
            x["days_remaining"] if x["days_remaining"] else 999999  # Sooner dates first
        ), reverse=True)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Progress data berhasil diambil",
                "data": {
                    "monthly_savings_progress": {
                        "target": monthly_capacity["target_monthly_savings"],
                        "achieved": monthly_capacity["actual_monthly_savings"],
                        "remaining": max(monthly_capacity["target_monthly_savings"] - monthly_capacity["actual_monthly_savings"], 0),
                        "progress_percentage": round(monthly_capacity["achievement_percentage"], 1),
                        "formatted_target": format_currency(monthly_capacity["target_monthly_savings"]),
                        "formatted_achieved": format_currency(monthly_capacity["actual_monthly_savings"]),
                        "formatted_remaining": format_currency(max(monthly_capacity["target_monthly_savings"] - monthly_capacity["actual_monthly_savings"], 0)),
                        "is_completed": monthly_capacity["achievement_percentage"] >= 100,
                        "month_year": IndonesiaDatetime.now().strftime("%B %Y"),
                        "status": "excellent" if monthly_capacity["achievement_percentage"] > 120 else \
                                 "good" if monthly_capacity["achievement_percentage"] > 100 else \
                                 "on_track" if monthly_capacity["achievement_percentage"] > 75 else \
                                 "needs_improvement",
                        "days_left_in_month": (IndonesiaDatetime.now().replace(day=28) - IndonesiaDatetime.now()).days + 3
                    },
                    "savings_goals_progress": goals_progress,
                    "summary": {
                        "total_active_goals": len(goals_progress),
                        "completed_goals": len([g for g in goals_progress if g["is_completed"]]),
                        "urgent_goals": len([g for g in goals_progress if g["is_urgent"]]),
                        "total_target_amount": sum(g["target_amount"] for g in goals_progress),
                        "total_saved_amount": sum(g["current_amount"] for g in goals_progress),
                        "total_remaining_amount": sum(g["target_amount"] - g["current_amount"] for g in goals_progress),
                        "overall_progress": round((sum(g["current_amount"] for g in goals_progress) / sum(g["target_amount"] for g in goals_progress)) * 100, 1) if goals_progress else 0,
                        "formatted_total_target": format_currency(sum(g["target_amount"] for g in goals_progress)),
                        "formatted_total_saved": format_currency(sum(g["current_amount"] for g in goals_progress)),
                        "formatted_total_remaining": format_currency(sum(g["target_amount"] - g["current_amount"] for g in goals_progress))
                    },
                    "insights": {
                        "most_urgent_goal": next((g for g in goals_progress if g["is_urgent"]), None),
                        "closest_to_completion": max(goals_progress, key=lambda x: x["progress_percentage"]) if goals_progress else None,
                        "largest_goal": max(goals_progress, key=lambda x: x["target_amount"]) if goals_progress else None,
                        "recommended_focus": goals_progress[0] if goals_progress else None,
                        "total_monthly_needed": sum(g["monthly_needed"] for g in goals_progress if g["monthly_needed"]),
                        "affordability_analysis": {
                            "easy_goals": len([g for g in goals_progress if g["affordability"] == "easy"]),
                            "moderate_goals": len([g for g in goals_progress if g["affordability"] == "moderate"]),
                            "challenging_goals": len([g for g in goals_progress if g["affordability"] == "challenging"]),
                            "difficult_goals": len([g for g in goals_progress if g["affordability"] == "difficult"])
                        }
                    }
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil progress data: {str(e)}")

# === 8. CHARTS DATA - BY CATEGORY ===

@router.get("/charts/by-category")
async def get_category_chart_data(
    type: str = Query("expense", description="income atau expense"),
    period: str = Query("monthly", description="daily, weekly, monthly, yearly"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """Mendapatkan data chart berdasarkan kategori untuk mahasiswa Indonesia"""
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
        
        # Prepare chart data dengan student-friendly colors
        labels = [cat[0] for cat in sorted_categories]
        amounts = [cat[1] for cat in sorted_categories]
        percentages = [(amount/total_amount)*100 if total_amount > 0 else 0 for amount in amounts]
        
        # Enhanced colors untuk mahasiswa Indonesia
        colors = [
            "#EF4444",  # Red - Pengeluaran tinggi
            "#22C55E",  # Green - Pemasukan/tabungan
            "#3B82F6",  # Blue - Kebutuhan
            "#F59E0B",  # Yellow - Hiburan
            "#A855F7",  # Purple - Pendidikan
            "#EC4899",  # Pink - Gaya hidup
            "#14B8A6",  # Teal - Transport
            "#FB923C",  # Orange - Makanan
            "#8B5CF6",  # Violet
            "#06B6D4",  # Cyan
        ]
        
        chart_data = {
            "labels": labels,
            "datasets": [{
                "label": f"{type.title()} by Category",
                "data": amounts,
                "backgroundColor": colors[:len(labels)],
                "borderWidth": 2,
                "borderColor": "#ffffff"
            }]
        }
        
        # Detailed breakdown dengan student insights
        categories_breakdown = []
        for i, (category, amount) in enumerate(sorted_categories):
            # Student-specific insights berdasarkan kategori
            student_insight = ""
            recommendation = ""
            
            if type == "expense":
                if category == "Makanan & Minuman":
                    if percentages[i] > 40:
                        student_insight = "⚠️ Pengeluaran makan terlalu tinggi untuk mahasiswa"
                        recommendation = "Coba masak sendiri atau cari tempat makan lebih hemat"
                    elif percentages[i] > 25:
                        student_insight = "✅ Pengeluaran makan dalam batas wajar"
                        recommendation = "Sudah baik, bisa dioptimalkan sedikit lagi"
                    else:
                        student_insight = "🎉 Pengeluaran makan sangat efisien!"
                        recommendation = "Pertahankan pola hemat ini"
                
                elif category == "Transportasi":
                    if percentages[i] > 20:
                        student_insight = "⚠️ Ongkos transport cukup tinggi"
                        recommendation = "Gunakan transport umum atau berbagi ongkos"
                    else:
                        student_insight = "✅ Ongkos transport sudah efisien"
                        recommendation = "Sudah optimal"
                
                elif category == "Hiburan & Sosial":
                    if percentages[i] > 15:
                        student_insight = "⚠️ Budget hiburan bisa dikurangi"
                        recommendation = "Batasi ke 10-15% dari total pengeluaran"
                    else:
                        student_insight = "✅ Budget hiburan seimbang"
                        recommendation = "Balance yang baik"
                
                elif category == "Pendidikan":
                    student_insight = "📚 Investasi yang sangat baik untuk masa depan"
                    recommendation = "Pertahankan dan tingkatkan jika memungkinkan"
            
            else:  # income
                if category == "Uang Saku/Kiriman Ortu":
                    student_insight = "💝 Support keluarga - sangat berharga"
                    recommendation = "Gunakan dengan bijak dan bersyukur"
                elif category == "Part-time Job":
                    student_insight = "💪 Mandiri dan bertanggung jawab"
                    recommendation = "Pertahankan sambil tetap fokus kuliah"
                elif category == "Beasiswa":
                    student_insight = "🏆 Prestasi yang membanggakan"
                    recommendation = "Manfaatkan dengan maksimal untuk pendidikan"
            
            categories_breakdown.append({
                "category": category,
                "amount": amount,
                "formatted_amount": format_currency(amount),
                "percentage": round(percentages[i], 1),
                "color": colors[i % len(colors)],
                "student_insight": student_insight,
                "recommendation": recommendation,
                "priority": "high" if percentages[i] > 30 else "medium" if percentages[i] > 15 else "low"
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
                        "period": period,
                        "dominant_category": categories_breakdown[0]["category"] if categories_breakdown else "N/A",
                        "dominant_percentage": categories_breakdown[0]["percentage"] if categories_breakdown else 0
                    },
                    "student_analysis": {
                        "health_score": 100 - max(0, sum(cat["percentage"] for cat in categories_breakdown if cat["priority"] == "high") - 50),
                        "top_concern": next((cat for cat in categories_breakdown if cat["priority"] == "high"), None),
                        "balanced_categories": len([cat for cat in categories_breakdown if cat["priority"] == "medium"]),
                        "efficient_categories": len([cat for cat in categories_breakdown if cat["priority"] == "low"]),
                        "recommendations_count": len([cat for cat in categories_breakdown if cat["recommendation"]])
                    }
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil chart kategori: {str(e)}")

# === 9. FINANCIAL RECOMMENDATIONS FOR STUDENTS ===

@router.get("/recommendations")
async def get_student_financial_recommendations(
    current_user: User = Depends(get_current_user)
):
    """Mendapatkan rekomendasi keuangan khusus untuk mahasiswa Indonesia"""
    try:
        # Get comprehensive financial data
        real_total_savings = await StudentFinanceCalculator.calculate_real_total_savings(
            current_user.id, finance_service
        )
        
        monthly_capacity = await StudentFinanceCalculator.calculate_monthly_savings_capacity(
            current_user.id, finance_service
        )
        
        monthly_summary = await finance_service.get_financial_summary(current_user.id, "monthly")
        active_goals = await finance_service.get_user_savings_goals(current_user.id, "active")
        
        # Get user context
        user_profile = current_user.profile
        university = user_profile.university if user_profile else ""
        city = user_profile.city if user_profile else ""
        
        recommendations = []
        
        # 1. Emergency fund recommendation
        if real_total_savings < 500000:
            recommendations.append({
                "id": "emergency_fund",
                "type": "critical",
                "priority": "high",
                "title": "Bangun Dana Darurat",
                "description": "Mahasiswa perlu dana darurat minimal Rp 500.000 untuk situasi mendesak seperti biaya kesehatan, keperluan kuliah mendadak, atau kehilangan sumber dana.",
                "action_plan": [
                    "Sisihkan Rp 25.000 per minggu",
                    "Buka rekening terpisah khusus dana darurat",
                    "Jangan gunakan kecuali benar-benar darurat"
                ],
                "target_amount": 500000,
                "current_amount": real_total_savings,
                "weekly_target": 25000,
                "time_needed_weeks": max(1, (500000 - real_total_savings) / 25000),
                "difficulty": "easy" if monthly_capacity["actual_monthly_savings"] > 100000 else "moderate",
                "impact": "high"
            })
        
        # 2. Savings rate optimization
        current_savings_rate = (monthly_capacity["actual_monthly_savings"] / max(monthly_capacity["monthly_income"], 1)) * 100
        if current_savings_rate < 15:
            recommendations.append({
                "id": "savings_rate",
                "type": "improvement",
                "priority": "medium",
                "title": "Tingkatkan Tingkat Tabungan",
                "description": f"Tingkat tabungan Anda {current_savings_rate:.1f}%, idealnya 15-20% untuk mahasiswa. Ini penting untuk masa depan finansial.",
                "action_plan": [
                    "Buat budget detail bulanan",
                    "Identifikasi pengeluaran yang bisa dikurangi",
                    "Set auto-transfer ke rekening tabungan"
                ],
                "current_rate": current_savings_rate,
                "target_rate": 20,
                "potential_monthly_increase": monthly_capacity["monthly_income"] * 0.2 - monthly_capacity["actual_monthly_savings"],
                "difficulty": "moderate",
                "impact": "high"
            })
        
        # 3. Food expense optimization
        food_expense = monthly_summary.expense_categories.get("Makanan & Minuman", 0)
        food_percentage = (food_expense / max(monthly_capacity["monthly_income"], 1)) * 100
        
        if food_percentage > 35:
            recommendations.append({
                "id": "food_optimization",
                "type": "expense_reduction",
                "priority": "medium",
                "title": "Optimalkan Pengeluaran Makan",
                "description": f"Pengeluaran makan Anda {food_percentage:.1f}% dari pemasukan. Target yang sehat untuk mahasiswa adalah 25-35%.",
                "action_plan": [
                    "Masak sendiri minimal 3x seminggu",
                    "Beli bahan makanan bareng teman kos",
                    "Cari tempat makan dengan harga mahasiswa",
                    "Bawa bekal ke kampus"
                ],
                "current_percentage": food_percentage,
                "target_percentage": 30,
                "potential_monthly_savings": food_expense - (monthly_capacity["monthly_income"] * 0.3),
                "difficulty": "easy",
                "impact": "medium"
            })
        
        # 4. Income diversification
        has_part_time = "Part-time Job" in monthly_summary.income_categories
        has_freelance = "Freelance/Project" in monthly_summary.income_categories
        
        if monthly_capacity["monthly_income"] < 1500000 and not (has_part_time or has_freelance):
            city_specific_jobs = []
            if "jakarta" in city.lower():
                city_specific_jobs = ["Online freelance", "Les private online", "Content creator", "Virtual assistant"]
            elif "bandung" in city.lower():
                city_specific_jobs = ["Design grafis", "Fotografi event", "Tour guide mahasiswa", "Jual produk kreatif"]
            elif "yogya" in city.lower() or "jogja" in city.lower():
                city_specific_jobs = ["Les private", "Tour guide", "Jual kerajinan", "Fotografi wisuda"]
            else:
                city_specific_jobs = ["Online freelance", "Les private", "Jual online", "Content writing"]
            
            recommendations.append({
                "id": "income_diversification",
                "type": "income_increase",
                "priority": "low",
                "title": "Pertimbangkan Penghasilan Tambahan",
                "description": f"Pemasukan bulanan Anda bisa ditingkatkan dengan kerja sampingan yang fleksibel dengan jadwal kuliah.",
                "action_plan": [
                    "Identifikasi skill yang bisa dimonetisasi",
                    "Mulai dengan freelance online",
                    "Cari part-time job yang fleksibel",
                    "Jangan sampai mengganggu kuliah"
                ],
                "current_income": monthly_capacity["monthly_income"],
                "potential_additional": 500000,
                "suitable_jobs": city_specific_jobs,
                "time_commitment": "5-10 jam per minggu",
                "difficulty": "moderate",
                "impact": "high"
            })
        
        # 5. Goal setting recommendation
        if len(active_goals) == 0 and real_total_savings > 1000000:
            recommendations.append({
                "id": "goal_setting",
                "type": "motivation",
                "priority": "low",
                "title": "Buat Target Tabungan Spesifik",
                "description": "Anda sudah punya tabungan yang cukup baik. Saatnya membuat target untuk barang atau keperluan spesifik agar lebih termotivasi.",
                "action_plan": [
                    "Tentukan barang yang ingin dibeli",
                    "Set target waktu yang realistis",
                    "Buat rencana menabung bulanan",
                    "Track progress secara berkala"
                ],
                "suggested_targets": [
                    {"item": "Laptop untuk kuliah", "estimate": "8-15 juta", "priority": "high"},
                    {"item": "Smartphone baru", "estimate": "3-8 juta", "priority": "medium"},
                    {"item": "Dana liburan", "estimate": "2-5 juta", "priority": "low"},
                    {"item": "Kursus online/sertifikasi", "estimate": "500rb-2 juta", "priority": "high"}
                ],
                "difficulty": "easy",
                "impact": "medium"
            })
        
        # 6. City-specific recommendations
        if city:
            city_rec = None
            if "jakarta" in city.lower():
                city_rec = {
                    "id": "jakarta_specific",
                    "type": "location_optimization",
                    "priority": "low",
                    "title": "Optimasi Keuangan di Jakarta",
                    "description": "Jakarta mahal, tapi ada banyak cara hemat khusus untuk mahasiswa.",
                    "action_plan": [
                        "Manfaatkan TransJakarta dan KRL",
                        "Cari kos/kontrakan dekat kampus",
                        "Makan di warteg atau kantin kampus",
                        "Manfaatkan diskon mahasiswa di mall/resto"
                    ],
                    "estimated_monthly_savings": 300000,
                    "specific_tips": [
                        "Kartu Flazz untuk TransJakarta lebih hemat",
                        "Aplikasi transportasi online sering ada promo mahasiswa",
                        "Foodcourt mall biasanya ada menu murah siang hari",
                        "Perpustakaan daerah gratis untuk belajar (hemat listrik kos)"
                    ]
                }
            elif "bandung" in city.lower():
                city_rec = {
                    "id": "bandung_specific",
                    "type": "location_optimization",
                    "priority": "low",
                    "title": "Optimasi Keuangan di Bandung",
                    "description": "Bandung ramah mahasiswa dengan banyak pilihan hemat.",
                    "action_plan": [
                        "Gunakan angkot untuk transport sehari-hari",
                        "Eksplorasi kuliner murah di sekitar kampus",
                        "Manfaatkan cuaca sejuk untuk jalan kaki",
                        "Cari distro lokal untuk pakaian murah"
                    ],
                    "estimated_monthly_savings": 200000,
                    "specific_tips": [
                        "Angkot lebih murah daripada ojol untuk jarak dekat",
                        "Banyak cafe mahasiswa dengan WiFi gratis",
                        "Pasar Baru Trade Center untuk belanja murah",
                        "Factory outlet untuk branded dengan harga mahasiswa"
                    ]
                }
            
            if city_rec:
                recommendations.append(city_rec)
        
        # Sort recommendations by priority and impact
        priority_order = {"high": 3, "medium": 2, "low": 1}
        recommendations.sort(key=lambda x: (
            priority_order.get(x["priority"], 0),
            1 if x.get("impact") == "high" else 0.5 if x.get("impact") == "medium" else 0
        ), reverse=True)
        
        # Calculate potential total improvement
        total_potential_savings = sum(r.get("potential_monthly_savings", 0) for r in recommendations if "potential_monthly_savings" in r)
        total_potential_income = sum(r.get("potential_additional", 0) for r in recommendations if "potential_additional" in r)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Rekomendasi keuangan mahasiswa berhasil dibuat",
                "data": {
                    "recommendations": recommendations,
                    "summary": {
                        "total_recommendations": len(recommendations),
                        "high_priority": len([r for r in recommendations if r["priority"] == "high"]),
                        "medium_priority": len([r for r in recommendations if r["priority"] == "medium"]),
                        "low_priority": len([r for r in recommendations if r["priority"] == "low"]),
                        "potential_monthly_savings": total_potential_savings,
                        "potential_additional_income": total_potential_income,
                        "formatted_potential_savings": format_currency(total_potential_savings),
                        "formatted_potential_income": format_currency(total_potential_income)
                    },
                    "current_financial_state": {
                        "real_total_savings": real_total_savings,
                        "monthly_income": monthly_capacity["monthly_income"],
                        "monthly_expense": monthly_capacity["monthly_expense"],
                        "monthly_net_savings": monthly_capacity["actual_monthly_savings"],
                        "savings_rate": current_savings_rate,
                        "emergency_fund_status": "adequate" if real_total_savings >= 500000 else "insufficient",
                        "overall_health": "good" if current_savings_rate > 15 and real_total_savings > 500000 else "needs_improvement"
                    },
                    "student_context": {
                        "university": university,
                        "city": city,
                        "recommendations_personalized": True,
                        "location_specific_included": bool(city)
                    }
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal membuat rekomendasi: {str(e)}")