# app/models/transaction.py
from datetime import datetime
from typing import List, Optional, Dict, Any, Annotated
from pydantic import BaseModel, Field, ConfigDict, field_validator
from bson import ObjectId
from enum import Enum

class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"

class PaymentMethod(str, Enum):
    CASH = "cash"
    E_WALLET = "e_wallet"
    BANK_TRANSFER = "bank_transfer"
    CREDIT = "credit"

class LocationType(str, Enum):
    CAMPUS = "campus"
    KOS = "kos"
    MALL = "mall"
    RESTAURANT = "restaurant"
    TRANSPORT = "transport"
    OTHER = "other"

class Location(BaseModel):
    name: str = Field(..., description="Kantin Fakultas, Warung Pak Udin")
    type: LocationType
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class ReceiptPhoto(BaseModel):
    filename: str
    url: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

class TransactionMetadata(BaseModel):
    is_shared_expense: bool = False
    shared_with: List[str] = []
    my_share: Optional[float] = None
    
    # ML features
    auto_categorized: bool = False
    confidence: float = 0.0
    is_unusual: bool = False
    
    # Context
    semester_week: Optional[int] = Field(None, description="week in semester (1-16)")
    is_exam_period: bool = False
    academic_related: bool = False

class BudgetImpact(BaseModel):
    weekly_budget_remaining: Optional[float] = None
    monthly_budget_remaining: Optional[float] = None
    category_budget_used: Optional[float] = None

class Transaction(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        str_strip_whitespace=True
    )
    
    id: Optional[str] = Field(default=None, alias="_id")
    student_id: str
    
    # Basic Info
    type: TransactionType
    amount: float = Field(..., gt=0, description="Amount must be greater than 0")
    currency: str = "IDR"
    
    # Categorization
    category_id: str
    subcategory: Optional[str] = None
    
    # Description
    title: str = Field(..., min_length=1, max_length=200)
    notes: Optional[str] = Field(None, max_length=500)
    
    # Dates
    transaction_date: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Payment method
    payment_method: PaymentMethod
    account_name: str = Field(..., description="GoPay, DANA, Cash, BCA", max_length=100)
    
    # Location (optional)
    location: Optional[Location] = None
    
    # Receipt photo
    receipt_photo: Optional[ReceiptPhoto] = None
    
    # Student-specific metadata
    metadata: TransactionMetadata = Field(default_factory=TransactionMetadata)
    
    # Budget tracking
    budget_impact: Optional[BudgetImpact] = None

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        return round(v, 2)
    
    @field_validator('student_id', 'category_id')
    @classmethod
    def validate_object_id_string(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError('Invalid ObjectId format')
        return v

# Request Models
class TransactionCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    
    type: TransactionType
    amount: float = Field(..., gt=0)
    category_id: str
    title: str = Field(..., min_length=1, max_length=200)
    notes: Optional[str] = Field(None, max_length=500)
    payment_method: PaymentMethod
    account_name: str = Field(..., max_length=100)
    transaction_date: Optional[datetime] = None
    location: Optional[Location] = None
    subcategory: Optional[str] = None

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        return round(v, 2)
    
    @field_validator('category_id')
    @classmethod
    def validate_category_id(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError('Invalid category ID format')
        return v

class TransactionUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    
    amount: Optional[float] = Field(None, gt=0)
    category_id: Optional[str] = None
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    notes: Optional[str] = Field(None, max_length=500)
    payment_method: Optional[PaymentMethod] = None
    account_name: Optional[str] = Field(None, max_length=100)
    transaction_date: Optional[datetime] = None
    location: Optional[Location] = None
    subcategory: Optional[str] = None

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Amount must be greater than 0')
        return round(v, 2) if v is not None else v
    
    @field_validator('category_id')
    @classmethod
    def validate_category_id(cls, v):
        if v is not None and not ObjectId.is_valid(v):
            raise ValueError('Invalid category ID format')
        return v

# Response Models
class TransactionResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    id: str = Field(alias="_id")
    type: TransactionType
    amount: float
    currency: str
    category_id: str
    subcategory: Optional[str]
    title: str
    notes: Optional[str]
    transaction_date: datetime
    created_at: datetime
    payment_method: PaymentMethod
    account_name: str
    location: Optional[Location]
    receipt_photo: Optional[ReceiptPhoto]
    metadata: TransactionMetadata
    budget_impact: Optional[BudgetImpact]

# Filter and Query Models
class TransactionFilter(BaseModel):
    type: Optional[TransactionType] = None
    category_id: Optional[str] = None
    payment_method: Optional[PaymentMethod] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_amount: Optional[float] = Field(None, ge=0)
    max_amount: Optional[float] = Field(None, ge=0)
    search: Optional[str] = Field(None, max_length=100)

class TransactionSort(str, Enum):
    DATE_DESC = "date_desc"
    DATE_ASC = "date_asc"
    AMOUNT_DESC = "amount_desc"
    AMOUNT_ASC = "amount_asc"
    TITLE_ASC = "title_asc"
    TITLE_DESC = "title_desc"

class TransactionListResponse(BaseModel):
    transactions: List[TransactionResponse]
    total: int
    page: int
    limit: int
    total_pages: int

# Analytics Models
class TransactionSummary(BaseModel):
    total_income: float
    total_expense: float
    net_balance: float
    transaction_count: int
    daily_average: float

class CategoryBreakdown(BaseModel):
    category_id: str
    category_name: str
    amount: float
    percentage: float
    transaction_count: int
    vs_previous_period: Optional[float] = None

class PeriodSummary(BaseModel):
    period: str
    start_date: datetime
    end_date: datetime
    summary: TransactionSummary
    category_breakdown: List[CategoryBreakdown]

class MonthlyTransactionSummary(BaseModel):
    month: int
    year: int
    summary: TransactionSummary
    category_breakdown: List[CategoryBreakdown]
    weekly_breakdown: List[PeriodSummary]

# Receipt upload model
class ReceiptUploadResponse(BaseModel):
    filename: str
    url: str
    uploaded_at: datetime

# Bulk operations
class BulkDeleteRequest(BaseModel):
    transaction_ids: List[str] = Field(..., min_length=1)
    
    @field_validator('transaction_ids')
    @classmethod
    def validate_transaction_ids(cls, v):
        for id_str in v:
            if not ObjectId.is_valid(id_str):
                raise ValueError(f'Invalid transaction ID format: {id_str}')
        return v

class BulkDeleteResponse(BaseModel):
    deleted_count: int
    failed_ids: List[str] = []

# Export models
class ExportFormat(str, Enum):
    CSV = "csv"
    EXCEL = "excel"
    PDF = "pdf"

class ExportRequest(BaseModel):
    format: ExportFormat
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    categories: Optional[List[str]] = None
    include_metadata: bool = False

# Example usage and schema
TRANSACTION_EXAMPLE = {
    "type": "expense",
    "amount": 25000,
    "currency": "IDR",
    "category_id": "507f1f77bcf86cd799439011",
    "title": "Makan Siang",
    "payment_method": "cash",
    "account_name": "Cash",
    "location": {
        "name": "Kantin Fakultas",
        "type": "campus"
    }
}