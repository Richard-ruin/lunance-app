# app/schemas/auth_schemas.py - UPDATED untuk metode 50/30/20
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
    """
    Schema untuk setup keuangan mahasiswa dengan metode 50/30/20 Elizabeth Warren
    
    Metode 50/30/20:
    - 50% Needs (Kebutuhan): Kos, makan, transport, pendidikan
    - 30% Wants (Keinginan): Hiburan, jajan, shopping, target tabungan barang
    - 20% Savings (Tabungan): Tabungan umum untuk masa depan
    """
    current_savings: float = Field(..., ge=0, description="Total tabungan awal saat ini")
    monthly_income: float = Field(..., gt=0, description="Pemasukan bulanan (uang saku/gaji)")
    primary_bank: str = Field(..., min_length=2, max_length=100, description="Bank/e-wallet utama")
    
    @field_validator('monthly_income')
    @classmethod
    def validate_monthly_income(cls, v):
        if v < 100000:  # Minimal 100rb per bulan untuk mahasiswa Indonesia
            raise ValueError('Pemasukan bulanan minimal Rp 100.000')
        if v > 50000000:  # Maksimal 50 juta (sanity check)
            raise ValueError('Pemasukan bulanan maksimal Rp 50.000.000')
        return v
    
    @field_validator('current_savings')
    @classmethod
    def validate_current_savings(cls, v):
        if v > 1000000000:  # Maksimal 1 miliar (sanity check)
            raise ValueError('Tabungan awal maksimal Rp 1.000.000.000')
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
    university: Optional[str] = Field(None, min_length=2, max_length=200)
    city: Optional[str] = Field(None, min_length=2, max_length=100)
    occupation: Optional[str] = Field(None, max_length=100)
    
    # Preferences yang bisa diupdate (language dan currency dihapus)
    notifications_enabled: Optional[bool] = None
    voice_enabled: Optional[bool] = None
    dark_mode: Optional[bool] = None
    auto_categorization: Optional[bool] = None

class UpdateFinancialSettings(BaseModel):
    """Schema untuk update financial settings 50/30/20"""
    current_savings: Optional[float] = Field(None, ge=0, description="Update tabungan awal")
    monthly_income: Optional[float] = Field(None, gt=0, description="Update pemasukan bulanan")
    primary_bank: Optional[str] = Field(None, min_length=2, max_length=100, description="Update bank utama")
    
    @field_validator('monthly_income')
    @classmethod
    def validate_monthly_income(cls, v):
        if v is not None:
            if v < 100000:
                raise ValueError('Pemasukan bulanan minimal Rp 100.000')
            if v > 50000000:
                raise ValueError('Pemasukan bulanan maksimal Rp 50.000.000')
        return v

class UpdateFinancialSettings(BaseModel):
    """Schema untuk update financial settings 50/30/20"""
    current_savings: Optional[float] = Field(None, ge=0, description="Update tabungan awal")
    monthly_income: Optional[float] = Field(None, gt=0, description="Update pemasukan bulanan")
    primary_bank: Optional[str] = Field(None, min_length=2, max_length=100, description="Update bank utama")
    
    @field_validator('monthly_income')
    @classmethod
    def validate_monthly_income(cls, v):
        if v is not None:
            if v < 100000:
                raise ValueError('Pemasukan bulanan minimal Rp 100.000')
            if v > 50000000:
                raise ValueError('Pemasukan bulanan maksimal Rp 50.000.000')
        return v

class ApiResponse(BaseModel):
    """Schema untuk standard API response"""
    success: bool
    message: str
    data: Optional[dict] = None
    errors: Optional[list] = None

# NEW: Budget allocation response schema
class BudgetAllocationResponse(BaseModel):
    """Schema untuk response alokasi budget 50/30/20"""
    monthly_income: float
    needs_budget: float      # 50%
    wants_budget: float      # 30% 
    savings_budget: float    # 20%
    needs_percentage: float = 50.0
    wants_percentage: float = 30.0
    savings_percentage: float = 20.0
    method: str = "50/30/20 Elizabeth Warren"
    reset_date: str  # Tanggal 1 setiap bulan
    
class MonthlyBudgetStatus(BaseModel):
    """Schema untuk status budget bulanan"""
    period: str  # "Januari 2025"
    budget_allocation: BudgetAllocationResponse
    actual_spending: dict  # {"needs": amount, "wants": amount, "savings": amount}
    remaining_budget: dict  # {"needs": amount, "wants": amount, "savings": amount}
    percentage_used: dict  # {"needs": %, "wants": %, "savings": %}
    budget_health: str  # "excellent", "good", "warning", "over_budget"
    recommendations: list  # Tips untuk mengoptimalkan budget