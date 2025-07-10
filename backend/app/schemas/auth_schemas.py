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
    """Schema untuk setup profil user"""
    full_name: str = Field(..., min_length=2, max_length=100)
    phone_number: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')
    date_of_birth: Optional[datetime] = None
    occupation: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    
    # Preferences
    language: str = Field(default="id", pattern=r'^(id|en)$')
    currency: str = Field(default="IDR", pattern=r'^[A-Z]{3}$')
    notifications_enabled: bool = True
    voice_enabled: bool = True
    dark_mode: bool = False

class FinancialSetup(BaseModel):
    """Schema untuk setup keuangan awal"""
    monthly_income: float = Field(..., gt=0)
    monthly_budget: Optional[float] = Field(None, gt=0)
    savings_goal_percentage: float = Field(default=20.0, ge=0, le=100)
    emergency_fund_target: Optional[float] = Field(None, gt=0)
    primary_bank: Optional[str] = Field(None, max_length=100)
    
    @model_validator(mode='after')
    def budget_not_exceed_income(self) -> Self:
        if self.monthly_budget and self.monthly_budget > self.monthly_income:
            raise ValueError('Budget bulanan tidak boleh melebihi pendapatan bulanan')
        return self
    
    @field_validator('emergency_fund_target')
    @classmethod
    def emergency_fund_reasonable(cls, v, info):
        if v and hasattr(info, 'data') and 'monthly_income' in info.data:
            # Emergency fund sebaiknya 3-12 bulan pengeluaran
            max_reasonable = info.data['monthly_income'] * 12
            if v > max_reasonable:
                raise ValueError('Target dana darurat terlalu besar (maksimal 12x pendapatan bulanan)')
        return v

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
    date_of_birth: Optional[datetime] = None
    occupation: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    
    # Preferences yang bisa diupdate
    language: Optional[str] = Field(None, pattern=r'^(id|en)$')
    currency: Optional[str] = Field(None, pattern=r'^[A-Z]{3}$')
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