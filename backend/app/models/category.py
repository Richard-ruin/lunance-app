# app/models/category.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from .base import BaseDocument, PyObjectId

class CategoryBase(BaseModel):
    nama_kategori: str = Field(..., min_length=1, max_length=50)
    icon: str = Field(..., min_length=1, max_length=100)
    color: str = Field(..., pattern=r'^#[0-9A-Fa-f]{6}$')
    type: str = Field(..., pattern=r'^(pemasukan|pengeluaran)$')
    is_global: bool = False
    is_active: bool = True

    @field_validator('nama_kategori')
    @classmethod
    def validate_nama_kategori(cls, v):
        if not v.strip():
            raise ValueError('Nama kategori tidak boleh kosong')
        return v.strip()

class CategoryCreate(CategoryBase):
    pass

class Category(BaseDocument):
    nama_kategori: str
    icon: str
    color: str
    type: str  # "pemasukan" atau "pengeluaran"
    is_global: bool = False
    created_by: PyObjectId
    is_active: bool = True

class CategoryResponse(BaseModel):
    model_config = {"populate_by_name": True}
    
    id: str = Field(alias="_id")
    nama_kategori: str
    icon: str
    color: str
    type: str
    is_global: bool
    is_active: bool
    created_at: datetime

class CategoryUpdate(BaseModel):
    nama_kategori: Optional[str] = Field(None, min_length=1, max_length=50)
    icon: Optional[str] = Field(None, min_length=1, max_length=100)
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    is_active: Optional[bool] = None