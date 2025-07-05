from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from .base import BaseDocument, PyObjectId

class UniversityBase(BaseModel):
    nama_universitas: str
    fakultas: List[str]
    program_studi: List[str]

class UniversityCreate(UniversityBase):
    pass

class University(BaseDocument):
    nama_universitas: str
    fakultas: List[str] = []
    program_studi: List[str] = []
    status: str = "pending"  # "approved", "pending", "rejected"
    requested_by: Optional[PyObjectId] = None
    approved_at: Optional[datetime] = None
    approved_by: Optional[PyObjectId] = None

class UniversityResponse(BaseModel):
    model_config = {"populate_by_name": True}
    
    id: str = Field(alias="_id")
    nama_universitas: str
    fakultas: List[str]
    program_studi: List[str]
    status: str
    created_at: datetime