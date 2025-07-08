# app/api/v1/endpoints/ai_chat.py
"""AI Chat endpoints for Luna chatbot."""

from fastapi import APIRouter, Depends, HTTPException, status, Query, WebSocket, WebSocketDisconnect
from typing import Optional, List, Dict, Any
import logging
import json
from datetime import datetime

from app.models.ai_chat import (
    ChatMessageCreate, ChatMessageResponse, ChatSessionCreate, ChatSessionResponse,
    ChatHistoryResponse, AIInsight, ChatAnalyticsRequest, ChatAnalyticsResponse,
    WebSocketMessage, MessageRole, MessageType
)
from app.models.common import (
    PaginatedResponse, PaginationParams, SuccessResponse
)
from app.services.chatbot_service import (
    ChatbotService, ChatbotServiceError, chatbot_service
)
from app.middleware.auth import (
    get_current_verified_user, rate_limit_dependency
)
from app.models.user import UserInDB

logger = logging.getLogger(__name__)

router = APIRouter()


# WebSocket connection manager
class ConnectionManager:
    """WebSocket connection manager for real-time chat."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept WebSocket connection."""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"WebSocket connected for user: {user_id}")
    
    def disconnect(self, user_id: str):
        """Remove WebSocket connection."""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            logger.info(f"WebSocket disconnected for user: {user_id}")
    
    async def send_personal_message(self, message: str, user_id: str):
        """Send message to specific user."""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(message)
            except Exception as e:
                logger.error(f"Error sending message to {user_id}: {e}")
                self.disconnect(user_id)
    
    async def send_json_message(self, data: Dict[str, Any], user_id: str):
        """Send JSON message to specific user."""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(data)
            except Exception as e:
                logger.error(f"Error sending JSON message to {user_id}: {e}")
                self.disconnect(user_id)


# Global connection manager
manager = ConnectionManager()


# Chat session management
@router.post("/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_chat_session(
    session_data: ChatSessionCreate,
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """Create new chat session."""
    try:
        session = await chatbot_service.create_chat_session(
            user_id=str(current_user.id),
            session_data=session_data
        )
        
        return session
        
    except ChatbotServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating chat session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create chat session"
        )


@router.get("/sessions", response_model=PaginatedResponse[ChatSessionResponse])
async def list_chat_sessions(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user: UserInDB = Depends(get_current_verified_user),
    _: None = Depends(rate_limit_dependency)
):
    """List user's chat sessions."""
    try:
        pagination = PaginationParams(
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        result = await chatbot_service.list_chat_sessions(
            user_id=str(current_user.id),
            pagination=pagination,
            is_active=is_active
        )
        
        return result
        
    except ChatbotServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error listing chat sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list chat sessions"
        )


@router.get("/sessions/{session_id}/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Items per page"),
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """Get chat history for a session."""
    try:
        pagination = PaginationParams(
            page=page,
            per_page=per_page,
            sort_by="created_at",
            sort_order="asc"
        )
        
        history = await chatbot_service.get_chat_history(
            user_id=str(current_user.id),
            session_id=session_id,
            pagination=pagination
        )
        
        return history
        
    except ChatbotServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get chat history"
        )


@router.delete("/sessions/{session_id}", response_model=SuccessResponse)
async def delete_chat_session(
    session_id: str,
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """Delete chat session."""
    try:
        success = await chatbot_service.delete_chat_session(
            user_id=str(current_user.id),
            session_id=session_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        return SuccessResponse(
            message="Chat session deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting chat session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete chat session"
        )


@router.delete("/history", response_model=SuccessResponse)
async def clear_chat_history(
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """Clear all chat history for user."""
    try:
        success = await chatbot_service.clear_user_chat_history(
            user_id=str(current_user.id)
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to clear chat history"
            )
        
        return SuccessResponse(
            message="Chat history cleared successfully"
        )
        
    except Exception as e:
        logger.error(f"Error clearing chat history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear chat history"
        )


# Message handling
@router.post("/sessions/{session_id}/messages", response_model=ChatMessageResponse)
async def send_message(
    session_id: str,
    message_data: ChatMessageCreate,
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """Send message to AI chatbot."""
    try:
        response = await chatbot_service.process_message(
            user_id=str(current_user.id),
            session_id=session_id,
            message_data=message_data
        )
        
        return response
        
    except ChatbotServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message"
        )


# Insights and analytics
@router.get("/insights", response_model=List[AIInsight])
async def get_proactive_insights(
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """Get proactive financial insights."""
    try:
        insights = await chatbot_service.generate_proactive_insights(
            user_id=str(current_user.id)
        )
        
        return insights
        
    except Exception as e:
        logger.error(f"Error getting insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get insights"
        )


@router.post("/analytics", response_model=ChatAnalyticsResponse)
async def get_chat_analytics(
    analytics_request: ChatAnalyticsRequest,
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """Get chat analytics and usage statistics."""
    try:
        # This is a placeholder for chat analytics
        # In a real implementation, you would analyze chat patterns
        
        return ChatAnalyticsResponse(
            total_messages=0,
            total_sessions=0,
            avg_messages_per_session=0.0,
            avg_session_duration=0.0,
            most_common_topics=[],
            user_engagement_score=0.0,
            ai_response_accuracy=0.0
        )
        
    except Exception as e:
        logger.error(f"Error getting chat analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get chat analytics"
        )


# WebSocket endpoint for real-time chat
@router.websocket("/ws/{session_id}")
async def websocket_chat_endpoint(
    websocket: WebSocket,
    session_id: str,
    token: str = Query(..., description="JWT token for authentication")
):
    """WebSocket endpoint for real-time chat."""
    try:
        # Authenticate user (simplified - in production, verify JWT token properly)
        # For now, we'll assume the token is valid and extract user_id
        user_id = "user_from_token"  # This should be extracted from JWT
        
        # Connect to WebSocket
        await manager.connect(websocket, user_id)
        
        # Send welcome message
        welcome_message = WebSocketMessage(
            type="system",
            data={
                "message": "Connected to Luna AI Assistant",
                "session_id": session_id
            }
        )
        await manager.send_json_message(welcome_message.model_dump(), user_id)
        
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_json()
                
                # Validate message format
                if "content" not in data:
                    await manager.send_json_message({
                        "type": "error",
                        "data": {"message": "Invalid message format"}
                    }, user_id)
                    continue
                
                # Create message object
                message_data = ChatMessageCreate(
                    content=data["content"],
                    role=MessageRole.USER,
                    message_type=MessageType(data.get("message_type", "text")),
                    context_data=data.get("context_data")
                )
                
                # Process message through chatbot service
                try:
                    response = await chatbot_service.process_message(
                        user_id=user_id,
                        session_id=session_id,
                        message_data=message_data
                    )
                    
                    # Send AI response back
                    response_message = WebSocketMessage(
                        type="message",
                        data={
                            "message_id": response.id,
                            "content": response.content,
                            "role": response.role.value,
                            "message_type": response.message_type.value,
                            "confidence_score": response.confidence_score,
                            "processing_time": response.processing_time,
                            "metadata": response.metadata
                        }
                    )
                    
                    await manager.send_json_message(response_message.model_dump(), user_id)
                    
                except ChatbotServiceError as e:
                    error_message = WebSocketMessage(
                        type="error",
                        data={"message": str(e)}
                    )
                    await manager.send_json_message(error_message.model_dump(), user_id)
                
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for user: {user_id}")
        except Exception as e:
            logger.error(f"WebSocket error for user {user_id}: {e}")
            error_message = WebSocketMessage(
                type="error",
                data={"message": "Internal server error"}
            )
            await manager.send_json_message(error_message.model_dump(), user_id)
        
        finally:
            manager.disconnect(user_id)
            
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        await websocket.close(code=1000)


# Health check for AI services
@router.get("/health", response_model=Dict[str, Any])
async def ai_health_check():
    """Check AI services health status."""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "chatbot_service": "available",
                "websocket_connections": len(manager.active_connections),
                "ai_models": {
                    "indonesian_nlp": "available",
                    "financial_analysis": "available"
                }
            }
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"AI health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }


# Development and testing endpoints
@router.post("/test/message", response_model=ChatMessageResponse)
async def test_ai_response(
    message_content: str = Query(..., description="Test message content"),
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """Test AI response without creating a session (development only)."""
    try:
        # Create temporary session for testing
        temp_session = await chatbot_service.create_chat_session(
            user_id=str(current_user.id),
            session_data=ChatSessionCreate(session_name="Test Session")
        )
        
        # Process test message
        test_message = ChatMessageCreate(
            content=message_content,
            role=MessageRole.USER,
            message_type=MessageType.TEXT
        )
        
        response = await chatbot_service.process_message(
            user_id=str(current_user.id),
            session_id=temp_session.id,
            message_data=test_message
        )
        
        # Clean up test session
        await chatbot_service.delete_chat_session(
            user_id=str(current_user.id),
            session_id=temp_session.id
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error testing AI response: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to test AI response"
        )