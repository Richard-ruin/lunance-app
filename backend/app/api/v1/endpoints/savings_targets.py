return DataResponse(
        message="Target retrieved successfully",
        data=SavingsTargetDetailResponse.model_validate(target_data)
    )


@router.put(
    "/{target_id}",
    response_model=DataResponse[SavingsTargetResponse],
    summary="Update savings target",
    description="Update savings target by ID"
)
@auth_rate_limit()
async def update_savings_target(
    *,
    target_id: str = Depends(validate_target_id),
    target_update: SavingsTargetUpdate,
    current_user: CurrentUser = Depends(get_current_active_user)
) -> DataResponse[SavingsTargetResponse]:
    """
    Update savings target
    
    - Users can only update their own targets
    - Validates target name uniqueness if changed
    """
    try:
        target = await crud_savings_target.update_target(
            target_id=target_id,
            obj_in=target_update,
            user_id=current_user.id
        )
        
        if not target:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target tabungan tidak ditemukan"
            )
        
        return DataResponse(
            message="Target berhasil diupdate",
            data=SavingsTargetResponse.model_validate(target.model_dump())
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{target_id}",
    response_model=SuccessResponse,
    summary="Delete savings target",
    description="Delete savings target by ID"
)
@auth_rate_limit()
async def delete_savings_target(
    *,
    target_id: str = Depends(validate_target_id),
    current_user: CurrentUser = Depends(get_current_active_user)
) -> SuccessResponse:
    """
    Delete savings target
    
    - Performs soft delete
    - Users can only delete their own targets
    """
    try:
        success = await crud_savings_target.delete_target(
            target_id=target_id,
            user_id=current_user.id,
            soft=True
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target tabungan tidak ditemukan"
            )
        
        return SuccessResponse(message="Target berhasil dihapus")
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/{target_id}/contribute",
    response_model=DataResponse[SavingsTargetDetailResponse],
    summary="Add contribution",
    description="Add contribution to savings target"
)
@auth_rate_limit()
async def add_contribution(
    *,
    target_id: str = Depends(validate_target_id),
    contribution: SavingsContribution,
    current_user: CurrentUser = Depends(get_current_active_user)
) -> DataResponse[SavingsTargetDetailResponse]:
    """
    Add contribution to savings target
    
    - Updates current amount and contribution count
    - Automatically marks as achieved if target reached
    """
    try:
        target = await crud_savings_target.add_contribution(
            target_id=target_id,
            amount=contribution.amount,
            user_id=current_user.id,
            description=contribution.description
        )
        
        if not target:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target tabungan tidak ditemukan"
            )
        
        # Add progress calculations
        target_data = target.model_dump()
        target_data["progress_percentage"] = target.get_progress_percentage()
        target_data["remaining_amount"] = target.get_remaining_amount()
        target_data["days_remaining"] = target.get_days_remaining()
        target_data["daily_savings_needed"] = target.get_daily_savings_needed()
        target_data["is_overdue"] = target.is_overdue()
        target_data["is_near_deadline"] = target.is_near_deadline()
        target_data["status_color"] = target.get_status_color()
        target_data["motivation_message"] = target.get_motivation_message()
        
        return DataResponse(
            message="Kontribusi berhasil ditambahkan",
            data=SavingsTargetDetailResponse.model_validate(target_data)
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/{target_id}/withdraw",
    response_model=DataResponse[SavingsTargetDetailResponse],
    summary="Withdraw from target",
    description="Withdraw amount from savings target"
)
@auth_rate_limit()
async def withdraw_from_target(
    *,
    target_id: str = Depends(validate_target_id),
    withdrawal: SavingsWithdrawal,
    current_user: CurrentUser = Depends(get_current_active_user)
) -> DataResponse[SavingsTargetDetailResponse]:
    """
    Withdraw from savings target
    
    - Reduces current amount
    - Updates achievement status if needed
    """
    try:
        target = await crud_savings_target.subtract_contribution(
            target_id=target_id,
            amount=withdrawal.amount,
            user_id=current_user.id,
            description=withdrawal.reason
        )
        
        if not target:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target tabungan tidak ditemukan"
            )
        
        # Add progress calculations
        target_data = target.model_dump()
        target_data["progress_percentage"] = target.get_progress_percentage()
        target_data["remaining_amount"] = target.get_remaining_amount()
        target_data["days_remaining"] = target.get_days_remaining()
        target_data["daily_savings_needed"] = target.get_daily_savings_needed()
        target_data["is_overdue"] = target.is_overdue()
        target_data["is_near_deadline"] = target.is_near_deadline()
        target_data["status_color"] = target.get_status_color()
        target_data["motivation_message"] = target.get_motivation_message()
        
        return DataResponse(
            message="Penarikan berhasil dilakukan",
            data=SavingsTargetDetailResponse.model_validate(target_data)
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch(
    "/{target_id}/complete",
    response_model=SuccessResponse,
    summary="Complete target",
    description="Mark target as achieved"
)
@auth_rate_limit()
async def complete_target(
    *,
    target_id: str = Depends(validate_target_id),
    current_user: CurrentUser = Depends(get_current_active_user)
) -> SuccessResponse:
    """Mark target as achieved manually"""
    success = await crud_savings_target.complete_target(target_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target tabungan tidak ditemukan"
        )
    
    return SuccessResponse(message="Target berhasil diselesaikan")


@router.patch(
    "/{target_id}/cancel",
    response_model=SuccessResponse,
    summary="Cancel target",
    description="Cancel savings target"
)
@auth_rate_limit()
async def cancel_target(
    *,
    target_id: str = Depends(validate_target_id),
    current_user: CurrentUser = Depends(get_current_active_user)
) -> SuccessResponse:
    """Cancel savings target"""
    success = await crud_savings_target.cancel_target(target_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target tabungan tidak ditemukan"
        )
    
    return SuccessResponse(message="Target berhasil dibatalkan")


@router.patch(
    "/{target_id}/reactivate",
    response_model=SuccessResponse,
    summary="Reactivate target",
    description="Reactivate cancelled target"
)
@auth_rate_limit()
async def reactivate_target(
    *,
    target_id: str = Depends(validate_target_id),
    current_user: CurrentUser = Depends(get_current_active_user)
) -> SuccessResponse:
    """Reactivate cancelled target"""
    success = await crud_savings_target.reactivate_target(target_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target tabungan tidak ditemukan"
        )
    
    return SuccessResponse(message="Target berhasil diaktifkan kembali")


@router.patch(
    "/{target_id}/extend",
    response_model=DataResponse[SavingsTargetResponse],
    summary="Extend target deadline",
    description="Extend target deadline"
)
@auth_rate_limit()
async def extend_target_deadline(
    *,
    target_id: str = Depends(validate_target_id),
    extend_data: SavingsTargetExtend,
    current_user: CurrentUser = Depends(get_current_active_user)
) -> DataResponse[SavingsTargetResponse]:
    """
    Extend target deadline
    
    - New date must be after current deadline
    - Reactivates expired targets
    """
    try:
        target = await crud_savings_target.extend_deadline(
            target_id=target_id,
            new_date=extend_data.new_date,
            user_id=current_user.id
        )
        
        if not target:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target tabungan tidak ditemukan"
            )
        
        return DataResponse(
            message="Deadline target berhasil diperpanjang",
            data=SavingsTargetResponse.model_validate(target.model_dump())
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/analytics/overview",
    response_model=DataResponse[dict],
    summary="Get savings analytics",
    description="Get comprehensive savings analytics"
)
@standard_rate_limit()
async def get_savings_analytics(
    *,
    period_months: int = Query(12, ge=1, le=24, description="Analysis period in months"),
    current_user: CurrentUser = Depends(get_current_active_user)
) -> DataResponse[dict]:
    """
    Get savings analytics
    
    - Savings patterns and trends
    - Category breakdown
    - Achievement analysis
    """
    analytics = await crud_savings_target.get_savings_analytics(
        user_id=current_user.id,
        period_months=period_months
    )
    
    return DataRespon"""
Savings Target Endpoints
API endpoints untuk savings target management
"""

from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query

from ....core.middleware import standard_rate_limit, auth_rate_limit
from ....crud.savings_target import crud_savings_target
from ....schemas.savings_target import (
    SavingsTargetCreate,
    SavingsTargetUpdate,
    SavingsTargetResponse,
    SavingsTargetDetailResponse,
    SavingsTargetUserSummary,
    SavingsContribution,
    SavingsWithdrawal,
    SavingsTargetExtend
)
from ....schemas.base import (
    DataResponse,
    SuccessResponse,
    PaginatedResponse
)
from ....models.savings_target import TargetStatus, TargetPriority
from ..deps import (
    get_pagination_params,
    get_current_active_user,
    validate_target_id,
    CurrentUser
)

router = APIRouter()


@router.get(
    "/",
    response_model=PaginatedResponse,
    summary="Get user savings targets",
    description="Get paginated savings targets untuk current user"
)
@standard_rate_limit()
async def get_user_savings_targets(
    *,
    pagination: tuple = Depends(get_pagination_params),
    status: Optional[TargetStatus] = Query(None, description="Filter by status"),
    is_achieved: Optional[bool] = Query(None, description="Filter by achievement"),
    current_user: CurrentUser = Depends(get_current_active_user)
) -> PaginatedResponse:
    """
    Get user's savings targets dengan filtering
    
    - Filter by status (active/achieved/expired/cancelled)
    - Filter by achievement status
    - Sorted by target date
    """
    skip, limit = pagination
    
    targets = await crud_savings_target.get_user_targets(
        user_id=current_user.id,
        status=status,
        is_achieved=is_achieved,
        skip=skip,
        limit=limit
    )
    
    # Get total count
    query = {"user_id": current_user.id, "is_deleted": {"$ne": True}}
    if status:
        query["status"] = status
    if is_achieved is not None:
        query["is_achieved"] = is_achieved
    
    total = await crud_savings_target.count(query=query)
    
    page = (skip // limit) + 1
    total_pages = (total + limit - 1) // limit
    
    # Add progress info to each target
    target_responses = []
    for target in targets:
        target_data = target.model_dump()
        target_data["progress_percentage"] = target.get_progress_percentage()
        target_data["remaining_amount"] = target.get_remaining_amount()
        target_data["days_remaining"] = target.get_days_remaining()
        target_data["daily_savings_needed"] = target.get_daily_savings_needed()
        target_data["is_overdue"] = target.is_overdue()
        target_data["is_near_deadline"] = target.is_near_deadline()
        target_data["status_color"] = target.get_status_color()
        target_data["motivation_message"] = target.get_motivation_message()
        
        target_responses.append(SavingsTargetDetailResponse.model_validate(target_data))
    
    return PaginatedResponse(
        data=target_responses,
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
    response_model=DataResponse[SavingsTargetResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create savings target",
    description="Create new savings target"
)
@auth_rate_limit()
async def create_savings_target(
    *,
    target_in: SavingsTargetCreate,
    current_user: CurrentUser = Depends(get_current_active_user)
) -> DataResponse[SavingsTargetResponse]:
    """
    Create new savings target
    
    - Target name must be unique for user
    - Validates target date not in past
    """
    try:
        target = await crud_savings_target.create_savings_target(
            obj_in=target_in,
            user_id=current_user.id
        )
        
        return DataResponse(
            message="Target tabungan berhasil dibuat",
            data=SavingsTargetResponse.model_validate(target.model_dump())
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/summary",
    response_model=DataResponse[SavingsTargetUserSummary],
    summary="Get user savings summary",
    description="Get comprehensive savings summary untuk user"
)
@standard_rate_limit()
async def get_user_savings_summary(
    current_user: CurrentUser = Depends(get_current_active_user)
) -> DataResponse[SavingsTargetUserSummary]:
    """
    Get user's savings summary
    
    - Total targets, achieved, active
    - Achievement rate and progress
    - Upcoming deadlines
    """
    summary = await crud_savings_target.get_user_summary(current_user.id)
    
    # Get upcoming deadlines
    upcoming_targets = await crud_savings_target.get_near_deadline_targets(
        user_id=current_user.id,
        days_threshold=30
    )
    
    summary["upcoming_deadlines"] = [
        SavingsTargetResponse.model_validate(t.model_dump()) for t in upcoming_targets
    ]
    
    return DataResponse(
        message="Savings summary retrieved successfully",
        data=SavingsTargetUserSummary.model_validate(summary)
    )


@router.get(
    "/active",
    response_model=DataResponse[List[SavingsTargetDetailResponse]],
    summary="Get active targets",
    description="Get all active savings targets"
)
@standard_rate_limit()
async def get_active_targets(
    current_user: CurrentUser = Depends(get_current_active_user)
) -> DataResponse[List[SavingsTargetDetailResponse]]:
    """Get all active savings targets dengan progress info"""
    targets = await crud_savings_target.get_active_targets(current_user.id)
    
    target_responses = []
    for target in targets:
        target_data = target.model_dump()
        target_data["progress_percentage"] = target.get_progress_percentage()
        target_data["remaining_amount"] = target.get_remaining_amount()
        target_data["days_remaining"] = target.get_days_remaining()
        target_data["daily_savings_needed"] = target.get_daily_savings_needed()
        target_data["is_overdue"] = target.is_overdue()
        target_data["is_near_deadline"] = target.is_near_deadline()
        target_data["status_color"] = target.get_status_color()
        target_data["motivation_message"] = target.get_motivation_message()
        
        target_responses.append(SavingsTargetDetailResponse.model_validate(target_data))
    
    return DataResponse(
        message="Active targets retrieved successfully",
        data=target_responses
    )


@router.get(
    "/achieved",
    response_model=DataResponse[List[SavingsTargetResponse]],
    summary="Get achieved targets",
    description="Get all achieved savings targets"
)
@standard_rate_limit()
async def get_achieved_targets(
    current_user: CurrentUser = Depends(get_current_active_user)
) -> DataResponse[List[SavingsTargetResponse]]:
    """Get all achieved savings targets"""
    targets = await crud_savings_target.get_achieved_targets(current_user.id)
    
    return DataResponse(
        message="Achieved targets retrieved successfully",
        data=[SavingsTargetResponse.model_validate(t.model_dump()) for t in targets]
    )


@router.get(
    "/overdue",
    response_model=DataResponse[List[SavingsTargetDetailResponse]],
    summary="Get overdue targets",
    description="Get overdue savings targets"
)
@standard_rate_limit()
async def get_overdue_targets(
    current_user: CurrentUser = Depends(get_current_active_user)
) -> DataResponse[List[SavingsTargetDetailResponse]]:
    """Get overdue savings targets"""
    targets = await crud_savings_target.get_overdue_targets(current_user.id)
    
    target_responses = []
    for target in targets:
        target_data = target.model_dump()
        target_data["progress_percentage"] = target.get_progress_percentage()
        target_data["remaining_amount"] = target.get_remaining_amount()
        target_data["days_remaining"] = target.get_days_remaining()
        target_data["daily_savings_needed"] = target.get_daily_savings_needed()
        target_data["is_overdue"] = target.is_overdue()
        target_data["is_near_deadline"] = target.is_near_deadline()
        target_data["status_color"] = target.get_status_color()
        target_data["motivation_message"] = target.get_motivation_message()
        
        target_responses.append(SavingsTargetDetailResponse.model_validate(target_data))
    
    return DataResponse(
        message="Overdue targets retrieved successfully",
        data=target_responses
    )


@router.get(
    "/{target_id}",
    response_model=DataResponse[SavingsTargetDetailResponse],
    summary="Get target by ID",
    description="Get detailed savings target information"
)
@standard_rate_limit()
async def get_target_by_id(
    *,
    target_id: str = Depends(validate_target_id),
    current_user: CurrentUser = Depends(get_current_active_user)
) -> DataResponse[SavingsTargetDetailResponse]:
    """Get savings target by ID dengan progress detail"""
    target = await crud_savings_target.get(target_id)
    
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target tabungan tidak ditemukan"
        )
    
    # Check ownership
    if target.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Anda tidak memiliki akses ke target ini"
        )
    
    # Add progress calculations
    target_data = target.model_dump()
    target_data["progress_percentage"] = target.get_progress_percentage()
    target_data["remaining_amount"] = target.get_remaining_amount()
    target_data["days_remaining"] = target.get_days_remaining()
    target_data["daily_savings_needed"] = target.get_daily_savings_needed()
    target_data["is_overdue"] = target.is_overdue()
    target_data["is_near_deadline"] = target.is_near_deadline()
    target_data["status_color"] = target.get_status_color()
    target_data["motivation_message"] = target.get_motivation_message()
    
    return DataResponse(
        message="Target retrieved successfully