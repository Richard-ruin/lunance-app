# app/routers/chat.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import logging
from bson import ObjectId

from ..middleware.auth_middleware import get_current_verified_user
from ..models.chat_session import (
    ChatSession, ChatSessionCreate, ChatSessionResponse, ChatSessionUpdate
)
from ..models.chat_message import (
    ChatMessage, ChatMessageCreate, ChatMessageResponse, ChatResponse
)
from ..database import get_database
from ..services.luna_ai import luna_ai
from ..services.indonesian_nlp import nlp_service
from ..utils.exceptions import CustomHTTPException

router = APIRouter(prefix="/chat", tags=["AI Chatbot Luna"])
logger = logging.getLogger(__name__)

@router.post("/message", response_model=ChatResponse)
async def send_message(
    message_data: ChatMessageCreate,
    current_user: Dict[str, Any] = Depends(get_current_verified_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Send message to Luna AI and get response"""
    try:
        db = await get_database()
        user_id = current_user["id"]
        
        # Validate session exists
        session = await db.chat_sessions.find_one({
            "session_id": message_data.session_id,
            "user_id": ObjectId(user_id)
        })
        
        if not session:
            raise CustomHTTPException(
                status_code=404,
                detail="Chat session not found",
                error_code="SESSION_NOT_FOUND"
            )
        
        # Store user message
        user_message = ChatMessage(
            session_id=message_data.session_id,
            user_id=ObjectId(user_id),
            message_type="user",
            content=message_data.content
        )
        
        # Extract entities and sentiment
        entities = await nlp_service.extract_entities(message_data.content)
        sentiment, sentiment_score = await nlp_service.analyze_sentiment(message_data.content)
        
        user_message.entities = entities
        user_message.sentiment = sentiment
        user_message.sentiment_score = sentiment_score
        
        user_message_doc = user_message.model_dump()
        user_message_doc["created_at"] = datetime.utcnow()
        user_message_doc["updated_at"] = datetime.utcnow()
        
        await db.chat_messages.insert_one(user_message_doc)
        
        # Process with Luna AI
        ai_response = await luna_ai.process_message(
            user_id=user_id,
            session_id=message_data.session_id,
            message=message_data.content,
            context=session.get("context", {})
        )
        
        # Store AI response message
        ai_message = ChatMessage(
            session_id=message_data.session_id,
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
        
        # Update session context and last message time
        await db.chat_sessions.update_one(
            {"session_id": message_data.session_id},
            {
                "$set": {
                    "context": ai_response.context,
                    "last_message_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return ai_response
        
    except CustomHTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise CustomHTTPException(
            status_code=500,
            detail="Failed to process message",
            error_code="MESSAGE_PROCESSING_ERROR"
        )

@router.get("/sessions", response_model=List[ChatSessionResponse])
async def get_chat_sessions(
    current_user: Dict[str, Any] = Depends(get_current_verified_user),
    limit: int = 20,
    skip: int = 0
):
    """Get user's chat sessions"""
    try:
        db = await get_database()
        user_id = current_user["id"]
        
        # Get sessions with message counts
        pipeline = [
            {"$match": {"user_id": ObjectId(user_id)}},
            {"$sort": {"last_message_at": -1, "created_at": -1}},
            {"$skip": skip},
            {"$limit": limit},
            {
                "$lookup": {
                    "from": "chat_messages",
                    "localField": "session_id",
                    "foreignField": "session_id",
                    "as": "messages"
                }
            },
            {
                "$addFields": {
                    "message_count": {"$size": "$messages"}
                }
            },
            {"$unset": "messages"}
        ]
        
        sessions = await db.chat_sessions.aggregate(pipeline).to_list(None)
        
        return [
            ChatSessionResponse(
                _id=str(session["_id"]),
                user_id=str(session["user_id"]),
                session_id=session["session_id"],
                title=session["title"],
                context=session["context"],
                is_active=session["is_active"],
                created_at=session["created_at"],
                updated_at=session["updated_at"],
                last_message_at=session.get("last_message_at"),
                message_count=session.get("message_count", 0)
            )
            for session in sessions
        ]
        
    except Exception as e:
        logger.error(f"Error getting chat sessions: {e}")
        raise CustomHTTPException(
            status_code=500,
            detail="Failed to get chat sessions",
            error_code="GET_SESSIONS_ERROR"
        )

@router.post("/sessions", response_model=ChatSessionResponse)
async def create_chat_session(
    session_data: ChatSessionCreate,
    current_user: Dict[str, Any] = Depends(get_current_verified_user)
):
    """Create new chat session"""
    try:
        db = await get_database()
        user_id = current_user["id"]
        
        session = ChatSession(
            user_id=ObjectId(user_id),
            session_id=str(uuid.uuid4()),
            title=session_data.title or f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            context=session_data.context or {}
        )
        
        session_doc = session.model_dump()
        session_doc["created_at"] = datetime.utcnow()
        session_doc["updated_at"] = datetime.utcnow()
        
        result = await db.chat_sessions.insert_one(session_doc)
        session_doc["_id"] = result.inserted_id
        
        return ChatSessionResponse(
            _id=str(session_doc["_id"]),
            user_id=str(session_doc["user_id"]),
            session_id=session_doc["session_id"],
            title=session_doc["title"],
            context=session_doc["context"],
            is_active=session_doc["is_active"],
            created_at=session_doc["created_at"],
            updated_at=session_doc["updated_at"],
            last_message_at=session_doc.get("last_message_at"),
            message_count=0
        )
        
    except Exception as e:
        logger.error(f"Error creating chat session: {e}")
        raise CustomHTTPException(
            status_code=500,
            detail="Failed to create chat session",
            error_code="CREATE_SESSION_ERROR"
        )

@router.get("/sessions/{session_id}", response_model=Dict[str, Any])
async def get_chat_session(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_verified_user),
    include_messages: bool = True,
    message_limit: int = 50
):
    """Get specific chat session with messages"""
    try:
        db = await get_database()
        user_id = current_user["id"]
        
        # Get session
        session = await db.chat_sessions.find_one({
            "session_id": session_id,
            "user_id": ObjectId(user_id)
        })
        
        if not session:
            raise CustomHTTPException(
                status_code=404,
                detail="Chat session not found",
                error_code="SESSION_NOT_FOUND"
            )
        
        response_data = {
            "session": ChatSessionResponse(
                _id=str(session["_id"]),
                user_id=str(session["user_id"]),
                session_id=session["session_id"],
                title=session["title"],
                context=session["context"],
                is_active=session["is_active"],
                created_at=session["created_at"],
                updated_at=session["updated_at"],
                last_message_at=session.get("last_message_at")
            )
        }
        
        # Get messages if requested
        if include_messages:
            messages = await db.chat_messages.find({
                "session_id": session_id
            }).sort("created_at", 1).limit(message_limit).to_list(None)
            
            response_data["messages"] = [
                ChatMessageResponse(
                    _id=str(msg["_id"]),
                    session_id=msg["session_id"],
                    user_id=str(msg["user_id"]),
                    message_type=msg["message_type"],
                    content=msg["content"],
                    intent=msg.get("intent"),
                    entities=msg.get("entities", []),
                    context=msg.get("context", {}),
                    response_data=msg.get("response_data", {}),
                    confidence_score=msg.get("confidence_score", 0.0),
                    processing_time=msg.get("processing_time", 0.0),
                    sentiment=msg.get("sentiment"),
                    sentiment_score=msg.get("sentiment_score", 0.0),
                    created_at=msg["created_at"]
                )
                for msg in messages
            ]
        
        return response_data
        
    except CustomHTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chat session: {e}")
        raise CustomHTTPException(
            status_code=500,
            detail="Failed to get chat session",
            error_code="GET_SESSION_ERROR"
        )

@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_verified_user)
):
    """Delete chat session and all its messages"""
    try:
        db = await get_database()
        user_id = current_user["id"]
        
        # Verify session ownership
        session = await db.chat_sessions.find_one({
            "session_id": session_id,
            "user_id": ObjectId(user_id)
        })
        
        if not session:
            raise CustomHTTPException(
                status_code=404,
                detail="Chat session not found",
                error_code="SESSION_NOT_FOUND"
            )
        
        # Delete all messages in the session
        await db.chat_messages.delete_many({"session_id": session_id})
        
        # Delete the session
        await db.chat_sessions.delete_one({"session_id": session_id})
        
        return {"message": "Chat session deleted successfully"}
        
    except CustomHTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting chat session: {e}")
        raise CustomHTTPException(
            status_code=500,
            detail="Failed to delete chat session",
            error_code="DELETE_SESSION_ERROR"
        )

@router.post("/sessions/{session_id}/clear")
async def clear_session_context(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_verified_user)
):
    """Clear session context (reset conversation memory)"""
    try:
        db = await get_database()
        user_id = current_user["id"]
        
        # Verify session ownership
        session = await db.chat_sessions.find_one({
            "session_id": session_id,
            "user_id": ObjectId(user_id)
        })
        
        if not session:
            raise CustomHTTPException(
                status_code=404,
                detail="Chat session not found",
                error_code="SESSION_NOT_FOUND"
            )
        
        # Clear context
        await db.chat_sessions.update_one(
            {"session_id": session_id},
            {
                "$set": {
                    "context": {},
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {"message": "Session context cleared successfully"}
        
    except CustomHTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing session context: {e}")
        raise CustomHTTPException(
            status_code=500,
            detail="Failed to clear session context",
            error_code="CLEAR_CONTEXT_ERROR"
        )