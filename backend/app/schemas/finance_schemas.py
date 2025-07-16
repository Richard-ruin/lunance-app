# app/schemas/finance_schemas.py - NEW schemas untuk 4 tabs system
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

# ==========================================
# TAB 1: DASHBOARD SCHEMAS
# ==========================================

class BudgetAllocation(BaseModel):
    """Schema untuk alokasi budget 50/30/20"""
    budget: float
    spent: float
    remaining: float
    percentage_used: float
    status: str  # "under", "over", "on_track"
    formatted_budget: str
    formatted_spent: str
    formatted_remaining: str

class DashboardOverview(BaseModel):
    """Schema untuk dashboard overview"""
    method: str = "50/30/20 Elizabeth Warren"
    current_month: str
    setup_completed: bool
    budget_overview: Dict[str, Any]
    financial_summary: Dict[str, Any]
    budget_health: Dict[str, Any]
    wants_savings_goals: Dict[str, Any]
    recent_activity: Dict[str, Any]
    quick_actions: List[Dict[str, Any]]
    next_reset: str
    timezone: str

class QuickStats(BaseModel):
    """Schema untuk quick stats widget"""
    real_total_savings: float
    formatted_savings: str
    monthly_income: float
    formatted_income: str
    current_month_spending: Dict[str, float]
    formatted_spending: Dict[str, str]
    budget_allocation: Dict[str, float]

# ==========================================
# TAB 2: ANALYTICS SCHEMAS
# ==========================================

class BudgetVsActual(BaseModel):
    """Schema untuk perbandingan budget vs actual"""
    budget: float
    actual: float
    variance: float
    percentage: float

class CategoryAnalysis(BaseModel):
    """Schema untuk analisis kategori"""
    amount: float
    formatted_amount: str
    percentage: float
    budget_type: str
    budget_type_color: str

class FinancialHealth(BaseModel):
    """Schema untuk financial health assessment"""
    health_score: float
    health_level: str  # excellent, good, fair, needs_improvement
    savings_rate: float
    income_expense_ratio: float
    net_balance: float
    formatted_net_balance: str

class AnalyticsResponse(BaseModel):
    """Schema untuk analytics response"""
    period: str
    period_display: str
    date_range: Dict[str, str]
    budget_performance: Dict[str, Any]
    category_breakdown: Dict[str, Any]
    financial_health: FinancialHealth
    insights: List[str]
    recommendations: List[str]
    summary: Dict[str, Any]

class ChartData(BaseModel):
    """Schema untuk chart data"""
    type: str  # bar, pie, line
    labels: List[str]
    datasets: List[Dict[str, Any]]

# ==========================================
# TAB 3: HISTORY SCHEMAS
# ==========================================

class TransactionHistory(BaseModel):
    """Schema untuk transaction history item"""
    id: str
    type: str  # income, expense
    amount: float
    formatted_amount: str
    category: str
    budget_type: str
    budget_type_color: str
    description: str
    date: str
    formatted_date: str
    formatted_time: str
    relative_date: str
    status: str
    source: str
    tags: List[str]

class SavingsGoalHistory(BaseModel):
    """Schema untuk savings goal history"""
    id: str
    type: str = "savings_goal"
    item_name: str
    target_amount: float
    current_amount: float
    progress_percentage: float
    status: str
    target_date: Optional[str]
    days_remaining: Optional[int]
    formatted_target: str
    formatted_current: str
    budget_source: str = "wants_30_percent"
    created_at: str

class HistorySummary(BaseModel):
    """Schema untuk history summary"""
    total_income: float
    total_expense: float
    net_balance: float
    formatted_income: str
    formatted_expense: str
    formatted_net: str
    transaction_count: int
    budget_breakdown: Dict[str, Dict[str, Any]]

class HistoryFilters(BaseModel):
    """Schema untuk history filters"""
    type: Optional[str] = None
    budget_type: Optional[str] = None
    category: Optional[str] = None
    date_range: Optional[str] = None
    search: Optional[str] = None

class Pagination(BaseModel):
    """Schema untuk pagination"""
    current_page: int
    per_page: int
    total_items: int
    has_next: bool
    has_prev: bool

class HistoryResponse(BaseModel):
    """Schema untuk history response"""
    items: List[Any]  # TransactionHistory atau SavingsGoalHistory
    summary: HistorySummary
    filters_applied: HistoryFilters
    pagination: Pagination
    available_filters: Dict[str, Any]

# ==========================================
# EXPORT SCHEMAS
# ==========================================

class ExportRequest(BaseModel):
    """Schema untuk export request"""
    format: str = Field("csv", description="csv, json, excel")
    type: Optional[str] = Field(None, description="income, expense, goals, all")
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    include_summary: bool = True
    include_charts: bool = False

class ExportResponse(BaseModel):
    """Schema untuk export response"""
    user_info: Dict[str, Any]
    transactions: List[Dict[str, Any]]
    summary: Dict[str, Any]
    download_info: Dict[str, Any]

# ==========================================
# BUDGET MANAGEMENT SCHEMAS
# ==========================================

class BudgetStatus(BaseModel):
    """Schema untuk budget status"""
    has_budget: bool
    method: str = "50/30/20 Elizabeth Warren"
    current_month: str
    budget_allocation: Dict[str, float]
    current_spending: Dict[str, float]
    remaining_budget: Dict[str, float]
    percentage_used: Dict[str, float]
    budget_health: str
    recommendations: List[str]
    reset_date: str

class BudgetResetRequest(BaseModel):
    """Schema untuk budget reset request"""
    force: bool = False
    reason: Optional[str] = None

class BudgetResetResponse(BaseModel):
    """Schema untuk budget reset response"""
    success: bool
    message: str
    reset_time: str
    budget_allocation: Dict[str, Any]

# ==========================================
# FINANCIAL SETTINGS SCHEMAS
# ==========================================

class FinancialSettingsUpdate(BaseModel):
    """Schema untuk update financial settings"""
    current_savings: Optional[float] = Field(None, ge=0)
    monthly_income: Optional[float] = Field(None, gt=0)
    primary_bank: Optional[str] = None

class FinancialOverview(BaseModel):
    """Schema untuk financial overview"""
    has_financial_setup: bool
    budget_method: str = "50/30/20 Elizabeth Warren"
    user_profile: Dict[str, Any]
    budget_allocation: Dict[str, Any]
    financial_dashboard: Dict[str, Any]
    student_context: Dict[str, Any]
    student_tips: List[str]
    method_explanation: Dict[str, str]

# ==========================================
# CATEGORY SCHEMAS
# ==========================================

class CategoryInfo(BaseModel):
    """Schema untuk category information"""
    name: str
    description: str
    keywords: List[str]
    budget_type: str
    essential: bool

class CategoriesByType(BaseModel):
    """Schema untuk categories grouped by budget type"""
    needs: List[str]
    wants: List[str]
    savings: List[str]
    income: List[str]

class BudgetAllocationGuide(BaseModel):
    """Schema untuk budget allocation guide"""
    method: str
    description: str
    allocation: Dict[str, Dict[str, Any]]
    reset_schedule: str
    flexibility: str

class CategoriesResponse(BaseModel):
    """Schema untuk categories response"""
    method: str
    categories_by_budget_type: CategoriesByType
    budget_allocation_guide: BudgetAllocationGuide
    total_categories: Dict[str, int]

# ==========================================
# API RESPONSE WRAPPERS
# ==========================================

class ApiResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool
    message: str
    data: Optional[Any] = None
    errors: Optional[List[str]] = None

class PaginatedApiResponse(BaseModel):
    """Paginated API response wrapper"""
    success: bool
    message: str
    data: Dict[str, Any]
    pagination: Pagination
    filters: Optional[Dict[str, Any]] = None

# ==========================================
# VALIDATION SCHEMAS
# ==========================================

class DateRangeRequest(BaseModel):
    """Schema untuk date range request"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    period: str = Field("monthly", description="daily, weekly, monthly, yearly")

class FilterRequest(BaseModel):
    """Schema untuk filter request"""
    type: Optional[str] = None
    budget_type: Optional[str] = None
    category: Optional[str] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    search: Optional[str] = None

class SortRequest(BaseModel):
    """Schema untuk sort request"""
    sort_by: str = Field("date", description="date, amount, category")
    sort_order: str = Field("desc", description="asc, desc")

# ==========================================
# ERROR SCHEMAS
# ==========================================

class ValidationError(BaseModel):
    """Schema untuk validation error"""
    field: str
    message: str
    value: Any

class ErrorResponse(BaseModel):
    """Schema untuk error response"""
    success: bool = False
    message: str
    errors: List[ValidationError]
    error_code: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

# ==========================================
# TRANSACTION & SAVINGS GOAL SCHEMAS
# ==========================================

class CreateTransactionRequest(BaseModel):
    """Schema untuk create transaction request"""
    type: str = Field(..., description="income atau expense")
    amount: float = Field(..., gt=0)
    category: str
    description: str = Field(..., min_length=1, max_length=200)
    date: Optional[datetime] = None
    tags: Optional[List[str]] = []
    notes: Optional[str] = None

class CreateSavingsGoalRequest(BaseModel):
    """Schema untuk create savings goal request"""
    item_name: str = Field(..., min_length=1, max_length=100)
    target_amount: float = Field(..., gt=0)
    target_date: Optional[datetime] = None
    description: Optional[str] = None
    monthly_target: Optional[float] = None

class UpdateSavingsGoalRequest(BaseModel):
    """Schema untuk update savings goal request"""
    item_name: Optional[str] = None
    target_amount: Optional[float] = Field(None, gt=0)
    target_date: Optional[datetime] = None
    description: Optional[str] = None
    monthly_target: Optional[float] = None
    status: Optional[str] = None

class AddSavingsRequest(BaseModel):
    """Schema untuk add savings to goal request"""
    amount: float = Field(..., gt=0, description="Jumlah yang ditambahkan ke target")
    note: Optional[str] = None