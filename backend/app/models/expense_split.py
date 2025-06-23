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

class SplitMethod(str, Enum):
    EQUAL = "equal"
    CUSTOM = "custom"
    PERCENTAGE = "percentage"

class ExpenseSplitStatus(str, Enum):
    PENDING = "pending"
    PARTIALLY_PAID = "partially_paid"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Participant(BaseModel):
    student_id: PyObjectId
    student_name: str
    amount_owed: float
    has_paid: bool = False
    paid_date: Optional[datetime] = None
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class ExpenseSplit(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    created_by: PyObjectId
    
    # Expense Details
    title: str = Field(..., description="Makan di KFC, Bensin bareng")
    total_amount: float
    currency: str = "IDR"
    category_id: PyObjectId
    transaction_date: datetime = Field(default_factory=datetime.utcnow)
    
    # Participants
    participants: List[Participant] = []
    
    # Split Details
    split_method: SplitMethod = SplitMethod.EQUAL
    split_details: Dict[str, Any] = Field(default_factory=dict)
    
    # Status
    status: ExpenseSplitStatus = ExpenseSplitStatus.PENDING
    notes: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "title": "Makan di KFC",
                "total_amount": 120000,
                "currency": "IDR",
                "split_method": "equal",
                "participants": [
                    {
                        "student_name": "Ahmad",
                        "amount_owed": 40000,
                        "has_paid": False
                    }
                ],
                "notes": "Makan bareng setelah ujian"
            }
        }

# Request/Response Models
class ParticipantCreate(BaseModel):
    student_id: str
    student_name: str
    amount_owed: Optional[float] = None  # Will be calculated if not provided

class ExpenseSplitCreate(BaseModel):
    title: str
    total_amount: float
    category_id: str
    transaction_date: Optional[datetime] = None
    participants: List[ParticipantCreate]
    split_method: SplitMethod = SplitMethod.EQUAL
    split_details: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None

class ExpenseSplitUpdate(BaseModel):
    title: Optional[str] = None
    total_amount: Optional[float] = None
    category_id: Optional[str] = None
    transaction_date: Optional[datetime] = None
    participants: Optional[List[ParticipantCreate]] = None
    split_method: Optional[SplitMethod] = None
    split_details: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    status: Optional[ExpenseSplitStatus] = None

class ParticipantResponse(BaseModel):
    student_id: str
    student_name: str
    amount_owed: float
    has_paid: bool
    paid_date: Optional[datetime]

class ExpenseSplitResponse(BaseModel):
    id: str = Field(alias="_id")
    created_by: str
    title: str
    total_amount: float
    currency: str
    category_id: str
    transaction_date: datetime
    participants: List[ParticipantResponse]
    split_method: SplitMethod
    split_details: Dict[str, Any]
    status: ExpenseSplitStatus
    notes: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    
    # Calculated fields
    total_paid: Optional[float] = None
    remaining_amount: Optional[float] = None
    my_share: Optional[float] = None
    i_owe: Optional[float] = None
    owed_to_me: Optional[float] = None

    class Config:
        allow_population_by_field_name = True

class PaymentUpdate(BaseModel):
    participant_student_id: str
    amount_paid: float
    paid_date: Optional[datetime] = None

class ExpenseSplitSummary(BaseModel):
    total_splits: int
    total_amount_split: float
    pending_splits: int
    completed_splits: int
    my_total_share: float
    amount_i_owe: float
    amount_owed_to_me: float
    recent_splits: List[ExpenseSplitResponse]

# Helper Models for Split Calculations
class SplitCalculation(BaseModel):
    participant_id: str
    participant_name: str
    amount: float
    percentage: Optional[float] = None

class SplitResult(BaseModel):
    total_amount: float
    split_method: SplitMethod
    calculations: List[SplitCalculation]
    creator_share: float