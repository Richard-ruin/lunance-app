from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum

# Request schemas
class CreateTransactionRequest(BaseModel):
    """Schema untuk membuat transaksi manual"""
    type: str  # "income" atau "expense"
    amount: float
    category: str
    description: Optional[str] = None
    date: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    
    @validator('amount')
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Jumlah harus lebih dari 0')
        return v
    
    @validator('type')
    def type_must_be_valid(cls, v):
        if v not in ['income', 'expense']:
            raise ValueError('Tipe harus "income" atau "expense"')
        return v

class CreateSavingsGoalRequest(BaseModel):
    """Schema untuk membuat target tabungan manual"""
    item_name: str
    target_amount: float
    description: Optional[str] = None
    target_date: Optional[datetime] = None
    monthly_target: Optional[float] = None
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    
    @validator('target_amount')
    def target_amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Target jumlah harus lebih dari 0')
        return v
    
    @validator('item_name')
    def item_name_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Nama barang tidak boleh kosong')
        return v.strip()

class UpdateSavingsGoalRequest(BaseModel):
    """Schema untuk update target tabungan"""
    item_name: Optional[str] = None
    target_amount: Optional[float] = None
    description: Optional[str] = None
    target_date: Optional[datetime] = None
    monthly_target: Optional[float] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    
    @validator('target_amount')
    def target_amount_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Target jumlah harus lebih dari 0')
        return v

class AddSavingsRequest(BaseModel):
    """Schema untuk menambah tabungan ke goal"""
    amount: float
    description: Optional[str] = None
    
    @validator('amount')
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Jumlah harus lebih dari 0')
        return v

class ConfirmFinancialDataRequest(BaseModel):
    """Schema untuk konfirmasi data keuangan dari chat"""
    pending_id: str
    confirmed: bool
    modifications: Optional[Dict[str, Any]] = None  # Jika user ingin modifikasi sebelum konfirmasi

# Response schemas
class TransactionResponse(BaseModel):
    """Schema response untuk transaksi"""
    id: str
    user_id: str
    type: str
    amount: float
    category: str
    description: Optional[str]
    date: datetime
    status: str
    source: str
    tags: List[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    confirmed_at: Optional[datetime]
    
    # Formatted fields untuk display
    formatted_amount: str
    formatted_date: str
    relative_date: str

class SavingsGoalResponse(BaseModel):
    """Schema response untuk target tabungan"""
    id: str
    user_id: str
    item_name: str
    target_amount: float
    current_amount: float
    description: Optional[str]
    target_date: Optional[datetime]
    status: str
    monthly_target: Optional[float]
    source: str
    tags: List[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    
    # Calculated fields
    progress_percentage: float
    remaining_amount: float
    
    # Formatted fields
    formatted_target_amount: str
    formatted_current_amount: str
    formatted_remaining_amount: str
    formatted_target_date: Optional[str]

class FinancialSummaryResponse(BaseModel):
    """Schema response untuk ringkasan keuangan"""
    user_id: str
    period: str
    
    # Income summary
    total_income: float
    income_count: int
    income_categories: Dict[str, float]
    formatted_total_income: str
    
    # Expense summary
    total_expense: float
    expense_count: int
    expense_categories: Dict[str, float]
    formatted_total_expense: str
    
    # Balance
    net_balance: float
    formatted_net_balance: str
    
    # Savings summary
    active_goals_count: int
    total_savings_target: float
    total_savings_current: float
    formatted_total_savings_target: str
    formatted_total_savings_current: str
    
    # Period info
    start_date: datetime
    end_date: datetime
    formatted_period: str
    generated_at: datetime

class PendingFinancialDataResponse(BaseModel):
    """Schema response untuk data keuangan yang pending"""
    id: str
    data_type: str
    parsed_data: Dict[str, Any]
    original_message: str
    luna_response: str
    expires_at: datetime
    created_at: datetime
    
    # Helper fields
    time_remaining: str
    formatted_expires_at: str

class ChatFinancialParseResult(BaseModel):
    """Schema untuk hasil parsing data keuangan dari chat"""
    is_financial_data: bool
    confidence: float  # 0.0 - 1.0
    data_type: Optional[str] = None  # "transaction", "savings_goal", "query"
    parsed_data: Optional[Dict[str, Any]] = None
    suggestions: List[str] = Field(default_factory=list)
    validation_errors: List[str] = Field(default_factory=list)

# Query schemas
class TransactionQueryParams(BaseModel):
    """Parameter query untuk transaksi"""
    type: Optional[str] = None  # income/expense
    category: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    search: Optional[str] = None
    limit: int = 50
    offset: int = 0
    sort_by: str = "date"
    sort_order: str = "desc"  # asc/desc

class SavingsGoalQueryParams(BaseModel):
    """Parameter query untuk target tabungan"""
    status: Optional[str] = None
    search: Optional[str] = None
    tags: Optional[List[str]] = None
    limit: int = 50
    offset: int = 0
    sort_by: str = "created_at"
    sort_order: str = "desc"

class FinancialStatsQueryParams(BaseModel):
    """Parameter untuk statistik keuangan"""
    period: str = "monthly"  # daily, weekly, monthly, yearly
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    include_pending: bool = False
    group_by_category: bool = True

# API Response wrapper
class FinanceApiResponse(BaseModel):
    """Wrapper response untuk semua endpoint finance"""
    success: bool
    message: str
    data: Optional[Any] = None
    errors: Optional[List[str]] = None
    meta: Optional[Dict[str, Any]] = None

class TransactionListResponse(BaseModel):
    """Response untuk list transaksi"""
    transactions: List[TransactionResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool

class SavingsGoalListResponse(BaseModel):
    """Response untuk list target tabungan"""
    savings_goals: List[SavingsGoalResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool