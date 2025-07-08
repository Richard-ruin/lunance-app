# app/models/user.py (Fixed PyObjectId section)
"""User models and schemas with fixed PyObjectId support for Pydantic v2."""

from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator, ConfigDict
from typing import Optional, Annotated, Any
from datetime import datetime
from enum import Enum
import re
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId class for Pydantic v2 compatibility."""
    
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler):
        """Pydantic v2 core schema method."""
        from pydantic_core import core_schema
        
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema([
                    core_schema.str_schema(),
                    core_schema.no_info_plain_validator_function(cls.validate),
                ])
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )
    
    @classmethod
    def validate(cls, v):
        """Validate ObjectId."""
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)
    
    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema, handler):
        """JSON schema for OpenAPI documentation."""
        field_schema.update(type="string", format="objectid")
        return field_schema


class UserRole(str, Enum):
    """User role enumeration."""
    ADMIN = "admin"
    STUDENT = "student"


class UserBase(BaseModel):
    """Base user model with common fields."""
    email: EmailStr = Field(..., description="User email address")
    full_name: str = Field(..., min_length=2, max_length=100, description="Full name")
    phone_number: str = Field(..., description="Phone number")
    university_id: Optional[str] = Field(None, description="University ID")
    faculty_id: Optional[str] = Field(None, description="Faculty ID")
    major_id: Optional[str] = Field(None, description="Major ID")
    role: UserRole = Field(default=UserRole.STUDENT, description="User role")
    initial_savings: Optional[float] = Field(None, ge=0, description="Initial savings amount")

    @field_validator('email')
    @classmethod
    def validate_email_domain(cls, v: str) -> str:
        """Validate that email ends with ac.id for academic domain."""
        if not v.endswith('ac.id'):
            raise ValueError('Email must be from academic domain (ending with ac.id)')
        return v.lower()

    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        """Validate Indonesian phone number format."""
        # Remove any non-digit characters
        phone = re.sub(r'\D', '', v)
        
        # Check if it starts with 08, +628, or 628
        if phone.startswith('08'):
            phone = '628' + phone[2:]
        elif phone.startswith('+628'):
            phone = phone[1:]
        elif not phone.startswith('628'):
            raise ValueError('Phone number must be valid Indonesian format')
        
        # Check length (should be 10-13 digits for Indonesian numbers)
        if len(phone) < 10 or len(phone) > 13:
            raise ValueError('Phone number must be 10-13 digits long')
        
        return phone

    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        """Validate and clean full name."""
        # Remove extra whitespace and title case
        name = ' '.join(v.strip().split())
        if not re.match(r'^[a-zA-Z\s]+$', name):
            raise ValueError('Full name must only contain letters and spaces')
        return name

    @model_validator(mode='after')
    def validate_academic_info(self):
        """Validate that academic info is consistent."""
        if self.faculty_id and not self.university_id:
            raise ValueError('University ID is required when faculty ID is provided')
        if self.major_id and not self.faculty_id:
            raise ValueError('Faculty ID is required when major ID is provided')
        return self


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, description="Password")

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone_number: Optional[str] = Field(None)
    university_id: Optional[str] = Field(None)
    faculty_id: Optional[str] = Field(None)
    major_id: Optional[str] = Field(None)
    initial_savings: Optional[float] = Field(None, ge=0)

    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number if provided."""
        if v is None:
            return v
        return UserBase.validate_phone_number(v)

    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate full name if provided."""
        if v is None:
            return v
        return UserBase.validate_full_name(v)


class UserInDB(UserBase):
    """User model as stored in database."""
    id: Optional[PyObjectId] = Field(None, alias="_id", description="User ID")
    password_hash: str = Field(..., description="Hashed password")
    is_active: bool = Field(default=True, description="Whether user is active")
    is_verified: bool = Field(default=False, description="Whether email is verified")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            'example': {
                'email': 'student@university.ac.id',
                'full_name': 'John Doe',
                'phone_number': '+6281234567890',
                'university_id': '507f1f77bcf86cd799439011',
                'faculty_id': '507f1f77bcf86cd799439012',
                'major_id': '507f1f77bcf86cd799439013',
                'role': 'student',
                'is_active': True,
                'is_verified': True,
                'initial_savings': 1000000.0
            }
        }
    )


class UserResponse(UserBase):
    """Schema for user response (without sensitive data)."""
    id: Optional[str] = Field(None, alias="_id", description="User ID")
    is_active: bool = Field(..., description="Whether user is active")
    is_verified: bool = Field(..., description="Whether email is verified")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )


class UserProfile(BaseModel):
    """Schema for user profile information."""
    id: str = Field(..., alias="_id", description="User ID")
    email: EmailStr = Field(..., description="User email")
    full_name: str = Field(..., description="Full name")
    phone_number: str = Field(..., description="Phone number")
    role: UserRole = Field(..., description="User role")
    is_active: bool = Field(..., description="Whether user is active")
    is_verified: bool = Field(..., description="Whether email is verified")
    university_name: Optional[str] = Field(None, description="University name")
    faculty_name: Optional[str] = Field(None, description="Faculty name")
    major_name: Optional[str] = Field(None, description="Major name")
    initial_savings: Optional[float] = Field(None, description="Initial savings")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )


class PasswordChange(BaseModel):
    """Schema for password change."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """Validate new password strength."""
        return UserCreate.validate_password(v)


class PasswordReset(BaseModel):
    """Schema for password reset."""
    email: EmailStr = Field(..., description="User email")


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""
    email: EmailStr = Field(..., description="User email")
    otp_code: str = Field(..., min_length=6, max_length=6, description="OTP code")
    new_password: str = Field(..., min_length=8, description="New password")

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """Validate new password strength."""
        return UserCreate.validate_password(v)

    @field_validator('otp_code')
    @classmethod
    def validate_otp_code(cls, v: str) -> str:
        """Validate OTP code format."""
        if not v.isdigit():
            raise ValueError('OTP code must contain only digits')
        return v


class UserStats(BaseModel):
    """Schema for user statistics."""
    total_transactions: int = Field(..., description="Total number of transactions")
    total_income: float = Field(..., description="Total income amount")
    total_expense: float = Field(..., description="Total expense amount")
    current_balance: float = Field(..., description="Current balance")
    active_savings_targets: int = Field(..., description="Number of active savings targets")
    achieved_savings_targets: int = Field(..., description="Number of achieved savings targets")
    categories_used: int = Field(..., description="Number of categories used")
    last_transaction_date: Optional[datetime] = Field(None, description="Last transaction date")

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'total_transactions': 150,
                'total_income': 5000000.0,
                'total_expense': 3500000.0,
                'current_balance': 1500000.0,
                'active_savings_targets': 3,
                'achieved_savings_targets': 1,
                'categories_used': 8,
                'last_transaction_date': '2024-01-15T10:30:00'
            }
        }
    )