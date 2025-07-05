# app/routers/recurring_transactions.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
from bson import ObjectId

from ..middleware.auth_middleware import get_current_verified_user
from ..services.recurring_transaction_service import RecurringTransactionService
from ..database import get_database
from ..utils.exceptions import CustomHTTPException

router = APIRouter(prefix="/recurring-transactions", tags=["Recurring Transactions"])

class CreateRecurringTransactionRequest(BaseModel):
    template_name: str = Field(..., min_length=1, max_length=100)
    transaction_data: Dict[str, Any] = Field(...)
    recurrence_pattern: Dict[str, Any] = Field(...)

class UpdateRecurringTransactionRequest(BaseModel):
    template_name: Optional[str] = Field(None, min_length=1, max_length=100)
    transaction_data: Optional[Dict[str, Any]] = None
    recurrence_pattern: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

@router.get("")
async def get_recurring_transactions(
    current_user: Dict[str, Any] = Depends(get_current_verified_user)
):
    """Get all recurring transactions for the current user"""
    try:
        service = RecurringTransactionService()
        recurring_transactions = await service.get_user_recurring_transactions(current_user["id"])
        
        return {
            "status": "success",
            "recurring_transactions": recurring_transactions,
            "total_count": len(recurring_transactions),
            "active_count": len([rt for rt in recurring_transactions if rt["is_active"]]),
            "upcoming_executions": [
                {
                    "id": rt["id"],
                    "template_name": rt["template_name"],
                    "next_execution": rt["next_execution"],
                    "days_until_next": rt["days_until_next"]
                }
                for rt in recurring_transactions
                if rt["is_active"] and rt["days_until_next"] <= 7
            ]
        }
        
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal mendapatkan recurring transactions: {str(e)}",
            error_code="RECURRING_TRANSACTIONS_FETCH_ERROR"
        )

@router.post("")
async def create_recurring_transaction(
    request: CreateRecurringTransactionRequest,
    current_user: Dict[str, Any] = Depends(get_current_verified_user),
    db = Depends(get_database)
):
    """Create a new recurring transaction"""
    try:
        # Validate transaction data
        required_fields = ["type", "amount", "description", "category_id", "payment_method"]
        for field in required_fields:
            if field not in request.transaction_data:
                raise CustomHTTPException(
                    status_code=400,
                    detail=f"Missing required field in transaction_data: {field}",
                    error_code="MISSING_TRANSACTION_FIELD"
                )
        
        # Validate category exists and user has access
        category = await db.categories.find_one({"_id": ObjectId(request.transaction_data["category_id"])})
        if not category:
            raise CustomHTTPException(
                status_code=404,
                detail="Category not found",
                error_code="CATEGORY_NOT_FOUND"
            )
        
        # Check category access
        if category.get("user_id") and str(category["user_id"]) != current_user["id"]:
            raise CustomHTTPException(
                status_code=403,
                detail="Access denied to this category",
                error_code="CATEGORY_ACCESS_DENIED"
            )
        
        # Validate recurrence pattern
        required_pattern_fields = ["frequency"]
        for field in required_pattern_fields:
            if field not in request.recurrence_pattern:
                raise CustomHTTPException(
                    status_code=400,
                    detail=f"Missing required field in recurrence_pattern: {field}",
                    error_code="MISSING_PATTERN_FIELD"
                )
        
        valid_frequencies = ["daily", "weekly", "monthly", "yearly"]
        if request.recurrence_pattern["frequency"] not in valid_frequencies:
            raise CustomHTTPException(
                status_code=400,
                detail=f"Invalid frequency. Must be one of: {valid_frequencies}",
                error_code="INVALID_FREQUENCY"
            )
        
        # Validate transaction type and amount
        if request.transaction_data["type"] not in ["income", "expense"]:
            raise CustomHTTPException(
                status_code=400,
                detail="Transaction type must be 'income' or 'expense'",
                error_code="INVALID_TRANSACTION_TYPE"
            )
        
        if request.transaction_data["amount"] <= 0:
            raise CustomHTTPException(
                status_code=400,
                detail="Amount must be greater than 0",
                error_code="INVALID_AMOUNT"
            )
        
        service = RecurringTransactionService()
        recurring_id = await service.create_recurring_transaction(
            user_id=current_user["id"],
            template_name=request.template_name,
            transaction_data=request.transaction_data,
            recurrence_pattern=request.recurrence_pattern
        )
        
        return {
            "status": "success",
            "message": "Recurring transaction created successfully",
            "recurring_transaction_id": recurring_id,
            "template_name": request.template_name
        }
        
    except CustomHTTPException:
        raise
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal membuat recurring transaction: {str(e)}",
            error_code="CREATE_RECURRING_ERROR"
        )

@router.put("/{recurring_id}")
async def update_recurring_transaction(
    recurring_id: str,
    request: UpdateRecurringTransactionRequest,
    current_user: Dict[str, Any] = Depends(get_current_verified_user),
    db = Depends(get_database)
):
    """Update a recurring transaction"""
    try:
        # Prepare updates dictionary
        updates = {}
        
        if request.template_name is not None:
            updates["template_name"] = request.template_name
        
        if request.transaction_data is not None:
            # Validate category if being updated
            if "category_id" in request.transaction_data:
                category = await db.categories.find_one({"_id": ObjectId(request.transaction_data["category_id"])})
                if not category:
                    raise CustomHTTPException(
                        status_code=404,
                        detail="Category not found",
                        error_code="CATEGORY_NOT_FOUND"
                    )
                
                if category.get("user_id") and str(category["user_id"]) != current_user["id"]:
                    raise CustomHTTPException(
                        status_code=403,
                        detail="Access denied to this category",
                        error_code="CATEGORY_ACCESS_DENIED"
                    )
            
            # Validate amount if being updated
            if "amount" in request.transaction_data and request.transaction_data["amount"] <= 0:
                raise CustomHTTPException(
                    status_code=400,
                    detail="Amount must be greater than 0",
                    error_code="INVALID_AMOUNT"
                )
            
            updates["transaction_data"] = request.transaction_data
        
        if request.recurrence_pattern is not None:
            # Validate frequency if being updated
            if "frequency" in request.recurrence_pattern:
                valid_frequencies = ["daily", "weekly", "monthly", "yearly"]
                if request.recurrence_pattern["frequency"] not in valid_frequencies:
                    raise CustomHTTPException(
                        status_code=400,
                        detail=f"Invalid frequency. Must be one of: {valid_frequencies}",
                        error_code="INVALID_FREQUENCY"
                    )
            
            updates["recurrence_pattern"] = request.recurrence_pattern
        
        if request.is_active is not None:
            updates["is_active"] = request.is_active
        
        if not updates:
            raise CustomHTTPException(
                status_code=400,
                detail="No fields to update",
                error_code="NO_UPDATES"
            )
        
        service = RecurringTransactionService()
        success = await service.update_recurring_transaction(
            recurring_id=recurring_id,
            user_id=current_user["id"],
            updates=updates
        )
        
        if not success:
            raise CustomHTTPException(
                status_code=404,
                detail="Recurring transaction not found",
                error_code="RECURRING_NOT_FOUND"
            )
        
        return {
            "status": "success",
            "message": "Recurring transaction updated successfully",
            "recurring_transaction_id": recurring_id,
            "updated_fields": list(updates.keys())
        }
        
    except CustomHTTPException:
        raise
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal update recurring transaction: {str(e)}",
            error_code="UPDATE_RECURRING_ERROR"
        )

@router.delete("/{recurring_id}")
async def delete_recurring_transaction(
    recurring_id: str,
    current_user: Dict[str, Any] = Depends(get_current_verified_user)
):
    """Delete a recurring transaction"""
    try:
        service = RecurringTransactionService()
        success = await service.delete_recurring_transaction(
            recurring_id=recurring_id,
            user_id=current_user["id"]
        )
        
        if not success:
            raise CustomHTTPException(
                status_code=404,
                detail="Recurring transaction not found",
                error_code="RECURRING_NOT_FOUND"
            )
        
        return {
            "status": "success",
            "message": "Recurring transaction deleted successfully",
            "recurring_transaction_id": recurring_id
        }
        
    except CustomHTTPException:
        raise
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal menghapus recurring transaction: {str(e)}",
            error_code="DELETE_RECURRING_ERROR"
        )

@router.post("/{recurring_id}/execute")
async def execute_recurring_transaction(
    recurring_id: str,
    current_user: Dict[str, Any] = Depends(get_current_verified_user)
):
    """Execute a recurring transaction manually"""
    try:
        service = RecurringTransactionService()
        transaction_id = await service.execute_recurring_transaction(
            recurring_id=recurring_id,
            user_id=current_user["id"]
        )
        
        if not transaction_id:
            raise CustomHTTPException(
                status_code=404,
                detail="Recurring transaction not found or inactive",
                error_code="RECURRING_NOT_FOUND"
            )
        
        return {
            "status": "success",
            "message": "Recurring transaction executed successfully",
            "recurring_transaction_id": recurring_id,
            "created_transaction_id": transaction_id
        }
        
    except CustomHTTPException:
        raise
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal execute recurring transaction: {str(e)}",
            error_code="EXECUTE_RECURRING_ERROR"
        )

@router.get("/upcoming")
async def get_upcoming_executions(
    days_ahead: int = 30,
    current_user: Dict[str, Any] = Depends(get_current_verified_user),
    db = Depends(get_database)
):
    """Get upcoming recurring transaction executions"""
    try:
        end_date = datetime.utcnow() + timedelta(days=days_ahead)
        
        pipeline = [
            {
                "$match": {
                    "user_id": ObjectId(current_user["id"]),
                    "is_active": True,
                    "next_execution": {
                        "$gte": datetime.utcnow(),
                        "$lte": end_date
                    }
                }
            },
            {
                "$lookup": {
                    "from": "categories",
                    "localField": "transaction_data.category_id",
                    "foreignField": "_id",
                    "as": "category"
                }
            },
            {"$unwind": "$category"},
            {"$sort": {"next_execution": 1}}
        ]
        
        upcoming = await db.recurring_transactions.aggregate(pipeline).to_list(None)
        
        formatted_upcoming = []
        for item in upcoming:
            days_until = (item["next_execution"] - datetime.utcnow()).days
            
            formatted_upcoming.append({
                "id": str(item["_id"]),
                "template_name": item["template_name"],
                "transaction_data": {
                    "type": item["transaction_data"]["type"],
                    "amount": item["transaction_data"]["amount"],
                    "description": item["transaction_data"]["description"],
                    "category": {
                        "nama": item["category"]["nama_kategori"],
                        "icon": item["category"]["icon"],
                        "color": item["category"]["color"]
                    }
                },
                "next_execution": item["next_execution"],
                "days_until": max(0, days_until),
                "frequency": item["recurrence_pattern"]["frequency"]
            })
        
        # Group by days
        grouped_by_days = {}
        for item in formatted_upcoming:
            days = item["days_until"]
            if days not in grouped_by_days:
                grouped_by_days[days] = []
            grouped_by_days[days].append(item)
        
        return {
            "status": "success",
            "upcoming_executions": formatted_upcoming,
            "grouped_by_days": grouped_by_days,
            "total_upcoming": len(formatted_upcoming),
            "summary": {
                "today": len(grouped_by_days.get(0, [])),
                "tomorrow": len(grouped_by_days.get(1, [])),
                "this_week": len([item for item in formatted_upcoming if item["days_until"] <= 7]),
                "this_month": len(formatted_upcoming)
            }
        }
        
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal mendapatkan upcoming executions: {str(e)}",
            error_code="UPCOMING_EXECUTIONS_ERROR"
        )