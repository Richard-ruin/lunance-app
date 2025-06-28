# app/services/chat/websocket_manager.py
import json
import logging
import uuid
from typing import Dict, List, Optional
from datetime import datetime
import asyncio

from fastapi import WebSocket, WebSocketDisconnect
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.chat import (
    WebSocketMessage, WebSocketResponse, ConnectionInfo,
    ChatSession, ChatMessage, ChatMessageCreate
)
from backend.app.models.user import Student
from app.services.chat.chat_service import ChatService

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_info: Dict[str, ConnectionInfo] = {}
        self.chat_service = ChatService(db)
        
    async def connect(self, websocket: WebSocket, student: Student) -> str:
        """Accept WebSocket connection and create session"""
        await websocket.accept()
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Store connection
        self.active_connections[session_id] = websocket
        self.connection_info[session_id] = ConnectionInfo(
            student_id=str(student.id),
            session_id=session_id
        )
        
        # Create chat session in database
        chat_session = ChatSession(
            student_id=student.id,
            session_id=session_id
        )
        
        try:
            await self.db.chat_sessions.insert_one(chat_session.model_dump(by_alias=True))
        except Exception as e:
            logger.error(f"Failed to create chat session: {str(e)}")
        
        # Send welcome message
        welcome_response = WebSocketResponse(
            type="system",
            content="Koneksi berhasil! Saya Luna, asisten keuangan Anda. Ada yang bisa saya bantu?",
            session_id=session_id
        )
        
        await self._send_to_connection(session_id, welcome_response.model_dump())
        
        logger.info(f"WebSocket connected: session_id={session_id}, student_id={student.id}")
        return session_id
    
    def disconnect(self, session_id: str):
        """Remove WebSocket connection"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        
        if session_id in self.connection_info:
            del self.connection_info[session_id]
        
        # Update session end time in database
        asyncio.create_task(self._end_chat_session(session_id))
        
        logger.info(f"WebSocket disconnected: session_id={session_id}")
    
    async def process_message(self, session_id: str, message_data: dict, student: Student):
        """Process incoming message from WebSocket"""
        try:
            # Parse message
            ws_message = WebSocketMessage(**message_data)
            
            # Update last activity
            if session_id in self.connection_info:
                self.connection_info[session_id].last_activity = datetime.utcnow()
            
            # Send typing indicator
            await self._send_typing_indicator(session_id, True)
            
            # Process message based on type
            if ws_message.type == "message":
                await self._handle_chat_message(session_id, ws_message.content, student)
            elif ws_message.type == "ping":
                await self._handle_ping(session_id)
            else:
                logger.warning(f"Unknown message type: {ws_message.type}")
        
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            error_response = WebSocketResponse(
                type="error",
                content="Maaf, terjadi kesalahan saat memproses pesan Anda.",
                session_id=session_id
            )
            await self._send_to_connection(session_id, error_response.model_dump())
        
        finally:
            # Stop typing indicator
            await self._send_typing_indicator(session_id, False)
    
    async def _handle_chat_message(self, session_id: str, message_content: str, student: Student):
        """Handle chat message and generate response"""
        try:
            # Save user message to database
            user_message = ChatMessage(
                role="user",
                content=message_content
            )
            
            await self._save_message_to_session(session_id, user_message)
            
            # Process message with chat service
            chat_response = await self.chat_service.process_message(
                message_content, student, session_id
            )
            
            # Create assistant message
            assistant_message = ChatMessage(
                role="assistant",
                content=chat_response.message,
                intent=None,  # Could be populated from chat_response if needed
                response_type=chat_response.response_type,
                data_used=chat_response.data_used
            )
            
            # Save assistant message to database
            await self._save_message_to_session(session_id, assistant_message)
            
            # Send response via WebSocket
            ws_response = WebSocketResponse(
                type="response",
                content=chat_response.message,
                session_id=session_id,
                response_data=chat_response
            )
            
            await self._send_to_connection(session_id, ws_response.model_dump())
            
        except Exception as e:
            logger.error(f"Error handling chat message: {str(e)}")
            error_response = WebSocketResponse(
                type="error",
                content="Maaf, saya tidak bisa memproses pesan Anda saat ini. Coba lagi ya!",
                session_id=session_id
            )
            await self._send_to_connection(session_id, error_response.model_dump())
    
    async def _handle_ping(self, session_id: str):
        """Handle ping message to keep connection alive"""
        pong_response = WebSocketResponse(
            type="pong",
            content="pong",
            session_id=session_id
        )
        await self._send_to_connection(session_id, pong_response.model_dump())
    
    async def _send_typing_indicator(self, session_id: str, is_typing: bool):
        """Send typing indicator"""
        typing_response = WebSocketResponse(
            type="typing",
            content="typing" if is_typing else "stop_typing",
            session_id=session_id
        )
        await self._send_to_connection(session_id, typing_response.model_dump())
    
    async def _send_to_connection(self, session_id: str, message: dict):
        """Send message to specific WebSocket connection"""
        if session_id in self.active_connections:
            try:
                websocket = self.active_connections[session_id]
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send message to {session_id}: {str(e)}")
                # Remove dead connection
                self.disconnect(session_id)
    
    async def broadcast_to_student(self, student_id: str, message: dict):
        """Broadcast message to all sessions of a student"""
        sessions_to_notify = [
            session_id for session_id, info in self.connection_info.items()
            if info.student_id == student_id
        ]
        
        for session_id in sessions_to_notify:
            await self._send_to_connection(session_id, message)
    
    async def _save_message_to_session(self, session_id: str, message: ChatMessage):
        """Save message to chat session in database"""
        try:
            # Add message to session
            message_data = message.model_dump(by_alias=True)
            
            await self.db.chat_sessions.update_one(
                {"session_id": session_id},
                {
                    "$push": {"messages": message_data},
                    "$inc": {"summary.total_messages": 1},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
        except Exception as e:
            logger.error(f"Failed to save message to session: {str(e)}")
    
    async def _end_chat_session(self, session_id: str):
        """End chat session and update database"""
        try:
            await self.db.chat_sessions.update_one(
                {"session_id": session_id},
                {
                    "$set": {
                        "ended_at": datetime.utcnow(),
                        "summary.resolved": True  # Could be determined by analysis
                    }
                }
            )
        except Exception as e:
            logger.error(f"Failed to end chat session: {str(e)}")
    
    async def get_active_sessions_count(self) -> int:
        """Get number of active WebSocket connections"""
        return len(self.active_connections)
    
    async def get_student_session_history(self, student_id: str, limit: int = 10) -> List[Dict]:
        """Get chat session history for a student"""
        try:
            sessions_cursor = self.db.chat_sessions.find({
                "student_id": student_id
            }).sort("created_at", -1).limit(limit)
            
            sessions = []
            async for session in sessions_cursor:
                # Convert ObjectIds to strings
                session["_id"] = str(session["_id"])
                session["student_id"] = str(session["student_id"])
                
                # Convert message ObjectIds
                for message in session.get("messages", []):
                    if "_id" in message:
                        message["_id"] = str(message["_id"])
                
                sessions.append(session)
            
            return sessions
            
        except Exception as e:
            logger.error(f"Failed to get session history: {str(e)}")
            return []
    
    async def cleanup_inactive_sessions(self, timeout_minutes: int = 30):
        """Clean up inactive WebSocket connections"""
        current_time = datetime.utcnow()
        timeout_delta = timedelta(minutes=timeout_minutes)
        
        inactive_sessions = []
        
        for session_id, info in self.connection_info.items():
            if current_time - info.last_activity > timeout_delta:
                inactive_sessions.append(session_id)
        
        for session_id in inactive_sessions:
            logger.info(f"Cleaning up inactive session: {session_id}")
            self.disconnect(session_id)
    
    async def send_system_notification(self, student_id: str, message: str):
        """Send system notification to student's active sessions"""
        notification = WebSocketResponse(
            type="system",
            content=message,
            session_id="system"
        )
        
        await self.broadcast_to_student(student_id, notification.model_dump())


# Global WebSocket manager instance
websocket_manager: Optional[WebSocketManager] = None

def get_websocket_manager(db: AsyncIOMotorDatabase) -> WebSocketManager:
    """Get or create WebSocket manager instance"""
    global websocket_manager
    if websocket_manager is None:
        websocket_manager = WebSocketManager(db)
    return websocket_manager