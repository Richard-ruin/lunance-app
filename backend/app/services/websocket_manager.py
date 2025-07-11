from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Optional
import json
import asyncio
from datetime import datetime

from ..models.chat import WSMessage, WSMessageType

class WebSocketManager:
    """Manager untuk mengelola WebSocket connections"""
    
    def __init__(self):
        # Active connections: user_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}
        # User typing status: user_id -> is_typing
        self.typing_status: Dict[str, bool] = {}
        # Connection metadata: user_id -> connection_info
        self.connection_info: Dict[str, dict] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept new WebSocket connection"""
        await websocket.accept()
        
        # Store connection
        self.active_connections[user_id] = websocket
        self.typing_status[user_id] = False
        self.connection_info[user_id] = {
            "connected_at": datetime.utcnow(),
            "last_activity": datetime.utcnow()
        }
        
        # Send connection success message
        await self.send_personal_message(
            user_id=user_id,
            message_type=WSMessageType.SUCCESS,
            data={"message": "Connected to Luna chat successfully"}
        )
        
        print(f"📱 User {user_id} connected to WebSocket")
    
    def disconnect(self, user_id: str):
        """Remove user connection"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        
        if user_id in self.typing_status:
            del self.typing_status[user_id]
            
        if user_id in self.connection_info:
            del self.connection_info[user_id]
        
        print(f"📱 User {user_id} disconnected from WebSocket")
    
    async def send_personal_message(
        self, 
        user_id: str, 
        message_type: WSMessageType, 
        data: dict
    ):
        """Send message to specific user"""
        if user_id not in self.active_connections:
            return False
        
        websocket = self.active_connections[user_id]
        
        message = {
            "type": message_type.value,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            await websocket.send_text(json.dumps(message))
            
            # Update last activity
            if user_id in self.connection_info:
                self.connection_info[user_id]["last_activity"] = datetime.utcnow()
            
            return True
        except Exception as e:
            print(f"❌ Error sending message to {user_id}: {e}")
            # Remove broken connection
            self.disconnect(user_id)
            return False
    
    async def broadcast_to_users(
        self, 
        user_ids: List[str], 
        message_type: WSMessageType, 
        data: dict
    ):
        """Broadcast message to multiple users"""
        tasks = []
        for user_id in user_ids:
            task = self.send_personal_message(user_id, message_type, data)
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def broadcast_to_all(self, message_type: WSMessageType, data: dict):
        """Broadcast message to all connected users"""
        if not self.active_connections:
            return
        
        user_ids = list(self.active_connections.keys())
        await self.broadcast_to_users(user_ids, message_type, data)
    
    def is_connected(self, user_id: str) -> bool:
        """Check if user is connected"""
        return user_id in self.active_connections
    
    def get_connected_users(self) -> List[str]:
        """Get list of connected user IDs"""
        return list(self.active_connections.keys())
    
    def get_connection_count(self) -> int:
        """Get total number of active connections"""
        return len(self.active_connections)
    
    async def set_typing_status(self, user_id: str, is_typing: bool):
        """Set typing status for user"""
        if user_id in self.typing_status:
            self.typing_status[user_id] = is_typing
    
    def get_typing_status(self, user_id: str) -> bool:
        """Get typing status for user"""
        return self.typing_status.get(user_id, False)
    
    async def handle_ping(self, user_id: str):
        """Handle ping message to keep connection alive"""
        await self.send_personal_message(
            user_id=user_id,
            message_type=WSMessageType.SUCCESS,
            data={"message": "pong", "type": "pong"}
        )
    
    async def cleanup_inactive_connections(self, timeout_minutes: int = 30):
        """Remove connections that have been inactive for too long"""
        current_time = datetime.utcnow()
        inactive_users = []
        
        for user_id, info in self.connection_info.items():
            last_activity = info.get("last_activity", current_time)
            if (current_time - last_activity).total_seconds() > (timeout_minutes * 60):
                inactive_users.append(user_id)
        
        for user_id in inactive_users:
            print(f"🧹 Cleaning up inactive connection for user {user_id}")
            if user_id in self.active_connections:
                try:
                    await self.active_connections[user_id].close()
                except:
                    pass
            self.disconnect(user_id)
    
    def get_connection_stats(self) -> dict:
        """Get connection statistics"""
        return {
            "total_connections": self.get_connection_count(),
            "connected_users": self.get_connected_users(),
            "typing_users": [
                user_id for user_id, is_typing in self.typing_status.items() 
                if is_typing
            ]
        }
    
    async def send_chat_message_to_user(
        self, 
        user_id: str, 
        message_data: dict
    ):
        """Send chat message to specific user"""
        return await self.send_personal_message(
            user_id=user_id,
            message_type=WSMessageType.CHAT_MESSAGE,
            data={"message": message_data}
        )
    
    async def send_typing_indicator(
        self, 
        user_id: str, 
        sender: str, 
        is_typing: bool
    ):
        """Send typing indicator to user"""
        message_type = WSMessageType.TYPING_START if is_typing else WSMessageType.TYPING_STOP
        return await self.send_personal_message(
            user_id=user_id,
            message_type=message_type,
            data={"sender": sender}
        )
    
    async def send_error_to_user(self, user_id: str, error_message: str):
        """Send error message to user"""
        return await self.send_personal_message(
            user_id=user_id,
            message_type=WSMessageType.ERROR,
            data={"message": error_message}
        )
    
    async def send_success_to_user(self, user_id: str, success_message: str):
        """Send success message to user"""
        return await self.send_personal_message(
            user_id=user_id,
            message_type=WSMessageType.SUCCESS,
            data={"message": success_message}
        )
    
    async def handle_message_received(self, user_id: str, message_data: dict):
        """Handle incoming message from user"""
        message_type = message_data.get("type")
        data = message_data.get("data", {})
        
        # Update last activity
        if user_id in self.connection_info:
            self.connection_info[user_id]["last_activity"] = datetime.utcnow()
        
        if message_type == "ping":
            await self.handle_ping(user_id)
        elif message_type == "typing_start":
            await self.set_typing_status(user_id, True)
        elif message_type == "typing_stop":
            await self.set_typing_status(user_id, False)
        
        return {
            "type": message_type,
            "data": data,
            "user_id": user_id
        }
    
    async def graceful_shutdown(self):
        """Gracefully close all connections"""
        print("🔄 Shutting down WebSocket connections...")
        
        # Send shutdown notice to all users
        await self.broadcast_to_all(
            WSMessageType.SUCCESS,
            {"message": "Server is shutting down. Please reconnect in a moment."}
        )
        
        # Close all connections
        for user_id, websocket in list(self.active_connections.items()):
            try:
                await websocket.close(code=1000, reason="Server shutdown")
            except:
                pass
            self.disconnect(user_id)
        
        print("✅ All WebSocket connections closed")

# Global instance
websocket_manager = WebSocketManager()