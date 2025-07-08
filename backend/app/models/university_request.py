# app/models/university_request.py (Fixed)
"""University request models with fixed PyObjectId."""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from enum import Enum

# Import the fixed PyObjectId from user.py
from .user import PyObjectId


class RequestStatus(str, Enum):
    """University request status enumeration."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class UniversityRequestBase(BaseModel):
    """Base university request model."""
    university_name: str = Field(..., min_length=2, max_length=150)
    faculty_name: str = Field(..., min_length=2, max_length=100)
    major_name: str = Field(..., min_length=2, max_length=100)
    
    @field_validator('university_name')
    @classmethod
    def validate_university_name(cls, v):
        """Validate and clean university name."""
        return v.strip().title()
    
    @field_validator('faculty_name')
    @classmethod
    def validate_faculty_name(cls, v):
        """Validate and clean faculty name."""
        return v.strip().title()
    
    @field_validator('major_name')
    @classmethod
    def validate_major_name(cls, v):
        """Validate and clean major name."""
        return v.strip().title()


class UniversityRequestCreate(UniversityRequestBase):
    """University request creation schema."""
    pass


class UniversityRequestUpdate(BaseModel):
    """University request update schema (admin only)."""
    status: Optional[RequestStatus] = None
    admin_notes: Optional[str] = Field(None, max_length=500)
    
    @field_validator('admin_notes')
    @classmethod
    def validate_admin_notes(cls, v):
        """Validate and clean admin notes."""
        if v is not None:
            return v.strip()
        return v
    
    model_config = ConfigDict(extra='forbid')


class UniversityRequestInDB(UniversityRequestBase):
    """University request model in database."""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    status: RequestStatus = RequestStatus.PENDING
    admin_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )


class UniversityRequestResponse(UniversityRequestBase):
    """University request response schema."""
    id: str = Field(alias="_id")
    user_id: str
    status: RequestStatus
    admin_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )


class UniversityRequestWithUser(UniversityRequestResponse):
    """University request response with user details."""
    user_email: str
    user_full_name: str
    user_phone_number: Optional[str] = None


class UniversityRequestListResponse(BaseModel):
    """University request list response schema."""
    requests: List[UniversityRequestWithUser]
    total: int
    page: int
    per_page: int
    pages: int
    pending_count: int = 0
    approved_count: int = 0
    rejected_count: int = 0


class UniversityRequestStats(BaseModel):
    """University request statistics schema."""
    total_requests: int = 0
    pending_requests: int = 0
    approved_requests: int = 0
    rejected_requests: int = 0
    requests_today: int = 0
    requests_this_week: int = 0
    requests_this_month: int = 0


class UniversityRequestFilter(BaseModel):
    """University request filter schema."""
    status: Optional[RequestStatus] = None
    university_name: Optional[str] = Field(None, min_length=1, max_length=150)
    faculty_name: Optional[str] = Field(None, min_length=1, max_length=100)
    major_name: Optional[str] = Field(None, min_length=1, max_length=100)
    user_email: Optional[str] = Field(None, min_length=1, max_length=100)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    @field_validator('university_name', 'faculty_name', 'major_name', 'user_email')
    @classmethod
    def validate_search_fields(cls, v):
        """Validate and clean search fields."""
        if v is not None:
            return v.strip()
        return v
    
    def model_post_init(self, __context):
        """Validate filter logic."""
        if self.start_date is not None and self.end_date is not None:
            if self.start_date > self.end_date:
                raise ValueError('start_date cannot be after end_date')


class BulkUniversityRequestUpdate(BaseModel):
    """Bulk university request update schema."""
    request_ids: List[str] = Field(..., min_length=1, max_length=50)
    status: RequestStatus
    admin_notes: Optional[str] = Field(None, max_length=500)
    
    @field_validator('admin_notes')
    @classmethod
    def validate_admin_notes(cls, v):
        """Validate and clean admin notes."""
        if v is not None:
            return v.strip()
        return v


class BulkUniversityRequestResponse(BaseModel):
    """Bulk university request update response."""
    updated_count: int
    failed_count: int
    updated_requests: List[UniversityRequestResponse]
    errors: List[str] = []


class UniversityRequestSummary(BaseModel):
    """University request summary for admin dashboard."""
    stats: UniversityRequestStats
    recent_requests: List[UniversityRequestWithUser]
    pending_requests: List[UniversityRequestWithUser]
    
    
class UniversityDataSuggestion(BaseModel):
    """University data suggestion from requests."""
    university_name: str
    faculty_name: str
    major_name: str
    request_count: int = 1
    first_requested: datetime
    last_requested: datetime