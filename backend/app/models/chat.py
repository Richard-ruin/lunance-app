from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId
from app.models.base import PyObjectId


class DataUsed(BaseModel):
    transactions_count: int = 0
    period_analyzed: Optional[str] = None


class ChatMessage(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    role: str  # user, assistant
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Simple NLP
    intent: Optional[str] = None  # ask_balance, budget_help, savings_advice, expense_query
    entities: Dict[str, Any] = {}  # {amount: 50000, category: "makanan", period: "minggu ini"}
    confidence: Optional[float] = None
    
    # Response metadata
    response_type: Optional[str] = None  # info, advice, action, question
    data_used: Optional[DataUsed] = None


class SessionSummary(BaseModel):
    total_messages: int = 0
    main_topic: Optional[str] = None
    helpful_rating: Optional[int] = None  # 1-5 if user rates
    resolved: bool = False


class ChatSession(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    student_id: PyObjectId
    session_id: str
    
    messages: List[ChatMessage] = []
    
    # Session summary
    summary: SessionSummary = SessionSummary()
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ChatSessionInDB(ChatSession):
    pass


class ChatMessageCreate(BaseModel):
    role: str
    content: str
    intent: Optional[str] = None
    entities: Dict[str, Any] = {}
    confidence: Optional[float] = None
    response_type: Optional[str] = None
    data_used: Optional[DataUsed] = None


class ChatSessionCreate(BaseModel):
    student_id: PyObjectId
    session_id: str


class ChatSessionUpdate(BaseModel):
    summary: Optional[SessionSummary] = None
    ended_at: Optional[datetime] = None


class ChatResponse(BaseModel):
    message: str
    response_type: str
    data_used: Optional[DataUsed] = None
    suggestions: List[str] = []
    confidence: Optional[float] = None


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None