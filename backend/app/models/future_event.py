from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from bson import ObjectId
from app.models.base import PyObjectId


class FutureEvent(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    student_id: PyObjectId
    
    # Event Details
    event_name: str  # "Wisuda", "Liburan ke Bali", "Beli Laptop"
    event_type: str  # income, expense, mixed
    
    # Financial Impact
    estimated_amount: float
    certainty_level: str  # confirmed, likely, possible
    
    # Timing
    expected_date: datetime
    date_flexibility: int = 0  # days +/- from expected_date
    
    # Recurring Events
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None  # monthly, semester, yearly
    
    # Context for Predictions
    affects_categories: List[str] = []
    requires_preparation: bool = False  # need to save beforehand
    preparation_months: int = 0
    
    # Additional Context
    notes: Optional[str] = None
    related_goal_id: Optional[PyObjectId] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class FutureEventInDB(FutureEvent):
    pass


class FutureEventCreate(BaseModel):
    event_name: str
    event_type: str
    estimated_amount: float
    certainty_level: str
    expected_date: datetime
    date_flexibility: int = 0
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None
    affects_categories: List[str] = []
    requires_preparation: bool = False
    preparation_months: int = 0
    notes: Optional[str] = None
    related_goal_id: Optional[PyObjectId] = None


class FutureEventUpdate(BaseModel):
    event_name: Optional[str] = None
    event_type: Optional[str] = None
    estimated_amount: Optional[float] = None
    certainty_level: Optional[str] = None
    expected_date: Optional[datetime] = None
    date_flexibility: Optional[int] = None
    is_recurring: Optional[bool] = None
    recurrence_pattern: Optional[str] = None
    affects_categories: Optional[List[str]] = None
    requires_preparation: Optional[bool] = None
    preparation_months: Optional[int] = None
    notes: Optional[str] = None
    related_goal_id: Optional[PyObjectId] = None
    is_active: Optional[bool] = None