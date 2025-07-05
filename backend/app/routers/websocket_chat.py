# app/routers/websocket_chat.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from fastapi.websockets import WebSocketState
import json
import asyncio
import logging
from typing import Dict, List, Any
from datetime import datetime
from bson import ObjectId

from ..database import get_database
from ..services.luna_ai import luna_ai
from ..auth.jwt_handler import verify_token
from ..models.chat_message import ChatMessage

router = APIRouter()
logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info(f"User {user_id} connected to chat WebSocket")
    
    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            self.active_connections[user_id] = [
                conn for conn in self.active_connections[user_id] 
                if conn != websocket
            ]
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"User {user_id} disconnected from chat WebSocket")
    
    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                if connection.client_state == WebSocketState.CONNECTED:
                    try:
                        await connection.send_text(message)
                    except Exception as e:
                        logger.error(f"Error sending message to user {user_id}: {e}")
    
    async def broadcast_typing(self, user_id: str, session_id: str, is_typing: bool):
        """Broadcast typing indicator"""
        message = {
            "event": "typing_indicator",
            "data": {
                "user_id": user_id,
                "session_id": session_id,
                "is_typing": is_typing,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        await self.send_personal_message(json.dumps(message), user_id)

manager = ConnectionManager()

async def get_user_from_token(token: str = Query(...)):
    """Extract user from JWT token for WebSocket auth"""
    try:
        payload = verify_token(token)
        if not payload or payload.get("type") != "access":
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        # Verify user exists
        db = await get_database()
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        
        if not user or not user.get("is_active", True):
            return None
        
        return {
            "id": str(user["_id"]),
            "email": user["email"],
            "nama_lengkap": user["nama_lengkap"]
        }
        
    except Exception as e:
        logger.error(f"WebSocket auth error: {e}")
        return None

@router.websocket("/ws/chat/{user_id}")
async def websocket_chat_endpoint(
    websocket: WebSocket,
    user_id: str,
    token: str = Query(...)
):
    """WebSocket endpoint for real-time chat with Luna"""
    
    # Authenticate user
    user = await get_user_from_token(token)
    if not user or user["id"] != user_id:
        await websocket.close(code=4001, reason="Unauthorized")
        return
    
    await manager.connect(websocket, user_id)
    
    try:
        # Send welcome message
        welcome_message = {
            "event": "connection_established",
            "data": {
                "message": "Connected to Luna AI Chat",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        await websocket.send_text(json.dumps(welcome_message))
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            event = message_data.get("event")
            payload = message_data.get("data", {})
            
            if event == "send_message":
                await handle_chat_message(websocket, user_id, payload)
            
            elif event == "typing_start":
                await manager.broadcast_typing(
                    user_id, 
                    payload.get("session_id"), 
                    True
                )
            
            elif event == "typing_stop":
                await manager.broadcast_typing(
                    user_id, 
                    payload.get("session_id"), 
                    False
                )
            
            elif event == "ping":
                pong_message = {
                    "event": "pong",
                    "data": {"timestamp": datetime.utcnow().isoformat()}
                }
                await websocket.send_text(json.dumps(pong_message))
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(websocket, user_id)

async def handle_chat_message(websocket: WebSocket, user_id: str, payload: Dict[str, Any]):
    """Handle incoming chat message"""
    try:
        session_id = payload.get("session_id")
        message_content = payload.get("message")
        
        if not session_id or not message_content:
            error_response = {
                "event": "error",
                "data": {
                    "message": "Missing session_id or message",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            await websocket.send_text(json.dumps(error_response))
            return
        
        # Verify session exists
        db = await get_database()
        session = await db.chat_sessions.find_one({
            "session_id": session_id,
            "user_id": ObjectId(user_id)
        })
        
        if not session:
            error_response = {
                "event": "error",
                "data": {
                    "message": "Session not found",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            await websocket.send_text(json.dumps(error_response))
            return
        
        # Send message received confirmation
        received_response = {
            "event": "message_received",
            "data": {
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        await websocket.send_text(json.dumps(received_response))
        
        # Store user message
        user_message = ChatMessage(
            session_id=session_id,
            user_id=ObjectId(user_id),
            message_type="user",
            content=message_content
        )
        
        user_message_doc = user_message.model_dump()
        user_message_doc["created_at"] = datetime.utcnow()
        user_message_doc["updated_at"] = datetime.utcnow()
        
        await db.chat_messages.insert_one(user_message_doc)
        
        # Send typing indicator for AI
        typing_response = {
            "event": "ai_typing",
            "data": {
                "session_id": session_id,
                "is_typing": True,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        await websocket.send_text(json.dumps(typing_response))
        
        # Process with Luna AI
        ai_response = await luna_ai.process_message(
            user_id=user_id,
            session_id=session_id,
            message=message_content,
            context=session.get("context", {})
        )
        
        # Store AI response
        ai_message = ChatMessage(
            session_id=session_id,
            user_id=ObjectId(user_id),
            message_type="assistant",
            content=ai_response.message,
            intent=ai_response.intent,
            entities=[entity.model_dump() for entity in ai_response.entities],
            context=ai_response.context,
            response_data={
                "actions_performed": ai_response.actions_performed,
                "suggestions": ai_response.suggestions
            },
            confidence_score=ai_response.confidence,
            processing_time=ai_response.processing_time
        )
        
        ai_message_doc = ai_message.model_dump()
        ai_message_doc["created_at"] = datetime.utcnow()
        ai_message_doc["updated_at"] = datetime.utcnow()
        
        await db.chat_messages.insert_one(ai_message_doc)
        
        # Update session
        await db.chat_sessions.update_one(
            {"session_id": session_id},
            {
                "$set": {
                    "context": ai_response.context,
                    "last_message_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Stop typing indicator
        typing_stop_response = {
            "event": "ai_typing",
            "data": {
                "session_id": session_id,
                "is_typing": False,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        await websocket.send_text(json.dumps(typing_stop_response))
        
        # Send AI response
        ai_response_message = {
            "event": "ai_response",
            "data": {
                "session_id": session_id,
                "message": ai_response.message,
                "intent": ai_response.intent,
                "entities": [entity.model_dump() for entity in ai_response.entities],
                "actions_performed": ai_response.actions_performed,
                "suggestions": ai_response.suggestions,
                "confidence": ai_response.confidence,
                "processing_time": ai_response.processing_time,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        await websocket.send_text(json.dumps(ai_response_message))
        
        # Send suggestions if any
        if ai_response.suggestions:
            suggestions_message = {
                "event": "suggestions",
                "data": {
                    "session_id": session_id,
                    "suggestions": ai_response.suggestions,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            await websocket.send_text(json.dumps(suggestions_message))
        
    except Exception as e:
        logger.error(f"Error handling chat message: {e}")
        error_response = {
            "event": "error",
            "data": {
                "message": f"Failed to process message: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        await websocket.send_text(json.dumps(error_response))