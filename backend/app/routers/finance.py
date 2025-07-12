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
        categories = {
            "income_categories": [
                "gaji", "freelance", "bisnis", "investasi", "bonus", "lainnya"
            ],
            "expense_categories": [
                "makanan", "transportasi", "belanja", "hiburan", "kesehatan",
                "pendidikan", "tagihan", "rumah tangga", "lainnya"
            ]
        }
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Daftar kategori berhasil diambil",
                "data": categories
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
        
        stats = {
            "monthly_income": monthly_summary.total_income,
            "monthly_expense": monthly_summary.total_expense,
            "monthly_balance": monthly_summary.net_balance,
            "active_savings_goals": len(active_goals),
            "total_savings_progress": sum(g.current_amount for g in active_goals),
            "recent_transactions_count": len(recent_transactions),
            
            # Formatted versions
            "formatted_monthly_income": format_currency(monthly_summary.total_income),
            "formatted_monthly_expense": format_currency(monthly_summary.total_expense),
            "formatted_monthly_balance": format_currency(monthly_summary.net_balance),
            "formatted_total_savings_progress": format_currency(sum(g.current_amount for g in active_goals)),
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