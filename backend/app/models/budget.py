# app/models/budget.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from .base import BaseDocument, PyObjectId

class BudgetBase(BaseModel):
    category_id: PyObjectId
    amount: float = Field(..., gt=0)
    period: str = Field(..., pattern=r'^(weekly|monthly)$')
    start_date: datetime
    end_date: datetime

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Budget amount harus lebih besar dari 0')
        return round(v, 2)

    @field_validator('end_date')
    @classmethod
    def validate_end_date(cls, v, info):
        if 'start_date' in info.data and v <= info.data['start_date']:
            raise ValueError('End date harus setelah start date')
        return v

class BudgetCreate(BudgetBase):
    pass

class Budget(BaseDocument):
    user_id: PyObjectId
    category_id: PyObjectId
    amount: float
    period: str
    start_date: datetime
    end_date: datetime
    spent: float = 0.0
    is_active: bool = True

class BudgetResponse(BaseModel):
    model_config = {"populate_by_name": True}
    
    id: str = Field(alias="_id")
    category: dict  # Category info
    amount: float
    period: str
    start_date: datetime
    end_date: datetime
    spent: float
    remaining: float
    percentage_used: float
    is_active: bool
    created_at: datetime

class BudgetUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    period: Optional[str] = Field(None, pattern=r'^(weekly|monthly)$')
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None