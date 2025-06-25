from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId
from app.models.base import PyObjectId


class PredictionImpact(BaseModel):
    monthly_expense_increase: float
    duration_months: int
    special_conditions: Optional[str] = None  # "double payment di bulan gaji"


class DebtLoan(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    student_id: PyObjectId
    
    # Debt Details
    debt_type: str  # personal_loan, credit_card, pinjaman_teman, kredit_barang
    creditor_name: str  # "Teman", "Bank", "Shopee PayLater"
    
    # Financial Details
    principal_amount: float
    current_balance: float
    interest_rate: float = 0.0  # 0 for teman
    
    # Repayment Schedule
    monthly_payment: float
    payment_day: int  # day of month (1-31)
    remaining_payments: int
    
    # Dates
    loan_date: datetime
    due_date: datetime
    next_payment_date: datetime
    
    # Status
    status: str = "active"  # active, paid_off, overdue, restructured
    
    # Impact on Predictions
    affects_predictions: bool = True
    prediction_impact: Optional[PredictionImpact] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DebtLoanInDB(DebtLoan):
    pass


class DebtLoanCreate(BaseModel):
    debt_type: str
    creditor_name: str
    principal_amount: float
    current_balance: float
    interest_rate: float = 0.0
    monthly_payment: float
    payment_day: int
    remaining_payments: int
    loan_date: datetime
    due_date: datetime
    next_payment_date: datetime
    affects_predictions: bool = True
    prediction_impact: Optional[PredictionImpact] = None


class DebtLoanUpdate(BaseModel):
    debt_type: Optional[str] = None
    creditor_name: Optional[str] = None
    current_balance: Optional[float] = None
    interest_rate: Optional[float] = None
    monthly_payment: Optional[float] = None
    payment_day: Optional[int] = None
    remaining_payments: Optional[int] = None
    due_date: Optional[datetime] = None
    next_payment_date: Optional[datetime] = None
    status: Optional[str] = None
    affects_predictions: Optional[bool] = None
    prediction_impact: Optional[PredictionImpact] = None


class PaymentRecord(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    debt_id: PyObjectId
    student_id: PyObjectId
    payment_amount: float
    payment_date: datetime
    remaining_balance: float
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PaymentRecordCreate(BaseModel):
    debt_id: PyObjectId
    payment_amount: float
    payment_date: datetime
    notes: Optional[str] = None