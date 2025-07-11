from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import json
import asyncio
from datetime import datetime

from ..services.auth_dependency import get_current_user
from ..services.chat_service import ChatService
from ..models.user import User
from ..models.chat import WSMessage, WSMessageType
from ..schemas.chat_schemas import (
    ChatMessageRequest,
    ChatMessageResponse,
    ConversationResponse,
    CreateConversationRequest
)

router = APIRouter(prefix="/chat", tags=["Chat"])

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        
        # Send connection success message
        await self.send_personal_message({
            "type": WSMessageType.SUCCESS,
            "data": {"message": "Connected to Luna chat"},
            "timestamp": datetime.utcnow().isoformat()
        }, user_id)
    
    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
    
    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(json.dumps(message))
            except:
                # Connection closed, remove from active connections
                self.disconnect(user_id)
    
    async def broadcast_to_user(self, message: dict, user_id: str):
        await self.send_personal_message(message, user_id)

manager = ConnectionManager()
chat_service = ChatService()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint untuk real-time chat"""
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            message_type = message_data.get("type")
            content = message_data.get("data", {})
            
            if message_type == WSMessageType.CHAT_MESSAGE:
                # Handle chat message
                conversation_id = content.get("conversation_id")
                user_message = content.get("message")
                
                if not conversation_id or not user_message:
                    await manager.send_personal_message({
                        "type": WSMessageType.ERROR,
                        "data": {"message": "Missing conversation_id or message"},
                        "timestamp": datetime.utcnow().isoformat()
                    }, user_id)
                    continue
                
                # Send typing indicator
                await manager.send_personal_message({
                    "type": WSMessageType.TYPING_START,
                    "data": {"sender": "luna"},
                    "timestamp": datetime.utcnow().isoformat()
                }, user_id)
                
                # Process message
                result = await chat_service.send_message(user_id, conversation_id, user_message)
                
                # Stop typing indicator
                await manager.send_personal_message({
                    "type": WSMessageType.TYPING_STOP,
                    "data": {"sender": "luna"},
                    "timestamp": datetime.utcnow().isoformat()
                }, user_id)
                
                # Send user message back (for confirmation)
                await manager.send_personal_message({
                    "type": WSMessageType.CHAT_MESSAGE,
                    "data": {
                        "message": {
                            "id": result["user_message"].id,
                            "conversation_id": conversation_id,
                            "sender_type": "user",
                            "content": result["user_message"].content,
                            "timestamp": result["user_message"].timestamp.isoformat(),
                            "status": "delivered"
                        }
                    },
                    "timestamp": datetime.utcnow().isoformat()
                }, user_id)
                
                # Send Luna response
                await manager.send_personal_message({
                    "type": WSMessageType.CHAT_MESSAGE,
                    "data": {
                        "message": {
                            "id": result["luna_response"].id,
                            "conversation_id": conversation_id,
                            "sender_type": "luna",
                            "content": result["luna_response"].content,
                            "timestamp": result["luna_response"].timestamp.isoformat(),
                            "status": "delivered"
                        }
                    },
                    "timestamp": datetime.utcnow().isoformat()
                }, user_id)
                
            elif message_type == WSMessageType.TYPING_START:
                # Handle typing indicator (could be sent to other users in group chat)
                pass
            
            elif message_type == WSMessageType.TYPING_STOP:
                # Handle stop typing indicator
                pass
    
    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        await manager.send_personal_message({
            "type": WSMessageType.ERROR,
            "data": {"message": f"Error: {str(e)}"},
            "timestamp": datetime.utcnow().isoformat()
        }, user_id)
        manager.disconnect(user_id)

@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    request: CreateConversationRequest = None,
    current_user: User = Depends(get_current_user)
):
    """Membuat percakapan baru"""
    try:
        conversation = await chat_service.create_conversation(current_user.id)
        
        return JSONResponse(
            status_code=201,
            content={
                "success": True,
                "message": "Percakapan berhasil dibuat",
                "data": {
                    "conversation": {
                        "id": conversation.id,
                        "user_id": conversation.user_id,
                        "title": conversation.title,
                        "status": conversation.status,
                        "message_count": conversation.message_count,
                        "created_at": conversation.created_at.isoformat(),
                        "updated_at": conversation.updated_at.isoformat()
                    }
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal membuat percakapan: {str(e)}")

@router.get("/conversations")
async def get_conversations(
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    """Mengambil daftar percakapan user"""
    try:
        conversations = await chat_service.get_user_conversations(current_user.id, limit)
        
        conversation_list = []
        for conv in conversations:
            conversation_list.append({
                "id": conv.id,
                "title": conv.title or "New Chat",
                "last_message": conv.last_message,
                "last_message_at": conv.last_message_at.isoformat() if conv.last_message_at else None,
                "message_count": conv.message_count,
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat()
            })
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Daftar percakapan berhasil diambil",
                "data": {
                    "conversations": conversation_list,
                    "total": len(conversation_list)
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil percakapan: {str(e)}")

@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: str,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """Mengambil pesan dalam percakapan"""
    try:
        # Verify conversation belongs to user
        conversation = await chat_service.get_conversation_by_id(conversation_id)
        if not conversation or conversation.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Percakapan tidak ditemukan")
        
        messages = await chat_service.get_conversation_messages(conversation_id, limit)
        
        message_list = []
        for msg in messages:
            message_list.append({
                "id": msg.id,
                "conversation_id": msg.conversation_id,
                "sender_type": msg.sender_type,
                "content": msg.content,
                "message_type": msg.message_type,
                "status": msg.status,
                "timestamp": msg.timestamp.isoformat()
            })
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Pesan berhasil diambil",
                "data": {
                    "messages": message_list,
                    "conversation": {
                        "id": conversation.id,
                        "title": conversation.title,
                        "message_count": conversation.message_count
                    }
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil pesan: {str(e)}")

@router.post("/conversations/{conversation_id}/messages")
async def send_message_http(
    conversation_id: str,
    request: ChatMessageRequest,
    current_user: User = Depends(get_current_user)
):
    """Mengirim pesan melalui HTTP (alternative to WebSocket)"""
    try:
        # Verify conversation belongs to user
        conversation = await chat_service.get_conversation_by_id(conversation_id)
        if not conversation or conversation.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Percakapan tidak ditemukan")
        
        result = await chat_service.send_message(current_user.id, conversation_id, request.message)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Pesan berhasil dikirim",
                "data": {
                    "user_message": {
                        "id": result["user_message"].id,
                        "content": result["user_message"].content,
                        "timestamp": result["user_message"].timestamp.isoformat(),
                        "sender_type": "user"
                    },
                    "luna_response": {
                        "id": result["luna_response"].id,
                        "content": result["luna_response"].content,
                        "timestamp": result["luna_response"].timestamp.isoformat(),
                        "sender_type": "luna"
                    }
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengirim pesan: {str(e)}")

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user)
):
    """Menghapus percakapan"""
    try:
        success = await chat_service.delete_conversation(conversation_id, current_user.id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Percakapan tidak ditemukan")
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Percakapan berhasil dihapus",
                "data": None
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal menghapus percakapan: {str(e)}")

@router.get("/conversations/search")
async def search_conversations(
    q: str,
    current_user: User = Depends(get_current_user)
):
    """Mencari percakapan"""
    try:
        conversations = await chat_service.search_conversations(current_user.id, q)
        
        conversation_list = []
        for conv in conversations:
            conversation_list.append({
                "id": conv.id,
                "title": conv.title or "New Chat",
                "last_message": conv.last_message,
                "last_message_at": conv.last_message_at.isoformat() if conv.last_message_at else None,
                "message_count": conv.message_count,
                "created_at": conv.created_at.isoformat()
            })
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": f"Ditemukan {len(conversation_list)} percakapan",
                "data": {
                    "conversations": conversation_list,
                    "query": q,
                    "total": len(conversation_list)
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mencari percakapan: {str(e)}")