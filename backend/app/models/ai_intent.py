# app/models/ai_intent.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from .base import BaseDocument

class IntentPattern(BaseModel):
    text: str
    weight: float = 1.0

class IntentResponse(BaseModel):
    template: str
    conditions: Optional[Dict[str, Any]] = {}

class AIIntentCreate(BaseModel):
    intent_name: str
    intent_category: str
    patterns: List[IntentPattern]
    responses: List[IntentResponse]
    required_entities: List[str] = Field(default_factory=list)
    actions: List[str] = Field(default_factory=list)
    confidence_threshold: float = 0.7

class AIIntent(BaseDocument):
    intent_name: str = Field(..., unique=True)
    intent_category: str  # "transaction", "analysis", "goal", "general"
    patterns: List[IntentPattern]
    responses: List[IntentResponse]
    required_entities: List[str] = Field(default_factory=list)
    actions: List[str] = Field(default_factory=list)
    confidence_threshold: float = Field(default=0.7)
    is_active: bool = Field(default=True)
    usage_count: int = Field(default=0)

class AIIntentResponse(BaseModel):
    model_config = {"populate_by_name": True}
    
    id: str = Field(alias="_id")
    intent_name: str
    intent_category: str
    patterns: List[IntentPattern]
    responses: List[IntentResponse]
    required_entities: List[str]
    actions: List[str]
    confidence_threshold: float
    is_active: bool
    usage_count: int
    created_at: datetime
    updated_at: datetime