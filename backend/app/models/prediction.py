from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId
from app.models.base import PyObjectId


class TrainingData(BaseModel):
    start_date: datetime
    end_date: datetime
    transaction_count: int
    data_quality_score: float  # 0-1


class ForecastDataPoint(BaseModel):
    date: datetime
    predicted_value: float
    lower_bound: float
    upper_bound: float
    trend: float
    seasonal: float
    yearly: float
    weekly: float


class PredictionAdjustment(BaseModel):
    date: datetime
    original_prediction: float
    adjusted_prediction: float
    adjustment_reason: str
    adjustment_type: str  # debt_payment, event_impact, seasonal
    confidence: float


class ModelMetrics(BaseModel):
    mae: float  # Mean Absolute Error
    mape: float  # Mean Absolute Percentage Error
    rmse: float  # Root Mean Square Error
    accuracy_score: float  # custom accuracy for financial predictions


class PredictionInsight(BaseModel):
    type: str  # trend, seasonality, anomaly, recommendation
    message: str
    importance: str  # high, medium, low
    actionable: bool
    suggested_action: Optional[str] = None


class ProphetPrediction(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    student_id: PyObjectId
    
    # Prediction Metadata
    prediction_type: str  # income, expense, balance, category_specific
    model_version: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Time Range
    prediction_start: datetime
    prediction_end: datetime
    confidence_interval: float = 0.95  # 0.95 for 95% confidence
    
    # Historical Data Used
    training_data: TrainingData
    
    # Prophet Model Results
    forecast_data: List[ForecastDataPoint]
    
    # Business Logic Adjustments
    adjustments: List[PredictionAdjustment] = Field(default_factory=list)
    
    # Model Performance
    model_metrics: ModelMetrics
    
    # Insights Generated
    insights: List[PredictionInsight] = Field(default_factory=list)
    
    # Cache Info
    cache_until: datetime
    prediction_hash: str  # for caching similar predictions
    
    is_active: bool = True


class ProphetPredictionInDB(ProphetPrediction):
    pass


class PredictionRequest(BaseModel):
    prediction_type: str
    prediction_start: datetime
    prediction_end: datetime
    confidence_interval: float = 0.95
    include_adjustments: bool = True
    category_id: Optional[PyObjectId] = None  # for category-specific predictions


class PredictionResponse(BaseModel):
    prediction_id: PyObjectId
    prediction_type: str
    forecast_data: List[ForecastDataPoint]
    insights: List[PredictionInsight]
    model_metrics: ModelMetrics
    generated_at: datetime
    cache_until: datetime


# Business Rules for Predictions
class PredictionConditions(BaseModel):
    student_criteria: Dict[str, Any] = Field(default_factory=dict)  # semester, university, etc.
    financial_criteria: Dict[str, Any] = Field(default_factory=dict)  # debt_level, income_range, etc.
    temporal_criteria: Dict[str, Any] = Field(default_factory=dict)  # time of year, academic calendar
    transaction_criteria: Dict[str, Any] = Field(default_factory=dict)  # spending patterns, categories


class PredictionAdjustmentRule(BaseModel):
    period: str  # "next_month", "in_3_months"
    adjustment_type: str  # multiply, add, subtract
    value: float
    reason: str


class PredictionAdjustments(BaseModel):
    income_adjustments: List[PredictionAdjustmentRule] = Field(default_factory=list)
    expense_adjustments: List[PredictionAdjustmentRule] = Field(default_factory=list)
    balance_adjustments: List[PredictionAdjustmentRule] = Field(default_factory=list)


class PredictionRule(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    
    rule_name: str
    rule_type: str  # debt_impact, event_impact, seasonal, behavioral
    priority: int  # 1-10, higher overrides lower
    
    # Conditions
    conditions: PredictionConditions
    
    # Actions
    prediction_adjustments: PredictionAdjustments
    
    confidence_impact: float  # how much this rule affects prediction confidence
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    usage_count: int = 0
    success_rate: float = 0.0  # how often this rule improves prediction accuracy