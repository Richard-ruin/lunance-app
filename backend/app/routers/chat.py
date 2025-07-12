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
from ..utils.timezone_utils import IndonesiaDatetime
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
        
        # Send connection success message dengan timezone Indonesia
        await self.send_personal_message({
            "type": WSMessageType.SUCCESS,
            "data": {"message": "Connected to Luna chat"},
            "timestamp": IndonesiaDatetime.now().isoformat(),
            "timezone": "WIB"
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
    """WebSocket endpoint untuk real-time chat dengan timezone Indonesia"""
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
                        "timestamp": IndonesiaDatetime.now().isoformat()
                    }, user_id)
                    continue
                
                # Send typing indicator
                await manager.send_personal_message({
                    "type": WSMessageType.TYPING_START,
                    "data": {"sender": "luna"},
                    "timestamp": IndonesiaDatetime.now().isoformat()
                }, user_id)
                
                # Process message
                result = await chat_service.send_message(user_id, conversation_id, user_message)
                
                # Stop typing indicator
                await manager.send_personal_message({
                    "type": WSMessageType.TYPING_STOP,
                    "data": {"sender": "luna"},
                    "timestamp": IndonesiaDatetime.now().isoformat()
                }, user_id)
                
                # Convert timestamps ke Indonesia timezone untuk response
                user_timestamp_wib = IndonesiaDatetime.from_utc(result["user_message"].timestamp)
                luna_timestamp_wib = IndonesiaDatetime.from_utc(result["luna_response"].timestamp)
                
                # Send user message back (for confirmation)
                await manager.send_personal_message({
                    "type": WSMessageType.CHAT_MESSAGE,
                    "data": {
                        "message": {
                            "id": result["user_message"].id,
                            "conversation_id": conversation_id,
                            "sender_type": "user",
                            "content": result["user_message"].content,
                            "timestamp": user_timestamp_wib.isoformat(),
                            "status": "delivered",
                            "timezone": "WIB"
                        }
                    },
                    "timestamp": IndonesiaDatetime.now().isoformat()
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
                            "timestamp": luna_timestamp_wib.isoformat(),
                            "status": "delivered",
                            "timezone": "WIB"
                        }
                    },
                    "timestamp": IndonesiaDatetime.now().isoformat()
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
            "timestamp": IndonesiaDatetime.now().isoformat()
        }, user_id)
        manager.disconnect(user_id)

@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    request: CreateConversationRequest = None,
    current_user: User = Depends(get_current_user)
):
    """Membuat percakapan baru dan auto-cleanup conversations kosong"""
    try:
        # Auto-cleanup empty conversations sebelum membuat yang baru
        cleanup_stats = await chat_service.auto_delete_empty_conversations(current_user.id)
        print(f"🧹 Cleaned up {cleanup_stats} empty conversations before creating new one")
        
        conversation = await chat_service.create_conversation(current_user.id)
        
        # Convert timestamps ke Indonesia timezone untuk response
        created_time_wib = IndonesiaDatetime.from_utc(conversation.created_at)
        updated_time_wib = IndonesiaDatetime.from_utc(conversation.updated_at)
        
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
                        "created_at": created_time_wib.isoformat(),
                        "updated_at": updated_time_wib.isoformat(),
                        "timezone": "WIB"
                    },
                    "cleanup_stats": cleanup_stats
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal membuat percakapan: {str(e)}")

@router.get("/conversations")
async def get_conversations(
    limit: int = 20,
    auto_cleanup: bool = True,
    current_user: User = Depends(get_current_user)
):
    """Mengambil daftar percakapan user dengan timezone Indonesia yang benar"""
    try:
        # Auto-cleanup jika diminta
        cleanup_stats = {}
        if auto_cleanup:
            cleanup_stats = await chat_service.auto_delete_empty_conversations(current_user.id)
        
        conversations = await chat_service.get_user_conversations(current_user.id, limit)
        
        conversation_list = []
        for conv in conversations:
            # Convert all timestamps ke Indonesia timezone
            created_time_wib = IndonesiaDatetime.from_utc(conv.created_at)
            updated_time_wib = IndonesiaDatetime.from_utc(conv.updated_at)
            last_message_time_wib = None
            
            if conv.last_message_at:
                last_message_time_wib = IndonesiaDatetime.from_utc(conv.last_message_at)
            
            conversation_list.append({
                "id": conv.id,
                "title": conv.title or "Chat Baru",
                "last_message": conv.last_message,
                "last_message_at": last_message_time_wib.isoformat() if last_message_time_wib else None,
                "message_count": conv.message_count,
                "created_at": created_time_wib.isoformat(),
                "updated_at": updated_time_wib.isoformat(),
                "timezone": "WIB",
                "relative_time": IndonesiaDatetime.format_relative(conv.last_message_at or conv.created_at)
            })
        
        response_data = {
            "success": True,
            "message": "Daftar percakapan berhasil diambil",
            "data": {
                "conversations": conversation_list,
                "total": len(conversation_list),
                "timezone": "Asia/Jakarta (WIB/GMT+7)",
                "current_time_wib": IndonesiaDatetime.format(IndonesiaDatetime.now())
            }
        }
        
        if cleanup_stats:
            response_data["data"]["cleanup_stats"] = cleanup_stats
        
        return JSONResponse(status_code=200, content=response_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil percakapan: {str(e)}")

@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: str,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """Mengambil pesan dalam percakapan dengan timezone Indonesia yang benar"""
    try:
        # Verify conversation belongs to user
        conversation = await chat_service.get_conversation_by_id(conversation_id)
        if not conversation or conversation.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Percakapan tidak ditemukan")
        
        messages = await chat_service.get_conversation_messages(conversation_id, limit)
        
        message_list = []
        for msg in messages:
            # Convert timestamp ke Indonesia timezone
            timestamp_wib = IndonesiaDatetime.from_utc(msg.timestamp)
            
            message_list.append({
                "id": msg.id,
                "conversation_id": msg.conversation_id,
                "sender_type": msg.sender_type,
                "content": msg.content,
                "message_type": msg.message_type,
                "status": msg.status,
                "timestamp": timestamp_wib.isoformat(),
                "timezone": "WIB",
                "formatted_time": IndonesiaDatetime.format_time_only(msg.timestamp),
                "relative_time": IndonesiaDatetime.format_relative(msg.timestamp)
            })
        
        # Convert conversation timestamps
        created_time_wib = IndonesiaDatetime.from_utc(conversation.created_at)
        updated_time_wib = IndonesiaDatetime.from_utc(conversation.updated_at)
        
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
                        "message_count": conversation.message_count,
                        "created_at": created_time_wib.isoformat(),
                        "updated_at": updated_time_wib.isoformat(),
                        "timezone": "WIB"
                    },
                    "timezone": "Asia/Jakarta (WIB/GMT+7)",
                    "current_time_wib": IndonesiaDatetime.format(IndonesiaDatetime.now())
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
    """Mengirim pesan melalui HTTP dengan timezone Indonesia yang benar"""
    try:
        # Verify conversation belongs to user
        conversation = await chat_service.get_conversation_by_id(conversation_id)
        if not conversation or conversation.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Percakapan tidak ditemukan")
        
        result = await chat_service.send_message(current_user.id, conversation_id, request.message)
        
        # Convert timestamps ke Indonesia timezone
        user_timestamp_wib = IndonesiaDatetime.from_utc(result["user_message"].timestamp)
        luna_timestamp_wib = IndonesiaDatetime.from_utc(result["luna_response"].timestamp)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Pesan berhasil dikirim",
                "data": {
                    "user_message": {
                        "id": result["user_message"].id,
                        "content": result["user_message"].content,
                        "timestamp": user_timestamp_wib.isoformat(),
                        "sender_type": "user",
                        "timezone": "WIB",
                        "formatted_time": IndonesiaDatetime.format_time_only(result["user_message"].timestamp)
                    },
                    "luna_response": {
                        "id": result["luna_response"].id,
                        "content": result["luna_response"].content,
                        "timestamp": luna_timestamp_wib.isoformat(),
                        "sender_type": "luna",
                        "timezone": "WIB",
                        "formatted_time": IndonesiaDatetime.format_time_only(result["luna_response"].timestamp)
                    },
                    "current_time_wib": IndonesiaDatetime.format(IndonesiaDatetime.now())
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
                "data": {
                    "deleted_at": IndonesiaDatetime.format(IndonesiaDatetime.now()),
                    "timezone": "WIB"
                }
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
            created_time_wib = IndonesiaDatetime.from_utc(conv.created_at)
            last_message_time_wib = None
            
            if conv.last_message_at:
                last_message_time_wib = IndonesiaDatetime.from_utc(conv.last_message_at)
            
            conversation_list.append({
                "id": conv.id,
                "title": conv.title or "Chat Baru",
                "last_message": conv.last_message,
                "last_message_at": last_message_time_wib.isoformat() if last_message_time_wib else None,
                "message_count": conv.message_count,
                "created_at": created_time_wib.isoformat(),
                "timezone": "WIB",
                "relative_time": IndonesiaDatetime.format_relative(conv.last_message_at or conv.created_at)
            })
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": f"Ditemukan {len(conversation_list)} percakapan",
                "data": {
                    "conversations": conversation_list,
                    "query": q,
                    "total": len(conversation_list),
                    "timezone": "Asia/Jakarta (WIB/GMT+7)",
                    "search_time": IndonesiaDatetime.format(IndonesiaDatetime.now())
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mencari percakapan: {str(e)}")

@router.post("/cleanup")
async def cleanup_conversations(
    current_user: User = Depends(get_current_user)
):
    """Manual cleanup untuk conversations user"""
    try:
        cleanup_stats = await chat_service.cleanup_user_conversations(current_user.id)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Cleanup berhasil dilakukan",
                "data": {
                    "cleanup_stats": cleanup_stats,
                    "cleanup_time": IndonesiaDatetime.format(IndonesiaDatetime.now()),
                    "timezone": "WIB"
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal melakukan cleanup: {str(e)}")

@router.get("/statistics")
async def get_chat_statistics(
    current_user: User = Depends(get_current_user)
):
    """Mendapatkan statistik chat dengan timezone Indonesia"""
    try:
        stats = await chat_service.get_chat_statistics(current_user.id)
        
        # Convert last_activity timestamp if exists
        if stats.get("last_activity"):
            last_activity_wib = IndonesiaDatetime.from_utc(stats["last_activity"])
            stats["last_activity_wib"] = last_activity_wib.isoformat()
            stats["last_activity_formatted"] = IndonesiaDatetime.format(last_activity_wib)
            stats["last_activity_relative"] = IndonesiaDatetime.format_relative(stats["last_activity"])
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Statistik chat berhasil diambil",
                "data": stats
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil statistik: {str(e)}")