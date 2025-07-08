# app/api/v1/endpoints/savings_targets.py
"""Savings target management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
import logging

from app.models.savings_target import (
    SavingsTargetCreate, SavingsTargetUpdate, SavingsTargetResponse,
    SavingsTargetWithProjection, SavingsContribution, SavingsWithdrawal,
    SavingsTargetSummary, SavingsTargetHistory, SavingsTargetAnalytics
)
from app.models.common import (
    PaginatedResponse, PaginationParams, SuccessResponse
)
from app.services.savings_target_service import (
    SavingsTargetService, SavingsTargetServiceError, savings_target_service
)
from app.middleware.auth import (
    get_current_verified_user, require_admin, rate_limit_dependency
)
from app.models.user import UserInDB

logger = logging.getLogger(__name__)

router = APIRouter()


# Savings target CRUD endpoints
@router.get("", response_model=PaginatedResponse[SavingsTargetResponse])
async def list_savings_targets(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    is_achieved: Optional[bool] = Query(None, description="Filter by achievement status"),
    current_user: UserInDB = Depends(get_current_verified_user),
    _: None = Depends(rate_limit_dependency)
):
    """
    List user's savings targets.
    """
    try:
        pagination = PaginationParams(
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        result = await savings_target_service.list_savings_targets(
            user_id=str(current_user.id),
            pagination=pagination,
            is_achieved=is_achieved
        )
        
        return result
        
    except SavingsTargetServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error listing savings targets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list savings targets"
        )


@router.get("/summary", response_model=SavingsTargetSummary)
async def get_savings_summary(
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Get user's savings targets summary.
    """
    try:
        summary = await savings_target_service.get_user_savings_summary(
            user_id=str(current_user.id)
        )
        
        return summary
        
    except Exception as e:
        logger.error(f"Error getting savings summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get savings summary"
        )


@router.get("/{target_id}", response_model=SavingsTargetResponse)
async def get_savings_target_detail(
    target_id: str,
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Get savings target detail by ID.
    """
    try:
        target = await savings_target_service.get_savings_target_by_id(
            target_id=target_id,
            user_id=str(current_user.id)
        )
        
        if not target:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Savings target not found"
            )
        
        return target
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting savings target detail {target_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get savings target detail"
        )


@router.get("/{target_id}/projection", response_model=SavingsTargetWithProjection)
async def get_savings_target_with_projection(
    target_id: str,
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Get savings target with projection calculations.
    """
    try:
        target = await savings_target_service.get_savings_target_with_projection(
            target_id=target_id,
            user_id=str(current_user.id)
        )
        
        if not target:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Savings target not found"
            )
        
        return target
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting savings target projection {target_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get savings target projection"
        )


@router.post("", response_model=SavingsTargetResponse, status_code=status.HTTP_201_CREATED)
async def create_savings_target(
    target_data: SavingsTargetCreate,
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Create new savings target.
    """
    try:
        target = await savings_target_service.create_savings_target(
            user_id=str(current_user.id),
            target_data=target_data
        )
        
        return target
        
    except SavingsTargetServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating savings target: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create savings target"
        )


@router.put("/{target_id}", response_model=SavingsTargetResponse)
async def update_savings_target(
    target_id: str,
    update_data: SavingsTargetUpdate,
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Update savings target.
    """
    try:
        updated_target = await savings_target_service.update_savings_target(
            target_id=target_id,
            user_id=str(current_user.id),
            update_data=update_data
        )
        
        if not updated_target:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Savings target not found"
            )
        
        return updated_target
        
    except SavingsTargetServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating savings target {target_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update savings target"
        )


@router.delete("/{target_id}", response_model=SuccessResponse)
async def delete_savings_target(
    target_id: str,
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Delete savings target.
    """
    try:
        success = await savings_target_service.delete_savings_target(
            target_id=target_id,
            user_id=str(current_user.id)
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Savings target not found"
            )
        
        return SuccessResponse(
            message="Savings target deleted successfully"
        )
        
    except SavingsTargetServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error deleting savings target {target_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete savings target"
        )


# Savings target actions
@router.post("/{target_id}/contribute", response_model=SavingsTargetResponse)
async def add_contribution(
    target_id: str,
    contribution: SavingsContribution,
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Add contribution to savings target.
    """
    try:
        updated_target = await savings_target_service.add_contribution(
            target_id=target_id,
            user_id=str(current_user.id),
            contribution=contribution
        )
        
        if not updated_target:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Savings target not found"
            )
        
        return updated_target
        
    except SavingsTargetServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error adding contribution to target {target_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add contribution"
        )


@router.post("/{target_id}/withdraw", response_model=SavingsTargetResponse)
async def add_withdrawal(
    target_id: str,
    withdrawal: SavingsWithdrawal,
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Add withdrawal from savings target.
    """
    try:
        updated_target = await savings_target_service.add_withdrawal(
            target_id=target_id,
            user_id=str(current_user.id),
            withdrawal=withdrawal
        )
        
        if not updated_target:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Savings target not found"
            )
        
        return updated_target
        
    except SavingsTargetServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error processing withdrawal from target {target_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process withdrawal"
        )


# History and analytics
@router.get("/{target_id}/history", response_model=PaginatedResponse[SavingsTargetHistory])
async def get_savings_target_history(
    target_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Get savings target transaction history.
    """
    try:
        pagination = PaginationParams(
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        history = await savings_target_service.get_savings_target_history(
            target_id=target_id,
            user_id=str(current_user.id),
            pagination=pagination
        )
        
        return history
        
    except SavingsTargetServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting savings target history {target_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get savings target history"
        )


# Admin analytics endpoint
@router.get("/admin/analytics", response_model=SavingsTargetAnalytics)
async def get_savings_analytics(
    current_user: UserInDB = Depends(require_admin())
):
    """
    Get savings target analytics (admin only).
    """
    try:
        analytics = await savings_target_service.get_savings_analytics()
        return analytics
        
    except Exception as e:
        logger.error(f"Error getting savings analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get savings analytics"
        )


# Dashboard endpoint for user overview
@router.get("/dashboard/overview", response_model=dict)
async def get_savings_dashboard_overview(
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Get savings dashboard overview for user.
    """
    try:
        # Get summary
        summary = await savings_target_service.get_user_savings_summary(
            user_id=str(current_user.id)
        )
        
        # Get active targets with projections
        from app.models.common import PaginationParams
        active_targets_result = await savings_target_service.list_savings_targets(
            user_id=str(current_user.id),
            pagination=PaginationParams(page=1, per_page=5, sort_by="target_date", sort_order="asc"),
            is_achieved=False
        )
        
        # Get recently achieved targets
        achieved_targets_result = await savings_target_service.list_savings_targets(
            user_id=str(current_user.id),
            pagination=PaginationParams(page=1, per_page=3, sort_by="updated_at", sort_order="desc"),
            is_achieved=True
        )
        
        # Calculate additional metrics
        progress_data = []
        for target in active_targets_result.items:
            progress_data.append({
                "id": target.id,
                "name": target.target_name,
                "progress_percentage": target.progress_percentage,
                "current_amount": target.current_amount,
                "target_amount": target.target_amount,
                "days_remaining": target.days_remaining,
                "target_date": target.target_date
            })
        
        achievements = []
        for target in achieved_targets_result.items:
            achievements.append({
                "id": target.id,
                "name": target.target_name,
                "amount": target.target_amount,
                "achieved_date": target.updated_at
            })
        
        return {
            "summary": {
                "total_targets": summary.total_targets,
                "active_targets": summary.active_targets,
                "achieved_targets": summary.achieved_targets,
                "total_saved": summary.total_current_amount,
                "total_target_amount": summary.total_target_amount,
                "overall_progress": summary.overall_progress,
                "monthly_savings_needed": summary.monthly_savings_needed,
                "nearest_target_date": summary.nearest_target_date
            },
            "active_targets": progress_data,
            "recent_achievements": achievements,
            "stats": {
                "completion_rate": (summary.achieved_targets / summary.total_targets * 100) if summary.total_targets > 0 else 0,
                "average_target_amount": (summary.total_target_amount / summary.total_targets) if summary.total_targets > 0 else 0,
                "savings_momentum": "good" if summary.overall_progress > 50 else "needs_improvement" if summary.overall_progress > 25 else "low"
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting savings dashboard overview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get savings dashboard overview"
        )