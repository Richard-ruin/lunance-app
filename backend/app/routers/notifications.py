# app/routers/notifications.py
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Dict, Any, List, Optional
from datetime import datetime
from bson import ObjectId

from ..middleware.auth_middleware import get_current_verified_user
from ..services.notification_service import NotificationService
from ..database import get_database
from ..utils.exceptions import CustomHTTPException

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("")
async def get_notifications(
    limit: int = Query(20, ge=1, le=100, description="Number of notifications to fetch"),
    offset: int = Query(0, ge=0, description="Number of notifications to skip"),
    unread_only: bool = Query(False, description="Only fetch unread notifications"),
    type_filter: Optional[str] = Query(None, description="Filter by notification type"),
    current_user: Dict[str, Any] = Depends(get_current_verified_user)
):
    """Get user notifications with pagination and filtering"""
    try:
        notification_service = NotificationService()
        
        # Build query filters
        query_filters = {}
        if type_filter:
            query_filters["type"] = type_filter
        
        result = await notification_service.get_user_notifications(
            user_id=current_user["id"],
            limit=limit,
            offset=offset,
            unread_only=unread_only,
            filters=query_filters
        )
        
        return {
            "status": "success",
            "notifications": result["notifications"],
            "pagination": result["pagination"]
        }
        
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal mendapatkan notifications: {str(e)}",
            error_code="NOTIFICATIONS_FETCH_ERROR"
        )

@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: Dict[str, Any] = Depends(get_current_verified_user)
):
    """Mark a specific notification as read"""
    try:
        notification_service = NotificationService()
        
        success = await notification_service.mark_notification_read(
            notification_id=notification_id,
            user_id=current_user["id"]
        )
        
        if not success:
            raise CustomHTTPException(
                status_code=404,
                detail="Notification not found",
                error_code="NOTIFICATION_NOT_FOUND"
            )
        
        return {
            "status": "success",
            "message": "Notification marked as read",
            "notification_id": notification_id
        }
        
    except CustomHTTPException:
        raise
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal menandai notification sebagai read: {str(e)}",
            error_code="MARK_READ_ERROR"
        )

@router.put("/read-all")
async def mark_all_notifications_read(
    current_user: Dict[str, Any] = Depends(get_current_verified_user)
):
    """Mark all notifications as read for the current user"""
    try:
        notification_service = NotificationService()
        
        marked_count = await notification_service.mark_all_notifications_read(
            user_id=current_user["id"]
        )
        
        return {
            "status": "success",
            "message": f"Marked {marked_count} notifications as read",
            "marked_count": marked_count
        }
        
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal menandai semua notification sebagai read: {str(e)}",
            error_code="MARK_ALL_READ_ERROR"
        )

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: Dict[str, Any] = Depends(get_current_verified_user)
):
    """Delete a specific notification"""
    try:
        notification_service = NotificationService()
        
        success = await notification_service.delete_notification(
            notification_id=notification_id,
            user_id=current_user["id"]
        )
        
        if not success:
            raise CustomHTTPException(
                status_code=404,
                detail="Notification not found",
                error_code="NOTIFICATION_NOT_FOUND"
            )
        
        return {
            "status": "success",
            "message": "Notification deleted successfully",
            "notification_id": notification_id
        }
        
    except CustomHTTPException:
        raise
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal menghapus notification: {str(e)}",
            error_code="DELETE_NOTIFICATION_ERROR"
        )

@router.get("/settings")
async def get_notification_settings(
    current_user: Dict[str, Any] = Depends(get_current_verified_user),
    db = Depends(get_database)
):
    """Get user notification preferences"""
    try:
        # Get user's notification settings
        user = await db.users.find_one({"_id": ObjectId(current_user["id"])})
        
        default_settings = {
            "budget_alerts": {
                "enabled": True,
                "channels": ["in_app", "email"],
                "threshold_80": True,
                "threshold_100": True
            },
            "goal_reminders": {
                "enabled": True,
                "channels": ["in_app"],
                "weekly_progress": True,
                "deadline_alerts": True
            },
            "weekly_summary": {
                "enabled": True,
                "channels": ["in_app"],
                "day_of_week": 1  # Monday
            },
            "spending_insights": {
                "enabled": True,
                "channels": ["in_app"],
                "unusual_patterns": True,
                "seasonal_reminders": True
            },
            "push_notifications": {
                "enabled": False,
                "fcm_token": None
            }
        }
        
        # Merge with user's saved settings
        user_settings = user.get("notification_settings", {})
        for category, settings in default_settings.items():
            if category in user_settings:
                settings.update(user_settings[category])
        
        return {
            "status": "success",
            "notification_settings": default_settings
        }
        
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal mendapatkan notification settings: {str(e)}",
            error_code="SETTINGS_FETCH_ERROR"
        )

@router.put("/settings")
async def update_notification_settings(
    settings: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_verified_user),
    db = Depends(get_database)
):
    """Update user notification preferences"""
    try:
        # Validate settings structure
        valid_categories = ["budget_alerts", "goal_reminders", "weekly_summary", "spending_insights", "push_notifications"]
        valid_channels = ["in_app", "email", "push"]
        
        for category, config in settings.items():
            if category not in valid_categories:
                raise CustomHTTPException(
                    status_code=400,
                    detail=f"Invalid notification category: {category}",
                    error_code="INVALID_CATEGORY"
                )
            
            if "channels" in config:
                for channel in config["channels"]:
                    if channel not in valid_channels:
                        raise CustomHTTPException(
                            status_code=400,
                            detail=f"Invalid notification channel: {channel}",
                            error_code="INVALID_CHANNEL"
                        )
        
        # Update user's notification settings
        result = await db.users.update_one(
            {"_id": ObjectId(current_user["id"])},
            {"$set": {"notification_settings": settings}}
        )
        
        if result.modified_count == 0:
            raise CustomHTTPException(
                status_code=404,
                detail="User not found",
                error_code="USER_NOT_FOUND"
            )
        
        return {
            "status": "success",
            "message": "Notification settings updated successfully",
            "updated_settings": settings
        }
        
    except CustomHTTPException:
        raise
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal update notification settings: {str(e)}",
            error_code="SETTINGS_UPDATE_ERROR"
        )

@router.post("/test")
async def send_test_notification(
    notification_type: str = Query("test", description="Type of test notification"),
    current_user: Dict[str, Any] = Depends(get_current_verified_user)
):
    """Send a test notification to the user"""
    try:
        notification_service = NotificationService()
        
        test_messages = {
            "test": {
                "title": "Test Notification",
                "message": "Ini adalah test notification dari Lunance. Sistem notifikasi berfungsi dengan baik! 🎉"
            },
            "budget_alert": {
                "title": "Budget Alert Test",
                "message": "Test: Budget Makanan sudah 85% terpakai. Sisa budget: Rp150.000"
            },
            "goal_reminder": {
                "title": "Goal Reminder Test", 
                "message": "Test: Progress Liburan Bali tertinggal dari target. Nabung Rp500.000 per bulan untuk catch up!"
            },
            "weekly_summary": {
                "title": "Weekly Summary Test",
                "message": "Test: Ringkasan minggu ini - Pemasukan: Rp2.500.000, Pengeluaran: Rp1.800.000, Savings: Rp700.000"
            }
        }
        
        if notification_type not in test_messages:
            notification_type = "test"
        
        test_data = test_messages[notification_type]
        
        notification_id = await notification_service.create_notification(
            user_id=current_user["id"],
            title=test_data["title"],
            message=test_data["message"],
            notification_type=f"test_{notification_type}",
            priority="low",
            channels=["in_app"],
            data={"is_test": True, "sent_at": datetime.utcnow().isoformat()}
        )
        
        return {
            "status": "success",
            "message": "Test notification sent successfully",
            "notification_id": notification_id,
            "notification_type": notification_type
        }
        
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal mengirim test notification: {str(e)}",
            error_code="TEST_NOTIFICATION_ERROR"
        )

@router.get("/summary")
async def get_notifications_summary(
    current_user: Dict[str, Any] = Depends(get_current_verified_user),
    db = Depends(get_database)
):
    """Get notifications summary and statistics"""
    try:
        user_id = ObjectId(current_user["id"])
        
        # Get notification counts by type and status
        pipeline = [
            {"$match": {"user_id": user_id}},
            {
                "$group": {
                    "_id": {
                        "type": "$type",
                        "is_read": "$is_read"
                    },
                    "count": {"$sum": 1}
                }
            }
        ]
        
        counts = await db.notifications.aggregate(pipeline).to_list(None)
        
        # Process counts into summary
        summary = {
            "total_notifications": 0,
            "unread_count": 0,
            "by_type": {},
            "recent_activity": []
        }
        
        for count in counts:
            notification_type = count["_id"]["type"]
            is_read = count["_id"]["is_read"]
            count_value = count["count"]
            
            summary["total_notifications"] += count_value
            
            if not is_read:
                summary["unread_count"] += count_value
            
            if notification_type not in summary["by_type"]:
                summary["by_type"][notification_type] = {"read": 0, "unread": 0, "total": 0}
            
            summary["by_type"][notification_type]["total"] += count_value
            if is_read:
                summary["by_type"][notification_type]["read"] += count_value
            else:
                summary["by_type"][notification_type]["unread"] += count_value
        
        # Get recent notifications (last 5)
        recent_notifications = await db.notifications.find(
            {"user_id": user_id}
        ).sort("created_at", -1).limit(5).to_list(5)
        
        summary["recent_activity"] = [
            {
                "id": str(notif["_id"]),
                "title": notif["title"],
                "type": notif["type"],
                "is_read": notif["is_read"],
                "created_at": notif["created_at"]
            }
            for notif in recent_notifications
        ]
        
        return {
            "status": "success",
            "summary": summary
        }
        
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal mendapatkan notifications summary: {str(e)}",
            error_code="SUMMARY_FETCH_ERROR"
        )