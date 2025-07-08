# app/api/v1/endpoints/transactions.py
"""Transaction management endpoints with analytics."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List
from datetime import date, datetime
import logging

from app.models.transaction import (
    TransactionCreate, TransactionUpdate, TransactionResponse, TransactionWithCategory,
    TransactionSummary, MonthlyTransactionSummary, CategoryTransactionSummary,
    DailyTransactionSummary, TransactionFilters, TransactionBulkCreate, TransactionType
)
from app.models.common import (
    PaginatedResponse, PaginationParams, SuccessResponse
)
from app.services.transaction_service import (
    TransactionService, TransactionServiceError, transaction_service
)
from app.middleware.auth import (
    get_current_verified_user, rate_limit_dependency
)
from app.models.user import UserInDB

logger = logging.getLogger(__name__)

router = APIRouter()


# Transaction CRUD endpoints
@router.get("", response_model=PaginatedResponse[TransactionWithCategory])
async def list_transactions(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    category_id: Optional[str] = Query(None, description="Filter by category ID"),
    transaction_type: Optional[TransactionType] = Query(None, description="Filter by transaction type"),
    min_amount: Optional[float] = Query(None, ge=0, description="Minimum amount"),
    max_amount: Optional[float] = Query(None, ge=0, description="Maximum amount"),
    search: Optional[str] = Query(None, min_length=1, max_length=100, description="Search in description"),
    current_user: UserInDB = Depends(get_current_verified_user),
    _: None = Depends(rate_limit_dependency)
):
    """
    List user transactions with filtering and pagination.
    """
    try:
        pagination = PaginationParams(
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        # Parse date filters
        start_date_parsed = None
        end_date_parsed = None
        
        if start_date:
            start_date_parsed = date.fromisoformat(start_date)
        if end_date:
            end_date_parsed = date.fromisoformat(end_date)
        
        # Create filters
        filters = TransactionFilters(
            start_date=start_date_parsed,
            end_date=end_date_parsed,
            category_id=category_id,
            transaction_type=transaction_type,
            min_amount=min_amount,
            max_amount=max_amount,
            search=search
        )
        
        result = await transaction_service.list_transactions(
            user_id=str(current_user.id),
            pagination=pagination,
            filters=filters
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    except TransactionServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error listing transactions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list transactions"
        )


@router.get("/{transaction_id}", response_model=TransactionWithCategory)
async def get_transaction_detail(
    transaction_id: str,
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Get transaction detail by ID.
    """
    try:
        transaction = await transaction_service.get_transaction_by_id(
            transaction_id=transaction_id,
            user_id=str(current_user.id)
        )
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        return transaction
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting transaction detail {transaction_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get transaction detail"
        )


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Create new transaction.
    """
    try:
        transaction = await transaction_service.create_transaction(
            user_id=str(current_user.id),
            transaction_data=transaction_data
        )
        
        return transaction
        
    except TransactionServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating transaction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create transaction"
        )


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: str,
    update_data: TransactionUpdate,
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Update transaction.
    """
    try:
        updated_transaction = await transaction_service.update_transaction(
            transaction_id=transaction_id,
            user_id=str(current_user.id),
            update_data=update_data
        )
        
        if not updated_transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        return updated_transaction
        
    except TransactionServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating transaction {transaction_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update transaction"
        )


@router.delete("/{transaction_id}", response_model=SuccessResponse)
async def delete_transaction(
    transaction_id: str,
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Delete transaction.
    """
    try:
        success = await transaction_service.delete_transaction(
            transaction_id=transaction_id,
            user_id=str(current_user.id)
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        return SuccessResponse(
            message="Transaction deleted successfully"
        )
        
    except TransactionServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error deleting transaction {transaction_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete transaction"
        )


# Bulk operations
@router.post("/bulk", response_model=SuccessResponse)
async def bulk_create_transactions(
    transactions_data: TransactionBulkCreate,
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Create multiple transactions at once.
    """
    try:
        result = await transaction_service.bulk_create_transactions(
            user_id=str(current_user.id),
            transactions_data=transactions_data
        )
        
        return SuccessResponse(
            message=f"Bulk operation completed: {result['success_count']} created, {result['failure_count']} failed",
            data=result
        )
        
    except TransactionServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in bulk transaction creation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create transactions"
        )


# Analytics endpoints
@router.get("/summary", response_model=TransactionSummary)
async def get_transaction_summary(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Get transaction summary (income/expense totals).
    """
    try:
        # Parse date filters
        start_date_parsed = None
        end_date_parsed = None
        
        if start_date:
            start_date_parsed = date.fromisoformat(start_date)
        if end_date:
            end_date_parsed = date.fromisoformat(end_date)
        
        summary = await transaction_service.get_transaction_summary(
            user_id=str(current_user.id),
            start_date=start_date_parsed,
            end_date=end_date_parsed
        )
        
        return summary
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    except Exception as e:
        logger.error(f"Error getting transaction summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get transaction summary"
        )


@router.get("/monthly-summary", response_model=List[MonthlyTransactionSummary])
async def get_monthly_summary(
    year: Optional[int] = Query(None, ge=2000, le=3000, description="Year for monthly breakdown"),
    limit: int = Query(12, ge=1, le=24, description="Number of months to return"),
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Get monthly transaction breakdown.
    """
    try:
        monthly_summary = await transaction_service.get_monthly_summary(
            user_id=str(current_user.id),
            year=year,
            limit=limit
        )
        
        return monthly_summary
        
    except Exception as e:
        logger.error(f"Error getting monthly summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get monthly summary"
        )


@router.get("/category-summary", response_model=List[CategoryTransactionSummary])
async def get_category_summary(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    transaction_type: Optional[TransactionType] = Query(None, description="Filter by transaction type"),
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Get transaction summary by category.
    """
    try:
        # Parse date filters
        start_date_parsed = None
        end_date_parsed = None
        
        if start_date:
            start_date_parsed = date.fromisoformat(start_date)
        if end_date:
            end_date_parsed = date.fromisoformat(end_date)
        
        category_summary = await transaction_service.get_category_summary(
            user_id=str(current_user.id),
            start_date=start_date_parsed,
            end_date=end_date_parsed,
            transaction_type=transaction_type
        )
        
        return category_summary
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    except Exception as e:
        logger.error(f"Error getting category summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get category summary"
        )


@router.get("/daily-summary", response_model=List[DailyTransactionSummary])
async def get_daily_summary(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Get daily transaction breakdown for date range.
    """
    try:
        # Parse dates
        start_date_parsed = date.fromisoformat(start_date)
        end_date_parsed = date.fromisoformat(end_date)
        
        # Validate date range
        if start_date_parsed > end_date_parsed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start date cannot be after end date"
            )
        
        # Limit date range to prevent excessive data
        date_diff = (end_date_parsed - start_date_parsed).days
        if date_diff > 365:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Date range cannot exceed 365 days"
            )
        
        daily_summary = await transaction_service.get_daily_summary(
            user_id=str(current_user.id),
            start_date=start_date_parsed,
            end_date=end_date_parsed
        )
        
        return daily_summary
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting daily summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get daily summary"
        )


# Dashboard endpoint for overview
@router.get("/dashboard/overview", response_model=dict)
async def get_dashboard_overview(
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Get dashboard overview with key metrics.
    """
    try:
        # Get current month summary
        current_month_summary = await transaction_service.get_transaction_summary(
            user_id=str(current_user.id),
            start_date=date.today().replace(day=1),
            end_date=date.today()
        )
        
        # Get last 6 months for trend
        monthly_trends = await transaction_service.get_monthly_summary(
            user_id=str(current_user.id),
            year=date.today().year,
            limit=6
        )
        
        # Get top categories for current month
        top_categories = await transaction_service.get_category_summary(
            user_id=str(current_user.id),
            start_date=date.today().replace(day=1),
            end_date=date.today(),
            transaction_type=TransactionType.EXPENSE
        )
        
        # Get recent transactions (last 5)
        from app.models.common import PaginationParams
        recent_transactions_result = await transaction_service.list_transactions(
            user_id=str(current_user.id),
            pagination=PaginationParams(page=1, per_page=5, sort_by="created_at", sort_order="desc"),
            filters=None
        )
        
        return {
            "current_month": {
                "total_income": current_month_summary.total_income,
                "total_expense": current_month_summary.total_expense,
                "net_amount": current_month_summary.net_amount,
                "transaction_count": current_month_summary.transaction_count
            },
            "monthly_trends": [
                {
                    "month": trend.month_name,
                    "year": trend.year,
                    "income": trend.total_income,
                    "expense": trend.total_expense,
                    "net": trend.net_amount
                }
                for trend in monthly_trends[-6:]  # Last 6 months
            ],
            "top_expense_categories": [
                {
                    "name": cat.category_name,
                    "amount": cat.total_amount,
                    "percentage": cat.percentage,
                    "color": cat.category_color
                }
                for cat in top_categories[:5]  # Top 5 categories
            ],
            "recent_transactions": [
                {
                    "id": trans.id,
                    "description": trans.description,
                    "amount": trans.amount,
                    "type": trans.type.value,
                    "category": trans.category_name,
                    "date": trans.date,
                    "category_color": trans.category_color
                }
                for trans in recent_transactions_result.items
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard overview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get dashboard overview"
        )


# Export endpoint (placeholder)
@router.post("/export", response_model=SuccessResponse)
async def export_transactions(
    format: str = Query("csv", regex="^(csv|excel)$", description="Export format"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    category_id: Optional[str] = Query(None, description="Filter by category"),
    transaction_type: Optional[TransactionType] = Query(None, description="Filter by type"),
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Export transactions data (placeholder implementation).
    """
    try:
        # This is a placeholder for export functionality
        # In a real implementation, you would:
        # 1. Get filtered transaction data
        # 2. Generate the export file (CSV/Excel)
        # 3. Store it temporarily or send via email
        # 4. Return download URL or success message
        
        return SuccessResponse(
            message="Export functionality not yet implemented",
            data={
                "format": format,
                "filters": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "category_id": category_id,
                    "transaction_type": transaction_type.value if transaction_type else None
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error exporting transactions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export transactions"
        )