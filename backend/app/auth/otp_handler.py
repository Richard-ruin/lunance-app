import random
import string
from datetime import datetime, timedelta
from typing import Optional
from ..config import settings

def generate_otp() -> str:
    """Generate 6 digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def is_otp_valid(otp_expires: Optional[datetime]) -> bool:
    """Check if OTP is still valid"""
    if not otp_expires:
        return False
    return datetime.utcnow() < otp_expires

def get_otp_expiry() -> datetime:
    """Get OTP expiry time"""
    return datetime.utcnow() + timedelta(minutes=settings.otp_expire_minutes)