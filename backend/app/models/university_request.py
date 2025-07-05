# app/models/university_request.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .base import BaseDocument, PyObjectId

class UniversityRequestBase(BaseModel):
    nama_universitas: str
    fakultas: str
    program_studi: str

class UniversityRequestCreate(UniversityRequestBase):
    pass

class UniversityRequest(BaseDocument):
    user_id: PyObjectId
    nama_universitas: str
    fakultas: str
    program_studi: str
    status: str = "pending"  # "pending", "approved", "rejected"
    admin_notes: str = ""
    processed_at: Optional[datetime] = None
    processed_by: Optional[PyObjectId] = None

class UniversityRequestResponse(BaseModel):
    model_config = {"populate_by_name": True}
    
    id: str = Field(alias="_id")
    user_id: str
    nama_universitas: str
    fakultas: str
    program_studi: str
    status: str
    admin_notes: str
    requested_at: datetime = Field(alias="created_at")
    processed_at: Optional[datetime] = None
    processed_by: Optional[str] = None

class UniversityRequestUpdate(BaseModel):
    status: str
    admin_notes: str = ""