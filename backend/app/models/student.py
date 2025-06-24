from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
from bson import ObjectId
from enum import Enum

class PyObjectId(ObjectId):
    """
    Custom ObjectId class compatible with Pydantic v2
    """
    
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: Any
    ) -> core_schema.CoreSchema:
        return core_schema.union_schema([
            core_schema.is_instance_schema(ObjectId),
            core_schema.chain_schema([
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(cls.validate),
            ]),
        ])

    @classmethod
    def __get_pydantic_json_schema__(
        cls, schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return {"type": "string", "format": "objectid"}

    @classmethod
    def validate(cls, v: Any) -> ObjectId:
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str):
            if ObjectId.is_valid(v):
                return ObjectId(v)
            raise ValueError("Invalid ObjectId")
        raise ValueError("Invalid ObjectId")

    def __str__(self) -> str:
        return str(super())

    def __repr__(self) -> str:
        return f"PyObjectId('{super().__str__()}')"

class OTPType(str, Enum):
    REGISTRATION = "registration"
    FORGOT_PASSWORD = "forgot_password"
    EMAIL_VERIFICATION = "email_verification"
    LOGIN_VERIFICATION = "login_verification"

class OTPStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    EXPIRED = "expired"
    USED = "used"

class OTPRecord(BaseModel):
    code: str = Field(..., description="6-digit OTP code")
    type: OTPType
    status: OTPStatus = OTPStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(minutes=10))
    verified_at: Optional[datetime] = None
    attempts: int = 0
    max_attempts: int = 3
    
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self) -> bool:
        return (
            self.status == OTPStatus.PENDING and 
            not self.is_expired() and 
            self.attempts < self.max_attempts
        )

class AccountVerification(BaseModel):
    email_verified: bool = False
    email_verified_at: Optional[datetime] = None
    phone_verified: bool = False
    phone_verified_at: Optional[datetime] = None
    registration_completed: bool = False
    registration_completed_at: Optional[datetime] = None

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
    phone_number: Optional[str] = None
    
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
    
    # Account Verification
    verification: AccountVerification = Field(default_factory=AccountVerification)
    
    # OTP Records
    otp_records: List[OTPRecord] = []
    
    # Settings
    settings: Settings = Field(default_factory=Settings)
    
    # Gamification
    gamification: Gamification = Field(default_factory=Gamification)
    
    # Security
    password_reset_token: Optional[str] = None
    password_reset_expires: Optional[datetime] = None
    failed_login_attempts: int = 0
    account_locked_until: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    is_active: bool = True

    def add_otp_record(self, code: str, otp_type: OTPType) -> OTPRecord:
        """Add new OTP record and deactivate previous ones of the same type"""
        # Deactivate previous OTP records of the same type
        for otp in self.otp_records:
            if otp.type == otp_type and otp.status == OTPStatus.PENDING:
                otp.status = OTPStatus.EXPIRED
        
        # Create new OTP record
        new_otp = OTPRecord(code=code, type=otp_type)
        self.otp_records.append(new_otp)
        return new_otp
    
    def get_active_otp(self, otp_type: OTPType) -> Optional[OTPRecord]:
        """Get active OTP record for specific type"""
        for otp in reversed(self.otp_records):  # Get most recent first
            if otp.type == otp_type and otp.is_valid():
                return otp
        return None
    
    def verify_otp(self, code: str, otp_type: OTPType) -> bool:
        """Verify OTP code"""
        otp_record = self.get_active_otp(otp_type)
        if not otp_record:
            return False
        
        otp_record.attempts += 1
        
        if otp_record.code == code:
            otp_record.status = OTPStatus.VERIFIED
            otp_record.verified_at = datetime.utcnow()
            
            # Update verification status based on OTP type
            if otp_type == OTPType.REGISTRATION:
                self.verification.email_verified = True
                self.verification.email_verified_at = datetime.utcnow()
                self.verification.registration_completed = True
                self.verification.registration_completed_at = datetime.utcnow()
            elif otp_type == OTPType.EMAIL_VERIFICATION:
                self.verification.email_verified = True
                self.verification.email_verified_at = datetime.utcnow()
            
            return True
        else:
            if otp_record.attempts >= otp_record.max_attempts:
                otp_record.status = OTPStatus.EXPIRED
            return False
    
    def is_account_locked(self) -> bool:
        """Check if account is locked due to failed login attempts"""
        if self.account_locked_until:
            if datetime.utcnow() < self.account_locked_until:
                return True
            else:
                # Reset lock if time has passed
                self.account_locked_until = None
                self.failed_login_attempts = 0
        return False

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
        "json_schema_extra": {
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
    verification: AccountVerification
    settings: Settings
    gamification: Gamification
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool

    model_config = {"populate_by_name": True}

# OTP Related Request/Response Models
class OTPRequest(BaseModel):
    email: EmailStr
    type: OTPType

class OTPVerification(BaseModel):
    email: EmailStr
    code: str
    type: OTPType

class OTPResponse(BaseModel):
    message: str
    expires_at: datetime
    attempts_remaining: int

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp_code: str
    new_password: str

class VerificationStatusResponse(BaseModel):
    email_verified: bool
    phone_verified: bool
    registration_completed: bool