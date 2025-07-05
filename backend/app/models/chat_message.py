# app/models/chat_message.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from .base import BaseDocument, PyObjectId

class MessageEntity(BaseModel):
    entity_type: str  # "amount", "category", "date", "transaction_type"
    value: Any
    confidence: float
    start_pos: int
    end_pos: int

class ChatMessageCreate(BaseModel):
    session_id: str
    content: str
    message_type: str = "user"  # "user", "assistant", "system"

class ChatMessage(BaseDocument):
    session_id: str
    user_id: PyObjectId
    message_type: str = Field(..., description="user, assistant, or system")
    content: str
    intent: Optional[str] = None
    entities: List[MessageEntity] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)
    response_data: Dict[str, Any] = Field(default_factory=dict)
    confidence_score: float = Field(default=0.0)
    processing_time: float = Field(default=0.0)
    sentiment: Optional[str] = None  # "positive", "negative", "neutral"
    sentiment_score: float = Field(default=0.0)

class ChatMessageResponse(BaseModel):
    model_config = {"populate_by_name": True}
    
    id: str = Field(alias="_id")
    session_id: str
    user_id: str
    message_type: str
    content: str
    intent: Optional[str]
    entities: List[MessageEntity]
    context: Dict[str, Any]
    response_data: Dict[str, Any]
    confidence_score: float
    processing_time: float
    sentiment: Optional[str]
    sentiment_score: float
    created_at: datetime

class ChatResponse(BaseModel):
    message: str
    intent: Optional[str]
    entities: List[MessageEntity]
    actions_performed: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)
    confidence: float
    processing_time: float