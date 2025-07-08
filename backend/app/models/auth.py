# app/models/auth.py (Fixed)
"""Authentication models with fixed PyObjectId."""

from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
from typing import Optional
from datetime import datetime

# Import the fixed PyObjectId from user.py
from .user import UserRole, PyObjectId


class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str = Field(..., min_length=1)
    remember_me: bool = False
    
    @field_validator('email')
    @classmethod
    def validate_email_domain(cls, v):
        """Validate email is academic domain (ac.id)."""
        if not str(v).endswith('.ac.id'):
            raise ValueError('Email must be from academic domain (.ac.id)')
        return v


class RegisterRequest(BaseModel):
    """Registration request schema."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=2, max_length=100)
    phone_number: Optional[str] = Field(None, pattern=r'^\+?[\d\s\-\(\)]{10,15}$')
    university_id: Optional[str] = None
    faculty_id: Optional[str] = None
    major_id: Optional[str] = None
    initial_savings: Optional[float] = Field(None, ge=0)
    otp_code: str = Field(..., min_length=6, max_length=6, pattern=r'^\d{6}$')
    
    @field_validator('email')
    @classmethod
    def validate_email_domain(cls, v):
        """Validate email is academic domain (ac.id)."""
        if not str(v).endswith('.ac.id'):
            raise ValueError('Email must be from academic domain (.ac.id)')
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in v):
            raise ValueError('Password must contain at least one special character')
        return v
    
    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v):
        """Validate full name contains only letters and spaces."""
        if not v.replace(' ', '').replace('.', '').isalpha():
            raise ValueError('Full name must contain only letters, spaces, and dots')
        return v.title()
    
    @field_validator('otp_code')
    @classmethod
    def validate_otp_code(cls, v):
        """Validate OTP code format."""
        if not v.isdigit():
            raise ValueError('OTP code must contain only digits')
        return v
    
    def model_post_init(self, __context):
        """Validate password confirmation."""
        if self.password != self.confirm_password:
            raise ValueError('Passwords do not match')


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    refresh_expires_in: int  # seconds


class LoginResponse(BaseModel):
    """Login response schema."""
    user: dict  # UserResponse will be used here
    tokens: TokenResponse
    message: str = "Login successful"


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""
    refresh_token: str = Field(..., min_length=1)


class LogoutRequest(BaseModel):
    """Logout request schema."""
    refresh_token: Optional[str] = None


class PasswordResetRequest(BaseModel):
    """Password reset request schema."""
    email: EmailStr
    
    @field_validator('email')
    @classmethod
    def validate_email_domain(cls, v):
        """Validate email is academic domain (ac.id)."""
        if not str(v).endswith('.ac.id'):
            raise ValueError('Email must be from academic domain (.ac.id)')
        return v


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema."""
    email: EmailStr
    otp_code: str = Field(..., min_length=6, max_length=6, pattern=r'^\d{6}$')
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_new_password: str = Field(..., min_length=8, max_length=128)
    
    @field_validator('email')
    @classmethod
    def validate_email_domain(cls, v):
        """Validate email is academic domain (ac.id)."""
        if not str(v).endswith('.ac.id'):
            raise ValueError('Email must be from academic domain (.ac.id)')
        return v
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        """Validate new password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in v):
            raise ValueError('Password must contain at least one special character')
        return v
    
    @field_validator('otp_code')
    @classmethod
    def validate_otp_code(cls, v):
        """Validate OTP code format."""
        if not v.isdigit():
            raise ValueError('OTP code must contain only digits')
        return v
    
    def model_post_init(self, __context):
        """Validate password confirmation."""
        if self.new_password != self.confirm_new_password:
            raise ValueError('New passwords do not match')


class EmailVerificationRequest(BaseModel):
    """Email verification request schema."""
    email: EmailStr
    
    @field_validator('email')
    @classmethod
    def validate_email_domain(cls, v):
        """Validate email is academic domain (ac.id)."""
        if not str(v).endswith('.ac.id'):
            raise ValueError('Email must be from academic domain (.ac.id)')
        return v


class EmailVerificationConfirm(BaseModel):
    """Email verification confirmation schema."""
    email: EmailStr
    otp_code: str = Field(..., min_length=6, max_length=6, pattern=r'^\d{6}$')
    
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


class ChangePasswordRequest(BaseModel):
    """Change password request schema."""
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_new_password: str = Field(..., min_length=8, max_length=128)
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        """Validate new password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in v):
            raise ValueError('Password must contain at least one special character')
        return v
    
    def model_post_init(self, __context):
        """Validate password confirmation."""
        if self.new_password != self.confirm_new_password:
            raise ValueError('New passwords do not match')


class TokenPayload(BaseModel):
    """JWT token payload schema."""
    sub: str  # subject (user_id)
    email: str
    role: UserRole
    exp: int  # expiration timestamp
    iat: int  # issued at timestamp
    token_type: str  # "access" or "refresh"


class AuthResponse(BaseModel):
    """General authentication response schema."""
    success: bool
    message: str
    data: Optional[dict] = None


class UserSession(BaseModel):
    """User session schema."""
    user_id: str
    email: str
    role: UserRole
    is_active: bool
    is_verified: bool
    login_time: datetime
    last_activity: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    model_config = ConfigDict(
        json_encoders={PyObjectId: str}
    )


class SecurityEvent(BaseModel):
    """Security event schema for logging."""
    user_id: Optional[str] = None
    email: Optional[str] = None
    event_type: str  # "login", "logout", "failed_login", "password_change", etc.
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    details: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    success: bool = True
    
    model_config = ConfigDict(
        json_encoders={PyObjectId: str}
    )