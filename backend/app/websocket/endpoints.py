# app/websocket/endpoints.py
"""WebSocket endpoints for real-time features."""

import json
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, HTTPException
from datetime import datetime

from .websocket_manager import connection_manager
from ..models.user import UserRole
from ..utils.jwt import verify_token, TokenExpiredError, InvalidTokenError
from ..services.chatbot_service import ChatbotService
from ..services.notification_service import NotificationService
from ..services.realtime_service import RealtimeService

logger = logging.getLogger(__name__)

router = APIRouter()


async def authenticate_websocket(token: str) -> Dict[str, Any]:
    """
    Authenticate WebSocket connection.
    
    Args:
        token: JWT token
        
    Returns:
        User information
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        payload = verify_token(token)
        return {
            "user_id": payload.sub,
            "email": payload.email,
            "role": payload.role
        }
    except (TokenExpiredError, InvalidTokenError) as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.websocket("/ws/chat/{user_id}")
async def websocket_chat_endpoint(
    websocket: WebSocket,
    user_id: str,
    token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for AI chat.
    
    Args:
        websocket: WebSocket connection
        user_id: User ID
        token: JWT token for authentication
    """
    chatbot_service = ChatbotService()
    
    try:
        # Authenticate user
        if token:
            auth_info = await authenticate_websocket(token)
            if auth_info["user_id"] != user_id:
                await websocket.close(code=4001, reason="Invalid user ID")
                return
            user_role = auth_info["role"]
        else:
            user_role = UserRole.STUDENT
        
        # Connect to WebSocket manager
        connected = await connection_manager.connect(
            websocket, "chat", user_id, user_role, token
        )
        
        if not connected:
            await websocket.close(code=4002, reason="Connection failed")
            return
        
        logger.info(f"Chat WebSocket connected for user: {user_id}")
        
        # Main message handling loop
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # Validate message structure
                if "type" not in message_data:
                    await connection_manager.send_personal_message(
                        {"type": "error", "message": "Message type required"},
                        "chat", user_id
                    )
                    continue
                
                message_type = message_data["type"]
                
                if message_type == "chat_message":
                    # Handle chat message
                    user_message = message_data.get("message", "")
                    session_id = message_data.get("session_id")
                    
                    if not user_message.strip():
                        await connection_manager.send_personal_message(
                            {"type": "error", "message": "Empty message not allowed"},
                            "chat", user_id
                        )
                        continue
                    
                    # Process with chatbot service
                    response = await chatbot_service.process_message(
                        user_id=user_id,
                        message=user_message,
                        session_id=session_id
                    )
                    
                    # Send response back to client
                    await connection_manager.send_personal_message(
                        {
                            "type": "chat_response",
                            "data": response
                        },
                        "chat", user_id
                    )
                
                elif message_type == "typing":
                    # Handle typing indicator
                    typing_status = message_data.get("typing", False)
                    
                    # Could broadcast typing status to other relevant users
                    # For now, just acknowledge
                    await connection_manager.send_personal_message(
                        {
                            "type": "typing_ack",
                            "typing": typing_status
                        },
                        "chat", user_id
                    )
                
                elif message_type == "get_chat_history":
                    # Handle chat history request
                    session_id = message_data.get("session_id")
                    limit = message_data.get("limit", 50)
                    
                    history = await chatbot_service.get_chat_history(
                        user_id=user_id,
                        session_id=session_id,
                        limit=limit
                    )
                    
                    await connection_manager.send_personal_message(
                        {
                            "type": "chat_history",
                            "data": history
                        },
                        "chat", user_id
                    )
                
                elif message_type == "heartbeat":
                    # Handle heartbeat/ping
                    await connection_manager.send_personal_message(
                        {"type": "heartbeat_ack", "timestamp": datetime.utcnow().isoformat()},
                        "chat", user_id
                    )
                
                else:
                    # Unknown message type
                    await connection_manager.send_personal_message(
                        {"type": "error", "message": f"Unknown message type: {message_type}"},
                        "chat", user_id
                    )
                
            except json.JSONDecodeError:
                await connection_manager.send_personal_message(
                    {"type": "error", "message": "Invalid JSON format"},
                    "chat", user_id
                )
            except Exception as e:
                logger.error(f"Error processing chat message for user {user_id}: {e}")
                await connection_manager.send_personal_message(
                    {"type": "error", "message": "Message processing failed"},
                    "chat", user_id
                )
    
    except WebSocketDisconnect:
        logger.info(f"Chat WebSocket disconnected for user: {user_id}")
    except Exception as e:
        logger.error(f"Chat WebSocket error for user {user_id}: {e}")
    finally:
        await connection_manager.disconnect("chat", user_id)


@router.websocket("/ws/dashboard/{user_id}")
async def websocket_dashboard_endpoint(
    websocket: WebSocket,
    user_id: str,
    token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for dashboard updates.
    
    Args:
        websocket: WebSocket connection
        user_id: User ID
        token: JWT token for authentication
    """
    realtime_service = RealtimeService()
    
    try:
        # Authenticate user
        if token:
            auth_info = await authenticate_websocket(token)
            if auth_info["user_id"] != user_id:
                await websocket.close(code=4001, reason="Invalid user ID")
                return
            user_role = auth_info["role"]
        else:
            user_role = UserRole.STUDENT
        
        # Connect to WebSocket manager
        connected = await connection_manager.connect(
            websocket, "dashboard", user_id, user_role, token
        )
        
        if not connected:
            await websocket.close(code=4002, reason="Connection failed")
            return
        
        logger.info(f"Dashboard WebSocket connected for user: {user_id}")
        
        # Send initial dashboard data
        initial_data = await realtime_service.get_dashboard_data(user_id)
        await connection_manager.send_personal_message(
            {
                "type": "dashboard_initial",
                "data": initial_data
            },
            "dashboard", user_id
        )
        
        # Main message handling loop
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                message_type = message_data.get("type")
                
                if message_type == "refresh_dashboard":
                    # Handle dashboard refresh request
                    dashboard_data = await realtime_service.get_dashboard_data(user_id)
                    await connection_manager.send_personal_message(
                        {
                            "type": "dashboard_refresh",
                            "data": dashboard_data
                        },
                        "dashboard", user_id
                    )
                
                elif message_type == "get_transactions":
                    # Handle transaction data request
                    filters = message_data.get("filters", {})
                    transactions = await realtime_service.get_recent_transactions(
                        user_id, filters
                    )
                    await connection_manager.send_personal_message(
                        {
                            "type": "transactions_data",
                            "data": transactions
                        },
                        "dashboard", user_id
                    )
                
                elif message_type == "get_analytics":
                    # Handle analytics request
                    period = message_data.get("period", "month")
                    analytics = await realtime_service.get_analytics_data(
                        user_id, period
                    )
                    await connection_manager.send_personal_message(
                        {
                            "type": "analytics_data",
                            "data": analytics
                        },
                        "dashboard", user_id
                    )
                
                elif message_type == "heartbeat":
                    # Handle heartbeat
                    await connection_manager.send_personal_message(
                        {"type": "heartbeat_ack", "timestamp": datetime.utcnow().isoformat()},
                        "dashboard", user_id
                    )
                
                else:
                    await connection_manager.send_personal_message(
                        {"type": "error", "message": f"Unknown message type: {message_type}"},
                        "dashboard", user_id
                    )
                
            except json.JSONDecodeError:
                await connection_manager.send_personal_message(
                    {"type": "error", "message": "Invalid JSON format"},
                    "dashboard", user_id
                )
            except Exception as e:
                logger.error(f"Error processing dashboard message for user {user_id}: {e}")
                await connection_manager.send_personal_message(
                    {"type": "error", "message": "Message processing failed"},
                    "dashboard", user_id
                )
    
    except WebSocketDisconnect:
        logger.info(f"Dashboard WebSocket disconnected for user: {user_id}")
    except Exception as e:
        logger.error(f"Dashboard WebSocket error for user {user_id}: {e}")
    finally:
        await connection_manager.disconnect("dashboard", user_id)


@router.websocket("/ws/notifications/{user_id}")
async def websocket_notifications_endpoint(
    websocket: WebSocket,
    user_id: str,
    token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time notifications.
    
    Args:
        websocket: WebSocket connection
        user_id: User ID
        token: JWT token for authentication
    """
    notification_service = NotificationService()
    
    try:
        # Authenticate user
        if token:
            auth_info = await authenticate_websocket(token)
            if auth_info["user_id"] != user_id:
                await websocket.close(code=4001, reason="Invalid user ID")
                return
            user_role = auth_info["role"]
        else:
            user_role = UserRole.STUDENT
        
        # Connect to WebSocket manager
        connected = await connection_manager.connect(
            websocket, "notifications", user_id, user_role, token
        )
        
        if not connected:
            await websocket.close(code=4002, reason="Connection failed")
            return
        
        logger.info(f"Notifications WebSocket connected for user: {user_id}")
        
        # Send unread notifications count
        unread_count = await notification_service.get_unread_count(user_id)
        await connection_manager.send_personal_message(
            {
                "type": "unread_count",
                "count": unread_count
            },
            "notifications", user_id
        )
        
        # Main message handling loop
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                message_type = message_data.get("type")
                
                if message_type == "get_notifications":
                    # Handle notifications request
                    page = message_data.get("page", 1)
                    per_page = message_data.get("per_page", 20)
                    
                    notifications = await notification_service.get_user_notifications(
                        user_id, page, per_page
                    )
                    await connection_manager.send_personal_message(
                        {
                            "type": "notifications_list",
                            "data": notifications
                        },
                        "notifications", user_id
                    )
                
                elif message_type == "mark_read":
                    # Handle mark as read
                    notification_id = message_data.get("notification_id")
                    if notification_id:
                        success = await notification_service.mark_as_read(
                            user_id, notification_id
                        )
                        await connection_manager.send_personal_message(
                            {
                                "type": "mark_read_response",
                                "notification_id": notification_id,
                                "success": success
                            },
                            "notifications", user_id
                        )
                
                elif message_type == "mark_all_read":
                    # Handle mark all as read
                    count = await notification_service.mark_all_as_read(user_id)
                    await connection_manager.send_personal_message(
                        {
                            "type": "mark_all_read_response",
                            "marked_count": count
                        },
                        "notifications", user_id
                    )
                
                elif message_type == "delete_notification":
                    # Handle notification deletion
                    notification_id = message_data.get("notification_id")
                    if notification_id:
                        success = await notification_service.delete_notification(
                            user_id, notification_id
                        )
                        await connection_manager.send_personal_message(
                            {
                                "type": "delete_response",
                                "notification_id": notification_id,
                                "success": success
                            },
                            "notifications", user_id
                        )
                
                elif message_type == "heartbeat":
                    # Handle heartbeat
                    await connection_manager.send_personal_message(
                        {"type": "heartbeat_ack", "timestamp": datetime.utcnow().isoformat()},
                        "notifications", user_id
                    )
                
                else:
                    await connection_manager.send_personal_message(
                        {"type": "error", "message": f"Unknown message type: {message_type}"},
                        "notifications", user_id
                    )
                
            except json.JSONDecodeError:
                await connection_manager.send_personal_message(
                    {"type": "error", "message": "Invalid JSON format"},
                    "notifications", user_id
                )
            except Exception as e:
                logger.error(f"Error processing notification message for user {user_id}: {e}")
                await connection_manager.send_personal_message(
                    {"type": "error", "message": "Message processing failed"},
                    "notifications", user_id
                )
    
    except WebSocketDisconnect:
        logger.info(f"Notifications WebSocket disconnected for user: {user_id}")
    except Exception as e:
        logger.error(f"Notifications WebSocket error for user {user_id}: {e}")
    finally:
        await connection_manager.disconnect("notifications", user_id)


@router.websocket("/ws/admin/{admin_id}")
async def websocket_admin_endpoint(
    websocket: WebSocket,
    admin_id: str,
    token: str = Query(...)
):
    """
    WebSocket endpoint for admin panel updates.
    
    Args:
        websocket: WebSocket connection
        admin_id: Admin user ID
        token: JWT token for authentication
    """
    try:
        # Authenticate admin
        auth_info = await authenticate_websocket(token)
        if auth_info["user_id"] != admin_id:
            await websocket.close(code=4001, reason="Invalid admin ID")
            return
        
        if auth_info["role"] != UserRole.ADMIN:
            await websocket.close(code=4003, reason="Admin access required")
            return
        
        # Connect to WebSocket manager
        connected = await connection_manager.connect(
            websocket, "admin", admin_id, UserRole.ADMIN, token
        )
        
        if not connected:
            await websocket.close(code=4002, reason="Connection failed")
            return
        
        logger.info(f"Admin WebSocket connected for admin: {admin_id}")
        
        # Send initial admin data
        stats = connection_manager.get_connection_stats()
        await connection_manager.send_personal_message(
            {
                "type": "admin_initial",
                "data": {
                    "connection_stats": stats,
                    "timestamp": datetime.utcnow().isoformat()
                }
            },
            "admin", admin_id
        )
        
        # Main message handling loop
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                message_type = message_data.get("type")
                
                if message_type == "get_stats":
                    # Handle stats request
                    stats = connection_manager.get_connection_stats()
                    await connection_manager.send_personal_message(
                        {
                            "type": "stats_data",
                            "data": stats
                        },
                        "admin", admin_id
                    )
                
                elif message_type == "broadcast_announcement":
                    # Handle admin broadcast
                    announcement = message_data.get("announcement")
                    target_type = message_data.get("target_type", "all")
                    
                    if announcement:
                        broadcast_message = {
                            "type": "announcement",
                            "message": announcement,
                            "from_admin": True,
                            "admin_id": admin_id
                        }
                        
                        if target_type == "all":
                            # Broadcast to all connection types
                            for conn_type in ["chat", "dashboard", "notifications"]:
                                await connection_manager.broadcast_to_type(
                                    broadcast_message, conn_type
                                )
                        else:
                            # Broadcast to specific type
                            await connection_manager.broadcast_to_type(
                                broadcast_message, target_type
                            )
                        
                        await connection_manager.send_personal_message(
                            {
                                "type": "broadcast_success",
                                "message": "Announcement broadcasted successfully"
                            },
                            "admin", admin_id
                        )
                
                elif message_type == "heartbeat":
                    # Handle heartbeat
                    await connection_manager.send_personal_message(
                        {"type": "heartbeat_ack", "timestamp": datetime.utcnow().isoformat()},
                        "admin", admin_id
                    )
                
                else:
                    await connection_manager.send_personal_message(
                        {"type": "error", "message": f"Unknown message type: {message_type}"},
                        "admin", admin_id
                    )
                
            except json.JSONDecodeError:
                await connection_manager.send_personal_message(
                    {"type": "error", "message": "Invalid JSON format"},
                    "admin", admin_id
                )
            except Exception as e:
                logger.error(f"Error processing admin message for admin {admin_id}: {e}")
                await connection_manager.send_personal_message(
                    {"type": "error", "message": "Message processing failed"},
                    "admin", admin_id
                )
    
    except WebSocketDisconnect:
        logger.info(f"Admin WebSocket disconnected for admin: {admin_id}")
    except Exception as e:
        logger.error(f"Admin WebSocket error for admin {admin_id}: {e}")
    finally:
        await connection_manager.disconnect("admin", admin_id)


# WebSocket status endpoint
@router.get("/ws/status")
async def websocket_status():
    """Get WebSocket server status."""
    stats = connection_manager.get_connection_stats()
    
    return {
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "websocket_stats": stats,
        "available_endpoints": [
            "/ws/chat/{user_id}",
            "/ws/dashboard/{user_id}",
            "/ws/notifications/{user_id}",
            "/ws/admin/{admin_id}"
        ]
    }