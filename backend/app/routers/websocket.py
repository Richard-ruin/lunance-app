# app/routers/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, List, Any
import json
import asyncio
from datetime import datetime

from ..database import get_database
from ..auth.jwt_handler import verify_token
from ..utils.exceptions import CustomHTTPException

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(message)
                except:
                    # Remove broken connections
                    self.active_connections[user_id].remove(connection)

    async def broadcast_to_user(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            message_str = json.dumps(message, default=str)
            for connection in self.active_connections[user_id].copy():
                try:
                    await connection.send_text(message_str)
                except:
                    self.active_connections[user_id].remove(connection)

manager = ConnectionManager()

@router.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    # Verify JWT token
    payload = verify_token(token)
    if not payload or payload.get("type") != "access":
        await websocket.close(code=4001, reason="Invalid token")
        return
    
    user_id = payload.get("sub")
    if not user_id:
        await websocket.close(code=4001, reason="Invalid user")
        return

    await manager.connect(websocket, user_id)
    
    try:
        # Send initial connection message
        await manager.send_personal_message(
            json.dumps({
                "type": "connection_established",
                "message": "Connected to real-time updates",
                "timestamp": datetime.utcnow().isoformat()
            }),
            user_id
        )
        
        # Listen for client messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "ping":
                await manager.send_personal_message(
                    json.dumps({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    }),
                    user_id
                )
            elif message.get("type") == "subscribe_dashboard":
                # Subscribe to dashboard updates
                await start_dashboard_updates(user_id)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, user_id)

async def start_dashboard_updates(user_id: str):
    """Start sending periodic dashboard updates"""
    try:
        db = await get_database()
        
        # Send updated dashboard data every 30 seconds
        while user_id in manager.active_connections:
            # Get latest dashboard data
            from ..utils.analytics_helpers import calculate_dashboard_metrics
            from bson import ObjectId
            
            dashboard_data = await calculate_dashboard_metrics(db, ObjectId(user_id))
            
            await manager.broadcast_to_user({
                "type": "dashboard_update",
                "data": dashboard_data,
                "timestamp": datetime.utcnow().isoformat()
            }, user_id)
            
            await asyncio.sleep(30)  # Update every 30 seconds
            
    except Exception as e:
        print(f"Dashboard update error: {e}")

# Function to broadcast transaction updates
async def broadcast_transaction_update(user_id: str, transaction_data: dict, event_type: str):
    """Broadcast transaction updates to connected users"""
    message = {
        "type": "transaction_update",
        "event": event_type,  # "created", "updated", "deleted"
        "data": transaction_data,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await manager.broadcast_to_user(message, user_id)

# Function to broadcast goal updates  
async def broadcast_goal_update(user_id: str, goal_data: dict, event_type: str):
    """Broadcast savings goal updates to connected users"""
    message = {
        "type": "goal_update", 
        "event": event_type,  # "created", "updated", "achieved"
        "data": goal_data,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await manager.broadcast_to_user(message, user_id)

# Function to broadcast budget alerts
async def broadcast_budget_alert(user_id: str, alert_data: dict):
    """Broadcast budget alerts to connected users"""
    message = {
        "type": "budget_alert",
        "data": alert_data,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await manager.broadcast_to_user(message, user_id)