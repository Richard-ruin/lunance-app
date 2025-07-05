# app/models/chat_session.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from .base import BaseDocument, PyObjectId

class ChatSessionCreate(BaseModel):
    title: Optional[str] = None
    context: Optional[Dict[str, Any]] = {}

class ChatSession(BaseDocument):
    user_id: PyObjectId
    session_id: str = Field(..., description="Unique session identifier")
    title: str = Field(default="New Chat Session")
    context: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = Field(default=True)
    last_message_at: Optional[datetime] = None

class ChatSessionResponse(BaseModel):
    model_config = {"populate_by_name": True}
    
    id: str = Field(alias="_id")
    user_id: str
    session_id: str
    title: str
    context: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_message_at: Optional[datetime]
    message_count: Optional[int] = 0

class ChatSessionUpdate(BaseModel):
    title: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None