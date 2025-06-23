from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId


class FinancialImpact(BaseModel):
    multiplier: float = Field(..., description="Financial impact multiplier")
    delay_days: Optional[int] = Field(None, description="Days after event for income impact")
    preparation_days: Optional[int] = Field(None, description="Days before event for expense impact")
    affected_categories: List[str] = Field(default_factory=list)


class AdditionalExpense(BaseModel):
    category: str = Field(..., description="Expense category")
    estimated_amount: float = Field(..., description="Estimated expense amount")
    frequency: str = Field(..., description="Frequency during event")


class ExpenseImpact(FinancialImpact):
    preparation_days: Optional[int] = Field(None, description="Expenses start X days before event")
    typical_additional_expenses: List[AdditionalExpense] = Field(default_factory=list)


class IncomeImpact(FinancialImpact):
    delay_days: Optional[int] = Field(None, description="Income comes X days after event")


class BehavioralChanges(BaseModel):
    transaction_frequency_change: float = Field(1.0, description="Change in transaction frequency")
    category_preference_shifts: Dict[str, Any] = Field(default_factory=dict)
    location_based_changes: List[str] = Field(default_factory=list)


class AcademicEvent(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    event_name: str = Field(..., description="Name of the academic event")
    event_type: str = Field(..., description="Type of event: exam, holiday, registration, graduation")
    university: str = Field(..., description="Specific university or 'general'")
    
    # Timing (recurring yearly)
    typical_start_date: str = Field(..., description="Typical start date in YYYY-MM-DD format")
    typical_end_date: str = Field(..., description="Typical end date in YYYY-MM-DD format")
    duration_days: int = Field(..., description="Duration in days")
    
    # Financial Impact Patterns
    income_impact: IncomeImpact = Field(default_factory=IncomeImpact)
    expense_impact: ExpenseImpact = Field(default_factory=ExpenseImpact)
    
    # Student Behavior Patterns
    behavioral_changes: BehavioralChanges = Field(default_factory=BehavioralChanges)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(True)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}