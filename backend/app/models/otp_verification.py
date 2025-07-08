# app/models/otp_verification.py (Fixed)
"""OTP verification models with fixed PyObjectId."""

from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime, timedelta
from bson import ObjectId
from enum import Enum

# Import the fixed PyObjectId from user.py
from .user import PyObjectId


class OTPType(str, Enum):
    """OTP type enumeration."""
    REGISTER = "register"
    RESET_PASSWORD = "reset_password"
    EMAIL_VERIFICATION = "email_verification"
    LOGIN_2FA = "login_2fa"


class OTPVerificationBase(BaseModel):
    """Base OTP verification model."""
    email: EmailStr
    otp_type: OTPType
    
    @field_validator('email')
    @classmethod
    def validate_email_domain(cls, v):
        """Validate email is academic domain (ac.id)."""
        if not str(v).endswith('.ac.id'):
            raise ValueError('Email must be from academic domain (.ac.id)')
        return v


class OTPVerificationCreate(OTPVerificationBase):
    """OTP verification creation schema."""
    pass


class OTPVerificationVerify(BaseModel):
    """OTP verification verify schema."""
    email: EmailStr
    otp_code: str = Field(..., min_length=6, max_length=6, pattern=r'^\d{6}$')
    otp_type: OTPType
    
    @field_validator('email')
    @classmethod
    def validate_email_domain(cls, v):
        """Validate email is academic domain (ac.id)."""
        if not str(v).endswith('.ac.id'):
            raise ValueError('Email must be from academic domain (.ac.id)')
        return v
    
    @field_validator('otp_code')
    @classmethod
    def validate_otp_code(cls, v):
        """Validate OTP code format."""
        if not v.isdigit():
            raise ValueError('OTP code must contain only digits')
        return v


class OTPVerificationInDB(OTPVerificationBase):
    """OTP verification model in database."""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    otp_code: str = Field(..., min_length=6, max_length=6)
    expires_at: datetime
    is_used: bool = False
    attempts: int = 0
    max_attempts: int = 3
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @classmethod
    def create_otp(cls, email: str, otp_type: OTPType, otp_code: str, 
                   expires_minutes: int = 15) -> 'OTPVerificationInDB':
        """Create new OTP verification entry."""
        return cls(
            email=email,
            otp_type=otp_type,
            otp_code=otp_code,
            expires_at=datetime.utcnow() + timedelta(minutes=expires_minutes)
        )
    
    def is_expired(self) -> bool:
        """Check if OTP is expired."""
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self) -> bool:
        """Check if OTP is valid (not used, not expired, attempts not exceeded)."""
        return (
            not self.is_used and 
            not self.is_expired() and 
            self.attempts < self.max_attempts
        )
    
    def increment_attempts(self):
        """Increment verification attempts."""
        self.attempts += 1
    
    def mark_as_used(self):
        """Mark OTP as used."""
        self.is_used = True
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )


class OTPVerificationResponse(BaseModel):
    """OTP verification response schema."""
    id: str = Field(alias="_id")
    email: EmailStr
    otp_type: OTPType
    expires_at: datetime
    is_used: bool
    attempts: int
    max_attempts: int
    created_at: datetime
    
    # Calculated fields
    is_expired: bool = False
    is_valid: bool = False
    time_remaining_seconds: int = 0
    
    def model_post_init(self, __context):
        """Calculate derived fields."""
        now = datetime.utcnow()
        self.is_expired = now > self.expires_at
        self.is_valid = (
            not self.is_used and 
            not self.is_expired and 
            self.attempts < self.max_attempts
        )
        if not self.is_expired:
            self.time_remaining_seconds = max(0, int((self.expires_at - now).total_seconds()))
    
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )


class OTPVerificationListResponse(BaseModel):
    """OTP verification list response schema."""
    otps: List[OTPVerificationResponse]
    total: int
    page: int
    per_page: int
    pages: int


class OTPStats(BaseModel):
    """OTP statistics schema."""
    total_otps_sent: int = 0
    total_otps_verified: int = 0
    total_otps_expired: int = 0
    total_otps_failed: int = 0
    verification_rate: float = 0.0
    otps_sent_today: int = 0
    otps_verified_today: int = 0


class OTPResendRequest(BaseModel):
    """OTP resend request schema."""
    email: EmailStr
    otp_type: OTPType
    
    @field_validator('email')
    @classmethod
    def validate_email_domain(cls, v):
        """Validate email is academic domain (ac.id)."""
        if not str(v).endswith('.ac.id'):
            raise ValueError('Email must be from academic domain (.ac.id)')
        return v


class OTPVerificationResult(BaseModel):
    """OTP verification result schema."""
    success: bool
    message: str
    remaining_attempts: Optional[int] = None
    time_remaining_seconds: Optional[int] = None
    can_resend: bool = False


class OTPSendResult(BaseModel):
    """OTP send result schema."""
    success: bool
    message: str
    expires_at: Optional[datetime] = None
    time_remaining_seconds: Optional[int] = None
    attempts_remaining: Optional[int] = None


class OTPFilter(BaseModel):
    """OTP filter schema."""
    email: Optional[EmailStr] = None
    otp_type: Optional[OTPType] = None
    is_used: Optional[bool] = None
    is_expired: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    def model_post_init(self, __context):
        """Validate filter logic."""
        if self.start_date is not None and self.end_date is not None:
            if self.start_date > self.end_date:
                raise ValueError('start_date cannot be after end_date')


class OTPCleanupResult(BaseModel):
    """OTP cleanup result schema."""
    expired_otps_removed: int = 0
    used_otps_removed: int = 0
    old_otps_removed: int = 0
    total_removed: int = 0