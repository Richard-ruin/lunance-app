from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId
from enum import Enum

class UserPreferences(BaseModel):
    """Model untuk preferensi user"""
    language: str = "id"  # Default Bahasa Indonesia
    currency: str = "IDR"  # Default Rupiah
    date_format: str = "DD/MM/YYYY"
    time_format: str = "24h"
    notifications_enabled: bool = True
    voice_enabled: bool = True
    dark_mode: bool = False
    auto_categorization: bool = True

class FinancialSettings(BaseModel):
    """Model untuk pengaturan keuangan"""
    monthly_income: Optional[float] = None
    monthly_budget: Optional[float] = None
    savings_goal_percentage: float = 20.0  # Default 20% dari income
    emergency_fund_target: Optional[float] = None
    primary_bank: Optional[str] = None
    expense_categories: list = Field(default_factory=lambda: [
        "Makanan & Minuman",
        "Transportasi", 
        "Belanja",
        "Hiburan",
        "Kesehatan",
        "Pendidikan",
        "Tagihan",
        "Lainnya"
    ])
    income_categories: list = Field(default_factory=lambda: [
        "Gaji",
        "Freelance",
        "Bisnis",
        "Investasi",
        "Lainnya"
    ])

class UserProfile(BaseModel):
    """Model untuk profil user"""
    full_name: str
    phone_number: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    occupation: Optional[str] = None
    city: Optional[str] = None
    profile_picture: Optional[str] = None

class User(BaseModel):
    """Model utama untuk User"""
    id: Optional[str] = Field(default=None, alias="_id")
    username: str
    email: EmailStr
    hashed_password: str
    
    # Profile information
    profile: Optional[UserProfile] = None
    
    # App preferences
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    
    # Financial settings
    financial_settings: Optional[FinancialSettings] = None
    
    # Account status
    is_active: bool = True
    is_verified: bool = False
    is_premium: bool = False
    
    # Setup status
    profile_setup_completed: bool = False
    financial_setup_completed: bool = False
    onboarding_completed: bool = False
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    # Refresh token untuk session management
    refresh_token: Optional[str] = None
    
    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }
    
    @classmethod
    def from_mongo(cls, data: Dict[str, Any]) -> "User":
        """Mengkonversi data dari MongoDB ke User model"""
        if data is None:
            return None
            
        # Konversi ObjectId ke string
        if "_id" in data and data["_id"] is not None:
            data["_id"] = str(data["_id"])
        elif "_id" not in data:
            data["_id"] = None
            
        return cls(**data)
    
    def to_mongo(self) -> Dict[str, Any]:
        """Mengkonversi User model ke format MongoDB"""
        # Gunakan dict dengan by_alias=True untuk mendapatkan _id
        data = self.dict(by_alias=True, exclude_unset=True)
        
        # Hapus _id jika None (untuk insert baru)
        if "_id" in data and data["_id"] is None:
            del data["_id"]
            
        return data
    
    def update_last_login(self):
        """Update timestamp last login"""
        self.last_login = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def complete_profile_setup(self):
        """Menandai profile setup sebagai selesai"""
        self.profile_setup_completed = True
        self.updated_at = datetime.utcnow()
    
    def complete_financial_setup(self):
        """Menandai financial setup sebagai selesai"""
        self.financial_setup_completed = True
        self.updated_at = datetime.utcnow()
        
        # Check jika semua setup sudah selesai
        if self.profile_setup_completed and self.financial_setup_completed:
            self.onboarding_completed = True
    
    def is_setup_complete(self) -> bool:
        """Mengecek apakah setup user sudah lengkap"""
        return self.profile_setup_completed and self.financial_setup_completed

class UserInDB(User):
    """Model untuk user yang disimpan di database"""
    pass