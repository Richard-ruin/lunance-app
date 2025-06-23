from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId
from enum import Enum

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class IncomeSource(BaseModel):
    type: str = Field(..., description="allowance, part_time, scholarship, freelance")
    amount: float
    frequency: str = Field(..., description="monthly, weekly")

class ExamPeriod(BaseModel):
    start_date: datetime
    end_date: datetime
    type: str = Field(..., description="midterm, final, thesis_defense")

class HolidayPeriod(BaseModel):
    start_date: datetime
    end_date: datetime
    name: str

class AcademicInfo(BaseModel):
    university: str
    semester_start: datetime
    semester_end: datetime
    exam_periods: List[ExamPeriod] = []
    holiday_periods: List[HolidayPeriod] = []

class SeasonalAdjustment(BaseModel):
    period: str = Field(..., description="exam_week, holiday, semester_start")
    income_multiplier: float = Field(default=1.0, description="1.2 means 20% increase")
    expense_multiplier: float = Field(default=1.0)

class SpendingPatterns(BaseModel):
    weekly_cycle: bool = False
    monthly_cycle: bool = False
    academic_cycle: bool = False
    seasonal_adjustments: List[SeasonalAdjustment] = []

class SavingsGoal(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(..., description="Laptop Baru, Liburan, Emergency Fund")
    target_amount: float
    current_amount: float = 0.0
    target_date: datetime
    priority: str = Field(..., description="high, medium, low")
    category: str = Field(..., description="gadget, travel, emergency, academic")
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Profile(BaseModel):
    full_name: str
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    
    # University Info
    university: str
    faculty: str
    major: str
    student_id: str
    semester: int
    graduation_year: int
    
    # Academic Calendar Context
    academic_info: AcademicInfo
    
    # Financial Profile
    monthly_allowance: float = 0.0
    income_sources: List[IncomeSource] = []
    
    # Financial Patterns for Prophet
    spending_patterns: SpendingPatterns = Field(default_factory=SpendingPatterns)
    
    # Living Situation
    accommodation: str = Field(..., description="kos, rumah_ortu, asrama")
    transportation: str = Field(..., description="motor, public_transport, walking")
    
    # Savings Goals
    savings_goals: List[SavingsGoal] = []

class NotificationSettings(BaseModel):
    budget_alerts: bool = True
    savings_reminders: bool = True
    expense_sharing_updates: bool = True
    achievement_notifications: bool = True

class DisplaySettings(BaseModel):
    currency: str = "IDR"
    theme: str = "light"
    language: str = "id"

class PrivacySettings(BaseModel):
    show_in_leaderboard: bool = True
    allow_expense_sharing: bool = True

class Settings(BaseModel):
    notifications: NotificationSettings = Field(default_factory=NotificationSettings)
    display: DisplaySettings = Field(default_factory=DisplaySettings)
    privacy: PrivacySettings = Field(default_factory=PrivacySettings)

class CurrentStreak(BaseModel):
    type: str = Field(..., description="daily_logging, savings, budget_adherence")
    count: int = 0
    last_update: datetime = Field(default_factory=datetime.utcnow)

class Achievement(BaseModel):
    achievement_id: str
    earned_date: datetime
    progress: float = 0.0

class Gamification(BaseModel):
    level: int = 1
    experience_points: int = 0
    badges: List[str] = []
    current_streak: Optional[CurrentStreak] = None
    achievements: List[Achievement] = []

class Student(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    email: EmailStr
    password_hash: str
    
    # Student Profile
    profile: Profile
    
    # Settings
    settings: Settings = Field(default_factory=Settings)
    
    # Gamification
    gamification: Gamification = Field(default_factory=Gamification)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    is_active: bool = True

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "email": "student@univ.ac.id",
                "profile": {
                    "full_name": "Ahmad Kurniawan",
                    "nickname": "Ahmad",
                    "university": "Universitas Indonesia",
                    "faculty": "Fakultas Teknik",
                    "major": "Teknik Informatika",
                    "student_id": "1906123456",
                    "semester": 5,
                    "graduation_year": 2025,
                    "monthly_allowance": 1500000,
                    "accommodation": "kos",
                    "transportation": "motor"
                }
            }
        }

# Request/Response Models
class StudentCreate(BaseModel):
    email: EmailStr
    password: str
    profile: Profile

class StudentUpdate(BaseModel):
    profile: Optional[Profile] = None
    settings: Optional[Settings] = None

class StudentResponse(BaseModel):
    id: str = Field(alias="_id")
    email: EmailStr
    profile: Profile
    settings: Settings
    gamification: Gamification
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool

    class Config:
        allow_population_by_field_name = True