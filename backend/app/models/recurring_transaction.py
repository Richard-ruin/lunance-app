# app/models/recurring_transaction.py
from pydantic import BaseModel, Field
from bson import ObjectId
from datetime import datetime, timezone
from typing import Dict, Optional, Any
from .base import PyObjectId

class TransactionData(BaseModel):
    type: str
    amount: float
    description: str
    category_id: PyObjectId
    payment_method: str

class RecurrencePattern(BaseModel):
    frequency: str  # "daily", "weekly", "monthly", "yearly"
    interval: int = 1  # Every X days/weeks/months
    day_of_week: Optional[int] = None  # For weekly (0-6)
    day_of_month: Optional[int] = None  # For monthly (1-31)
    end_date: Optional[datetime] = None

class RecurringTransaction(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    template_name: str
    transaction_data: TransactionData
    recurrence_pattern: RecurrencePattern
    next_execution: datetime
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_executed: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}