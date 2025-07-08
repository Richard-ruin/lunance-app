# app/models/notification.py
"""Notification models and schemas - FIXED VERSION."""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class NotificationType(str, Enum):
    """Notification type enumeration."""
    TRANSACTION = "transaction"
    SAVINGS_GOAL = "savings_goal"
    BUDGET_ALERT = "budget_alert"
    SYSTEM = "system"
    ADMIN = "admin"
    AI_INSIGHT = "ai_insight"
    REMINDER = "reminder"


class NotificationPriority(str, Enum):
    """Notification priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationBase(BaseModel):
    """Base notification model."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )
    
    title: str = Field(..., min_length=1, max_length=200, description="Notification title")
    message: str = Field(..., min_length=1, max_length=1000, description="Notification message")
    type: NotificationType = Field(..., description="Notification type")
    priority: NotificationPriority = Field(default=NotificationPriority.NORMAL, description="Priority level")
    action_url: Optional[str] = Field(None, description="URL for notification action")
    action_text: Optional[str] = Field(None, description="Text for action button")
    data: Optional[Dict[str, Any]] = Field(default={}, description="Additional notification data")

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate notification title."""
        return v.strip()

    @field_validator('message')
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Validate notification message."""
        return v.strip()


class NotificationCreate(NotificationBase):
    """Schema for creating a notification."""
    pass


class NotificationInDB(NotificationBase):
    """Notification model as stored in database."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )
    
    notification_id: Optional[str] = Field(None, description="Notification ID")
    user_id: str = Field(..., description="Target user ID")
    is_read: bool = Field(default=False, description="Read status")
    read_at: Optional[datetime] = Field(None, description="Read timestamp")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")


class NotificationResponse(NotificationBase):
    """Schema for notification response."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )
    
    notification_id: str = Field(..., description="Notification ID")
    user_id: str = Field(..., description="Target user ID")
    is_read: bool = Field(..., description="Read status")
    read_at: Optional[datetime] = Field(None, description="Read timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")
    time_ago: Optional[str] = Field(None, description="Human-readable time ago")


class NotificationUpdate(BaseModel):
    """Schema for updating notification."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )
    
    is_read: Optional[bool] = Field(None, description="Read status")
    read_at: Optional[datetime] = Field(None, description="Read timestamp")


class NotificationSettings(BaseModel):
    """User notification preferences."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )
    
    settings_id: Optional[str] = Field(None, description="Settings ID")
    user_id: str = Field(..., description="User ID")
    
    # Email notifications
    email_enabled: bool = Field(default=True, description="Enable email notifications")
    email_transactions: bool = Field(default=True, description="Email for transactions")
    email_savings_goals: bool = Field(default=True, description="Email for savings goals")
    email_budget_alerts: bool = Field(default=True, description="Email for budget alerts")
    email_ai_insights: bool = Field(default=True, description="Email for AI insights")
    email_reminders: bool = Field(default=True, description="Email for reminders")
    
    # Push notifications
    push_enabled: bool = Field(default=True, description="Enable push notifications")
    push_transactions: bool = Field(default=True, description="Push for transactions")
    push_savings_goals: bool = Field(default=True, description="Push for savings goals")
    push_budget_alerts: bool = Field(default=True, description="Push for budget alerts")
    push_ai_insights: bool = Field(default=True, description="Push for AI insights")
    push_reminders: bool = Field(default=True, description="Push for reminders")
    
    # WebSocket notifications
    websocket_enabled: bool = Field(default=True, description="Enable real-time notifications")
    
    # Frequency settings
    digest_frequency: str = Field(default="daily", description="Digest frequency (daily, weekly, never)")
    quiet_hours_start: Optional[str] = Field(None, description="Quiet hours start (HH:MM)")
    quiet_hours_end: Optional[str] = Field(None, description="Quiet hours end (HH:MM)")
    
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Update timestamp")


class NotificationSettingsUpdate(BaseModel):
    """Schema for updating notification settings."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )
    
    email_enabled: Optional[bool] = None
    email_transactions: Optional[bool] = None
    email_savings_goals: Optional[bool] = None
    email_budget_alerts: Optional[bool] = None
    email_ai_insights: Optional[bool] = None
    email_reminders: Optional[bool] = None
    
    push_enabled: Optional[bool] = None
    push_transactions: Optional[bool] = None
    push_savings_goals: Optional[bool] = None
    push_budget_alerts: Optional[bool] = None
    push_ai_insights: Optional[bool] = None
    push_reminders: Optional[bool] = None
    
    websocket_enabled: Optional[bool] = None
    digest_frequency: Optional[str] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None

    @field_validator('digest_frequency')
    @classmethod
    def validate_digest_frequency(cls, v: Optional[str]) -> Optional[str]:
        """Validate digest frequency."""
        if v and v not in ['daily', 'weekly', 'never']:
            raise ValueError('Digest frequency must be daily, weekly, or never')
        return v

    @field_validator('quiet_hours_start', 'quiet_hours_end')
    @classmethod
    def validate_time_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate time format (HH:MM)."""
        if v:
            try:
                hours, minutes = map(int, v.split(':'))
                if not (0 <= hours <= 23 and 0 <= minutes <= 59):
                    raise ValueError('Invalid time format')
                return f"{hours:02d}:{minutes:02d}"
            except (ValueError, AttributeError):
                raise ValueError('Time must be in HH:MM format')
        return v


class NotificationTemplate(BaseModel):
    """Notification template for different types."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )
    
    type: NotificationType = Field(..., description="Notification type")
    title_template: str = Field(..., description="Title template with placeholders")
    message_template: str = Field(..., description="Message template with placeholders")
    priority: NotificationPriority = Field(default=NotificationPriority.NORMAL, description="Default priority")
    action_text: Optional[str] = Field(None, description="Default action text")
    variables: List[str] = Field(default=[], description="Required template variables")


class NotificationDigest(BaseModel):
    """Daily/weekly notification digest."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )
    
    user_id: str = Field(..., description="User ID")
    digest_type: str = Field(..., description="Digest type (daily/weekly)")
    period_start: datetime = Field(..., description="Digest period start")
    period_end: datetime = Field(..., description="Digest period end")
    
    transaction_count: int = Field(default=0, description="Number of transactions")
    total_income: float = Field(default=0.0, description="Total income in period")
    total_expense: float = Field(default=0.0, description="Total expense in period")
    
    savings_progress: List[Dict[str, Any]] = Field(default=[], description="Savings goals progress")
    budget_status: List[Dict[str, Any]] = Field(default=[], description="Budget status")
    ai_insights: List[str] = Field(default=[], description="AI-generated insights")
    
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")


class NotificationStats(BaseModel):
    """Notification statistics."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )
    
    total_sent: int = Field(..., description="Total notifications sent")
    total_read: int = Field(..., description="Total notifications read")
    total_unread: int = Field(..., description="Total unread notifications")
    read_rate: float = Field(..., description="Read rate percentage")
    
    by_type: Dict[str, int] = Field(..., description="Count by notification type")
    by_priority: Dict[str, int] = Field(..., description="Count by priority")
    
    recent_activity: List[Dict[str, Any]] = Field(..., description="Recent notification activity")
    
    calculated_at: datetime = Field(default_factory=datetime.utcnow, description="Calculation timestamp")