# app/models/finance.py (Fixed untuk Pydantic V2)
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId
from enum import Enum

class TransactionType(str, Enum):
    """Tipe transaksi keuangan"""
    INCOME = "income"        # Pemasukan
    EXPENSE = "expense"      # Pengeluaran

class TransactionStatus(str, Enum):
    """Status transaksi"""
    PENDING = "pending"      # Menunggu konfirmasi
    CONFIRMED = "confirmed"  # Dikonfirmasi user
    CANCELLED = "cancelled"  # Dibatalkan

class SavingsGoalStatus(str, Enum):
    """Status target tabungan"""
    ACTIVE = "active"        # Aktif
    COMPLETED = "completed"  # Tercapai
    PAUSED = "paused"       # Dipause
    CANCELLED = "cancelled"  # Dibatalkan

class Transaction(BaseModel):
    """Model untuk transaksi keuangan (pemasukan/pengeluaran)"""
    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }
    )
    
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    
    # Basic transaction info
    type: TransactionType  # income atau expense
    amount: float
    category: str
    description: Optional[str] = None
    
    # Transaction details
    date: datetime = Field(default_factory=datetime.utcnow)
    status: TransactionStatus = TransactionStatus.PENDING
    
    # Chat integration
    chat_message_id: Optional[str] = None  # ID pesan chat yang memicu transaksi
    conversation_id: Optional[str] = None
    
    # Metadata
    source: str = "chat"  # chat, manual, import
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    confirmed_at: Optional[datetime] = None
    
    @classmethod
    def from_mongo(cls, data: Dict[str, Any]) -> "Transaction":
        """Mengkonversi data dari MongoDB ke Transaction model"""
        if data is None:
            return None
        
        if "_id" in data and data["_id"] is not None:
            data["_id"] = str(data["_id"])
        elif "_id" not in data:
            data["_id"] = None
            
        return cls(**data)
    
    def to_mongo(self, exclude_id: bool = False) -> Dict[str, Any]:
        """Mengkonversi Transaction model ke format MongoDB"""
        data = self.model_dump(by_alias=True, exclude_unset=True)
        
        if exclude_id or ("_id" in data and data["_id"] is None):
            data.pop("_id", None)
            
        return data
    
    def confirm(self):
        """Konfirmasi transaksi"""
        self.status = TransactionStatus.CONFIRMED
        self.confirmed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def cancel(self):
        """Batalkan transaksi"""
        self.status = TransactionStatus.CANCELLED
        self.updated_at = datetime.utcnow()

class SavingsGoal(BaseModel):
    """Model untuk target tabungan untuk membeli sesuatu"""
    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }
    )
    
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    
    # Goal details
    item_name: str  # Nama barang yang ingin dibeli
    target_amount: float  # Jumlah target
    current_amount: float = 0.0  # Jumlah yang sudah terkumpul
    description: Optional[str] = None
    
    # Timeline
    target_date: Optional[datetime] = None  # Deadline target
    status: SavingsGoalStatus = SavingsGoalStatus.ACTIVE
    
    # Progress tracking
    monthly_target: Optional[float] = None  # Target bulanan (opsional)
    
    # Chat integration
    chat_message_id: Optional[str] = None
    conversation_id: Optional[str] = None
    
    # Metadata
    source: str = "chat"
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    @classmethod
    def from_mongo(cls, data: Dict[str, Any]) -> "SavingsGoal":
        """Mengkonversi data dari MongoDB ke SavingsGoal model"""
        if data is None:
            return None
        
        if "_id" in data and data["_id"] is not None:
            data["_id"] = str(data["_id"])
        elif "_id" not in data:
            data["_id"] = None
            
        return cls(**data)
    
    def to_mongo(self, exclude_id: bool = False) -> Dict[str, Any]:
        """Mengkonversi SavingsGoal model ke format MongoDB"""
        data = self.model_dump(by_alias=True, exclude_unset=True)
        
        if exclude_id or ("_id" in data and data["_id"] is None):
            data.pop("_id", None)
            
        return data
    
    @property
    def progress_percentage(self) -> float:
        """Hitung persentase progress"""
        if self.target_amount <= 0:
            return 0.0
        return min((self.current_amount / self.target_amount) * 100, 100.0)
    
    @property
    def remaining_amount(self) -> float:
        """Sisa jumlah yang perlu ditabung"""
        return max(self.target_amount - self.current_amount, 0.0)
    
    def add_savings(self, amount: float):
        """Tambah tabungan ke goal"""
        self.current_amount += amount
        self.updated_at = datetime.utcnow()
        
        # Check if goal completed
        if self.current_amount >= self.target_amount and self.status == SavingsGoalStatus.ACTIVE:
            self.status = SavingsGoalStatus.COMPLETED
            self.completed_at = datetime.utcnow()
    
    def subtract_savings(self, amount: float):
        """Kurangi tabungan dari goal"""
        self.current_amount = max(self.current_amount - amount, 0.0)
        self.updated_at = datetime.utcnow()
        
        # If was completed but now not enough, mark as active again
        if self.current_amount < self.target_amount and self.status == SavingsGoalStatus.COMPLETED:
            self.status = SavingsGoalStatus.ACTIVE
            self.completed_at = None

class FinancialSummary(BaseModel):
    """Model untuk ringkasan keuangan"""
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
    
    user_id: str
    period: str  # daily, weekly, monthly, yearly
    
    # Income data
    total_income: float = 0.0
    income_count: int = 0
    income_categories: Dict[str, float] = Field(default_factory=dict)
    
    # Expense data
    total_expense: float = 0.0
    expense_count: int = 0
    expense_categories: Dict[str, float] = Field(default_factory=dict)
    
    # Balance
    net_balance: float = 0.0  # income - expense
    
    # Savings goals
    active_goals_count: int = 0
    total_savings_target: float = 0.0
    total_savings_current: float = 0.0
    
    # Period info
    start_date: datetime
    end_date: datetime
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class PendingFinancialData(BaseModel):
    """Model untuk data keuangan yang menunggu konfirmasi dari chat"""
    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }
    )
    
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    conversation_id: str
    chat_message_id: str
    
    # Data type
    data_type: str  # "transaction" atau "savings_goal"
    
    # Parsed data
    parsed_data: Dict[str, Any]  # Data yang sudah di-parse dari chat
    
    # Original message
    original_message: str
    luna_response: str
    
    # Status
    is_confirmed: bool = False
    expires_at: datetime  # Expired jika tidak dikonfirmasi dalam waktu tertentu
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    confirmed_at: Optional[datetime] = None
    
    @classmethod
    def from_mongo(cls, data: Dict[str, Any]) -> "PendingFinancialData":
        """Mengkonversi data dari MongoDB ke PendingFinancialData model"""
        if data is None:
            return None
        
        if "_id" in data and data["_id"] is not None:
            data["_id"] = str(data["_id"])
        elif "_id" not in data:
            data["_id"] = None
            
        return cls(**data)
    
    def to_mongo(self, exclude_id: bool = False) -> Dict[str, Any]:
        """Mengkonversi PendingFinancialData model ke format MongoDB"""
        data = self.model_dump(by_alias=True, exclude_unset=True)
        
        if exclude_id or ("_id" in data and data["_id"] is None):
            data.pop("_id", None)
            
        return data