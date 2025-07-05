# app/models/savings_goal.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from .base import BaseDocument, PyObjectId

class SavingsGoalCreate(BaseModel):
    nama_goal: str = Field(..., min_length=1, max_length=100)
    deskripsi: Optional[str] = Field(None, max_length=500)
    target_amount: float = Field(..., gt=0)
    target_date: datetime
    category: str = Field(..., regex="^(gadget|travel|emergency|other)$")
    priority: str = Field(..., regex="^(high|medium|low)$")
    image_url: Optional[str] = None

    @field_validator('target_date')
    @classmethod
    def validate_target_date(cls, v):
        if v <= datetime.now():
            raise ValueError('Target date must be in the future')
        return v

class SavingsGoal(BaseDocument):
    user_id: PyObjectId
    nama_goal: str
    deskripsi: Optional[str] = None
    target_amount: float
    current_amount: float = 0.0
    target_date: datetime
    category: str  # "gadget", "travel", "emergency", "other"
    priority: str  # "high", "medium", "low"
    image_url: Optional[str] = None
    is_achieved: bool = False
    achieved_date: Optional[datetime] = None

class SavingsGoalUpdate(BaseModel):
    nama_goal: Optional[str] = Field(None, min_length=1, max_length=100)
    deskripsi: Optional[str] = Field(None, max_length=500)
    target_amount: Optional[float] = Field(None, gt=0)
    target_date: Optional[datetime] = None
    category: Optional[str] = Field(None, regex="^(gadget|travel|emergency|other)$")
    priority: Optional[str] = Field(None, regex="^(high|medium|low)$")
    image_url: Optional[str] = None

class SavingsGoalResponse(BaseModel):
    model_config = {"populate_by_name": True}
    
    id: str = Field(alias="_id")
    user_id: str
    nama_goal: str
    deskripsi: Optional[str]
    target_amount: float
    current_amount: float
    target_date: datetime
    category: str
    priority: str
    image_url: Optional[str]
    is_achieved: bool
    achieved_date: Optional[datetime]
    progress_percentage: float = Field(default=0.0)
    days_left: int = Field(default=0)
    monthly_required: float = Field(default=0.0)
    created_at: datetime
    updated_at: datetime

class GoalDeposit(BaseModel):
    amount: float = Field(..., gt=0)
    notes: Optional[str] = Field(None, max_length=200)

class GoalWithdraw(BaseModel):
    amount: float = Field(..., gt=0)
    notes: Optional[str] = Field(None, max_length=200)