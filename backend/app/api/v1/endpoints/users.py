# app/api/v1/endpoints/users.py
"""User management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from typing import Optional, List
import logging

from app.models.user import (
    UserUpdate, UserResponse, UserProfile, UserStats, PasswordChange
)
from app.models.common import (
    PaginatedResponse, PaginationParams, SuccessResponse
)
from app.services.user_service import UserService, UserServiceError, user_service
from app.middleware.auth import (
    get_current_verified_user, require_admin, get_current_user,
    rate_limit_dependency
)
from app.models.user import UserInDB

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/profile", response_model=UserProfile)
async def get_current_user_profile(
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Get current user's profile with enriched data.
    """
    try:
        profile = await user_service.get_user_profile(str(current_user.id))
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        return profile
        
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user profile"
        )


@router.put("/profile", response_model=UserResponse)
async def update_current_user_profile(
    update_data: UserUpdate,
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Update current user's profile.
    """
    try:
        updated_user = await user_service.update_user_profile(
            str(current_user.id),
            update_data
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return updated_user
        
    except UserServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )


@router.get("/stats", response_model=UserStats)
async def get_current_user_stats(
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Get current user's statistics.
    """
    try:
        stats = await user_service.get_user_stats(str(current_user.id))
        
        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User statistics not found"
            )
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user statistics"
        )


@router.post("/change-password", response_model=SuccessResponse)
async def change_user_password(
    password_data: PasswordChange,
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Change current user's password.
    """
    try:
        success = await user_service.change_user_password(
            str(current_user.id),
            password_data.current_password,
            password_data.new_password
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to change password"
            )
        
        return SuccessResponse(
            message="Password changed successfully"
        )
        
    except UserServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error changing password: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )


# Admin-only endpoints
@router.get("", response_model=PaginatedResponse[UserResponse])
async def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    search: Optional[str] = Query(None, min_length=1, max_length=100, description="Search term"),
    role: Optional[str] = Query(None, regex="^(admin|student)$", description="Filter by role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_verified: Optional[bool] = Query(None, description="Filter by verification status"),
    university_id: Optional[str] = Query(None, description="Filter by university"),
    current_user: UserInDB = Depends(require_admin()),
    _: None = Depends(rate_limit_dependency)
):
    """
    List all users with pagination and filters (admin only).
    """
    try:
        pagination = PaginationParams(
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        result = await user_service.list_users(
            pagination=pagination,
            search=search,
            role=role,
            is_active=is_active,
            is_verified=is_verified,
            university_id=university_id
        )
        
        return result
        
    except UserServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list users"
        )


@router.get("/search", response_model=List[UserResponse])
async def search_users(
    q: str = Query(..., min_length=1, max_length=100, description="Search term"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
    current_user: UserInDB = Depends(require_admin()),
    _: None = Depends(rate_limit_dependency)
):
    """
    Search users by name or email (admin only).
    """
    try:
        users = await user_service.search_users(q, limit)
        return users
        
    except Exception as e:
        logger.error(f"Error searching users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search users"
        )


@router.get("/{user_id}", response_model=UserProfile)
async def get_user_detail(
    user_id: str,
    current_user: UserInDB = Depends(require_admin())
):
    """
    Get user detail by ID (admin only).
    """
    try:
        user_profile = await user_service.get_user_profile(user_id)
        
        if not user_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user_profile
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user detail {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user detail"
        )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    update_data: UserUpdate,
    current_user: UserInDB = Depends(require_admin())
):
    """
    Update user by ID (admin only).
    """
    try:
        updated_user = await user_service.update_user(
            user_id,
            update_data,
            str(current_user.id)
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return updated_user
        
    except UserServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )


@router.delete("/{user_id}", response_model=SuccessResponse)
async def delete_user(
    user_id: str,
    current_user: UserInDB = Depends(require_admin())
):
    """
    Delete (deactivate) user by ID (admin only).
    """
    try:
        # Prevent admin from deleting themselves
        if str(current_user.id) == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        
        success = await user_service.delete_user(user_id, str(current_user.id))
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return SuccessResponse(
            message="User deleted successfully"
        )
        
    except HTTPException:
        raise
    except UserServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )


@router.get("/{user_id}/stats", response_model=UserStats)
async def get_user_stats(
    user_id: str,
    current_user: UserInDB = Depends(require_admin())
):
    """
    Get user statistics by ID (admin only).
    """
    try:
        stats = await user_service.get_user_stats(user_id)
        
        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or no statistics available"
            )
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user stats {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user statistics"
        )


@router.post("/bulk-update", response_model=SuccessResponse)
async def bulk_update_users(
    user_ids: List[str],
    update_data: dict,
    current_user: UserInDB = Depends(require_admin())
):
    """
    Bulk update multiple users (admin only).
    """
    try:
        if not user_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No user IDs provided"
            )
        
        if len(user_ids) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update more than 100 users at once"
            )
        
        # Prevent admin from updating themselves in bulk operations
        if str(current_user.id) in user_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot include your own account in bulk operations"
            )
        
        result = await user_service.bulk_update_users(
            user_ids,
            update_data,
            str(current_user.id)
        )
        
        return SuccessResponse(
            message=f"Successfully updated {result['modified_count']} out of {result['matched_count']} users",
            data=result
        )
        
    except HTTPException:
        raise
    except UserServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in bulk update: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to bulk update users"
        )


@router.post("/{user_id}/send-welcome-email", response_model=SuccessResponse)
async def send_welcome_email(
    user_id: str,
    background_tasks: BackgroundTasks,
    current_user: UserInDB = Depends(require_admin())
):
    """
    Send welcome email to user (admin only).
    """
    try:
        # Get user details
        user = await user_service.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Send email in background
        background_tasks.add_task(
            user_service.send_welcome_email,
            user.email,
            user.full_name
        )
        
        return SuccessResponse(
            message="Welcome email queued for sending"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending welcome email to user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send welcome email"
        )


@router.post("/export", response_model=SuccessResponse)
async def export_users(
    format: str = Query("csv", regex="^(csv|excel)$", description="Export format"),
    search: Optional[str] = Query(None, description="Search filter"),
    role: Optional[str] = Query(None, description="Role filter"),
    is_active: Optional[bool] = Query(None, description="Active status filter"),
    is_verified: Optional[bool] = Query(None, description="Verification status filter"),
    university_id: Optional[str] = Query(None, description="University filter"),
    current_user: UserInDB = Depends(require_admin())
):
    """
    Export users data (admin only).
    """
    try:
        # This is a placeholder for export functionality
        # In a real implementation, you would:
        # 1. Get filtered user data
        # 2. Generate the export file (CSV/Excel)
        # 3. Store it temporarily
        # 4. Return download URL or send via email
        
        return SuccessResponse(
            message="Export functionality not yet implemented",
            data={
                "format": format,
                "filters": {
                    "search": search,
                    "role": role,
                    "is_active": is_active,
                    "is_verified": is_verified,
                    "university_id": university_id
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error exporting users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export users"
        )


# Statistics endpoint for admin dashboard
@router.get("/admin/dashboard-stats", response_model=dict)
async def get_admin_dashboard_stats(
    current_user: UserInDB = Depends(require_admin())
):
    """
    Get user statistics for admin dashboard.
    """
    try:
        from ..config.database import get_database
        
        db = await get_database()
        users_collection = db.users
        
        # Total users
        total_users = await users_collection.count_documents({})
        
        # Active users
        active_users = await users_collection.count_documents({"is_active": True})
        
        # Verified users
        verified_users = await users_collection.count_documents({"is_verified": True})
        
        # Students vs admins
        students = await users_collection.count_documents({"role": "student"})
        admins = await users_collection.count_documents({"role": "admin"})
        
        # Recent registrations (last 30 days)
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_registrations = await users_collection.count_documents({
            "created_at": {"$gte": thirty_days_ago}
        })
        
        # Users by university (top 10)
        university_pipeline = [
            {"$match": {"university_id": {"$ne": None}, "is_active": True}},
            {"$group": {"_id": "$university_id", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10},
            {
                "$lookup": {
                    "from": "universities",
                    "localField": "_id",
                    "foreignField": "_id",
                    "as": "university"
                }
            },
            {"$unwind": {"path": "$university", "preserveNullAndEmptyArrays": True}},
            {
                "$project": {
                    "university_name": {"$ifNull": ["$university.name", "Unknown"]},
                    "count": 1
                }
            }
        ]
        
        users_by_university = await users_collection.aggregate(university_pipeline).to_list(10)
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "verified_users": verified_users,
            "unverified_users": total_users - verified_users,
            "students": students,
            "admins": admins,
            "recent_registrations": recent_registrations,
            "users_by_university": users_by_university,
            "activity_rate": round((active_users / total_users * 100) if total_users > 0 else 0, 2),
            "verification_rate": round((verified_users / total_users * 100) if total_users > 0 else 0, 2)
        }
        
    except Exception as e:
        logger.error(f"Error getting admin dashboard stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get dashboard statistics"
        )