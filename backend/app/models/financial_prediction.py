# app/models/financial_prediction.py
from pydantic import BaseModel, Field
from bson import ObjectId
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any
from .base import PyObjectId

class PredictionData(BaseModel):
    dates: List[datetime]
    predicted_values: List[float]
    confidence_intervals: Dict[str, List[float]]

class FinancialPrediction(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    prediction_type: str  # "income", "expense", "balance", "category_spending"
    period: str  # "daily", "weekly", "monthly"
    prediction_data: PredictionData
    model_accuracy: float
    training_data_points: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime
    model_version: str = "1.0"
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}