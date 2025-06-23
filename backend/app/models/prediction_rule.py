from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId


class Adjustment(BaseModel):
    period: str = Field(..., description="Time period for adjustment")
    adjustment_type: str = Field(..., description="Type of adjustment: multiply, add, subtract")
    value: float = Field(..., description="Adjustment value")
    reason: str = Field(..., description="Reason for adjustment")


class CategoryAdjustment(Adjustment):
    category: str = Field(..., description="Category to adjust")


class PredictionAdjustments(BaseModel):
    income_adjustments: List[Adjustment] = Field(default_factory=list)
    expense_adjustments: List[CategoryAdjustment] = Field(default_factory=list)
    balance_adjustments: List[Adjustment] = Field(default_factory=list)


class RuleConditions(BaseModel):
    student_criteria: Dict[str, Any] = Field(default_factory=dict, description="Student criteria like semester, university")
    financial_criteria: Dict[str, Any] = Field(default_factory=dict, description="Financial criteria like debt level, income range")
    temporal_criteria: Dict[str, Any] = Field(default_factory=dict, description="Time-based criteria")
    transaction_criteria: Dict[str, Any] = Field(default_factory=dict, description="Transaction pattern criteria")


class PredictionRule(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    rule_name: str = Field(..., description="Name of the prediction rule")
    rule_type: str = Field(..., description="Type: debt_impact, event_impact, seasonal, behavioral")
    priority: int = Field(..., ge=1, le=10, description="Priority 1-10, higher overrides lower")
    
    # Conditions
    conditions: RuleConditions = Field(default_factory=RuleConditions)
    
    # Actions
    prediction_adjustments: PredictionAdjustments = Field(default_factory=PredictionAdjustments)
    
    confidence_impact: float = Field(0.0, description="How much this rule affects prediction confidence")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(True)
    usage_count: int = Field(0, description="How often this rule has been used")
    success_rate: float = Field(0.0, description="Success rate of prediction improvements")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# Example rules for reference:
EXAMPLE_RULES = [
    {
        "rule_name": "Debt Payment Impact",
        "rule_type": "debt_impact",
        "priority": 8,
        "conditions": {
            "financial_criteria": {
                "has_active_debt": True,
                "debt_amount_min": 500000
            }
        },
        "prediction_adjustments": {
            "expense_adjustments": [{
                "category": "debt_payment",
                "period": "next_month",
                "adjustment_type": "add",
                "value": "debt.monthly_payment",
                "reason": "Monthly debt payment obligation"
            }]
        }
    },
    {
        "rule_name": "Exam Period Spending Reduction",
        "rule_type": "seasonal",
        "priority": 6,
        "conditions": {
            "temporal_criteria": {
                "is_exam_period": True
            }
        },
        "prediction_adjustments": {
            "expense_adjustments": [{
                "category": "entertainment",
                "period": "exam_period",
                "adjustment_type": "multiply",
                "value": 0.7,
                "reason": "Reduced entertainment spending during exams"
            }]
        }
    }
]