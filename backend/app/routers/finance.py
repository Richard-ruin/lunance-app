# app/routers/finance.py (Enhanced Version)
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..services.auth_dependency import get_current_user
from ..services.finance_service import FinanceService
from ..models.user import User
from ..utils.timezone_utils import IndonesiaDatetime
from ..schemas.finance_schemas import (
    CreateTransactionRequest,
    CreateSavingsGoalRequest,
    UpdateSavingsGoalRequest,
    AddSavingsRequest,
    ConfirmFinancialDataRequest,
    TransactionResponse,
    SavingsGoalResponse,
    FinancialSummaryResponse,
    PendingFinancialDataResponse,
    TransactionListResponse,
    SavingsGoalListResponse,
    FinanceApiResponse
)

router = APIRouter(prefix="/finance", tags=["Finance"])
finance_service = FinanceService()

def format_currency(amount: float) -> str:
    """Format jumlah uang ke format Rupiah"""
    return f"Rp {amount:,.0f}".replace(',', '.')

def format_transaction_response(transaction, user_preferences=None) -> Dict[str, Any]:
    """Format transaction untuk response"""
    return {
        "id": transaction.id,
        "user_id": transaction.user_id,
        "type": transaction.type,
        "amount": transaction.amount,
        "category": transaction.category,
        "description": transaction.description,
        "date": transaction.date,
        "status": transaction.status,
        "source": transaction.source,
        "tags": transaction.tags,
        "notes": transaction.notes,
        "created_at": transaction.created_at,
        "updated_at": transaction.updated_at,
        "confirmed_at": transaction.confirmed_at,
        
        # Formatted fields
        "formatted_amount": format_currency(transaction.amount),
        "formatted_date": IndonesiaDatetime.format_date_only(transaction.date),
        "relative_date": IndonesiaDatetime.format_relative(transaction.date)
    }

def format_savings_goal_response(goal, user_preferences=None) -> Dict[str, Any]:
    """Format savings goal untuk response"""
    return {
        "id": goal.id,
        "user_id": goal.user_id,
        "item_name": goal.item_name,
        "target_amount": goal.target_amount,
        "current_amount": goal.current_amount,
        "description": goal.description,
        "target_date": goal.target_date,
        "status": goal.status,
        "monthly_target": goal.monthly_target,
        "source": goal.source,
        "tags": goal.tags,
        "notes": goal.notes,
        "created_at": goal.created_at,
        "updated_at": goal.updated_at,
        "completed_at": goal.completed_at,
        
        # Calculated fields
        "progress_percentage": goal.progress_percentage,
        "remaining_amount": goal.remaining_amount,
        
        # Formatted fields
        "formatted_target_amount": format_currency(goal.target_amount),
        "formatted_current_amount": format_currency(goal.current_amount),
        "formatted_remaining_amount": format_currency(goal.remaining_amount),
        "formatted_target_date": IndonesiaDatetime.format_date_only(goal.target_date) if goal.target_date else None
    }

# === 🆕 NEW: Dashboard & Sync Endpoints ===

@router.get("/dashboard", response_model=FinanceApiResponse)
async def get_financial_dashboard(
    current_user: User = Depends(get_current_user)
):
    """Mengambil dashboard keuangan lengkap dengan integrasi user financial settings"""
    try:
        dashboard_data = await finance_service.get_financial_dashboard(current_user.id)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Dashboard keuangan berhasil diambil",
                "data": dashboard_data
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil dashboard: {str(e)}")

@router.post("/sync", response_model=FinanceApiResponse)
async def sync_financial_settings(
    current_user: User = Depends(get_current_user)
):
    """Sinkronisasi financial settings user dengan data aktual"""
    try:
        sync_result = await finance_service.sync_user_financial_settings(current_user.id)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Sinkronisasi berhasil dilakukan",
                "data": sync_result
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal sinkronisasi: {str(e)}")

@router.get("/monthly-progress", response_model=FinanceApiResponse)
async def get_monthly_progress(
    current_user: User = Depends(get_current_user)
):
    """Mengambil progress tabungan bulanan"""
    try:
        monthly_progress = await finance_service._calculate_monthly_savings_progress(current_user.id)
        
        # Format currency for display
        monthly_progress.update({
            "formatted_monthly_target": format_currency(monthly_progress["monthly_target"]),
            "formatted_income_this_month": format_currency(monthly_progress["income_this_month"]),
            "formatted_expense_this_month": format_currency(monthly_progress["expense_this_month"]),
            "formatted_net_savings_this_month": format_currency(monthly_progress["net_savings_this_month"]),
            "formatted_remaining_to_target": format_currency(monthly_progress["remaining_to_target"])
        })
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Progress bulanan berhasil diambil",
                "data": monthly_progress
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil progress bulanan: {str(e)}")

@router.post("/create-monthly-goal", response_model=FinanceApiResponse)
async def create_monthly_savings_goal(
    current_user: User = Depends(get_current_user)
):
    """Membuat target tabungan bulanan otomatis"""
    try:
        goal = await finance_service.create_monthly_savings_goal(current_user.id)
        
        if not goal:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": "Tidak dapat membuat target bulanan. Pastikan monthly_savings_target sudah diset.",
                    "data": None
                }
            )
        
        return JSONResponse(
            status_code=201,
            content={
                "success": True,
                "message": "Target tabungan bulanan berhasil dibuat",
                "data": {
                    "savings_goal": format_savings_goal_response(goal)
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal membuat target bulanan: {str(e)}")

# === Transaction Endpoints ===

@router.post("/transactions", response_model=FinanceApiResponse)
async def create_transaction(
    request: CreateTransactionRequest,
    current_user: User = Depends(get_current_user)
):
    """Membuat transaksi baru secara manual"""
    try:
        transaction = await finance_service.create_transaction(
            current_user.id,
            request.dict()
        )
        
        # Auto-confirm manual transactions
        await finance_service.confirm_transaction(transaction.id, current_user.id)
        
        # Get updated transaction
        updated_transaction = await finance_service.get_user_transactions(
            current_user.id,
            {"_id": transaction.id}
        )
        
        return JSONResponse(
            status_code=201,
            content={
                "success": True,
                "message": "Transaksi berhasil dibuat",
                "data": {
                    "transaction": format_transaction_response(updated_transaction[0] if updated_transaction else transaction)
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal membuat transaksi: {str(e)}")

@router.get("/transactions", response_model=FinanceApiResponse)
async def get_transactions(
    type: Optional[str] = Query(None, description="income atau expense"),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user)
):
    """Mengambil daftar transaksi user"""
    try:
        filters = {}
        if type:
            filters["type"] = type
        if category:
            filters["category"] = category
        if status:
            filters["status"] = status
        if start_date:
            filters["start_date"] = start_date
        if end_date:
            filters["end_date"] = end_date
        
        transactions = await finance_service.get_user_transactions(
            current_user.id,
            filters,
            limit,
            offset
        )
        
        transaction_list = [format_transaction_response(t) for t in transactions]
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Daftar transaksi berhasil diambil",
                "data": {
                    "transactions": transaction_list,
                    "total": len(transaction_list),
                    "limit": limit,
                    "offset": offset,
                    "timezone": "WIB"
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil transaksi: {str(e)}")

@router.get("/transactions/{transaction_id}", response_model=FinanceApiResponse)
async def get_transaction_detail(
    transaction_id: str,
    current_user: User = Depends(get_current_user)
):
    """Mengambil detail transaksi"""
    try:
        transactions = await finance_service.get_user_transactions(
            current_user.id,
            {"_id": transaction_id}
        )
        
        if not transactions:
            raise HTTPException(status_code=404, detail="Transaksi tidak ditemukan")
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Detail transaksi berhasil diambil",
                "data": {
                    "transaction": format_transaction_response(transactions[0])
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil detail transaksi: {str(e)}")

# === Savings Goal Endpoints ===

@router.post("/savings-goals", response_model=FinanceApiResponse)
async def create_savings_goal(
    request: CreateSavingsGoalRequest,
    current_user: User = Depends(get_current_user)
):
    """Membuat target tabungan baru"""
    try:
        goal = await finance_service.create_savings_goal(
            current_user.id,
            request.dict()
        )
        
        return JSONResponse(
            status_code=201,
            content={
                "success": True,
                "message": "Target tabungan berhasil dibuat",
                "data": {
                    "savings_goal": format_savings_goal_response(goal)
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal membuat target tabungan: {str(e)}")

@router.get("/savings-goals", response_model=FinanceApiResponse)
async def get_savings_goals(
    status: Optional[str] = Query(None, description="active, completed, paused, cancelled"),
    current_user: User = Depends(get_current_user)
):
    """Mengambil daftar target tabungan user"""
    try:
        goals = await finance_service.get_user_savings_goals(current_user.id, status)
        
        goal_list = [format_savings_goal_response(g) for g in goals]
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Daftar target tabungan berhasil diambil",
                "data": {
                    "savings_goals": goal_list,
                    "total": len(goal_list),
                    "timezone": "WIB"
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil target tabungan: {str(e)}")

@router.get("/savings-goals/{goal_id}", response_model=FinanceApiResponse)
async def get_savings_goal_detail(
    goal_id: str,
    current_user: User = Depends(get_current_user)
):
    """Mengambil detail target tabungan"""
    try:
        goals = await finance_service.get_user_savings_goals(current_user.id)
        goal = next((g for g in goals if g.id == goal_id), None)
        
        if not goal:
            raise HTTPException(status_code=404, detail="Target tabungan tidak ditemukan")
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Detail target tabungan berhasil diambil",
                "data": {
                    "savings_goal": format_savings_goal_response(goal)
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil detail target tabungan: {str(e)}")

@router.put("/savings-goals/{goal_id}", response_model=FinanceApiResponse)
async def update_savings_goal(
    goal_id: str,
    request: UpdateSavingsGoalRequest,
    current_user: User = Depends(get_current_user)
):
    """Update target tabungan"""
    try:
        # Get current goal
        goals = await finance_service.get_user_savings_goals(current_user.id)
        goal = next((g for g in goals if g.id == goal_id), None)
        
        if not goal:
            raise HTTPException(status_code=404, detail="Target tabungan tidak ditemukan")
        
        # Update goal fields
        update_data = {}
        if request.item_name is not None:
            update_data["item_name"] = request.item_name
        if request.target_amount is not None:
            update_data["target_amount"] = request.target_amount
        if request.description is not None:
            update_data["description"] = request.description
        if request.target_date is not None:
            update_data["target_date"] = request.target_date
        if request.monthly_target is not None:
            update_data["monthly_target"] = request.monthly_target
        if request.status is not None:
            update_data["status"] = request.status
        if request.tags is not None:
            update_data["tags"] = request.tags
        if request.notes is not None:
            update_data["notes"] = request.notes
        
        if update_data:
            from bson import ObjectId
            result = finance_service.db.savings_goals.update_one(
                {"_id": ObjectId(goal_id), "user_id": current_user.id},
                {"$set": {**update_data, "updated_at": IndonesiaDatetime.now_for_db()}}
            )
            
            if result.modified_count == 0:
                raise HTTPException(status_code=400, detail="Tidak ada perubahan yang dilakukan")
            
            # Sync financial settings
            await finance_service.sync_user_financial_settings(current_user.id)
        
        # Get updated goal
        updated_goals = await finance_service.get_user_savings_goals(current_user.id)
        updated_goal = next((g for g in updated_goals if g.id == goal_id), None)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Target tabungan berhasil diperbarui",
                "data": {
                    "savings_goal": format_savings_goal_response(updated_goal) if updated_goal else None
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memperbarui target tabungan: {str(e)}")

@router.post("/savings-goals/{goal_id}/add-savings", response_model=FinanceApiResponse)
async def add_savings_to_goal(
    goal_id: str,
    request: AddSavingsRequest,
    current_user: User = Depends(get_current_user)
):
    """Menambah tabungan ke target"""
    try:
        success = await finance_service.add_savings_to_goal(
            goal_id,
            current_user.id,
            request.amount
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Target tabungan tidak ditemukan")
        
        # Get updated goal
        goals = await finance_service.get_user_savings_goals(current_user.id)
        updated_goal = next((g for g in goals if g.id == goal_id), None)
        
        # Create income transaction for this savings addition
        if request.description:
            transaction_data = {
                "type": "income",
                "amount": request.amount,
                "category": "tabungan",
                "description": f"Menabung untuk {updated_goal.item_name if updated_goal else 'target'}: {request.description}"
            }
            
            transaction = await finance_service.create_transaction(
                current_user.id,
                transaction_data,
                {"source": "savings_addition"}
            )
            await finance_service.confirm_transaction(transaction.id, current_user.id)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": f"Berhasil menambah tabungan {format_currency(request.amount)}",
                "data": {
                    "savings_goal": format_savings_goal_response(updated_goal) if updated_goal else None,
                    "added_amount": request.amount,
                    "formatted_added_amount": format_currency(request.amount)
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal menambah tabungan: {str(e)}")

@router.delete("/savings-goals/{goal_id}", response_model=FinanceApiResponse)
async def delete_savings_goal(
    goal_id: str,
    current_user: User = Depends(get_current_user)
):
    """Hapus target tabungan"""
    try:
        from bson import ObjectId
        
        result = finance_service.db.savings_goals.delete_one({
            "_id": ObjectId(goal_id),
            "user_id": current_user.id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Target tabungan tidak ditemukan")
        
        # Sync financial settings
        await finance_service.sync_user_financial_settings(current_user.id)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Target tabungan berhasil dihapus",
                "data": {"deleted_goal_id": goal_id}
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal menghapus target tabungan: {str(e)}")

# === Pending Data Endpoints ===

@router.get("/pending", response_model=FinanceApiResponse)
async def get_pending_financial_data(
    current_user: User = Depends(get_current_user)
):
    """Mengambil data keuangan yang menunggu konfirmasi"""
    try:
        pending_data = await finance_service.get_user_pending_data(current_user.id)
        
        pending_list = []
        for pending in pending_data:
            time_remaining = pending.expires_at - IndonesiaDatetime.now_for_db()
            pending_list.append({
                "id": pending.id,
                "data_type": pending.data_type,
                "parsed_data": pending.parsed_data,
                "original_message": pending.original_message,
                "luna_response": pending.luna_response,
                "expires_at": pending.expires_at,
                "created_at": pending.created_at,
                "time_remaining": f"{max(0, time_remaining.total_seconds() / 3600):.1f} jam",
                "formatted_expires_at": IndonesiaDatetime.format(pending.expires_at)
            })
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": f"Ditemukan {len(pending_list)} data yang menunggu konfirmasi",
                "data": {
                    "pending_data": pending_list,
                    "total": len(pending_list)
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil data pending: {str(e)}")

@router.post("/pending/{pending_id}/confirm", response_model=FinanceApiResponse)
async def confirm_pending_financial_data(
    pending_id: str,
    request: ConfirmFinancialDataRequest,
    current_user: User = Depends(get_current_user)
):
    """Konfirmasi atau batalkan data keuangan yang pending"""
    try:
        result = await finance_service.confirm_pending_data(
            pending_id,
            current_user.id,
            request.confirmed,
            request.modifications
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        response_data = {
            "success": True,
            "message": result["message"],
            "data": {
                "confirmed": request.confirmed,
                "pending_id": pending_id
            }
        }
        
        # Add created object to response if confirmed
        if request.confirmed and "data" in result:
            created_object = result["data"]
            if hasattr(created_object, 'type'):  # Transaction
                response_data["data"]["created_transaction"] = format_transaction_response(created_object)
            else:  # Savings Goal
                response_data["data"]["created_savings_goal"] = format_savings_goal_response(created_object)
        
        return JSONResponse(status_code=200, content=response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memproses konfirmasi: {str(e)}")

# === Financial Summary Endpoints ===

@router.get("/summary", response_model=FinanceApiResponse)
async def get_financial_summary(
    period: str = Query("monthly", description="daily, weekly, monthly, yearly"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """Mengambil ringkasan keuangan"""
    try:
        summary = await finance_service.get_financial_summary(
            current_user.id,
            period,
            start_date,
            end_date
        )
        
        # Format summary response
        summary_data = {
            "user_id": summary.user_id,
            "period": summary.period,
            
            # Income summary
            "total_income": summary.total_income,
            "income_count": summary.income_count,
            "income_categories": summary.income_categories,
            "formatted_total_income": format_currency(summary.total_income),
            
            # Expense summary
            "total_expense": summary.total_expense,
            "expense_count": summary.expense_count,
            "expense_categories": summary.expense_categories,
            "formatted_total_expense": format_currency(summary.total_expense),
            
            # Balance
            "net_balance": summary.net_balance,
            "formatted_net_balance": format_currency(summary.net_balance),
            
            # Savings summary
            "active_goals_count": summary.active_goals_count,
            "total_savings_target": summary.total_savings_target,
            "total_savings_current": summary.total_savings_current,
            "formatted_total_savings_target": format_currency(summary.total_savings_target),
            "formatted_total_savings_current": format_currency(summary.total_savings_current),
            
            # Period info
            "start_date": summary.start_date,
            "end_date": summary.end_date,
            "formatted_period": f"{IndonesiaDatetime.format_date_only(summary.start_date)} - {IndonesiaDatetime.format_date_only(summary.end_date)}",
            "generated_at": summary.generated_at
        }
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Ringkasan keuangan berhasil diambil",
                "data": summary_data
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil ringkasan keuangan: {str(e)}")

# === Categories Endpoints ===

@router.get("/categories", response_model=FinanceApiResponse)
async def get_categories(
    current_user: User = Depends(get_current_user)
):
    """Mengambil daftar kategori default"""
    try:
        # Get categories from user financial settings or use default
        user_categories = {
            "income_categories": current_user.financial_settings.income_categories if current_user.financial_settings else [
                "Uang Saku/Kiriman Ortu",
                "Part-time Job", 
                "Freelance",
                "Beasiswa",
                "Lainnya"
            ],
            "expense_categories": current_user.financial_settings.expense_categories if current_user.financial_settings else [
                "Makanan & Minuman",
                "Transportasi",
                "Buku & Alat Tulis", 
                "Hiburan",
                "Kesehatan",
                "Kos/Tempat Tinggal",
                "Internet & Pulsa",
                "Lainnya"
            ]
        }
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Daftar kategori berhasil diambil",
                "data": user_categories
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil kategori: {str(e)}")

@router.get("/stats", response_model=FinanceApiResponse)
async def get_financial_stats(
    current_user: User = Depends(get_current_user)
):
    """Mengambil statistik keuangan singkat"""
    try:
        # Get current month summary
        monthly_summary = await finance_service.get_financial_summary(
            current_user.id,
            "monthly"
        )
        
        # Get all active savings goals
        active_goals = await finance_service.get_user_savings_goals(
            current_user.id,
            "active"
        )
        
        # Get recent transactions
        recent_transactions = await finance_service.get_user_transactions(
            current_user.id,
            {"status": "confirmed"},
            5,  # last 5 transactions
            0
        )
        
        # Calculate additional stats
        total_savings_progress = sum(g.current_amount for g in active_goals)
        total_savings_target = sum(g.target_amount for g in active_goals)
        overall_savings_progress = (total_savings_progress / total_savings_target * 100) if total_savings_target > 0 else 0
        
        stats = {
            "monthly_income": monthly_summary.total_income,
            "monthly_expense": monthly_summary.total_expense,
            "monthly_balance": monthly_summary.net_balance,
            "active_savings_goals": len(active_goals),
            "total_savings_progress": total_savings_progress,
            "total_savings_target": total_savings_target,
            "overall_savings_progress_percentage": min(overall_savings_progress, 100),
            "recent_transactions_count": len(recent_transactions),
            
            # Formatted versions
            "formatted_monthly_income": format_currency(monthly_summary.total_income),
            "formatted_monthly_expense": format_currency(monthly_summary.total_expense),
            "formatted_monthly_balance": format_currency(monthly_summary.net_balance),
            "formatted_total_savings_progress": format_currency(total_savings_progress),
            "formatted_total_savings_target": format_currency(total_savings_target),
            
            # User financial settings comparison
            "user_monthly_target": current_user.financial_settings.monthly_savings_target if current_user.financial_settings else 0,
            "user_current_savings": current_user.financial_settings.current_savings if current_user.financial_settings else 0,
            "formatted_user_monthly_target": format_currency(current_user.financial_settings.monthly_savings_target if current_user.financial_settings else 0),
            "formatted_user_current_savings": format_currency(current_user.financial_settings.current_savings if current_user.financial_settings else 0),
        }
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Statistik keuangan berhasil diambil",
                "data": stats
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil statistik: {str(e)}")

# === 🆕 NEW: Financial Analysis Endpoints ===

@router.get("/insights", response_model=FinanceApiResponse)
async def get_financial_insights(
    current_user: User = Depends(get_current_user)
):
    """Mendapatkan insights keuangan berbasis AI"""
    try:
        # Get monthly data for analysis
        monthly_summary = await finance_service.get_financial_summary(current_user.id, "monthly")
        monthly_progress = await finance_service._calculate_monthly_savings_progress(current_user.id)
        
        # Generate insights
        insights = []
        
        # Income vs Expense Analysis
        if monthly_summary.total_income > 0:
            expense_ratio = (monthly_summary.total_expense / monthly_summary.total_income) * 100
            if expense_ratio > 80:
                insights.append({
                    "type": "warning",
                    "category": "spending",
                    "title": "Pengeluaran Tinggi",
                    "message": f"Pengeluaran kamu {expense_ratio:.1f}% dari pemasukan. Coba kurangi pengeluaran non-esensial.",
                    "priority": "high"
                })
            elif expense_ratio < 50:
                insights.append({
                    "type": "success", 
                    "category": "saving",
                    "title": "Hebat! Pengeluaran Terkendali",
                    "message": f"Pengeluaran hanya {expense_ratio:.1f}% dari pemasukan. Kamu bisa menabung lebih banyak!",
                    "priority": "medium"
                })
        
        # Monthly Savings Target Analysis
        if monthly_progress["monthly_target"] > 0:
            progress_pct = monthly_progress["progress_percentage"]
            if progress_pct >= 100:
                insights.append({
                    "type": "success",
                    "category": "target",
                    "title": "Target Bulanan Tercapai!",
                    "message": f"Kamu sudah mencapai {progress_pct:.1f}% dari target tabungan bulanan. Luar biasa!",
                    "priority": "high"
                })
            elif progress_pct < 25:
                days_left = 30 - IndonesiaDatetime.now().day
                if days_left > 0:
                    daily_needed = monthly_progress["remaining_to_target"] / days_left
                    insights.append({
                        "type": "info",
                        "category": "target",
                        "title": "Kejar Target Bulanan",
                        "message": f"Butuh menabung {format_currency(daily_needed)} per hari untuk mencapai target bulan ini.",
                        "priority": "medium"
                    })
        
        # Top Expense Category
        if monthly_summary.expense_categories:
            top_category = max(monthly_summary.expense_categories.items(), key=lambda x: x[1])
            category_percentage = (top_category[1] / monthly_summary.total_expense) * 100
            if category_percentage > 40:
                insights.append({
                    "type": "info",
                    "category": "spending",
                    "title": f"Pengeluaran Terbesar: {top_category[0].title()}",
                    "message": f"{category_percentage:.1f}% pengeluaran untuk {top_category[0]}. Cek apakah masih wajar.",
                    "priority": "medium"
                })
        
        # Savings Goals Progress
        active_goals = await finance_service.get_user_savings_goals(current_user.id, "active")
        near_completion = [g for g in active_goals if g.progress_percentage >= 80]
        if near_completion:
            insights.append({
                "type": "success",
                "category": "goals",
                "title": "Target Hampir Tercapai!",
                "message": f"{len(near_completion)} target tabungan hampir selesai. Sedikit lagi!",
                "priority": "medium"
            })
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Insights keuangan berhasil diambil",
                "data": {
                    "insights": insights,
                    "analysis_period": "monthly",
                    "generated_at": IndonesiaDatetime.now_for_db()
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil insights: {str(e)}")

# === Chat Integration Test Endpoint ===

@router.post("/parse-message", response_model=FinanceApiResponse)
async def parse_financial_message(
    message: dict,
    current_user: User = Depends(get_current_user)
):
    """Test endpoint untuk parsing pesan keuangan (development only)"""
    try:
        user_message = message.get("message", "")
        if not user_message:
            raise HTTPException(status_code=400, detail="Message required")
        
        result = finance_service.parse_financial_message(user_message)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Parsing berhasil",
                "data": {
                    "original_message": user_message,
                    "parse_result": result,
                    "examples": [
                        "Dapat gaji 5 juta",
                        "Bayar listrik 200 ribu",
                        "Belanja groceries 150rb", 
                        "Mau nabung buat beli laptop 10 juta",
                        "Target beli motor 20 juta"
                    ]
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing: {str(e)}")