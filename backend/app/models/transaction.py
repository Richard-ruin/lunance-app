# app/models/transaction.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from .base import BaseDocument, PyObjectId

class RecurringConfig(BaseModel):
    frequency: str = Field(..., pattern=r'^(daily|weekly|monthly)$')
    end_date: Optional[datetime] = None
    next_date: Optional[datetime] = None

class TransactionBase(BaseModel):
    type: str = Field(..., pattern=r'^(pemasukan|pengeluaran)$')
    amount: float = Field(..., gt=0)
    description: str = Field(..., min_length=1, max_length=200)
    category_id: PyObjectId
    date: datetime
    payment_method: str = Field(..., pattern=r'^(cash|transfer|e-wallet|card)$')
    location: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=500)
    tags: Optional[List[str]] = Field(default_factory=list)
    is_recurring: bool = False
    recurring_config: Optional[RecurringConfig] = None

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount harus lebih besar dari 0')
        return round(v, 2)

    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        if not v.strip():
            raise ValueError('Deskripsi tidak boleh kosong')
        return v.strip()

    @field_validator('date')
    @classmethod
    def validate_date(cls, v):
        if v > datetime.utcnow():
            raise ValueError('Tanggal tidak boleh di masa depan')
        return v

class TransactionCreate(TransactionBase):
    pass

class Transaction(BaseDocument):
    user_id: PyObjectId
    type: str
    amount: float
    description: str
    category_id: PyObjectId
    date: datetime
    payment_method: str
    location: Optional[str] = None
    notes: Optional[str] = None
    receipt_url: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    is_recurring: bool = False
    recurring_config: Optional[RecurringConfig] = None

class TransactionResponse(BaseModel):
    model_config = {"populate_by_name": True}
    
    id: str = Field(alias="_id")
    type: str
    amount: float
    description: str
    category: dict  # Category info
    date: datetime
    payment_method: str
    location: Optional[str] = None
    notes: Optional[str] = None
    receipt_url: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    is_recurring: bool = False
    recurring_config: Optional[RecurringConfig] = None
    created_at: datetime

class TransactionUpdate(BaseModel):
    type: Optional[str] = Field(None, pattern=r'^(pemasukan|pengeluaran)$')
    amount: Optional[float] = Field(None, gt=0)
    description: Optional[str] = Field(None, min_length=1, max_length=200)
    category_id: Optional[PyObjectId] = None
    date: Optional[datetime] = None
    payment_method: Optional[str] = Field(None, pattern=r'^(cash|transfer|e-wallet|card)$')
    location: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=500)
    tags: Optional[List[str]] = None

class TransactionSummary(BaseModel):
    total_pemasukan: float
    total_pengeluaran: float
    balance: float
    transaction_count: int

class TransactionListResponse(BaseModel):
    data: List[TransactionResponse]
    pagination: dict
    summary: TransactionSummary