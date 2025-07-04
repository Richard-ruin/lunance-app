"""
Base Schemas
Schema dasar untuk request/response dengan Pydantic v2
"""

from datetime import datetime
from typing import Optional, Any, Dict, List
from pydantic import BaseModel, Field, ConfigDict


class BaseSchema(BaseModel):
    """Base schema untuk semua schemas"""
    
    model_config = ConfigDict(
        # Pydantic v2 configuration
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True,
        populate_by_name=True,
        from_attributes=True
    )


class TimestampMixin(BaseModel):
    """Mixin untuk timestamp fields"""
    created_at: datetime = Field(..., description="Waktu dibuat")
    updated_at: Optional[datetime] = Field(default=None, description="Waktu diupdate")


class BaseResponse(BaseSchema, TimestampMixin):
    """Base response schema dengan timestamp"""
    id: str = Field(..., description="ID document")


class BaseCreate(BaseSchema):
    """Base schema untuk create operations"""
    pass


class BaseUpdate(BaseSchema):
    """Base schema untuk update operations"""
    pass


class BaseList(BaseSchema):
    """Base schema untuk list responses dengan pagination"""
    pass


# Pagination Schemas
class PaginationInfo(BaseSchema):
    """Schema untuk informasi pagination"""
    page: int = Field(..., ge=1, description="Halaman saat ini")
    per_page: int = Field(..., ge=1, le=100, description="Jumlah item per halaman")
    total: int = Field(..., ge=0, description="Total item")
    total_pages: int = Field(..., ge=0, description="Total halaman")
    has_next: bool = Field(..., description="Ada halaman berikutnya")
    has_prev: bool = Field(..., description="Ada halaman sebelumnya")
    next_page: Optional[int] = Field(default=None, description="Nomor halaman berikutnya")
    prev_page: Optional[int] = Field(default=None, description="Nomor halaman sebelumnya")


class PaginatedResponse(BaseSchema):
    """Schema untuk response dengan pagination"""
    data: List[Any] = Field(..., description="Data items")
    pagination: PaginationInfo = Field(..., description="Informasi pagination")


# Error Schemas
class ErrorDetail(BaseSchema):
    """Schema untuk detail error"""
    field: Optional[str] = Field(default=None, description="Field yang error")
    message: str = Field(..., description="Pesan error")
    code: Optional[str] = Field(default=None, description="Kode error")


class ErrorResponse(BaseSchema):
    """Schema untuk response error"""
    success: bool = Field(default=False, description="Status success")
    message: str = Field(..., description="Pesan error utama")
    details: Optional[List[ErrorDetail]] = Field(default=None, description="Detail error")
    error_code: Optional[str] = Field(default=None, description="Kode error")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Waktu error")


# Success Schemas
class SuccessResponse(BaseSchema):
    """Schema untuk response sukses tanpa data"""
    success: bool = Field(default=True, description="Status success")
    message: str = Field(..., description="Pesan sukses")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Waktu response")


class DataResponse(BaseSchema):
    """Schema untuk response sukses dengan data"""
    success: bool = Field(default=True, description="Status success")
    message: str = Field(..., description="Pesan sukses")
    data: Any = Field(..., description="Data response")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Waktu response")


# Filter Schemas
class DateRangeFilter(BaseSchema):
    """Schema untuk filter range tanggal"""
    start_date: Optional[datetime] = Field(default=None, description="Tanggal mulai")
    end_date: Optional[datetime] = Field(default=None, description="Tanggal akhir")


class SearchFilter(BaseSchema):
    """Schema untuk filter pencarian"""
    search: Optional[str] = Field(default=None, min_length=1, max_length=100, description="Kata kunci pencarian")
    
    
class SortFilter(BaseSchema):
    """Schema untuk sorting"""
    sort_by: Optional[str] = Field(default=None, description="Field untuk sorting")
    sort_order: Optional[str] = Field(default="desc", pattern="^(asc|desc)$", description="Urutan sorting")


class BaseFilter(BaseSchema, DateRangeFilter, SearchFilter, SortFilter):
    """Base schema untuk filtering"""
    page: int = Field(default=1, ge=1, description="Halaman")
    per_page: int = Field(default=10, ge=1, le=100, description="Item per halaman")


# Bulk Operations
class BulkDeleteRequest(BaseSchema):
    """Schema untuk bulk delete"""
    ids: List[str] = Field(..., min_length=1, description="List ID yang akan dihapus")


class BulkUpdateRequest(BaseSchema):
    """Schema untuk bulk update"""
    ids: List[str] = Field(..., min_length=1, description="List ID yang akan diupdate")
    data: Dict[str, Any] = Field(..., description="Data untuk update")


class BulkOperationResponse(BaseSchema):
    """Schema untuk response bulk operations"""
    success: bool = Field(..., description="Status operasi")
    message: str = Field(..., description="Pesan operasi")
    total_requested: int = Field(..., description="Total item yang diminta")
    total_processed: int = Field(..., description="Total item yang diproses")
    total_success: int = Field(..., description="Total item yang berhasil")
    total_failed: int = Field(..., description="Total item yang gagal")
    failed_items: Optional[List[Dict[str, Any]]] = Field(default=None, description="Item yang gagal")


# Statistics & Analytics
class CountResponse(BaseSchema):
    """Schema untuk response count"""
    count: int = Field(..., ge=0, description="Jumlah item")


class StatsResponse(BaseSchema):
    """Schema untuk response statistik"""
    stats: Dict[str, Any] = Field(..., description="Data statistik")


# Health Check
class HealthCheckResponse(BaseSchema):
    """Schema untuk health check response"""
    status: str = Field(..., description="Status aplikasi")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Waktu check")
    version: str = Field(..., description="Versi aplikasi")
    database: Dict[str, Any] = Field(..., description="Status database")
    uptime: Optional[str] = Field(default=None, description="Uptime aplikasi")


# File Upload
class FileUploadResponse(BaseSchema):
    """Schema untuk response file upload"""
    filename: str = Field(..., description="Nama file")
    original_filename: str = Field(..., description="Nama file original")
    file_size: int = Field(..., description="Ukuran file")
    file_type: str = Field(..., description="Tipe file")
    file_url: str = Field(..., description="URL file")
    uploaded_at: datetime = Field(default_factory=datetime.utcnow, description="Waktu upload")


# OTP & Verification
class OTPRequest(BaseSchema):
    """Schema untuk request OTP"""
    email: str = Field(..., description="Email untuk OTP")
    purpose: str = Field(..., description="Tujuan OTP")


class OTPVerifyRequest(BaseSchema):
    """Schema untuk verifikasi OTP"""
    email: str = Field(..., description="Email")
    otp_code: str = Field(..., min_length=4, max_length=8, description="Kode OTP")
    purpose: str = Field(..., description="Tujuan OTP")


class OTPResponse(BaseSchema):
    """Schema untuk response OTP"""
    success: bool = Field(..., description="Status pengiriman OTP")
    message: str = Field(..., description="Pesan")
    expires_at: datetime = Field(..., description="Waktu kadaluarsa OTP")


# Custom Validators untuk schemas
def validate_indonesian_phone(phone: str) -> str:
    """Validator untuk nomor telepon Indonesia"""
    if not phone:
        return phone
    
    # Remove spaces and dashes
    phone = phone.replace(" ", "").replace("-", "")
    
    # Normalize Indonesian phone numbers
    if phone.startswith("0"):
        phone = "+62" + phone[1:]
    elif phone.startswith("62"):
        phone = "+" + phone
    elif not phone.startswith("+62"):
        phone = "+62" + phone
    
    return phone


def validate_university_email(email: str, valid_domains: List[str] = ["ac.id"]) -> str:
    """Validator untuk email universitas"""
    if not email:
        return email
    
    email = email.lower().strip()
    
    if not any(email.endswith(f".{domain}") for domain in valid_domains):
        raise ValueError(f"Email harus menggunakan domain: {valid_domains}")
    
    return email