from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator
from bson import ObjectId
from enum import Enum

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic._internal._core_utils import CoreMetadataHandler
        from pydantic._internal._generate_schema import GenerateSchema
        from pydantic_core import core_schema
        
        def validate_object_id(value):
            if isinstance(value, ObjectId):
                return value
            if isinstance(value, str):
                if ObjectId.is_valid(value):
                    return ObjectId(value)
            raise ValueError("Invalid ObjectId")
        
        return core_schema.no_info_plain_validator_function(
            validate_object_id,
            serialization=core_schema.plain_serializer_function(str)
        )

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
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    student_id: PyObjectId
    student_name: str
    amount_owed: float
    has_paid: bool = False
    paid_date: Optional[datetime] = None

class ExpenseSplit(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
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

    @classmethod
    def model_json_schema(cls, by_alias: bool = True, ref_template: str = '#/$defs/{model}') -> Dict[str, Any]:
        schema = super().model_json_schema(by_alias=by_alias, ref_template=ref_template)
        # Add the example to the schema
        schema['example'] = {
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
        return schema

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
    model_config = ConfigDict(
        populate_by_name=True
    )
    
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