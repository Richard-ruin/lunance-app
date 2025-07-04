"""
University, Faculty, Department Schemas
Schemas untuk institusi pendidikan dengan approval system
"""

from datetime import datetime
from typing import Optional
from pydantic import Field, field_validator, HttpUrl
from enum import Enum

from .base import BaseSchema, BaseResponse, BaseCreate, BaseUpdate, BaseFilter
from ..models.university import ApprovalStatus


# Enums for schemas
class ApprovalStatusSchema(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"


# University Schemas
class UniversityBase(BaseSchema):
    """Base university schema"""
    name: str = Field(..., min_length=3, max_length=200, description="Nama universitas")
    domain: str = Field(..., description="Domain email universitas")
    website: Optional[HttpUrl] = Field(default=None, description="Website resmi")
    email: Optional[str] = Field(default=None, description="Email kontak")
    phone: Optional[str] = Field(default=None, description="Nomor telepon")
    address: Optional[str] = Field(default=None, max_length=500, description="Alamat lengkap")
    city: Optional[str] = Field(default=None, description="Kota")
    province: Optional[str] = Field(default=None, description="Provinsi")
    postal_code: Optional[str] = Field(default=None, description="Kode pos")
    description: Optional[str] = Field(default=None, max_length=1000, description="Deskripsi")
    established_year: Optional[int] = Field(default=None, ge=1900, le=2030, description="Tahun berdiri")
    
    @field_validator("domain")
    @classmethod
    def validate_domain(cls, v):
        """Validasi domain universitas"""
        if not v:
            raise ValueError("Domain tidak boleh kosong")
        
        v = v.lower().strip()
        
        if not v.endswith(".ac.id"):
            raise ValueError("Domain universitas harus berakhiran .ac.id")
        
        return v


class UniversityCreate(UniversityBase):
    """Schema untuk create university"""
    logo_url: Optional[str] = Field(default=None, description="URL logo universitas")


class UniversityUpdate(BaseSchema):
    """Schema untuk update university"""
    name: Optional[str] = Field(default=None, min_length=3, max_length=200, description="Nama universitas")
    website: Optional[HttpUrl] = Field(default=None, description="Website resmi")
    email: Optional[str] = Field(default=None, description="Email kontak")
    phone: Optional[str] = Field(default=None, description="Nomor telepon")
    address: Optional[str] = Field(default=None, max_length=500, description="Alamat lengkap")
    city: Optional[str] = Field(default=None, description="Kota")
    province: Optional[str] = Field(default=None, description="Provinsi")
    postal_code: Optional[str] = Field(default=None, description="Kode pos")
    description: Optional[str] = Field(default=None, max_length=1000, description="Deskripsi")
    established_year: Optional[int] = Field(default=None, ge=1900, le=2030, description="Tahun berdiri")
    logo_url: Optional[str] = Field(default=None, description="URL logo universitas")


class UniversityResponse(UniversityBase, BaseResponse):
    """Schema untuk response university"""
    approval_status: ApprovalStatusSchema = Field(..., description="Status approval")
    is_approved: bool = Field(..., description="Status approval (legacy)")
    approved_by: Optional[str] = Field(default=None, description="ID admin yang approve")
    approved_at: Optional[datetime] = Field(default=None, description="Waktu approval")
    rejection_reason: Optional[str] = Field(default=None, description="Alasan penolakan")
    logo_url: Optional[str] = Field(default=None, description="URL logo")
    student_count: int = Field(..., description="Jumlah mahasiswa")
    faculty_count: int = Field(..., description="Jumlah fakultas")


class UniversityDetailResponse(UniversityResponse):
    """Schema untuk response university detail dengan faculties"""
    faculties: Optional[list] = Field(default=None, description="List fakultas")


# Approval Operations
class UniversityApproval(BaseSchema):
    """Schema untuk approval university"""
    university_id: str = Field(..., description="ID universitas")
    action: str = Field(..., pattern="^(approve|reject|suspend)$", description="Aksi approval")
    reason: Optional[str] = Field(default=None, description="Alasan (untuk reject/suspend)")


class UniversityApprovalBulk(BaseSchema):
    """Schema untuk bulk approval"""
    university_ids: list[str] = Field(..., min_length=1, description="List ID universitas")
    action: str = Field(..., pattern="^(approve|reject|suspend)$", description="Aksi approval")
    reason: Optional[str] = Field(default=None, description="Alasan (untuk reject/suspend)")


# Filter Schemas
class UniversityFilter(BaseFilter):
    """Schema untuk filter university"""
    approval_status: Optional[ApprovalStatusSchema] = Field(default=None, description="Filter status approval")
    city: Optional[str] = Field(default=None, description="Filter kota")
    province: Optional[str] = Field(default=None, description="Filter provinsi")
    is_approved: Optional[bool] = Field(default=None, description="Filter approved")


# Faculty Schemas
class FacultyBase(BaseSchema):
    """Base faculty schema"""
    name: str = Field(..., min_length=2, max_length=200, description="Nama fakultas")
    code: Optional[str] = Field(default=None, max_length=10, description="Kode fakultas")
    description: Optional[str] = Field(default=None, max_length=1000, description="Deskripsi fakultas")


class FacultyCreate(FacultyBase):
    """Schema untuk create faculty"""
    university_id: str = Field(..., description="ID Universitas")


class FacultyUpdate(BaseSchema):
    """Schema untuk update faculty"""
    name: Optional[str] = Field(default=None, min_length=2, max_length=200, description="Nama fakultas")
    code: Optional[str] = Field(default=None, max_length=10, description="Kode fakultas")
    description: Optional[str] = Field(default=None, max_length=1000, description="Deskripsi fakultas")


class FacultyResponse(FacultyBase, BaseResponse):
    """Schema untuk response faculty"""
    university_id: str = Field(..., description="ID Universitas")
    department_count: int = Field(..., description="Jumlah jurusan")
    student_count: int = Field(..., description="Jumlah mahasiswa")


class FacultyDetailResponse(FacultyResponse):
    """Schema untuk response faculty detail dengan departments"""
    university_name: Optional[str] = Field(default=None, description="Nama universitas")
    departments: Optional[list] = Field(default=None, description="List jurusan")


class FacultyFilter(BaseFilter):
    """Schema untuk filter faculty"""
    university_id: Optional[str] = Field(default=None, description="Filter universitas")


# Department Schemas
class DepartmentBase(BaseSchema):
    """Base department schema"""
    name: str = Field(..., min_length=2, max_length=200, description="Nama jurusan")
    code: Optional[str] = Field(default=None, max_length=10, description="Kode jurusan")
    description: Optional[str] = Field(default=None, max_length=1000, description="Deskripsi jurusan")
    degree_level: Optional[str] = Field(default=None, description="Jenjang (S1/S2/S3/D3/D4)")
    accreditation: Optional[str] = Field(default=None, description="Akreditasi")
    
    @field_validator("degree_level")
    @classmethod
    def validate_degree_level(cls, v):
        """Validasi jenjang pendidikan"""
        if not v:
            return v
        
        valid_levels = ["D3", "D4", "S1", "S2", "S3"]
        v = v.upper()
        
        if v not in valid_levels:
            raise ValueError(f"Jenjang harus salah satu dari: {valid_levels}")
        
        return v


class DepartmentCreate(DepartmentBase):
    """Schema untuk create department"""
    faculty_id: str = Field(..., description="ID Fakultas")


class DepartmentUpdate(BaseSchema):
    """Schema untuk update department"""
    name: Optional[str] = Field(default=None, min_length=2, max_length=200, description="Nama jurusan")
    code: Optional[str] = Field(default=None, max_length=10, description="Kode jurusan")
    description: Optional[str] = Field(default=None, max_length=1000, description="Deskripsi jurusan")
    degree_level: Optional[str] = Field(default=None, description="Jenjang")
    accreditation: Optional[str] = Field(default=None, description="Akreditasi")


class DepartmentResponse(DepartmentBase, BaseResponse):
    """Schema untuk response department"""
    faculty_id: str = Field(..., description="ID Fakultas")
    student_count: int = Field(..., description="Jumlah mahasiswa")


class DepartmentDetailResponse(DepartmentResponse):
    """Schema untuk response department detail"""
    faculty_name: Optional[str] = Field(default=None, description="Nama fakultas")
    university_name: Optional[str] = Field(default=None, description="Nama universitas")
    university_id: Optional[str] = Field(default=None, description="ID universitas")


class DepartmentFilter(BaseFilter):
    """Schema untuk filter department"""
    faculty_id: Optional[str] = Field(default=None, description="Filter fakultas")
    university_id: Optional[str] = Field(default=None, description="Filter universitas")
    degree_level: Optional[str] = Field(default=None, description="Filter jenjang")
    accreditation: Optional[str] = Field(default=None, description="Filter akreditasi")


# Statistics
class UniversityStatsResponse(BaseSchema):
    """Schema untuk statistik universitas"""
    total_universities: int = Field(..., description="Total universitas")
    approved_universities: int = Field(..., description="Universitas disetujui")
    pending_approval: int = Field(..., description="Menunggu persetujuan")
    rejected_universities: int = Field(..., description="Universitas ditolak")
    total_faculties: int = Field(..., description="Total fakultas")
    total_departments: int = Field(..., description="Total jurusan")
    total_students: int = Field(..., description="Total mahasiswa")


class InstitutionHierarchy(BaseSchema):
    """Schema untuk hierarki institusi"""
    university: UniversityResponse = Field(..., description="Data universitas")
    faculties: list[FacultyResponse] = Field(..., description="List fakultas")
    departments: list[DepartmentResponse] = Field(..., description="List jurusan")


# Bulk Operations
class UniversityBulkUpdate(BaseSchema):
    """Schema untuk bulk update universities"""
    university_ids: list[str] = Field(..., min_length=1, description="List ID universitas")
    data: UniversityUpdate = Field(..., description="Data untuk update")


class FacultyBulkCreate(BaseSchema):
    """Schema untuk bulk create faculties"""
    university_id: str = Field(..., description="ID Universitas")
    faculties: list[FacultyBase] = Field(..., min_length=1, description="List fakultas")


class DepartmentBulkCreate(BaseSchema):
    """Schema untuk bulk create departments"""
    faculty_id: str = Field(..., description="ID Fakultas")
    departments: list[DepartmentBase] = Field(..., min_length=1, description="List jurusan")