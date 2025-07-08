# app/models/prediction.py
"""Financial prediction models and schemas - FIXED VERSION."""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from datetime import date as date_type  # Alias to avoid conflicts
from enum import Enum


class PredictionType(str, Enum):
    """Prediction type enumeration."""
    INCOME = "income"
    EXPENSE = "expense"
    SAVINGS = "savings"
    CATEGORY = "category"
    BALANCE = "balance"
    GOAL_ACHIEVEMENT = "goal_achievement"


class PredictionPeriod(str, Enum):
    """Prediction period enumeration."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class PredictionAlgorithm(str, Enum):
    """Prediction algorithm enumeration."""
    PROPHET = "prophet"
    LINEAR_REGRESSION = "linear_regression"
    MOVING_AVERAGE = "moving_average"
    SEASONAL_DECOMPOSITION = "seasonal_decomposition"
    ARIMA = "arima"


class PredictionRequest(BaseModel):
    """Request for financial prediction."""
    prediction_type: PredictionType = Field(..., description="Type of prediction")
    period: PredictionPeriod = Field(..., description="Prediction period")
    periods_ahead: int = Field(..., ge=1, le=365, description="Number of periods to predict")
    category_id: Optional[str] = Field(None, description="Category ID for category-specific predictions")
    algorithm: PredictionAlgorithm = Field(default=PredictionAlgorithm.PROPHET, description="Algorithm to use")
    include_confidence_intervals: bool = Field(default=True, description="Include confidence intervals")
    seasonality: bool = Field(default=True, description="Include seasonal patterns")

    @field_validator('periods_ahead')
    @classmethod
    def validate_periods_ahead(cls, v: int, info) -> int:
        """Validate periods ahead based on period type."""
        if hasattr(info, 'data') and info.data and 'period' in info.data:
            period = info.data['period']
            max_periods = {
                PredictionPeriod.DAILY: 90,
                PredictionPeriod.WEEKLY: 52,
                PredictionPeriod.MONTHLY: 24,
                PredictionPeriod.QUARTERLY: 8,
                PredictionPeriod.YEARLY: 5
            }
            
            if v > max_periods.get(period, 365):
                raise ValueError(f'Too many periods for {period} prediction')
        
        return v


class PredictionPoint(BaseModel):
    """Single prediction point."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )
    
    prediction_date: date_type = Field(..., description="Prediction date")
    predicted_value: float = Field(..., description="Predicted value")
    lower_bound: Optional[float] = Field(None, description="Lower confidence bound")
    upper_bound: Optional[float] = Field(None, description="Upper confidence bound")
    confidence: float = Field(..., ge=0, le=1, description="Prediction confidence")
    is_anomaly: bool = Field(default=False, description="Whether value is anomalous")


class PredictionResponse(BaseModel):
    """Financial prediction response."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )
    
    prediction_id: str = Field(..., description="Prediction ID")
    user_id: str = Field(..., description="User ID")
    prediction_type: PredictionType = Field(..., description="Type of prediction")
    period: PredictionPeriod = Field(..., description="Prediction period")
    algorithm_used: PredictionAlgorithm = Field(..., description="Algorithm used")
    category_id: Optional[str] = Field(None, description="Category ID if applicable")
    category_name: Optional[str] = Field(None, description="Category name if applicable")
    
    # Prediction data
    predictions: List[PredictionPoint] = Field(..., description="Prediction points")
    summary: Dict[str, Any] = Field(..., description="Prediction summary")
    
    # Model metrics
    model_accuracy: float = Field(..., ge=0, le=1, description="Model accuracy score")
    mean_absolute_error: Optional[float] = Field(None, description="Mean absolute error")
    r_squared: Optional[float] = Field(None, description="R-squared score")
    
    # Metadata
    data_points_used: int = Field(..., description="Number of historical data points used")
    training_period_start: date_type = Field(..., description="Training period start date")
    training_period_end: date_type = Field(..., description="Training period end date")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    expires_at: datetime = Field(..., description="When prediction expires")


# FIXED: Changed "IncomePredictin" to "IncomePrediction"
class IncomePrediction(BaseModel):
    """Income prediction specific response."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )
    
    prediction_response: PredictionResponse = Field(..., description="Base prediction response")
    income_sources: List[Dict[str, Any]] = Field(..., description="Income sources breakdown")
    seasonal_patterns: Dict[str, Any] = Field(..., description="Seasonal income patterns")
    growth_rate: float = Field(..., description="Monthly growth rate")
    stability_score: float = Field(..., ge=0, le=1, description="Income stability score")


class ExpensePrediction(BaseModel):
    """Expense prediction specific response."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )
    
    prediction_response: PredictionResponse = Field(..., description="Base prediction response")
    category_breakdown: List[Dict[str, Any]] = Field(..., description="Expense by category")
    spending_trends: Dict[str, Any] = Field(..., description="Spending trend analysis")
    budget_recommendations: List[str] = Field(..., description="Budget recommendations")
    cost_optimization_opportunities: List[str] = Field(..., description="Cost optimization suggestions")


class SavingsPrediction(BaseModel):
    """Savings prediction specific response."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )
    
    prediction_response: PredictionResponse = Field(..., description="Base prediction response")
    savings_rate: float = Field(..., description="Predicted savings rate")
    goal_achievement_dates: Dict[str, date_type] = Field(..., description="Goal achievement predictions")
    savings_optimization_tips: List[str] = Field(..., description="Savings optimization tips")
    emergency_fund_timeline: Optional[Dict[str, Any]] = Field(None, description="Emergency fund timeline")


class CategoryPrediction(BaseModel):
    """Category-specific prediction response."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )
    
    prediction_response: PredictionResponse = Field(..., description="Base prediction response")
    category_trends: Dict[str, Any] = Field(..., description="Category-specific trends")
    peer_comparison: Optional[Dict[str, Any]] = Field(None, description="Comparison with similar users")
    optimization_suggestions: List[str] = Field(..., description="Category optimization suggestions")


class AnomalyDetection(BaseModel):
    """Anomaly detection in spending patterns."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )
    
    detection_id: str = Field(..., description="Detection ID")
    user_id: str = Field(..., description="User ID")
    anomaly_type: str = Field(..., description="Type of anomaly")
    description: str = Field(..., description="Anomaly description")
    severity: str = Field(..., description="Severity level (low/medium/high)")
    affected_period: str = Field(..., description="Affected time period")
    suggested_actions: List[str] = Field(..., description="Suggested actions")
    confidence: float = Field(..., ge=0, le=1, description="Detection confidence")
    detected_at: datetime = Field(default_factory=datetime.utcnow, description="Detection timestamp")


class PredictionAccuracy(BaseModel):
    """Prediction accuracy tracking."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )
    
    prediction_id: str = Field(..., description="Original prediction ID")
    actual_value: float = Field(..., description="Actual observed value")
    predicted_value: float = Field(..., description="Originally predicted value")
    absolute_error: float = Field(..., description="Absolute error")
    percentage_error: float = Field(..., description="Percentage error")
    observation_date: date_type = Field(..., description="Date of comparison")
    updated_accuracy: float = Field(..., ge=0, le=1, description="Updated model accuracy")


class ModelPerformance(BaseModel):
    """Model performance metrics."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )
    
    algorithm: PredictionAlgorithm = Field(..., description="Algorithm used")
    prediction_type: PredictionType = Field(..., description="Prediction type")
    accuracy_score: float = Field(..., ge=0, le=1, description="Overall accuracy")
    mean_absolute_error: float = Field(..., description="Mean absolute error")
    root_mean_square_error: float = Field(..., description="Root mean square error")
    r_squared: float = Field(..., description="R-squared score")
    predictions_made: int = Field(..., description="Total predictions made")
    last_updated: datetime = Field(..., description="Last update timestamp")


class PredictionSettings(BaseModel):
    """User prediction settings."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )
    
    user_id: str = Field(..., description="User ID")
    default_algorithm: PredictionAlgorithm = Field(default=PredictionAlgorithm.PROPHET, description="Default algorithm")
    auto_predictions: bool = Field(default=True, description="Enable automatic predictions")
    prediction_frequency: str = Field(default="weekly", description="Prediction update frequency")
    notification_enabled: bool = Field(default=True, description="Enable prediction notifications")
    confidence_threshold: float = Field(default=0.7, ge=0, le=1, description="Minimum confidence for notifications")
    categories_to_predict: List[str] = Field(default=[], description="Categories to include in predictions")
    advanced_features: bool = Field(default=False, description="Enable advanced prediction features")


class TrendAnalysis(BaseModel):
    """Financial trend analysis."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )
    
    analysis_id: str = Field(..., description="Analysis ID")
    user_id: str = Field(..., description="User ID")
    period: str = Field(..., description="Analysis period")
    trends: Dict[str, Any] = Field(..., description="Identified trends")
    insights: List[str] = Field(..., description="Key insights")
    recommendations: List[str] = Field(..., description="Recommendations")
    confidence: float = Field(..., ge=0, le=1, description="Analysis confidence")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")


class ForecastComparison(BaseModel):
    """Comparison between different forecasting models."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )
    
    user_id: str = Field(..., description="User ID")
    prediction_type: PredictionType = Field(..., description="Prediction type")
    models_compared: List[PredictionAlgorithm] = Field(..., description="Models compared")
    accuracy_comparison: Dict[str, float] = Field(..., description="Accuracy by model")
    best_model: PredictionAlgorithm = Field(..., description="Best performing model")
    recommendation_reason: str = Field(..., description="Why this model is recommended")
    comparison_date: datetime = Field(default_factory=datetime.utcnow, description="Comparison timestamp")


class SeasonalPattern(BaseModel):
    """Seasonal spending pattern analysis."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )
    
    pattern_id: str = Field(..., description="Pattern ID")
    user_id: str = Field(..., description="User ID")
    category_id: Optional[str] = Field(None, description="Category ID")
    pattern_type: str = Field(..., description="Pattern type (weekly/monthly/yearly)")
    seasonal_factors: Dict[str, float] = Field(..., description="Seasonal multiplication factors")
    peak_periods: List[str] = Field(..., description="Peak spending periods")
    low_periods: List[str] = Field(..., description="Low spending periods")
    volatility_score: float = Field(..., ge=0, le=1, description="Pattern volatility")
    reliability_score: float = Field(..., ge=0, le=1, description="Pattern reliability")


# Default prediction configurations
DEFAULT_PREDICTION_CONFIGS = {
    "income": {
        "algorithm": PredictionAlgorithm.PROPHET,
        "seasonality": True,
        "confidence_interval": 0.8,
        "min_data_points": 12
    },
    "expense": {
        "algorithm": PredictionAlgorithm.PROPHET,
        "seasonality": True,
        "confidence_interval": 0.8,
        "min_data_points": 20
    },
    "savings": {
        "algorithm": PredictionAlgorithm.LINEAR_REGRESSION,
        "seasonality": False,
        "confidence_interval": 0.9,
        "min_data_points": 15
    },
    "category": {
        "algorithm": PredictionAlgorithm.MOVING_AVERAGE,
        "seasonality": True,
        "confidence_interval": 0.7,
        "min_data_points": 10
    }
}