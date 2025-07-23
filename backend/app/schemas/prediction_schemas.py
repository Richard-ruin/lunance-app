# app/schemas/prediction_schemas.py - Schemas untuk Financial Predictions API
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field

# ==========================================
# BASE PREDICTION SCHEMAS
# ==========================================

class PredictionRequest(BaseModel):
    """Base schema untuk prediction requests"""
    forecast_days: int = Field(30, ge=7, le=90, description="Periode prediksi dalam hari")
    include_confidence_interval: bool = Field(True, description="Include confidence intervals")
    seasonality_mode: str = Field("multiplicative", description="Prophet seasonality mode")

class ModelPerformance(BaseModel):
    """Schema untuk model performance metrics"""
    mae: float = Field(description="Mean Absolute Error")
    mape: float = Field(description="Mean Absolute Percentage Error")
    rmse: float = Field(description="Root Mean Square Error")
    accuracy_score: float = Field(description="Accuracy score (100 - MAPE)")
    r2_score: float = Field(description="R-squared score")
    data_points: int = Field(description="Number of data points used")

class PredictionPoint(BaseModel):
    """Schema untuk single prediction point"""
    ds: datetime = Field(description="Date")
    yhat: float = Field(description="Predicted value")
    yhat_lower: float = Field(description="Lower confidence bound")
    yhat_upper: float = Field(description="Upper confidence bound")
    formatted_date: Optional[str] = None
    formatted_value: Optional[str] = None

class BudgetPredictionPoint(PredictionPoint):
    """Extended prediction point dengan budget analysis"""
    daily_budget: Optional[float] = None
    budget_status: Optional[str] = None  # "within_budget", "over_budget"
    budget_usage_percentage: Optional[float] = None
    formatted_daily_budget: Optional[str] = None

# ==========================================
# INCOME PREDICTION SCHEMAS
# ==========================================

class IncomePredictionRequest(PredictionRequest):
    """Schema untuk income prediction request"""
    include_income_sources: bool = Field(False, description="Include breakdown by income source")

class IncomePredictionSummary(BaseModel):
    """Summary hasil prediksi income"""
    total_predicted_income: float
    average_daily_income: float
    formatted_total: str
    formatted_daily_avg: str
    confidence_level: str  # "Tinggi", "Menengah", "Rendah"

class IncomePredictionResponse(BaseModel):
    """Complete response untuk income prediction"""
    method: str = "Prophet AI Time Series Forecasting"
    prediction_type: str = "income"
    forecast_period: str
    generated_at: str
    
    prediction_summary: IncomePredictionSummary
    historical_analysis: Dict[str, Any]
    daily_predictions: List[PredictionPoint]
    model_performance: ModelPerformance
    ai_insights: List[str]
    recommendations: List[str]
    student_context: Dict[str, Any]

# ==========================================
# EXPENSE PREDICTION SCHEMAS
# ==========================================

class ExpensePredictionRequest(PredictionRequest):
    """Schema untuk expense prediction request"""
    budget_type: str = Field(description="needs, wants, or savings")

class BudgetAllocation(BaseModel):
    """Schema untuk budget allocation info"""
    has_budget: bool
    monthly_income: Optional[float] = None
    budget_percentage: Optional[float] = None
    budget_amount: Optional[float] = None
    formatted_budget: Optional[str] = None

class ExpensePredictionSummary(BaseModel):
    """Summary hasil prediksi expense"""
    total_predicted_expense: float
    average_daily_expense: float
    formatted_total: str
    formatted_daily_avg: str

class ExpensePredictionResponse(BaseModel):
    """Complete response untuk expense prediction"""
    method: str = "Prophet AI + 50/30/20 Budget Analysis"
    prediction_type: str
    budget_type: str
    forecast_period: str
    generated_at: str
    
    prediction_summary: ExpensePredictionSummary
    budget_analysis: Dict[str, Any]
    historical_analysis: Dict[str, Any]
    daily_predictions: List[BudgetPredictionPoint]
    model_performance: ModelPerformance
    ai_insights: List[str]
    budget_recommendations: List[str]
    category_context: Dict[str, Any]

# ==========================================
# BUDGET PERFORMANCE SCHEMAS
# ==========================================

class BudgetComparisonItem(BaseModel):
    """Comparison item untuk target vs predicted"""
    target: float
    predicted: float
    variance: float
    status: str  # "over", "under", "on_track"

class BudgetComparison(BaseModel):
    """Complete budget comparison untuk 50/30/20"""
    needs: BudgetComparisonItem
    wants: BudgetComparisonItem
    savings: BudgetComparisonItem

class BudgetHealth(BaseModel):
    """Budget health assessment"""
    health_level: str  # "excellent", "good", "fair", "poor"
    health_score: float
    average_variance: float
    individual_variances: Dict[str, float]

class PredictedTotals(BaseModel):
    """Predicted financial totals"""
    income: float
    expense: float
    net_balance: float
    needs_expense: float
    wants_expense: float
    savings_expense: float

class FormattedTotals(BaseModel):
    """Formatted versions of predicted totals"""
    income: str
    expense: str
    net_balance: str
    needs_expense: str
    wants_expense: str
    savings_expense: str

class BudgetPerformancePredictionResponse(BaseModel):
    """Complete response untuk budget performance prediction"""
    method: str = "Prophet AI + 50/30/20 Elizabeth Warren Analysis"
    prediction_type: str = "comprehensive_budget_performance"
    forecast_period: str
    generated_at: str
    
    prediction_summary: Dict[str, Any]
    budget_analysis_50_30_20: Dict[str, Any]
    detailed_predictions: Dict[str, Any]
    ai_analysis: Dict[str, Any]
    student_guidance: Dict[str, Any]

# ==========================================
# SAVINGS GOAL SCHEMAS
# ==========================================

class SavingsGoalInfo(BaseModel):
    """Info tentang savings goal"""
    item_name: str
    target_amount: float
    current_amount: float
    remaining_amount: float
    progress_percentage: float

class SavingsScenario(BaseModel):
    """Scenario untuk savings achievement"""
    monthly_rate: float
    months_needed: float
    achievement_date: str
    formatted_rate: str
    additional_required: Optional[float] = None
    formatted_additional: Optional[str] = None

class SavingsAchievementPrediction(BaseModel):
    """Prediction hasil untuk savings achievement"""
    monthly_savings_rate: float
    months_needed: float
    estimated_achievement_date: str
    formatted_monthly_rate: str
    formatted_achievement_date: str

class SavingsGoalPredictionResponse(BaseModel):
    """Complete response untuk savings goal prediction"""
    method: str = "Prophet AI Savings Pattern Analysis"
    prediction_type: str = "savings_goal_achievement"
    generated_at: str
    
    goal_info: SavingsGoalInfo
    formatted_amounts: Dict[str, str]
    achievement_status: str
    achievement_prediction: SavingsAchievementPrediction
    achievement_scenarios: Dict[str, SavingsScenario]
    acceleration_strategies: Dict[str, Any]
    student_guidance: Dict[str, Any]

# ==========================================
# ANALYTICS SCHEMAS
# ==========================================

class PredictionSummary(BaseModel):
    """Summary status prediksi"""
    income_prediction_available: bool
    budget_prediction_available: bool
    data_quality: str  # "good", "limited", "poor"

class IncomeInsights(BaseModel):
    """Insights untuk income analytics"""
    predicted_monthly: float
    confidence: float
    recommendations: List[str]

class BudgetInsights(BaseModel):
    """Insights untuk budget analytics"""
    health_score: float
    predicted_allocations: Dict[str, float]
    optimization_opportunities: List[str]

class PredictionAnalyticsResponse(BaseModel):
    """Complete response untuk prediction analytics"""
    method: str = "Prophet AI Comprehensive Analytics"
    analytics_type: str = "comprehensive_prediction_analytics"
    generated_at: str
    
    user_info: Dict[str, Any]
    prediction_summary: PredictionSummary
    income_analytics: Optional[IncomeInsights] = None
    budget_analytics: Optional[BudgetInsights] = None
    ai_recommendations: Dict[str, List[str]]
    student_guidance: Dict[str, Any]

# ==========================================
# HISTORY SCHEMAS
# ==========================================

class PredictionHistoryItem(BaseModel):
    """Single item dalam prediction history"""
    prediction_id: str
    prediction_type: str
    created_at: datetime
    forecast_period: int
    predicted_value: float
    actual_value: Optional[float] = None
    accuracy: Optional[float] = None
    status: str  # "pending", "completed", "evaluated"

class PredictionHistorySummary(BaseModel):
    """Summary untuk prediction history"""
    total_predictions_made: int
    average_accuracy: float
    best_performing_type: str
    improvement_trend: str  # "improving", "stable", "declining"

class PredictionHistoryResponse(BaseModel):
    """Complete response untuk prediction history"""
    method: str = "Prediction History Analysis"
    history_type: str = "prediction_accuracy_tracking"
    generated_at: str
    
    history_summary: PredictionHistorySummary
    prediction_history: List[PredictionHistoryItem]
    implementation_notes: Dict[str, Any]
    next_steps: List[str]

# ==========================================
# INFO SCHEMAS
# ==========================================

class PredictionCapability(BaseModel):
    """Capability info untuk prediction type"""
    description: str
    min_data_required: str
    forecast_range: str
    accuracy_typical: str

class DataRequirements(BaseModel):
    """Data requirements untuk prediksi"""
    minimum_transactions: Dict[str, Union[int, str]]
    optimal_data: Dict[str, Union[int, str]]

class PredictionInfoResponse(BaseModel):
    """Complete response untuk prediction info"""
    prediction_system: Dict[str, str]
    capabilities: Dict[str, PredictionCapability]
    data_requirements: DataRequirements
    accuracy_factors: Dict[str, str]
    usage_tips: Dict[str, List[str]]
    technical_details: Dict[str, str]

# ==========================================
# ERROR SCHEMAS
# ==========================================

class PredictionError(BaseModel):
    """Schema untuk prediction errors"""
    error_type: str
    message: str
    suggestion: Optional[str] = None
    min_required_data: Optional[int] = None
    current_data_points: Optional[int] = None

class PredictionErrorResponse(BaseModel):
    """Error response untuk predictions"""
    success: bool = False
    message: str
    error: Optional[str] = None
    suggestion: Optional[str] = None
    data: Dict[str, Any]

# ==========================================
# API RESPONSE WRAPPERS
# ==========================================

class PredictionApiResponse(BaseModel):
    """Standard API response wrapper untuk predictions"""
    success: bool
    message: str
    data: Union[
        IncomePredictionResponse,
        ExpensePredictionResponse, 
        BudgetPerformancePredictionResponse,
        SavingsGoalPredictionResponse,
        PredictionAnalyticsResponse,
        PredictionHistoryResponse,
        PredictionInfoResponse,
        Dict[str, Any]
    ]

# ==========================================
# VALIDATION SCHEMAS
# ==========================================

class BudgetTypeValidator(BaseModel):
    """Validator untuk budget type"""
    budget_type: str = Field(regex="^(needs|wants|savings)$")

class ForecastPeriodValidator(BaseModel):
    """Validator untuk forecast period"""
    forecast_days: int = Field(ge=7, le=90)

class GoalIdValidator(BaseModel):
    """Validator untuk goal ID"""
    goal_id: str = Field(min_length=24, max_length=24)

# ==========================================
# UTILITY FUNCTIONS
# ==========================================

def format_prediction_confidence(accuracy_score: float) -> str:
    """Format confidence level berdasarkan accuracy score"""
    if accuracy_score >= 85:
        return "Tinggi"
    elif accuracy_score >= 70:
        return "Menengah"
    else:
        return "Rendah"

def format_budget_status(percentage_used: float) -> str:
    """Format budget status berdasarkan percentage used"""
    if percentage_used > 100:
        return "over_budget"
    elif percentage_used > 80:
        return "warning"
    elif percentage_used > 50:
        return "good"
    else:
        return "excellent"

def format_health_level(health_score: float) -> str:
    """Format health level berdasarkan score"""
    if health_score >= 80:
        return "excellent"
    elif health_score >= 60:
        return "good"
    elif health_score >= 40:
        return "fair"
    else:
        return "poor"