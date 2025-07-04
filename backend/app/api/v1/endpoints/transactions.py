"""
Transaction Endpoints
API endpoints untuk transaction management
"""

from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query

from ....core.middleware import standard_rate_limit, auth_rate_limit
from ....crud.transaction import crud_transaction
from ....schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    TransactionDetailResponse,
    TransactionStatsResponse,
    MonthlyTransactionSummary,
    BalanceResponse
)
from ....schemas.base import (
    DataResponse,
    SuccessResponse,
    PaginatedResponse
)
from ....models.transaction import TransactionStatus
from ....models.category import CategoryType
from ..deps import (
    get_pagination_params,
    get_search_params,
    get_current_active_user,
    validate_transaction_id,
    CurrentUser
)

router = APIRouter()


@router.get(
    "/",
    response_model=PaginatedResponse,
    summary="Get user transactions",
    description="Get paginated transactions untuk current user"
)
@standard_rate_limit()
async def get_user_transactions(
    *,
    pagination: tuple = Depends(get_pagination_params),
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    transaction_type: Optional[CategoryType] = Query(None, description="Transaction type filter"),
    category_id: Optional[str] = Query(None, description="Category filter"),
    status: Optional[TransactionStatus] = Query(None, description="Status filter"),
    current_user: CurrentUser = Depends(get_current_active_user)
) -> PaginatedResponse:
    """
    Get user's transactions dengan filtering
    
    - Supports date range filtering
    - Filter by category, type, status
    - Pagination support
    """
    skip, limit = pagination
    
    transactions = await crud_transaction.get_user_transactions(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        transaction_type=transaction_type,
        category_id=category_id,
        status=status,
        skip=skip,
        limit=limit
    )
    
    # Get total count for pagination
    query = {"user_id": current_user.id, "is_deleted": {"$ne": True}}
    if start_date or end_date:
        date_filter = {}
        if start_date:
            date_filter["$gte"] = start_date
        if end_date:
            date_filter["$lte"] = end_date
        query["date"] = date_filter
    if transaction_type:
        query["type"] = transaction_type
    if category_id:
        query["category_id"] = category_id
    if status:
        query["status"] = status
    
    total = await crud_transaction.count(query=query)
    
    page = (skip // limit) + 1
    total_pages = (total + limit - 1) // limit
    
    return PaginatedResponse(
        data=[TransactionResponse.model_validate(t.model_dump()) for t in transactions],
        pagination={
            "page": page,
            "per_page": limit,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
            "next_page": page + 1 if page < total_pages else None,
            "prev_page": page - 1 if page > 1 else None
        }
    )


@router.post(
    "/",
    response_model=DataResponse[TransactionResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create transaction",
    description="Create new transaction"
)
@auth_rate_limit()
async def create_transaction(
    *,
    transaction_in: TransactionCreate,
    current_user: CurrentUser = Depends(get_current_active_user)
) -> DataResponse[TransactionResponse]:
    """
    Create new transaction
    
    - Validates category access and type consistency
    - Increments category usage count
    """
    try:
        transaction = await crud_transaction.create_transaction(
            obj_in=transaction_in,
            user_id=current_user.id
        )
        
        return DataResponse(
            message="Transaksi berhasil dibuat",
            data=TransactionResponse.model_validate(transaction.model_dump())
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/balance",
    response_model=DataResponse[BalanceResponse],
    summary="Get user balance",
    description="Get current balance calculation"
)
@standard_rate_limit()
async def get_user_balance(
    current_user: CurrentUser = Depends(get_current_active_user)
) -> DataResponse[BalanceResponse]:
    """
    Get user's current balance
    
    - Calculates from all completed transactions
    - Returns income, expense, and balance
    """
    balance_data = await crud_transaction.get_user_balance(current_user.id)
    
    # Get last transaction
    recent_transactions = await crud_transaction.get_recent_transactions(
        user_id=current_user.id,
        limit=1
    )
    
    last_transaction = None
    if recent_transactions:
        last_transaction = TransactionResponse.model_validate(recent_transactions[0].model_dump())
    
    # Determine trend (simplified)
    trend = "stable"
    if balance_data["balance"] > 0:
        trend = "increasing"
    elif balance_data["balance"] < 0:
        trend = "decreasing"
    
    response_data = BalanceResponse(
        current_balance=balance_data["balance"],
        total_income=balance_data["income"],
        total_expense=balance_data["expense"],
        last_transaction=last_transaction,
        balance_trend=trend
    )
    
    return DataResponse(
        message="Balance retrieved successfully",
        data=response_data
    )


@router.get(
    "/analytics",
    response_model=DataResponse[dict],
    summary="Get transaction analytics",
    description="Get spending analytics untuk user"
)
@standard_rate_limit()
async def get_transaction_analytics(
    *,
    period_months: int = Query(6, ge=1, le=24, description="Analysis period in months"),
    current_user: CurrentUser = Depends(get_current_active_user)
) -> DataResponse[dict]:
    """
    Get transaction analytics
    
    - Spending patterns analysis
    - Category breakdown
    - Monthly trends
    """
    analytics = await crud_transaction.get_spending_analytics(
        user_id=current_user.id,
        period_months=period_months
    )
    
    return DataResponse(
        message="Analytics retrieved successfully",
        data=analytics
    )


@router.get(
    "/monthly/{year}/{month}",
    response_model=DataResponse[MonthlyTransactionSummary],
    summary="Get monthly summary",
    description="Get transaction summary untuk bulan tertentu"
)
@standard_rate_limit()
async def get_monthly_summary(
    *,
    year: int = Query(..., ge=2020, le=2030, description="Year"),
    month: int = Query(..., ge=1, le=12, description="Month"),
    current_user: CurrentUser = Depends(get_current_active_user)
) -> DataResponse[MonthlyTransactionSummary]:
    """Get monthly transaction summary"""
    summary = await crud_transaction.get_monthly_summary(
        user_id=current_user.id,
        year=year,
        month=month
    )
    
    return DataResponse(
        message="Monthly summary retrieved successfully",
        data=MonthlyTransactionSummary.model_validate(summary)
    )


@router.get(
    "/recent",
    response_model=DataResponse[List[TransactionResponse]],
    summary="Get recent transactions",
    description="Get recent transactions untuk user"
)
@standard_rate_limit()
async def get_recent_transactions(
    *,
    limit: int = Query(10, ge=1, le=50, description="Number of transactions"),
    current_user: CurrentUser = Depends(get_current_active_user)
) -> DataResponse[List[TransactionResponse]]:
    """Get recent transactions"""
    transactions = await crud_transaction.get_recent_transactions(
        user_id=current_user.id,
        limit=limit
    )
    
    return DataResponse(
        message="Recent transactions retrieved successfully",
        data=[TransactionResponse.model_validate(t.model_dump()) for t in transactions]
    )


@router.get(
    "/search",
    response_model=DataResponse[List[TransactionResponse]],
    summary="Search transactions",
    description="Search transactions by description, notes, tags"
)
@standard_rate_limit()
async def search_transactions(
    *,
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(50, ge=1, le=100, description="Number of results"),
    current_user: CurrentUser = Depends(get_current_active_user)
) -> DataResponse[List[TransactionResponse]]:
    """Search transactions"""
    transactions = await crud_transaction.search_transactions(
        user_id=current_user.id,
        search_term=q,
        limit=limit
    )
    
    return DataResponse(
        message="Search results retrieved successfully",
        data=[TransactionResponse.model_validate(t.model_dump()) for t in transactions]
    )


@router.get(
    "/{transaction_id}",
    response_model=DataResponse[TransactionDetailResponse],
    summary="Get transaction by ID",
    description="Get detailed transaction information"
)
@standard_rate_limit()
async def get_transaction_by_id(
    *,
    transaction_id: str = Depends(validate_transaction_id),
    current_user: CurrentUser = Depends(get_current_active_user)
) -> DataResponse[TransactionDetailResponse]:
    """Get transaction by ID dengan detail category info"""
    transaction = await crud_transaction.get(transaction_id)
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaksi tidak ditemukan"
        )
    
    # Check ownership
    if transaction.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Anda tidak memiliki akses ke transaksi ini"
        )
    
    # Get category info
    from ....crud.category import crud_category
    category = await crud_category.get(transaction.category_id)
    
    transaction_data = transaction.model_dump()
    if category:
        transaction_data["category_name"] = category.name
        transaction_data["category_icon"] = category.icon
        transaction_data["category_color"] = category.color
    
    transaction_data["formatted_amount"] = f"Rp {transaction.amount:,.2f}"
    
    return DataResponse(
        message="Transaction retrieved successfully",
        data=TransactionDetailResponse.model_validate(transaction_data)
    )


@router.put(
    "/{transaction_id}",
    response_model=DataResponse[TransactionResponse],
    summary="Update transaction",
    description="Update transaction by ID"
)
@auth_rate_limit()
async def update_transaction(
    *,
    transaction_id: str = Depends(validate_transaction_id),
    transaction_update: TransactionUpdate,
    current_user: CurrentUser = Depends(get_current_active_user)
) -> DataResponse[TransactionResponse]:
    """
    Update transaction
    
    - Users can only update their own transactions
    - Validates category access if changed
    """
    try:
        transaction = await crud_transaction.update_transaction(
            transaction_id=transaction_id,
            obj_in=transaction_update,
            user_id=current_user.id
        )
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaksi tidak ditemukan"
            )
        
        return DataResponse(
            message="Transaksi berhasil diupdate",
            data=TransactionResponse.model_validate(transaction.model_dump())
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{transaction_id}",
    response_model=SuccessResponse,
    summary="Delete transaction",
    description="Delete transaction by ID"
)
@auth_rate_limit()
async def delete_transaction(
    *,
    transaction_id: str = Depends(validate_transaction_id),
    current_user: CurrentUser = Depends(get_current_active_user)
) -> SuccessResponse:
    """
    Delete transaction
    
    - Performs soft delete
    - Users can only delete their own transactions
    """
    try:
        success = await crud_transaction.delete_transaction(
            transaction_id=transaction_id,
            user_id=current_user.id,
            soft=True
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaksi tidak ditemukan"
            )
        
        return SuccessResponse(message="Transaksi berhasil dihapus")
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch(
    "/{transaction_id}/complete",
    response_model=SuccessResponse,
    summary="Complete transaction",
    description="Mark transaction as completed"
)
@auth_rate_limit()
async def complete_transaction(
    *,
    transaction_id: str = Depends(validate_transaction_id),
    current_user: CurrentUser = Depends(get_current_active_user)
) -> SuccessResponse:
    """Mark transaction as completed"""
    success = await crud_transaction.complete_transaction(transaction_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaksi tidak ditemukan"
        )
    
    return SuccessResponse(message="Transaksi berhasil diselesaikan")


@router.patch(
    "/{transaction_id}/cancel",
    response_model=SuccessResponse,
    summary="Cancel transaction",
    description="Cancel transaction"
)
@auth_rate_limit()
async def cancel_transaction(
    *,
    transaction_id: str = Depends(validate_transaction_id),
    current_user: CurrentUser = Depends(get_current_active_user)
) -> SuccessResponse:
    """Cancel transaction"""
    success = await crud_transaction.cancel_transaction(transaction_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaksi tidak ditemukan"
        )
    
    return SuccessResponse(message="Transaksi berhasil dibatalkan")