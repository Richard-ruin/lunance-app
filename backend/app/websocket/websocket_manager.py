# app/websocket/websocket_manager.py
"""WebSocket connection manager for real-time features."""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Set, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect
from collections import defaultdict
import time

from ..models.user import UserRole
from ..utils.jwt import verify_token, TokenExpiredError, InvalidTokenError

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections with authentication and message broadcasting."""
    
    def __init__(self):
        # Active connections by connection type
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {
            "chat": {},      # user_id -> websocket
            "dashboard": {}, # user_id -> websocket  
            "notifications": {}, # user_id -> websocket
            "admin": {}      # admin_user_id -> websocket
        }
        
        # Connection metadata
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Message queues for offline users
        self.message_queues: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        # Rate limiting
        self.rate_limits: Dict[str, List[float]] = defaultdict(list)
        self.max_messages_per_minute = 60
        
        # Connection statistics
        self.stats = {
            "total_connections": 0,
            "active_connections": 0,
            "messages_sent": 0,
            "messages_received": 0,
            "disconnections": 0
        }
    
    async def connect(
        self, 
        websocket: WebSocket, 
        connection_type: str, 
        user_id: str,
        user_role: UserRole = UserRole.STUDENT,
        token: Optional[str] = None
    ) -> bool:
        """
        Connect a new WebSocket.
        
        Args:
            websocket: WebSocket instance
            connection_type: Type of connection (chat, dashboard, notifications, admin)
            user_id: User ID
            user_role: User role
            token: JWT token for authentication
            
        Returns:
            True if connection successful
        """
        try:
            # Authenticate user if token provided
            if token:
                try:
                    payload = verify_token(token)
                    if payload.sub != user_id:
                        logger.warning(f"Token user ID mismatch: {payload.sub} != {user_id}")
                        return False
                except (TokenExpiredError, InvalidTokenError) as e:
                    logger.warning(f"WebSocket authentication failed: {e}")
                    return False
            
            # Accept connection
            await websocket.accept()
            
            # Store connection
            if connection_type not in self.active_connections:
                self.active_connections[connection_type] = {}
            
            # Disconnect existing connection if any
            if user_id in self.active_connections[connection_type]:
                try:
                    await self.active_connections[connection_type][user_id].close()
                except:
                    pass
            
            self.active_connections[connection_type][user_id] = websocket
            
            # Store metadata
            connection_id = f"{connection_type}:{user_id}"
            self.connection_metadata[connection_id] = {
                "user_id": user_id,
                "user_role": user_role.value,
                "connection_type": connection_type,
                "connected_at": datetime.utcnow(),
                "last_activity": datetime.utcnow(),
                "message_count": 0
            }
            
            # Update statistics
            self.stats["total_connections"] += 1
            self.stats["active_connections"] = self._count_active_connections()
            
            # Send queued messages if any
            await self._send_queued_messages(user_id, websocket)
            
            # Send connection success message
            await self._send_to_connection(websocket, {
                "type": "connection_status",
                "status": "connected",
                "connection_type": connection_type,
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id
            })
            
            logger.info(f"WebSocket connected: {connection_type}:{user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting WebSocket: {e}")
            return False
    
    async def disconnect(self, connection_type: str, user_id: str):
        """
        Disconnect a WebSocket.
        
        Args:
            connection_type: Type of connection
            user_id: User ID
        """
        try:
            if (connection_type in self.active_connections and 
                user_id in self.active_connections[connection_type]):
                
                # Remove connection
                del self.active_connections[connection_type][user_id]
                
                # Remove metadata
                connection_id = f"{connection_type}:{user_id}"
                if connection_id in self.connection_metadata:
                    del self.connection_metadata[connection_id]
                
                # Update statistics
                self.stats["disconnections"] += 1
                self.stats["active_connections"] = self._count_active_connections()
                
                logger.info(f"WebSocket disconnected: {connection_type}:{user_id}")
                
        except Exception as e:
            logger.error(f"Error disconnecting WebSocket: {e}")
    
    async def send_personal_message(
        self, 
        message: Dict[str, Any], 
        connection_type: str, 
        user_id: str
    ) -> bool:
        """
        Send message to specific user.
        
        Args:
            message: Message to send
            connection_type: Type of connection
            user_id: Target user ID
            
        Returns:
            True if message sent successfully
        """
        try:
            # Check rate limiting
            if not self._check_rate_limit(user_id):
                logger.warning(f"Rate limit exceeded for user {user_id}")
                return False
            
            # Get connection
            if (connection_type in self.active_connections and 
                user_id in self.active_connections[connection_type]):
                
                websocket = self.active_connections[connection_type][user_id]
                
                # Add metadata to message
                enhanced_message = {
                    **message,
                    "timestamp": datetime.utcnow().isoformat(),
                    "connection_type": connection_type
                }
                
                await self._send_to_connection(websocket, enhanced_message)
                
                # Update activity
                connection_id = f"{connection_type}:{user_id}"
                if connection_id in self.connection_metadata:
                    self.connection_metadata[connection_id]["last_activity"] = datetime.utcnow()
                    self.connection_metadata[connection_id]["message_count"] += 1
                
                self.stats["messages_sent"] += 1
                return True
            else:
                # Queue message for offline user
                await self._queue_message(user_id, message)
                return False
                
        except WebSocketDisconnect:
            await self.disconnect(connection_type, user_id)
            return False
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            return False
    
    async def broadcast_to_type(
        self, 
        message: Dict[str, Any], 
        connection_type: str,
        exclude_user_ids: Optional[List[str]] = None
    ):
        """
        Broadcast message to all connections of a specific type.
        
        Args:
            message: Message to broadcast
            connection_type: Type of connection
            exclude_user_ids: List of user IDs to exclude
        """
        try:
            if connection_type not in self.active_connections:
                return
            
            exclude_user_ids = exclude_user_ids or []
            
            # Enhanced message
            enhanced_message = {
                **message,
                "timestamp": datetime.utcnow().isoformat(),
                "connection_type": connection_type,
                "broadcast": True
            }
            
            # Send to all connections of this type
            disconnected_users = []
            for user_id, websocket in self.active_connections[connection_type].items():
                if user_id not in exclude_user_ids:
                    try:
                        await self._send_to_connection(websocket, enhanced_message)
                        self.stats["messages_sent"] += 1
                    except WebSocketDisconnect:
                        disconnected_users.append(user_id)
                    except Exception as e:
                        logger.error(f"Error broadcasting to {user_id}: {e}")
            
            # Clean up disconnected users
            for user_id in disconnected_users:
                await self.disconnect(connection_type, user_id)
                
        except Exception as e:
            logger.error(f"Error broadcasting message: {e}")
    
    async def broadcast_to_admins(self, message: Dict[str, Any]):
        """
        Broadcast message to all admin connections.
        
        Args:
            message: Message to broadcast
        """
        await self.broadcast_to_type(message, "admin")
    
    async def send_notification(
        self, 
        user_id: str, 
        notification: Dict[str, Any]
    ) -> bool:
        """
        Send notification to user.
        
        Args:
            user_id: Target user ID
            notification: Notification data
            
        Returns:
            True if notification sent
        """
        notification_message = {
            "type": "notification",
            "data": notification
        }
        
        return await self.send_personal_message(
            notification_message, 
            "notifications", 
            user_id
        )
    
    async def send_dashboard_update(
        self, 
        user_id: str, 
        update_data: Dict[str, Any]
    ) -> bool:
        """
        Send dashboard update to user.
        
        Args:
            user_id: Target user ID
            update_data: Dashboard update data
            
        Returns:
            True if update sent
        """
        dashboard_message = {
            "type": "dashboard_update",
            "data": update_data
        }
        
        return await self.send_personal_message(
            dashboard_message, 
            "dashboard", 
            user_id
        )
    
    async def send_chat_message(
        self, 
        user_id: str, 
        message: Dict[str, Any]
    ) -> bool:
        """
        Send chat message to user.
        
        Args:
            user_id: Target user ID
            message: Chat message data
            
        Returns:
            True if message sent
        """
        chat_message = {
            "type": "chat_message",
            "data": message
        }
        
        return await self.send_personal_message(
            chat_message, 
            "chat", 
            user_id
        )
    
    def get_active_users(self, connection_type: str) -> List[str]:
        """
        Get list of active users for connection type.
        
        Args:
            connection_type: Type of connection
            
        Returns:
            List of active user IDs
        """
        return list(self.active_connections.get(connection_type, {}).keys())
    
    def is_user_connected(self, user_id: str, connection_type: str) -> bool:
        """
        Check if user is connected for specific connection type.
        
        Args:
            user_id: User ID
            connection_type: Type of connection
            
        Returns:
            True if user is connected
        """
        return (connection_type in self.active_connections and 
                user_id in self.active_connections[connection_type])
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """
        Get connection statistics.
        
        Returns:
            Connection statistics
        """
        return {
            **self.stats,
            "connections_by_type": {
                conn_type: len(connections) 
                for conn_type, connections in self.active_connections.items()
            },
            "queued_messages": sum(len(queue) for queue in self.message_queues.values()),
            "oldest_connection": self._get_oldest_connection_time()
        }
    
    async def cleanup_inactive_connections(self, timeout_minutes: int = 30):
        """
        Clean up inactive connections.
        
        Args:
            timeout_minutes: Timeout in minutes
        """
        try:
            cutoff_time = datetime.utcnow().timestamp() - (timeout_minutes * 60)
            inactive_connections = []
            
            for connection_id, metadata in self.connection_metadata.items():
                last_activity = metadata["last_activity"].timestamp()
                if last_activity < cutoff_time:
                    inactive_connections.append(connection_id)
            
            # Disconnect inactive connections
            for connection_id in inactive_connections:
                connection_type, user_id = connection_id.split(":", 1)
                await self.disconnect(connection_type, user_id)
            
            if inactive_connections:
                logger.info(f"Cleaned up {len(inactive_connections)} inactive connections")
                
        except Exception as e:
            logger.error(f"Error cleaning up connections: {e}")
    
    async def _send_to_connection(self, websocket: WebSocket, message: Dict[str, Any]):
        """Send message to specific websocket connection."""
        try:
            await websocket.send_text(json.dumps(message, default=str))
        except Exception as e:
            logger.error(f"Error sending message to WebSocket: {e}")
            raise
    
    async def _send_queued_messages(self, user_id: str, websocket: WebSocket):
        """Send queued messages to newly connected user."""
        try:
            if user_id in self.message_queues:
                messages = self.message_queues[user_id]
                for message in messages:
                    await self._send_to_connection(websocket, message)
                # Clear queue after sending
                del self.message_queues[user_id]
                logger.info(f"Sent {len(messages)} queued messages to {user_id}")
        except Exception as e:
            logger.error(f"Error sending queued messages: {e}")
    
    async def _queue_message(self, user_id: str, message: Dict[str, Any]):
        """Queue message for offline user."""
        try:
            # Limit queue size
            max_queue_size = 100
            if len(self.message_queues[user_id]) >= max_queue_size:
                self.message_queues[user_id].pop(0)  # Remove oldest
            
            enhanced_message = {
                **message,
                "queued_at": datetime.utcnow().isoformat(),
                "queued": True
            }
            
            self.message_queues[user_id].append(enhanced_message)
            logger.debug(f"Queued message for offline user {user_id}")
            
        except Exception as e:
            logger.error(f"Error queuing message: {e}")
    
    def _check_rate_limit(self, user_id: str) -> bool:
        """Check if user is within rate limit."""
        try:
            now = time.time()
            minute_ago = now - 60
            
            # Clean old timestamps
            self.rate_limits[user_id] = [
                timestamp for timestamp in self.rate_limits[user_id] 
                if timestamp > minute_ago
            ]
            
            # Check limit
            if len(self.rate_limits[user_id]) >= self.max_messages_per_minute:
                return False
            
            # Add current timestamp
            self.rate_limits[user_id].append(now)
            return True
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            return True  # Allow on error
    
    def _count_active_connections(self) -> int:
        """Count total active connections."""
        return sum(
            len(connections) 
            for connections in self.active_connections.values()
        )
    
    def _get_oldest_connection_time(self) -> Optional[str]:
        """Get timestamp of oldest connection."""
        try:
            if not self.connection_metadata:
                return None
            
            oldest_time = min(
                metadata["connected_at"] 
                for metadata in self.connection_metadata.values()
            )
            return oldest_time.isoformat()
            
        except Exception:
            return None


# Global connection manager instance
connection_manager = ConnectionManager()


# Background task for connection cleanup
async def connection_cleanup_task():
    """Background task to cleanup inactive connections."""
    while True:
        try:
            await asyncio.sleep(300)  # Run every 5 minutes
            await connection_manager.cleanup_inactive_connections(30)
        except Exception as e:
            logger.error(f"Error in connection cleanup task: {e}")
            await asyncio.sleep(60)  # Wait 1 minute before retry