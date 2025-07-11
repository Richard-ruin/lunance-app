from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ChatMessageRequest(BaseModel):
    """Request model untuk mengirim pesan"""
    message: str = Field(..., min_length=1, max_length=2000, description="Isi pesan")

class ChatMessageResponse(BaseModel):
    """Response model untuk pesan"""
    id: str
    conversation_id: str
    sender_type: str  # "user" atau "luna"
    content: str
    message_type: str = "text"
    status: str = "sent"
    timestamp: datetime

class ConversationResponse(BaseModel):
    """Response model untuk percakapan"""
    id: str
    user_id: str
    title: Optional[str]
    status: str
    last_message: Optional[str]
    last_message_at: Optional[datetime]
    message_count: int
    created_at: datetime
    updated_at: datetime

class CreateConversationRequest(BaseModel):
    """Request model untuk membuat percakapan baru"""
    title: Optional[str] = None

class ConversationListResponse(BaseModel):
    """Response model untuk daftar percakapan"""
    conversations: List[ConversationResponse]
    total: int

class MessageListResponse(BaseModel):
    """Response model untuk daftar pesan"""
    messages: List[ChatMessageResponse]
    conversation: ConversationResponse

class WebSocketMessage(BaseModel):
    """Model untuk pesan WebSocket"""
    type: str  # "chat_message", "typing_start", "typing_stop", "error", "success"
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class TypingIndicator(BaseModel):
    """Model untuk indikator mengetik"""
    sender: str  # "user" atau "luna"
    is_typing: bool

class ChatStatisticsResponse(BaseModel):
    """Response model untuk statistik chat"""
    total_conversations: int
    total_messages: int
    today_messages: int
    weekly_messages: int
    last_activity: Optional[datetime]

class SearchConversationsRequest(BaseModel):
    """Request model untuk mencari percakapan"""
    query: str = Field(..., min_length=1, max_length=100)
    limit: Optional[int] = Field(20, ge=1, le=100)

class DeleteConversationResponse(BaseModel):
    """Response model untuk menghapus percakapan"""
    success: bool
    message: str
    deleted_conversation_id: str

class WebSocketConnectionInfo(BaseModel):
    """Model untuk informasi koneksi WebSocket"""
    user_id: str
    connected_at: datetime
    last_activity: datetime
    is_typing: bool = False

class BulkDeleteConversationsRequest(BaseModel):
    """Request model untuk menghapus beberapa percakapan sekaligus"""
    conversation_ids: List[str] = Field(..., min_items=1, max_items=50)

class ArchiveConversationRequest(BaseModel):
    """Request model untuk mengarsipkan percakapan"""
    conversation_id: str

class UpdateConversationTitleRequest(BaseModel):
    """Request model untuk mengupdate judul percakapan"""
    title: str = Field(..., min_length=1, max_length=100)

class ExportConversationRequest(BaseModel):
    """Request model untuk mengekspor percakapan"""
    conversation_id: str
    format: str = Field("json", pattern="^(json|txt|pdf)$")

class MessageReactionRequest(BaseModel):
    """Request model untuk reaksi pesan (future feature)"""
    message_id: str
    reaction: str = Field(..., pattern="^(like|dislike|helpful|not_helpful)$")

class MessageFeedbackRequest(BaseModel):
    """Request model untuk feedback pesan (future feature)"""
    message_id: str
    feedback: str = Field(..., min_length=1, max_length=500)
    rating: Optional[int] = Field(None, ge=1, le=5)

# Validation schemas
class ConversationIdValidation(BaseModel):
    """Validation untuk conversation ID"""
    conversation_id: str = Field(..., min_length=1, max_length=50)

class MessageIdValidation(BaseModel):
    """Validation untuk message ID"""
    message_id: str = Field(..., min_length=1, max_length=50)

class PaginationRequest(BaseModel):
    """Request model untuk pagination"""
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)
    sort_by: Optional[str] = Field("created_at", pattern="^(created_at|updated_at|title)$")
    sort_order: Optional[str] = Field("desc", pattern="^(asc|desc)$")

# Response wrappers
class BaseResponse(BaseModel):
    """Base response model"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None

class PaginatedResponse(BaseModel):
    """Paginated response model"""
    success: bool
    message: str
    data: Dict[str, Any]
    pagination: Dict[str, Any]  # Contains page, limit, total, has_next, has_prev

# Error response models
class ValidationErrorResponse(BaseModel):
    """Response model untuk validation error"""
    success: bool = False
    message: str = "Validation error"
    errors: List[Dict[str, Any]]

class NotFoundErrorResponse(BaseModel):
    """Response model untuk not found error"""
    success: bool = False
    message: str = "Resource not found"
    resource: str
    resource_id: str

class UnauthorizedErrorResponse(BaseModel):
    """Response model untuk unauthorized error"""
    success: bool = False
    message: str = "Unauthorized access"
    
class ForbiddenErrorResponse(BaseModel):
    """Response model untuk forbidden error"""
    success: bool = False
    message: str = "Access forbidden"

class InternalServerErrorResponse(BaseModel):
    """Response model untuk internal server error"""
    success: bool = False
    message: str = "Internal server error"
    error_id: Optional[str] = None