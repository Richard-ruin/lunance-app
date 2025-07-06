from typing import Optional
from datetime import datetime
from pydantic import Field, field_validator
from app.models.base import BaseModel, PyObjectId
from app.config.database import get_db

class User(BaseModel):
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.ac\.id$')
    password_hash: str = Field(...)
    nama: str = Field(..., min_length=3, max_length=100)
    nim: str = Field(..., min_length=8, max_length=20)
    
    # University information
    university_id: PyObjectId = Field(...)
    fakultas_id: PyObjectId = Field(...)
    program_studi_id: PyObjectId = Field(...)
    
    # Profile information
    angkatan: int = Field(...)
    semester: int = Field(default=1, ge=1, le=14)
    avatar_url: Optional[str] = None
    
    # Account status
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    last_login: Optional[datetime] = None
    
    @field_validator('email')
    @classmethod
    def validate_email_domain(cls, v):
        if not v.endswith('.ac.id'):
            raise ValueError('Email harus menggunakan domain .ac.id')
        return v.lower()
    
    @field_validator('nama')
    @classmethod
    def validate_nama(cls, v):
        return v.strip().title()
    
    @field_validator('nim')
    @classmethod
    def validate_nim(cls, v):
        return v.strip()
    
    def save(self):
        return super().save('users')
    
    @classmethod
    def find_by_id(cls, user_id: str):
        return super().find_by_id('users', user_id)
    
    @classmethod
    def find_by_email(cls, email: str):
        try:
            db = get_db()
            doc = db.users.find_one({'email': email.lower()})
            if doc:
                return cls(**doc)
            return None
        except Exception:
            return None
    
    @classmethod
    def find_by_nim(cls, nim: str):
        try:
            db = get_db()
            doc = db.users.find_one({'nim': nim})
            if doc:
                return cls(**doc)
            return None
        except Exception:
            return None
    
    def to_dict_safe(self):
        """Convert to dict without sensitive information"""
        user_dict = self.model_dump()
        user_dict.pop('password_hash', None)
        return user_dict