from typing import Optional
from datetime import datetime
from pydantic import Field, field_validator
from app.models.base import BaseModel, PyObjectId
from app.config.database import get_db

class User(BaseModel):
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.ac\.id$')
    password_hash: str = Field(...)
    nama_lengkap: str = Field(..., min_length=3, max_length=100)
    no_telepon: str = Field(..., min_length=8, max_length=20)
    
    # University information
    university_id: PyObjectId = Field(...)
    fakultas_id: PyObjectId = Field(...)
    prodi_id: PyObjectId = Field(...)
    
    # Role and status
    role: str = Field(default="mahasiswa", pattern=r'^(admin|mahasiswa)$')
    status: str = Field(default="pending", pattern=r'^(pending|approved|rejected)$')
    
    # Financial info
    tabungan_awal: float = Field(default=0.0, ge=0)
    
    # Verification fields
    otp_code: Optional[str] = None
    otp_expires: Optional[datetime] = None
    is_verified: bool = Field(default=False)
    
    # Activity tracking
    last_login: Optional[datetime] = None
    login_attempts: int = Field(default=0)
    last_attempt_at: Optional[datetime] = None
    
    @field_validator('email')
    @classmethod
    def validate_email_domain(cls, v):
        if not v.endswith('.ac.id'):
            raise ValueError('Email harus menggunakan domain .ac.id')
        return v.lower().strip()
    
    @field_validator('nama_lengkap')
    @classmethod
    def validate_nama(cls, v):
        return v.strip().title()
    
    @field_validator('no_telepon')
    @classmethod
    def validate_telepon(cls, v):
        # Remove non-numeric characters
        cleaned = ''.join(filter(str.isdigit, v))
        if len(cleaned) < 8:
            raise ValueError('Nomor telepon minimal 8 digit')
        return cleaned
    
    def save(self):
        return super().save('users')
    
    @classmethod
    def find_by_id(cls, user_id: str):
        return super().find_by_id('users', user_id)
    
    @classmethod
    def find_by_email(cls, email: str):
        try:
            db = get_db()
            doc = db.users.find_one({'email': email.lower().strip()})
            if doc:
                return cls(**doc)
            return None
        except Exception:
            return None
    
    @classmethod
    def find_by_otp(cls, otp_code: str):
        try:
            db = get_db()
            doc = db.users.find_one({
                'otp_code': otp_code,
                'otp_expires': {'$gt': datetime.utcnow()}
            })
            if doc:
                return cls(**doc)
            return None
        except Exception:
            return None
    
    @classmethod
    def find_pending_users(cls, page: int = 1, limit: int = 10):
        """Find users pending approval"""
        try:
            skip = (page - 1) * limit
            filter_dict = {'status': 'pending'}
            
            users = super().find_all('users', filter_dict, limit, skip, [('created_at', -1)])
            total = super().count_documents('users', filter_dict)
            
            return {
                'users': [user.to_dict_safe() for user in users],
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': (total + limit - 1) // limit,
                    'has_next': page * limit < total,
                    'has_prev': page > 1
                }
            }
        except Exception:
            return {'users': [], 'pagination': {}}
    
    def to_dict_safe(self):
        """Convert to dict without sensitive information"""
        user_dict = self.model_dump()
        # Remove sensitive fields
        user_dict.pop('password_hash', None)
        user_dict.pop('otp_code', None)
        user_dict.pop('login_attempts', None)
        user_dict.pop('last_attempt_at', None)
        return user_dict
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        self.login_attempts = 0
        self.last_attempt_at = None
        return self.save()
    
    def increment_login_attempts(self):
        """Increment failed login attempts"""
        self.login_attempts += 1
        self.last_attempt_at = datetime.utcnow()
        return self.save()
    
    def reset_login_attempts(self):
        """Reset login attempts after successful login"""
        self.login_attempts = 0
        self.last_attempt_at = None
        return self.save()
    
    def set_otp(self, otp_code: str, expires_in_minutes: int = 5):
        """Set OTP code with expiry"""
        from datetime import timedelta
        self.otp_code = otp_code
        self.otp_expires = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
        return self.save()
    
    def clear_otp(self):
        """Clear OTP code and expiry"""
        self.otp_code = None
        self.otp_expires = None
        return self.save()
    
    def verify_user(self):
        """Mark user as verified"""
        self.is_verified = True
        self.clear_otp()
        return self.save()
    
    def approve_user(self):
        """Approve user registration"""
        self.status = "approved"
        return self.save()
    
    def reject_user(self):
        """Reject user registration"""
        self.status = "rejected"
        return self.save()