# app/routers/dashboard.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from bson import ObjectId

from ..database import get_database
from ..middleware.auth_middleware import get_current_verified_user
from ..utils.analytics_helpers import calculate_dashboard_metrics, get_quick_stats, get_monthly_comparison
from ..utils.exceptions import CustomHTTPException

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/")
async def get_dashboard_data(
    current_user: Dict[str, Any] = Depends(get_current_verified_user)
):
    """Get main dashboard data with financial summary"""
    try:
        db = await get_database()
        user_id = ObjectId(current_user["id"])
        
        dashboard_data = await calculate_dashboard_metrics(db, user_id)
        
        return {
            "status": "success",
            "data": dashboard_data,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Failed to fetch dashboard data: {str(e)}",
            error_code="DASHBOARD_FETCH_ERROR"
        )

@router.get("/quick-stats")
async def get_dashboard_quick_stats(
    current_user: Dict[str, Any] = Depends(get_current_verified_user)
):
    """Get quick stats for fast menu"""
    try:
        db = await get_database()
        user_id = ObjectId(current_user["id"])
        
        quick_stats = await get_quick_stats(db, user_id)
        return {"status": "success", "data": quick_stats}
        
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Failed to fetch quick stats: {str(e)}",
            error_code="QUICK_STATS_ERROR"
        )

@router.get("/recent-transactions")
async def get_recent_transactions(
    limit: int = 5,
    current_user: Dict[str, Any] = Depends(get_current_verified_user)
):
    """Get recent transactions for dashboard"""
    try:
        db = await get_database()
        user_id = ObjectId(current_user["id"])
        
        recent_transactions = await db.transactions.find(
            {"user_id": user_id}
        ).sort("created_at", -1).limit(limit).to_list(limit)
        
        # Transform ObjectId to string
        for transaction in recent_transactions:
            transaction["_id"] = str(transaction["_id"])
            transaction["user_id"] = str(transaction["user_id"])
            transaction["category_id"] = str(transaction["category_id"])
        
        return {"status": "success", "data": {"recent_transactions": recent_transactions}}
        
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Failed to fetch recent transactions: {str(e)}",
            error_code="RECENT_TRANSACTIONS_ERROR"
        )

@router.get("/monthly-comparison")
async def get_monthly_comparison_data(
    current_user: Dict[str, Any] = Depends(get_current_verified_user)
):
    """Get comparison between current month and previous month"""
    try:
        db = await get_database()
        user_id = ObjectId(current_user["id"])
        
        comparison_data = await get_monthly_comparison(db, user_id)
        return {"status": "success", "data": comparison_data}
        
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Failed to fetch monthly comparison: {str(e)}",
            error_code="MONTHLY_COMPARISON_ERROR"
        )