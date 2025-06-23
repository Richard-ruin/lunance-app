from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId
from enum import Enum

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

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
    shared_with: List[PyObjectId] = []
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
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    student_id: PyObjectId
    
    # Basic Info
    type: TransactionType
    amount: float
    currency: str = "IDR"
    
    # Categorization
    category_id: PyObjectId
    subcategory: Optional[str] = None
    
    # Description
    title: str
    notes: Optional[str] = None
    
    # Dates
    transaction_date: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Payment method
    payment_method: PaymentMethod
    account_name: str = Field(..., description="GoPay, DANA, Cash, BCA")
    
    # Location (optional)
    location: Optional[Location] = None
    
    # Receipt photo
    receipt_photo: Optional[ReceiptPhoto] = None
    
    # Student-specific metadata
    metadata: TransactionMetadata = Field(default_factory=TransactionMetadata)
    
    # Budget tracking
    budget_impact: Optional[BudgetImpact] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "type": "expense",
                "amount": 25000,
                "currency": "IDR",
                "title": "Makan Siang",
                "payment_method": "cash",
                "account_name": "Cash",
                "location": {
                    "name": "Kantin Fakultas",
                    "type": "campus"
                }
            }
        }

# Student Categories Model
class CategoryTypicalAmount(BaseModel):
    min: float
    max: float
    avg: float

class Category(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str
    parent_id: Optional[PyObjectId] = None
    type: TransactionType
    icon: str
    color: str
    is_system: bool = True
    
    # Student-specific
    student_specific: bool = True
    typical_amount_range: Optional[CategoryTypicalAmount] = None
    
    # For auto-categorization
    keywords: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Request/Response Models
class TransactionCreate(BaseModel):
    type: TransactionType
    amount: float
    category_id: str
    title: str
    notes: Optional[str] = None
    payment_method: PaymentMethod
    account_name: str
    transaction_date: Optional[datetime] = None
    location: Optional[Location] = None
    subcategory: Optional[str] = None

class TransactionUpdate(BaseModel):
    amount: Optional[float] = None
    category_id: Optional[str] = None
    title: Optional[str] = None
    notes: Optional[str] = None
    payment_method: Optional[PaymentMethod] = None
    account_name: Optional[str] = None
    transaction_date: Optional[datetime] = None
    location: Optional[Location] = None
    subcategory: Optional[str] = None

class TransactionResponse(BaseModel):
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

    class Config:
        allow_population_by_field_name = True

class CategoryResponse(BaseModel):
    id: str = Field(alias="_id")
    name: str
    parent_id: Optional[str]
    type: TransactionType
    icon: str
    color: str
    is_system: bool
    student_specific: bool
    typical_amount_range: Optional[CategoryTypicalAmount]
    keywords: List[str]
    created_at: datetime

    class Config:
        allow_population_by_field_name = True

# Analytics Models
class TransactionSummary(BaseModel):
    total_income: float
    total_expense: float
    net_balance: float
    transaction_count: int
    daily_average: float

class CategoryBreakdown(BaseModel):
    category: str
    amount: float
    percentage: float
    transaction_count: int
    vs_previous_period: Optional[float] = None

class WeeklyTransactionSummary(BaseModel):
    week_start: datetime
    week_end: datetime
    summary: TransactionSummary
    category_breakdown: List[CategoryBreakdown]

class MonthlyTransactionSummary(BaseModel):
    month: int
    year: int
    summary: TransactionSummary
    category_breakdown: List[CategoryBreakdown]
    weekly_breakdown: List[WeeklyTransactionSummary]