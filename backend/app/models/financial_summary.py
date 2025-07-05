# app/models/financial_summary.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from .base import BaseDocument, PyObjectId

class CategorySummary(BaseModel):
    category_id: str
    nama_kategori: str
    total_amount: float
    percentage: float
    transaction_count: int

class FinancialSummary(BaseDocument):
    user_id: PyObjectId
    period: str  # "daily", "weekly", "monthly"
    date: datetime
    total_pemasukan: float
    total_pengeluaran: float
    balance: float
    top_categories: List[CategorySummary]
    transaction_count: int

class DashboardSummary(BaseModel):
    current_balance: float
    monthly_income: float
    monthly_expense: float
    monthly_savings: float
    savings_rate: float  # percentage
    vs_last_month: dict
    total_transactions: int
    active_goals: int
    total_saved_goals: float

class QuickStats(BaseModel):
    today_income: float
    today_expense: float
    week_income: float
    week_expense: float
    month_income: float
    month_expense: float
    balance_trend: str  # "up", "down", "stable"

class MonthlyComparison(BaseModel):
    current_month: dict
    previous_month: dict
    income_change: float  # percentage
    expense_change: float
    savings_change: float