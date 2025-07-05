# app/models/user.py (updated untuk backward compatibility)
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, Dict
from datetime import datetime
from .base import BaseDocument, PyObjectId
import re

class NotificationSettings(BaseModel):
    email_notifications: bool = True
    push_notifications: bool = True
    weekly_summary: bool = True
    goal_reminders: bool = True

class UserPreferences(BaseModel):
    language: str = "id"
    currency: str = "IDR"
    date_format: str = "DD/MM/YYYY"

class UserBase(BaseModel):
    email: EmailStr
    nama_lengkap: str
    nomor_telepon: str
    universitas_id: PyObjectId
    fakultas: str
    prodi: str
    role: str = "mahasiswa"

    @field_validator('email')
    @classmethod
    def validate_academic_email(cls, v):
        if not v.endswith('.ac.id'):
            raise ValueError('Email harus menggunakan domain kampus (.ac.id)')
        return v

    @field_validator('nomor_telepon')
    @classmethod
    def validate_phone(cls, v):
        if not re.match(r'^(\+62|0)[0-9]{9,12}$', v):
            raise ValueError('Format nomor telepon tidak valid')
        return v

class UserCreate(UserBase):
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password minimal 8 karakter')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Password harus mengandung huruf')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password harus mengandung angka')
        return v

class User(BaseDocument):
    email: EmailStr
    nama_lengkap: str
    nomor_telepon: str
    universitas_id: PyObjectId
    fakultas: str
    prodi: str
    password_hash: str
    role: str = "mahasiswa"
    is_verified: bool = False
    otp_code: Optional[str] = None
    otp_expires: Optional[datetime] = None
    is_active: bool = True
    
    # Extended fields dengan default values
    profile_picture: Optional[str] = None
    tabungan_awal: Optional[float] = None
    notification_settings: NotificationSettings = NotificationSettings()
    preferences: UserPreferences = UserPreferences()

class UserInDB(User):
    password_hash: str

class UserProfileUpdate(BaseModel):
    nama_lengkap: Optional[str] = None
    nomor_telepon: Optional[str] = None
    fakultas: Optional[str] = None
    prodi: Optional[str] = None
    
    @field_validator('nomor_telepon')
    @classmethod
    def validate_phone(cls, v):
        if v and not re.match(r'^(\+62|0)[0-9]{9,12}$', v):
            raise ValueError('Format nomor telepon tidak valid')
        return v

# Updated UserResponse dengan Optional fields untuk backward compatibility
class UserResponse(BaseModel):
    model_config = {"populate_by_name": True}
    
    id: str = Field(alias="_id")
    email: EmailStr
    nama_lengkap: str
    nomor_telepon: str
    universitas_id: str
    fakultas: str
    prodi: str
    role: str
    is_verified: bool
    is_active: bool
    profile_picture: Optional[str] = None
    tabungan_awal: Optional[float] = None
    # Make these optional untuk backward compatibility
    notification_settings: Optional[NotificationSettings] = NotificationSettings()
    preferences: Optional[UserPreferences] = UserPreferences()
    created_at: datetime

    @classmethod
    def from_db_user(cls, user_data: dict):
        """Create UserResponse from database user data with proper defaults"""
        # Set defaults if fields are missing
        notification_settings = user_data.get("notification_settings", {})
        if not notification_settings:
            notification_settings = NotificationSettings().model_dump()
        
        preferences = user_data.get("preferences", {})
        if not preferences:
            preferences = UserPreferences().model_dump()
        
        return cls(
            _id=str(user_data["_id"]),
            email=user_data["email"],
            nama_lengkap=user_data["nama_lengkap"],
            nomor_telepon=user_data["nomor_telepon"],
            universitas_id=str(user_data["universitas_id"]),
            fakultas=user_data["fakultas"],
            prodi=user_data["prodi"],
            role=user_data["role"],
            is_verified=user_data["is_verified"],
            is_active=user_data["is_active"],
            profile_picture=user_data.get("profile_picture"),
            tabungan_awal=user_data.get("tabungan_awal"),
            notification_settings=notification_settings,
            preferences=preferences,
            created_at=user_data["created_at"]
        )

class InitialBalanceSet(BaseModel):
    tabungan_awal: float
    
    @field_validator('tabungan_awal')
    @classmethod
    def validate_balance(cls, v):
        if v < 0:
            raise ValueError('Tabungan awal tidak boleh negatif')
        return v

class UserStats(BaseModel):
    total_users: int
    active_users: int
    verified_users: int
    pending_verifications: int
    total_admins: int
    recent_registrations: int