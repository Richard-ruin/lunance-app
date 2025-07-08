# app/api/v1/endpoints/notifications.py
"""Notification management endpoints."""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
import logging

from app.models.user import UserInDB, UserRole
from app.models.notification import (
    NotificationResponse, NotificationCreate, NotificationSettingsUpdate,
    NotificationSettings, NotificationStats, NotificationType
)
from app.models.common import PaginatedResponse, SuccessResponse
from app.middleware.auth import get_current_verified_user, require_admin
from app.services.notification_service import notification_service, NotificationServiceError

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[NotificationResponse])
async def get_notifications(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    unread_only: bool = Query(False, description="Only return unread notifications"),
    notification_type: Optional[NotificationType] = Query(None, description="Filter by type"),
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Get user notifications with pagination and filters.
    
    Returns paginated list of user's notifications with optional filtering.
    """
    try:
        notifications = await notification_service.get_user_notifications(
            user_id=str(current_user.id),
            page=page,
            per_page=per_page,
            unread_only=unread_only,
            notification_type=notification_type
        )
        
        return notifications
        
    except NotificationServiceError as e:
        logger.error(f"Error getting notifications for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve notifications"
        )


@router.get("/unread-count", response_model=dict)
async def get_unread_count(
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Get count of unread notifications.
    
    Returns the number of unread notifications for the current user.
    """
    try:
        count = await notification_service.get_unread_count(str(current_user.id))
        
        return {
            "unread_count": count,
            "user_id": str(current_user.id)
        }
        
    except Exception as e:
        logger.error(f"Error getting unread count for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get unread count"
        )


@router.get("/stats", response_model=NotificationStats)
async def get_notification_stats(
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Get notification statistics for current user.
    
    Returns comprehensive statistics about user's notifications.
    """
    try:
        stats = await notification_service.get_notification_stats(str(current_user.id))
        return stats
        
    except Exception as e:
        logger.error(f"Error getting notification stats for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get notification statistics"
        )


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: str,
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Get specific notification by ID.
    
    Returns detailed information about a specific notification.
    """
    try:
        notification = await notification_service.get_notification_by_id(
            notification_id=notification_id,
            user_id=str(current_user.id)
        )
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        return notification
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting notification {notification_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve notification"
        )


@router.put("/{notification_id}/read", response_model=SuccessResponse)
async def mark_notification_read(
    notification_id: str,
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Mark notification as read.
    
    Marks a specific notification as read for the current user.
    """
    try:
        success = await notification_service.mark_as_read(
            user_id=str(current_user.id),
            notification_id=notification_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found or already read"
            )
        
        return SuccessResponse(
            message="Notification marked as read successfully",
            data={"notification_id": notification_id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking notification {notification_id} as read: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark notification as read"
        )


@router.put("/mark-all-read", response_model=SuccessResponse)
async def mark_all_notifications_read(
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Mark all notifications as read.
    
    Marks all unread notifications as read for the current user.
    """
    try:
        count = await notification_service.mark_all_as_read(str(current_user.id))
        
        return SuccessResponse(
            message=f"Marked {count} notifications as read",
            data={"marked_count": count}
        )
        
    except Exception as e:
        logger.error(f"Error marking all notifications as read for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark all notifications as read"
        )


@router.delete("/{notification_id}", response_model=SuccessResponse)
async def delete_notification(
    notification_id: str,
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Delete notification.
    
    Permanently deletes a specific notification for the current user.
    """
    try:
        success = await notification_service.delete_notification(
            user_id=str(current_user.id),
            notification_id=notification_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        return SuccessResponse(
            message="Notification deleted successfully",
            data={"notification_id": notification_id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting notification {notification_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete notification"
        )


@router.get("/settings/", response_model=NotificationSettings)
async def get_notification_settings(
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Get user notification settings.
    
    Returns current notification preferences for the user.
    """
    try:
        settings = await notification_service.get_user_settings(str(current_user.id))
        
        if not settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification settings not found"
            )
        
        return settings
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting notification settings for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve notification settings"
        )


@router.put("/settings/", response_model=NotificationSettings)
async def update_notification_settings(
    settings_update: NotificationSettingsUpdate,
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Update user notification settings.
    
    Updates notification preferences for the current user.
    """
    try:
        updated_settings = await notification_service.update_user_settings(
            user_id=str(current_user.id),
            settings_update=settings_update
        )
        
        if not updated_settings:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update notification settings"
            )
        
        return updated_settings
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating notification settings for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update notification settings"
        )


# Admin-only endpoints
@router.post("/admin/broadcast", response_model=SuccessResponse)
async def broadcast_notification(
    notification_data: NotificationCreate,
    user_ids: Optional[List[str]] = None,
    current_user: UserInDB = Depends(require_admin())
):
    """
    Broadcast notification to users (Admin only).
    
    Sends a notification to specified users or all users if no user_ids provided.
    """
    try:
        await notification_service.broadcast_notification(
            title=notification_data.title,
            message=notification_data.message,
            user_ids=user_ids,
            notification_type=notification_data.type,
            priority=notification_data.priority,
            action_url=notification_data.action_url,
            data=notification_data.data
        )
        
        target_count = len(user_ids) if user_ids else "all"
        
        return SuccessResponse(
            message=f"Notification broadcasted to {target_count} users",
            data={
                "title": notification_data.title,
                "target_users": target_count,
                "sent_by": str(current_user.id)
            }
        )
        
    except Exception as e:
        logger.error(f"Error broadcasting notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to broadcast notification"
        )


@router.post("/admin/send", response_model=SuccessResponse)
async def send_admin_notification(
    user_id: str,
    notification_data: NotificationCreate,
    current_user: UserInDB = Depends(require_admin())
):
    """
    Send admin notification to specific user (Admin only).
    
    Sends an admin notification to a specific user.
    """
    try:
        notification = await notification_service.send_admin_notification(
            user_id=user_id,
            title=notification_data.title,
            message=notification_data.message,
            priority=notification_data.priority,
            action_url=notification_data.action_url,
            data=notification_data.data
        )
        
        return SuccessResponse(
            message="Admin notification sent successfully",
            data={
                "target_user_id": user_id,
                "title": notification_data.title,
                "sent_by": str(current_user.id)
            }
        )
        
    except Exception as e:
        logger.error(f"Error sending admin notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send admin notification"
        )


@router.get("/admin/stats", response_model=dict)
async def get_admin_notification_stats(
    current_user: UserInDB = Depends(require_admin())
):
    """
    Get global notification statistics (Admin only).
    
    Returns system-wide notification statistics for admin monitoring.
    """
    try:
        from ...config.database import get_database
        
        db = await get_database()
        notifications_collection = db.notifications
        
        # Get global stats
        total_notifications = await notifications_collection.count_documents({})
        total_read = await notifications_collection.count_documents({"is_read": True})
        total_unread = await notifications_collection.count_documents({"is_read": False})
        
        # Stats by type
        type_pipeline = [
            {"$group": {"_id": "$type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        type_stats = await notifications_collection.aggregate(type_pipeline).to_list(None)
        
        # Stats by priority
        priority_pipeline = [
            {"$group": {"_id": "$priority", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        priority_stats = await notifications_collection.aggregate(priority_pipeline).to_list(None)
        
        # Recent activity
        recent_notifications = await notifications_collection.find(
            {}, {"title": 1, "type": 1, "user_id": 1, "created_at": 1}
        ).sort("created_at", -1).limit(10).to_list(10)
        
        return {
            "global_stats": {
                "total_notifications": total_notifications,
                "total_read": total_read,
                "total_unread": total_unread,
                "read_rate": round((total_read / total_notifications * 100) if total_notifications > 0 else 0, 2)
            },
            "by_type": {item["_id"]: item["count"] for item in type_stats},
            "by_priority": {item["_id"]: item["count"] for item in priority_stats},
            "recent_activity": [
                {
                    "id": str(notif["_id"]),
                    "title": notif["title"],
                    "type": notif["type"],
                    "user_id": notif["user_id"],
                    "created_at": notif["created_at"].isoformat()
                }
                for notif in recent_notifications
            ],
            "calculated_at": logger.info("Admin notification stats retrieved")
        }
        
    except Exception as e:
        logger.error(f"Error getting admin notification stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get notification statistics"
        )


@router.post("/admin/cleanup", response_model=SuccessResponse)
async def cleanup_expired_notifications(
    current_user: UserInDB = Depends(require_admin())
):
    """
    Clean up expired notifications (Admin only).
    
    Removes expired notifications from the system.
    """
    try:
        await notification_service.cleanup_expired_notifications()
        
        return SuccessResponse(
            message="Expired notifications cleanup completed",
            data={"cleaned_by": str(current_user.id)}
        )
        
    except Exception as e:
        logger.error(f"Error cleaning up expired notifications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cleanup expired notifications"
        )