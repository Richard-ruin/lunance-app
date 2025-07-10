from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId
from enum import Enum

class TransactionType(str, Enum):
    """Enum untuk tipe transaksi"""
    INCOME = "income"
    EXPENSE = "expense"

class TransactionStatus(str, Enum):
    """Enum untuk status transaksi"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"

class SavingsGoalStatus(str, Enum):
    """Enum untuk status savings goal"""
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"

class GoalType(str, Enum):
    """Enum untuk tipe goal"""
    MONTHLY_AUTO = "monthly_auto"  # Target otomatis bulanan
    PURCHASE = "purchase"  # Target pembelian spesifik
    EMERGENCY_FUND = "emergency_fund"  # Dana darurat
    CUSTOM = "custom"  # Target custom

class Transaction(BaseModel):
    """Model untuk transaksi keuangan"""
    id: Optional[str] = Field(alias="_id")
    user_id: str
    
    # Transaction details
    amount: float = Field(..., gt=0)
    type: TransactionType
    category: str
    subcategory: Optional[str] = None
    description: str
    
    # Date and location
    date: datetime = Field(default_factory=datetime.utcnow)
    location: Optional[str] = None
    
    # Source information
    source: Optional[str] = None  # e.g., "manual", "voice", "image", "bank_sync"
    source_data: Optional[Dict[str, Any]] = None  # Data mentah dari source
    
    # Processing info
    confidence_score: Optional[float] = None  # AI confidence untuk kategorisasi
    is_recurring: bool = False
    recurring_pattern: Optional[str] = None  # e.g., "monthly", "weekly"
    
    # Status
    status: TransactionStatus = TransactionStatus.CONFIRMED
    
    # AI processing
    ai_categorized: bool = False
    ai_suggestion: Optional[str] = None
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }
    
    @classmethod
    def from_mongo(cls, data: Dict[str, Any]) -> "Transaction":
        """Mengkonversi data dari MongoDB ke Transaction model"""
        if data is None:
            return None
        if "_id" in data:
            data["_id"] = str(data["_id"])
        return cls(**data)
    
    def to_mongo(self) -> Dict[str, Any]:
        """Mengkonversi Transaction model ke format MongoDB"""
        data = self.dict(by_alias=True, exclude_unset=True)
        if "_id" in data and data["_id"] is None:
            del data["_id"]
        return data

class SavingsGoal(BaseModel):
    """Model untuk target tabungan"""
    id: Optional[str] = Field(alias="_id")
    user_id: str
    
    # Goal details
    name: str
    description: Optional[str] = None
    goal_type: GoalType
    target_amount: float = Field(..., gt=0)
    current_amount: float = Field(default=0, ge=0)
    
    # Timeline
    start_date: datetime = Field(default_factory=datetime.utcnow)
    target_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    
    # Status
    status: SavingsGoalStatus = SavingsGoalStatus.ACTIVE
    
    # AI calculations untuk monthly auto goals
    monthly_target: Optional[float] = None
    suggested_amount: Optional[float] = None
    
    # Progress tracking
    progress_percentage: float = Field(default=0, ge=0, le=100)
    days_to_target: Optional[int] = None
    
    # Metadata
    priority: int = Field(default=1, ge=1, le=5)  # 1 = highest priority
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }
    
    @classmethod
    def from_mongo(cls, data: Dict[str, Any]) -> "SavingsGoal":
        """Mengkonversi data dari MongoDB ke SavingsGoal model"""
        if data is None:
            return None
        if "_id" in data:
            data["_id"] = str(data["_id"])
        return cls(**data)
    
    def to_mongo(self) -> Dict[str, Any]:
        """Mengkonversi SavingsGoal model ke format MongoDB"""
        data = self.dict(by_alias=True, exclude_unset=True)
        if "_id" in data and data["_id"] is None:
            del data["_id"]
        return data
    
    def calculate_progress(self):
        """Menghitung persentase progress"""
        if self.target_amount > 0:
            self.progress_percentage = min((self.current_amount / self.target_amount) * 100, 100)
        else:
            self.progress_percentage = 0
        self.updated_at = datetime.utcnow()
    
    def add_savings(self, amount: float):
        """Menambah jumlah tabungan"""
        self.current_amount += amount
        self.calculate_progress()
        
        # Cek apakah goal sudah tercapai
        if self.current_amount >= self.target_amount and self.status == SavingsGoalStatus.ACTIVE:
            self.status = SavingsGoalStatus.COMPLETED
            self.completed_date = datetime.utcnow()
    
    def is_completed(self) -> bool:
        """Mengecek apakah goal sudah selesai"""
        return self.status == SavingsGoalStatus.COMPLETED or self.current_amount >= self.target_amount

class Category(BaseModel):
    """Model untuk kategori transaksi"""
    id: Optional[str] = Field(alias="_id")
    name: str
    type: TransactionType  # income atau expense
    
    # Hierarchy
    parent_category: Optional[str] = None
    subcategories: List[str] = Field(default_factory=list)
    
    # AI learning
    keywords: List[str] = Field(default_factory=list)  # Keywords untuk AI detection
    confidence_threshold: float = Field(default=0.7)  # Minimum confidence untuk auto-categorization
    
    # User customization
    user_id: Optional[str] = None  # None untuk default categories
    is_custom: bool = False
    is_active: bool = True
    
    # Display
    icon: Optional[str] = None
    color: Optional[str] = None
    order: int = Field(default=0)
    
    # Statistics
    usage_count: int = Field(default=0)
    total_amount: float = Field(default=0)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }
    
    @classmethod
    def from_mongo(cls, data: Dict[str, Any]) -> "Category":
        """Mengkonversi data dari MongoDB ke Category model"""
        if data is None:
            return None
        if "_id" in data:
            data["_id"] = str(data["_id"])
        return cls(**data)
    
    def to_mongo(self) -> Dict[str, Any]:
        """Mengkonversi Category model ke format MongoDB"""
        data = self.dict(by_alias=True, exclude_unset=True)
        if "_id" in data and data["_id"] is None:
            del data["_id"]
        return data

class Conversation(BaseModel):
    """Model untuk percakapan dengan AI"""
    id: Optional[str] = Field(alias="_id")
    user_id: str
    
    # Conversation details
    title: Optional[str] = None  # Auto-generated atau user defined
    summary: Optional[str] = None  # AI-generated summary
    
    # Status
    is_active: bool = True
    message_count: int = Field(default=0)
    
    # Financial context
    related_transactions: List[str] = Field(default_factory=list)  # Transaction IDs
    related_goals: List[str] = Field(default_factory=list)  # Goal IDs
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_message_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }
    
    @classmethod
    def from_mongo(cls, data: Dict[str, Any]) -> "Conversation":
        """Mengkonversi data dari MongoDB ke Conversation model"""
        if data is None:
            return None
        if "_id" in data:
            data["_id"] = str(data["_id"])
        return cls(**data)
    
    def to_mongo(self) -> Dict[str, Any]:
        """Mengkonversi Conversation model ke format MongoDB"""
        data = self.dict(by_alias=True, exclude_unset=True)
        if "_id" in data and data["_id"] is None:
            del data["_id"]
        return data

class Message(BaseModel):
    """Model untuk pesan dalam percakapan"""
    id: Optional[str] = Field(alias="_id")
    conversation_id: str
    user_id: str
    
    # Message content
    content: str
    message_type: str  # "user", "assistant", "system"
    input_method: Optional[str] = None  # "text", "voice", "image"
    
    # Processing data
    processed_data: Optional[Dict[str, Any]] = None  # Hasil AI processing
    intent: Optional[str] = None  # Detected intent
    entities: Optional[Dict[str, Any]] = None  # Extracted entities
    
    # Related financial data
    generated_transaction: Optional[str] = None  # Transaction ID jika ada
    updated_goal: Optional[str] = None  # Goal ID jika ada
    
    # Metadata
    confidence_score: Optional[float] = None
    processing_time: Optional[float] = None  # dalam seconds
    
    # Timestamps
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }
    
    @classmethod
    def from_mongo(cls, data: Dict[str, Any]) -> "Message":
        """Mengkonversi data dari MongoDB ke Message model"""
        if data is None:
            return None
        if "_id" in data:
            data["_id"] = str(data["_id"])
        return cls(**data)
    
    def to_mongo(self) -> Dict[str, Any]:
        """Mengkonversi Message model ke format MongoDB"""
        data = self.dict(by_alias=True, exclude_unset=True)
        if "_id" in data and data["_id"] is None:
            del data["_id"]
        return data