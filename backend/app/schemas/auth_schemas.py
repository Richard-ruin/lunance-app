from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from typing_extensions import Self
import re

class UserRegister(BaseModel):
    """Schema untuk registrasi user baru"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    confirm_password: str
    
    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v):
        if not re.match("^[a-zA-Z0-9_]+$", v):
            raise ValueError('Username hanya boleh mengandung huruf, angka, dan underscore')
        return v
    
    @field_validator('password')
    @classmethod
    def password_strength(cls, v):
        if len(v) < 6:
            raise ValueError('Password minimal 6 karakter')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Password harus mengandung minimal 1 huruf')
        if not re.search(r'\d', v):
            raise ValueError('Password harus mengandung minimal 1 angka')
        return v
    
    @model_validator(mode='after')
    def passwords_match(self) -> Self:
        if self.password != self.confirm_password:
            raise ValueError('Password dan konfirmasi password tidak sama')
        return self

class UserLogin(BaseModel):
    """Schema untuk login user"""
    email: EmailStr
    password: str

class Token(BaseModel):
    """Schema untuk response token"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # dalam detik

class TokenRefresh(BaseModel):
    """Schema untuk refresh token"""
    refresh_token: str

class ProfileSetup(BaseModel):
    """Schema untuk setup profil mahasiswa Indonesia"""
    full_name: str = Field(..., min_length=2, max_length=100)
    phone_number: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')
    university: str = Field(..., min_length=2, max_length=200)  # Universitas (wajib)
    city: str = Field(..., min_length=2, max_length=100)  # Kota/kecamatan (wajib)
    occupation: Optional[str] = Field(None, max_length=100)  # Pekerjaan sampingan (opsional)
    
    # Preferences (tetap sama, tapi language dan currency dihapus karena sudah fix untuk Indonesia)
    notifications_enabled: bool = True
    voice_enabled: bool = True
    dark_mode: bool = False

class FinancialSetup(BaseModel):
    """Schema untuk setup keuangan mahasiswa"""
    current_savings: float = Field(..., ge=0)  # Total tabungan saat ini
    monthly_savings_target: float = Field(..., gt=0)  # Target tabungan bulanan
    emergency_fund: float = Field(..., ge=0)  # Dana darurat saat ini
    primary_bank: str = Field(..., min_length=2, max_length=100)  # Bank/e-wallet utama (wajib)

class UserResponse(BaseModel):
    """Schema untuk response user data"""
    id: str
    username: str
    email: str
    profile: Optional[dict] = None
    preferences: dict
    financial_settings: Optional[dict] = None
    is_active: bool
    is_verified: bool
    is_premium: bool
    profile_setup_completed: bool
    financial_setup_completed: bool
    onboarding_completed: bool
    created_at: datetime
    last_login: Optional[datetime] = None

class ChangePassword(BaseModel):
    """Schema untuk ganti password"""
    current_password: str
    new_password: str = Field(..., min_length=6)
    confirm_password: str
    
    @field_validator('new_password')
    @classmethod
    def password_strength(cls, v):
        if len(v) < 6:
            raise ValueError('Password minimal 6 karakter')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Password harus mengandung minimal 1 huruf')
        if not re.search(r'\d', v):
            raise ValueError('Password harus mengandung minimal 1 angka')
        return v
    
    @model_validator(mode='after')
    def passwords_match(self) -> Self:
        if self.new_password != self.confirm_password:
            raise ValueError('Password baru dan konfirmasi tidak sama')
        return self

class UpdateProfile(BaseModel):
    """Schema untuk update profil"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone_number: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')
    university: Optional[str] = Field(None, min_length=2, max_length=200)
    city: Optional[str] = Field(None, min_length=2, max_length=100)
    occupation: Optional[str] = Field(None, max_length=100)
    
    # Preferences yang bisa diupdate (language dan currency dihapus)
    notifications_enabled: Optional[bool] = None
    voice_enabled: Optional[bool] = None
    dark_mode: Optional[bool] = None
    auto_categorization: Optional[bool] = None

class ApiResponse(BaseModel):
    """Schema untuk standard API response"""
    success: bool
    message: str
    data: Optional[dict] = None
    errors: Optional[list] = None