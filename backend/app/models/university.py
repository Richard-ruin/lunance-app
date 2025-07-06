from typing import Optional
from datetime import datetime
from pydantic import Field, field_validator
from app.models.base import BaseModel, PyObjectId
from app.config.database import get_db

class University(BaseModel):
    nama: str = Field(..., min_length=3, max_length=200)
    kode: str = Field(..., min_length=2, max_length=10)
    alamat: str = Field(..., min_length=10, max_length=500)
    status_aktif: bool = Field(default=True)
    website: Optional[str] = None
    telepon: Optional[str] = None
    email: Optional[str] = None
    
    @field_validator('kode')
    @classmethod
    def validate_kode(cls, v):
        return v.upper().strip()
    
    @field_validator('nama')
    @classmethod
    def validate_nama(cls, v):
        return v.strip().title()
    
    def save(self):
        return super().save('universities')
    
    @classmethod
    def find_by_id(cls, university_id: str):
        return super().find_by_id('universities', university_id)
    
    @classmethod
    def find_all(cls, **kwargs):
        return super().find_all('universities', **kwargs)
    
    @classmethod
    def count_documents(cls, filter_dict: dict = None):
        return super().count_documents('universities', filter_dict)
    
    @classmethod
    def find_by_kode(cls, kode: str):
        try:
            db = get_db()
            doc = db.universities.find_one({'kode': kode.upper()})
            if doc:
                return cls(**doc)
            return None
        except Exception:
            return None

class Fakultas(BaseModel):
    nama: str = Field(..., min_length=3, max_length=200)
    kode: str = Field(..., min_length=2, max_length=10)
    university_id: PyObjectId = Field(...)
    deskripsi: Optional[str] = None
    
    @field_validator('kode')
    @classmethod
    def validate_kode(cls, v):
        return v.upper().strip()
    
    @field_validator('nama')
    @classmethod
    def validate_nama(cls, v):
        return v.strip().title()
    
    def save(self):
        return super().save('fakultas')
    
    @classmethod
    def find_by_id(cls, fakultas_id: str):
        return super().find_by_id('fakultas', fakultas_id)
    
    @classmethod
    def find_by_university(cls, university_id: str):
        try:
            return super().find_all('fakultas', {'university_id': PyObjectId(university_id)})
        except Exception:
            return []

class ProgramStudi(BaseModel):
    nama: str = Field(..., min_length=3, max_length=200)
    kode: str = Field(..., min_length=2, max_length=10)
    fakultas_id: PyObjectId = Field(...)
    jenjang: str = Field(..., pattern=r'^(D3|D4|S1|S2|S3)$')
    akreditasi: Optional[str] = Field(None, pattern=r'^[A-C]$')
    
    @field_validator('kode')
    @classmethod
    def validate_kode(cls, v):
        return v.upper().strip()
    
    @field_validator('nama')
    @classmethod
    def validate_nama(cls, v):
        return v.strip().title()
    
    def save(self):
        return super().save('program_studi')
    
    @classmethod
    def find_by_id(cls, prodi_id: str):
        return super().find_by_id('program_studi', prodi_id)
    
    @classmethod
    def find_by_fakultas(cls, fakultas_id: str):
        try:
            return super().find_all('program_studi', {'fakultas_id': PyObjectId(fakultas_id)})
        except Exception:
            return []

class UniversityRequest(BaseModel):
    nama_university: str = Field(..., min_length=3, max_length=200)
    kode_university: str = Field(..., min_length=2, max_length=10)
    alamat_university: str = Field(..., min_length=10, max_length=500)
    website_university: Optional[str] = None
    
    # Requester information
    nama_pemohon: str = Field(..., min_length=3, max_length=100)
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.ac\.id$')
    nim: str = Field(..., min_length=8, max_length=20)
    
    # Request status
    status: str = Field(default='pending', pattern=r'^(pending|approved|rejected)$')
    catatan_admin: Optional[str] = None
    processed_at: Optional[datetime] = None
    processed_by: Optional[str] = None
    
    @field_validator('kode_university')
    @classmethod
    def validate_kode(cls, v):
        return v.upper().strip()
    
    @field_validator('nama_university')
    @classmethod
    def validate_nama(cls, v):
        return v.strip().title()
    
    @field_validator('email')
    @classmethod
    def validate_email_domain(cls, v):
        if not v.endswith('.ac.id'):
            raise ValueError('Email harus menggunakan domain .ac.id')
        return v.lower()
    
    def save(self):
        return super().save('university_requests')
    
    @classmethod
    def find_by_id(cls, request_id: str):
        return super().find_by_id('university_requests', request_id)
    
    @classmethod
    def find_all(cls, **kwargs):
        return super().find_all('university_requests', **kwargs)
    
    @classmethod
    def count_documents(cls, filter_dict: dict = None):
        return super().count_documents('university_requests', filter_dict)