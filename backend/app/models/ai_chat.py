# app/models/ai_chat.py
"""AI Chat models and schemas - FIXED VERSION."""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    """Message role enumeration."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageType(str, Enum):
    """Message type enumeration."""
    TEXT = "text"
    FINANCIAL_ADVICE = "financial_advice"
    BUDGET_RECOMMENDATION = "budget_recommendation"
    SPENDING_ANALYSIS = "spending_analysis"
    GOAL_SUGGESTION = "goal_suggestion"
    MOTIVATION = "motivation"


class ChatMessageBase(BaseModel):
    """Base chat message model."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )
    
    content: str = Field(..., min_length=1, max_length=2000, description="Message content")
    role: MessageRole = Field(..., description="Message role")
    message_type: MessageType = Field(default=MessageType.TEXT, description="Message type")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional message metadata")

    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate and clean message content."""
        content = v.strip()
        if not content:
            raise ValueError('Message content cannot be empty')
        return content


class ChatMessageCreate(ChatMessageBase):
    """Schema for creating a new chat message."""
    context_data: Optional[Dict[str, Any]] = Field(None, description="Context data for AI processing")


class ChatMessageResponse(ChatMessageBase):
    """Schema for chat message response."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )
    
    message_id: Optional[str] = Field(None, description="Message ID")
    user_id: str = Field(..., description="User ID")
    session_id: str = Field(..., description="Chat session ID")
    tokens_used: Optional[int] = Field(None, description="Tokens used for this message")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    confidence_score: Optional[float] = Field(None, ge=0, le=1, description="AI confidence score")
    created_at: datetime = Field(..., description="Creation timestamp")


class ChatSessionBase(BaseModel):
    """Base chat session model."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )
    
    session_name: Optional[str] = Field(None, max_length=100, description="Session name")
    is_active: bool = Field(default=True, description="Whether session is active")


class ChatSessionCreate(ChatSessionBase):
    """Schema for creating a new chat session."""
    pass


class ChatSessionResponse(ChatSessionBase):
    """Schema for chat session response."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )
    
    session_id: Optional[str] = Field(None, description="Session ID")
    user_id: str = Field(..., description="User ID")
    message_count: int = Field(default=0, description="Number of messages in session")
    last_activity: Optional[datetime] = Field(None, description="Last activity timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class ChatHistoryResponse(BaseModel):
    """Schema for chat history response."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )
    
    session: ChatSessionResponse = Field(..., description="Chat session")
    messages: List[ChatMessageResponse] = Field(..., description="Chat messages")
    total_messages: int = Field(..., description="Total number of messages")


class AIInsight(BaseModel):
    """AI insight/analysis result."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )
    
    insight_type: str = Field(..., description="Type of insight")
    title: str = Field(..., description="Insight title")
    description: str = Field(..., description="Insight description")
    data: Optional[Dict[str, Any]] = Field(None, description="Supporting data")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    priority: str = Field(..., description="Priority level (high/medium/low)")
    action_items: Optional[List[str]] = Field(None, description="Suggested actions")


class FinancialContext(BaseModel):
    """Financial context for AI processing."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )
    
    current_balance: float = Field(..., description="Current balance")
    monthly_income: float = Field(..., description="Average monthly income")
    monthly_expense: float = Field(..., description="Average monthly expense")
    top_categories: List[Dict[str, Any]] = Field(..., description="Top spending categories")
    savings_targets: List[Dict[str, Any]] = Field(..., description="Active savings targets")
    recent_transactions: List[Dict[str, Any]] = Field(..., description="Recent transactions")
    spending_trends: Optional[Dict[str, Any]] = Field(None, description="Spending trends")


class ChatAnalyticsRequest(BaseModel):
    """Request for chat analytics."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )
    
    start_date: Optional[datetime] = Field(None, description="Start date")
    end_date: Optional[datetime] = Field(None, description="End date")
    message_types: Optional[List[MessageType]] = Field(None, description="Filter by message types")


class ChatAnalyticsResponse(BaseModel):
    """Chat analytics response."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )
    
    total_messages: int = Field(..., description="Total messages")
    total_sessions: int = Field(..., description="Total sessions")
    avg_messages_per_session: float = Field(..., description="Average messages per session")
    avg_session_duration: float = Field(..., description="Average session duration in minutes")
    most_common_topics: List[Dict[str, Any]] = Field(..., description="Most common conversation topics")
    user_engagement_score: float = Field(..., ge=0, le=1, description="User engagement score")
    ai_response_accuracy: float = Field(..., ge=0, le=1, description="AI response accuracy")


class WebSocketMessage(BaseModel):
    """WebSocket message structure."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )
    
    type: str = Field(..., description="Message type")
    data: Dict[str, Any] = Field(..., description="Message data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")


class ChatPreferences(BaseModel):
    """User chat preferences."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )
    
    language: str = Field(default="id", description="Preferred language (id/en)")
    tone: str = Field(default="friendly", description="Preferred tone")
    detail_level: str = Field(default="medium", description="Detail level (low/medium/high)")
    financial_advice_frequency: str = Field(default="normal", description="Advice frequency")
    enable_proactive_insights: bool = Field(default=True, description="Enable proactive insights")
    enable_spending_alerts: bool = Field(default=True, description="Enable spending alerts")


class ContextMemory(BaseModel):
    """Context memory for chat continuity."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )
    
    user_goals: List[str] = Field(default=[], description="User financial goals")
    preferences: Dict[str, Any] = Field(default={}, description="User preferences")
    conversation_context: List[str] = Field(default=[], description="Recent conversation context")
    financial_situation: Optional[Dict[str, Any]] = Field(None, description="Financial situation summary")
    last_advice_given: Optional[datetime] = Field(None, description="Last advice timestamp")
    interaction_patterns: Dict[str, Any] = Field(default={}, description="User interaction patterns")


# Error handling models
class ChatError(BaseModel):
    """Chat error response."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )
    
    error_code: str = Field(..., description="Error code")
    error_message: str = Field(..., description="Error message")
    error_type: str = Field(..., description="Error type")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    context: Optional[Dict[str, Any]] = Field(None, description="Error context")


class AIModelConfig(BaseModel):
    """AI model configuration."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )
    
    model_name: str = Field(..., description="Model name")
    max_tokens: int = Field(default=1000, description="Maximum tokens")
    temperature: float = Field(default=0.7, ge=0, le=2, description="Temperature for creativity")
    top_p: float = Field(default=0.9, ge=0, le=1, description="Top-p sampling")
    frequency_penalty: float = Field(default=0.0, ge=-2, le=2, description="Frequency penalty")
    presence_penalty: float = Field(default=0.0, ge=-2, le=2, description="Presence penalty")
    indonesian_language_boost: bool = Field(default=True, description="Boost Indonesian language understanding")


# Chat templates
CHAT_TEMPLATES = {
    "greeting": {
        "id": "Halo! Saya Luna, asisten keuangan pintar Anda. Bagaimana saya bisa membantu mengelola keuangan Anda hari ini?",
        "en": "Hello! I'm Luna, your smart financial assistant. How can I help you manage your finances today?"
    },
    "financial_advice": {
        "id": "Berdasarkan analisis transaksi Anda, saya memiliki beberapa saran untuk meningkatkan pengelolaan keuangan Anda:",
        "en": "Based on your transaction analysis, I have some suggestions to improve your financial management:"
    },
    "budget_recommendation": {
        "id": "Mari kita buat rencana anggaran yang sesuai dengan pola pengeluaran Anda:",
        "en": "Let's create a budget plan that fits your spending patterns:"
    },
    "goal_motivation": {
        "id": "Anda sudah melakukan yang terbaik! Mari kita lihat progress menuju target finansial Anda:",
        "en": "You're doing great! Let's look at your progress towards your financial goals:"
    },
    "spending_alert": {
        "id": "Saya melihat ada pola pengeluaran yang perlu diperhatikan:",
        "en": "I notice some spending patterns that need attention:"
    },
    "error_fallback": {
        "id": "Maaf, saya mengalami sedikit kesulitan memahami permintaan Anda. Bisa Anda ulangi dengan cara yang berbeda?",
        "en": "Sorry, I'm having a bit of trouble understanding your request. Could you rephrase it differently?"
    }
}