# app/models/notification.py
from pydantic import BaseModel, Field
from bson import ObjectId
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any
from .base import PyObjectId

class Notification(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    title: str
    message: str
    type: str  # "budget_alert", "goal_reminder", "prediction", "weekly_summary"
    priority: str = "medium"  # "high", "medium", "low"
    channels: List[str] = ["in_app"]  # ["push", "email", "in_app"]
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    is_read: bool = False
    data: Optional[Dict[str, Any]] = {}
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}