# app/models/category.py (Fixed version)
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator
from bson import ObjectId
from app.models.base import PyObjectId


class TypicalAmountRange(BaseModel):
    min: float
    max: float
    avg: float  # from other students data


class Category(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str
    parent_id: Optional[PyObjectId] = None
    type: str  # income, expense
    icon: str
    color: str
    is_system: bool = False
    
    # Student-specific categories
    student_specific: bool = False
    typical_amount_range: Optional[TypicalAmountRange] = None
    
    # Indonesian student categories examples:
    # INCOME: Uang Saku, Part Time, Beasiswa, Freelance
    # EXPENSE: Makanan, Transport, Kos, Kuliah, Hiburan, Belanja, Kesehatan
    
    keywords: List[str] = []  # for auto-categorization
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CategoryInDB(Category):
    pass


class CategoryCreate(BaseModel):
    name: str
    parent_id: Optional[PyObjectId] = None
    type: str
    icon: str
    color: str
    is_system: bool = False
    student_specific: bool = False
    typical_amount_range: Optional[TypicalAmountRange] = None
    keywords: List[str] = []


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[PyObjectId] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    student_specific: Optional[bool] = None
    typical_amount_range: Optional[TypicalAmountRange] = None
    keywords: Optional[List[str]] = None


class CategoryWithStats(Category):
    # Additional stats for category analysis
    transaction_count: int = 0
    total_amount: float = 0.0
    avg_amount: float = 0.0
    last_used: Optional[datetime] = None
    
    @field_validator('total_amount', 'avg_amount', mode='before')
    @classmethod
    def validate_amounts(cls, v):
        # Handle None values from MongoDB aggregation
        if v is None:
            return 0.0
        return float(v)
    
    @field_validator('transaction_count', mode='before')
    @classmethod
    def validate_count(cls, v):
        if v is None:
            return 0
        return int(v)