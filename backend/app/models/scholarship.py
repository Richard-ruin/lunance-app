from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from bson import ObjectId
from app.models.base import PyObjectId


class ScholarshipRequirement(BaseModel):
    requirement_type: str  # gpa, income, essay, documents
    description: str
    is_mandatory: bool = True
    value: Optional[str] = None  # e.g., "3.5" for GPA requirement


class ScholarshipApplication(BaseModel):
    application_id: Optional[PyObjectId] = Field(default_factory=PyObjectId)
    student_id: PyObjectId
    application_date: datetime
    status: str  # pending, approved, rejected, interview, documents_needed
    documents_submitted: List[str] = []
    notes: Optional[str] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class ScholarshipDisbursement(BaseModel):
    disbursement_id: Optional[PyObjectId] = Field(default_factory=PyObjectId)
    amount: float
    disbursement_date: datetime
    semester: str
    status: str  # pending, disbursed, cancelled
    notes: Optional[str] = None


class Scholarship(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    
    # Scholarship Info
    name: str
    provider: str  # university, government, private
    type: str  # merit, need_based, research, sports
    
    # Financial Details
    amount: float
    currency: str = "IDR"
    payment_frequency: str  # one_time, semester, monthly
    duration_months: Optional[int] = None
    
    # Eligibility
    requirements: List[ScholarshipRequirement] = []
    eligible_majors: List[str] = []
    eligible_universities: List[str] = []
    min_semester: Optional[int] = None
    max_semester: Optional[int] = None
    
    # Application Details
    application_deadline: Optional[datetime] = None
    application_url: Optional[str] = None
    contact_info: Optional[str] = None
    
    # Status
    is_active: bool = True
    is_open_for_application: bool = True
    
    # Applications
    applications: List[ScholarshipApplication] = []
    
    # Disbursements (for awarded scholarships)
    disbursements: List[ScholarshipDisbursement] = []
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ScholarshipInDB(Scholarship):
    pass


class ScholarshipCreate(BaseModel):
    name: str
    provider: str
    type: str
    amount: float
    currency: str = "IDR"
    payment_frequency: str
    duration_months: Optional[int] = None
    requirements: List[ScholarshipRequirement] = []
    eligible_majors: List[str] = []
    eligible_universities: List[str] = []
    min_semester: Optional[int] = None
    max_semester: Optional[int] = None
    application_deadline: Optional[datetime] = None
    application_url: Optional[str] = None
    contact_info: Optional[str] = None


class ScholarshipUpdate(BaseModel):
    name: Optional[str] = None
    provider: Optional[str] = None
    type: Optional[str] = None
    amount: Optional[float] = None
    payment_frequency: Optional[str] = None
    duration_months: Optional[int] = None
    requirements: Optional[List[ScholarshipRequirement]] = None
    eligible_majors: Optional[List[str]] = None
    eligible_universities: Optional[List[str]] = None
    application_deadline: Optional[datetime] = None
    is_active: Optional[bool] = None
    is_open_for_application: Optional[bool] = None


class ScholarshipApplicationCreate(BaseModel):
    scholarship_id: PyObjectId
    documents_submitted: List[str] = []
    notes: Optional[str] = None


class ScholarshipApplicationUpdate(BaseModel):
    status: Optional[str] = None
    documents_submitted: Optional[List[str]] = None
    notes: Optional[str] = None


class DisbursementCreate(BaseModel):
    scholarship_id: PyObjectId
    amount: float
    disbursement_date: datetime
    semester: str
    notes: Optional[str] = None