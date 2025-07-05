# app/models/dashboard_widget.py
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from .base import BaseDocument, PyObjectId

class DashboardWidgetCreate(BaseModel):
    widget_type: str = Field(..., regex="^(balance|goal|spending|chart|recent_transactions)$")
    position: int = Field(..., ge=0)
    is_visible: bool = True
    config: Dict[str, Any] = Field(default_factory=dict)

class DashboardWidget(BaseDocument):
    user_id: PyObjectId
    widget_type: str
    position: int
    is_visible: bool
    config: Dict[str, Any]

class DashboardWidgetUpdate(BaseModel):
    position: Optional[int] = Field(None, ge=0)
    is_visible: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None

class WidgetResponse(BaseModel):
    model_config = {"populate_by_name": True}
    
    id: str = Field(alias="_id")
    widget_type: str
    position: int
    is_visible: bool
    config: Dict[str, Any]
    created_at: datetime
    updated_at: datetime