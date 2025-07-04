"""
User Schemas
Schemas untuk User model operations
"""

from datetime import datetime
from typing import Optional
from pydantic import Field, EmailStr, field_validator
from enum import Enum

from .base import BaseSchema, BaseResponse, BaseCreate, BaseUpdate, BaseFilter
from ..models.user import UserRole, UserStatus


# Enums for schemas
class UserRoleSchema(str, Enum):
    ADMIN = "admin"
    STUDENT = "student"


class UserStatusSchema(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


# Base User Schema
class UserBase(BaseSchema):
    """Base user schema dengan field umum"""
    email: EmailStr = Field(..., description="Email user")
    full_name: str = Field(..., min_length=2, max_length=100, description="Nama lengkap")
    phone_number: Optional[str] = Field(
        default=None, 
        description="Nomor telepon Indonesia"
    )
    
    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v):
        """Validasi nomor telepon Indonesia"""
        if not v:
            return v
        
        # Remove spaces and dashes
        v = v.replace(" ", "").replace("-", "")
        
        # Normalize Indonesian phone numbers
        if v.startswith("0"):
            v = "+62" + v[1:]
        elif v.startswith("62"):
            v = "+" + v
        elif not v.startswith("+62"):
            v = "+62" + v
        
        return v


# Create Schemas
class UserCreate(UserBase):
    """Schema untuk create user"""
    university_id: Optional[str] = Field(default=None, description="ID Universitas (required untuk student)")
    faculty_id: Optional[str] = Field(default=None, description="ID Fakultas (required untuk student)")
    department_id: Optional[str] = Field(default=None, description="ID Jurusan (required untuk student)")
    role: UserRoleSchema = Field(default=UserRoleSchema.STUDENT, description="Role user")
    initial_savings: float = Field(default=0.0, ge=0, description="Saldo awal tabungan")
    bio: Optional[str] = Field(default=None, max_length=500, description="Biografi singkat")
    
    @field_validator("email")
    @classmethod
    def validate_student_email(cls, v, info):
        """Validasi email untuk student harus .ac.id"""
        role = info.data.get("role", UserRoleSchema.STUDENT) if info.data else UserRoleSchema.STUDENT
        
        if role == UserRoleSchema.STUDENT:
            if not v.endswith(".ac.id"):
                raise ValueError("Email mahasiswa harus menggunakan domain .ac.id")
        
        return v.lower()
    
    @field_validator("initial_savings")
    @classmethod
    def validate_initial_savings(cls, v):
        """Validasi saldo awal"""
        if v < 0:
            raise ValueError("Saldo awal tidak boleh negatif")
        
        if v > 1_000_000_000:  # 1 Milyar
            raise ValueError("Saldo awal terlalu besar")
        
        return round(v, 2)


class UserCreateByAdmin(UserCreate):
    """Schema untuk create user oleh admin"""
    status: UserStatusSchema = Field(default=UserStatusSchema.ACTIVE, description="Status user")
    email_verified: bool = Field(default=False, description="Status verifikasi email")


# Update Schemas
class UserUpdate(BaseSchema):
    """Schema untuk update user"""
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=100, description="Nama lengkap")
    phone_number: Optional[str] = Field(default=None, description="Nomor telepon")
    university_id: Optional[str] = Field(default=None, description="ID Universitas")
    faculty_id: Optional[str] = Field(default=None, description="ID Fakultas")
    department_id: Optional[str] = Field(default=None, description="ID Jurusan")
    bio: Optional[str] = Field(default=None, max_length=500, description="Biografi")
    profile_picture: Optional[str] = Field(default=None, description="URL foto profil")
    
    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v):
        """Validasi nomor telepon"""
        if not v:
            return v
        
        v = v.replace(" ", "").replace("-", "")
        
        if v.startswith("0"):
            v = "+62" + v[1:]
        elif v.startswith("62"):
            v = "+" + v
        elif not v.startswith("+62"):
            v = "+62" + v
        
        return v


class UserUpdateByAdmin(UserUpdate):
    """Schema untuk update user oleh admin"""
    role: Optional[UserRoleSchema] = Field(default=None, description="Role user")
    status: Optional[UserStatusSchema] = Field(default=None, description="Status user")
    email_verified: Optional[bool] = Field(default=None, description="Status verifikasi email")


class UserUpdateProfile(BaseSchema):
    """Schema untuk update profile sendiri"""
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=100, description="Nama lengkap")
    phone_number: Optional[str] = Field(default=None, description="Nomor telepon")
    bio: Optional[str] = Field(default=None, max_length=500, description="Biografi")
    profile_picture: Optional[str] = Field(default=None, description="URL foto profil")


class UserUpdateUniversity(BaseSchema):
    """Schema untuk update informasi universitas"""
    university_id: str = Field(..., description="ID Universitas")
    faculty_id: str = Field(..., description="ID Fakultas")
    department_id: str = Field(..., description="ID Jurusan")


# Response Schemas
class UserResponse(UserBase, BaseResponse):
    """Schema untuk response user"""
    university_id: Optional[str] = Field(default=None, description="ID Universitas")
    faculty_id: Optional[str] = Field(default=None, description="ID Fakultas")
    department_id: Optional[str] = Field(default=None, description="ID Jurusan")
    role: UserRoleSchema = Field(..., description="Role user")
    status: UserStatusSchema = Field(..., description="Status user")
    initial_savings: float = Field(..., description="Saldo awal")
    profile_picture: Optional[str] = Field(default=None, description="URL foto profil")
    bio: Optional[str] = Field(default=None, description="Biografi")
    email_verified: bool = Field(..., description="Status verifikasi email")
    email_verified_at: Optional[datetime] = Field(default=None, description="Waktu verifikasi")
    last_login: Optional[datetime] = Field(default=None, description="Login terakhir")
    login_count: int = Field(..., description="Jumlah login")


class UserPublicResponse(BaseSchema):
    """Schema untuk response user public (tanpa info sensitive)"""
    id: str = Field(..., description="ID user")
    full_name: str = Field(..., description="Nama lengkap")
    email: EmailStr = Field(..., description="Email user")
    role: UserRoleSchema = Field(..., description="Role user")
    profile_picture: Optional[str] = Field(default=None, description="URL foto profil")
    bio: Optional[str] = Field(default=None, description="Biografi")
    university_id: Optional[str] = Field(default=None, description="ID Universitas")
    created_at: datetime = Field(..., description="Waktu dibuat")


class UserDetailResponse(UserResponse):
    """Schema untuk response user detail dengan info university"""
    university_name: Optional[str] = Field(default=None, description="Nama universitas")
    faculty_name: Optional[str] = Field(default=None, description="Nama fakultas")
    department_name: Optional[str] = Field(default=None, description="Nama jurusan")


class UserStatsResponse(BaseSchema):
    """Schema untuk response statistik user"""
    total_users: int = Field(..., description="Total user")
    total_students: int = Field(..., description="Total mahasiswa")
    total_admins: int = Field(..., description="Total admin")
    active_users: int = Field(..., description="User aktif")
    verified_users: int = Field(..., description="User terverifikasi")
    recent_registrations: int = Field(..., description="Registrasi bulan ini")


# Filter Schemas
class UserFilter(BaseFilter):
    """Schema untuk filter user"""
    role: Optional[UserRoleSchema] = Field(default=None, description="Filter role")
    status: Optional[UserStatusSchema] = Field(default=None, description="Filter status")
    university_id: Optional[str] = Field(default=None, description="Filter universitas")
    faculty_id: Optional[str] = Field(default=None, description="Filter fakultas")
    department_id: Optional[str] = Field(default=None, description="Filter jurusan")
    email_verified: Optional[bool] = Field(default=None, description="Filter verifikasi email")


# Authentication Schemas (untuk nanti)
class UserLogin(BaseSchema):
    """Schema untuk login user"""
    email: EmailStr = Field(..., description="Email user")
    password: str = Field(..., min_length=8, description="Password")


class UserRegister(UserCreate):
    """Schema untuk registrasi user"""
    password: str = Field(..., min_length=8, description="Password")
    confirm_password: str = Field(..., min_length=8, description="Konfirmasi password")
    
    @field_validator("confirm_password")
    @classmethod
    def validate_password_match(cls, v, info):
        """Validasi password match"""
        if info.data and "password" in info.data and v != info.data["password"]:
            raise ValueError("Password tidak cocok")
        return v


class UserPasswordChange(BaseSchema):
    """Schema untuk ganti password"""
    current_password: str = Field(..., description="Password saat ini")
    new_password: str = Field(..., min_length=8, description="Password baru")
    confirm_password: str = Field(..., min_length=8, description="Konfirmasi password baru")
    
    @field_validator("confirm_password")
    @classmethod
    def validate_password_match(cls, v, info):
        """Validasi password match"""
        if info.data and "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Password baru tidak cocok")
        return v


class UserPasswordReset(BaseSchema):
    """Schema untuk reset password"""
    email: EmailStr = Field(..., description="Email user")


class UserPasswordResetConfirm(BaseSchema):
    """Schema untuk konfirmasi reset password"""
    email: EmailStr = Field(..., description="Email user")
    otp_code: str = Field(..., min_length=4, max_length=8, description="Kode OTP")
    new_password: str = Field(..., min_length=8, description="Password baru")
    confirm_password: str = Field(..., min_length=8, description="Konfirmasi password baru")
    
    @field_validator("confirm_password")
    @classmethod
    def validate_password_match(cls, v, info):
        """Validasi password match"""
        if info.data and "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Password baru tidak cocok")
        return v


# Email Verification
class EmailVerificationRequest(BaseSchema):
    """Schema untuk request verifikasi email"""
    email: EmailStr = Field(..., description="Email untuk verifikasi")


class EmailVerificationConfirm(BaseSchema):
    """Schema untuk konfirmasi verifikasi email"""
    email: EmailStr = Field(..., description="Email")
    otp_code: str = Field(..., min_length=4, max_length=8, description="Kode OTP")


# Bulk Operations
class UserBulkStatusUpdate(BaseSchema):
    """Schema untuk bulk update status user"""
    user_ids: list[str] = Field(..., min_length=1, description="List ID user")
    status: UserStatusSchema = Field(..., description="Status baru")
    reason: Optional[str] = Field(default=None, description="Alasan perubahan")


class UserBulkDelete(BaseSchema):
    """Schema untuk bulk delete user"""
    user_ids: list[str] = Field(..., min_length=1, description="List ID user")
    permanent: bool = Field(default=False, description="Hapus permanen atau soft delete")