import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import re
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status
from app.config.settings import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

def validate_password_strength(password: str) -> tuple[bool, list[str]]:
    """
    Validate password strength based on policy
    Returns (is_valid, list_of_errors)
    """
    errors = []
    policy = settings.password_policy
    
    # Check minimum length
    if len(password) < policy["min_length"]:
        errors.append(f"Password must be at least {policy['min_length']} characters long")
    
    # Check for uppercase letters
    if policy["require_uppercase"] and not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    # Check for lowercase letters
    if policy["require_lowercase"] and not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    # Check for numbers
    if policy["require_numbers"] and not re.search(r'\d', password):
        errors.append("Password must contain at least one number")
    
    # Check for special characters
    if policy["require_special_chars"] and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    
    # Check for common weak passwords
    weak_passwords = [
        "password", "123456", "password123", "admin", "qwerty",
        "letmein", "welcome", "monkey", "dragon"
    ]
    if password.lower() in weak_passwords:
        errors.append("Password is too common and easily guessable")
    
    return len(errors) == 0, errors

# JWT Token handling
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
    """
    Verify JWT token and return payload
    Raises HTTPException if token is invalid
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Check token type
        if payload.get("type") != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check expiration
        exp = payload.get("exp")
        if exp is None or datetime.fromtimestamp(exp) < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return payload
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def extract_email_from_token(token: str) -> str:
    """Extract email from JWT token"""
    payload = verify_token(token)
    email = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return email

# OTP Generation and Validation
def generate_otp(length: int = None) -> str:
    """Generate numeric OTP code"""
    if length is None:
        length = settings.OTP_LENGTH
    
    return ''.join(secrets.choice(string.digits) for _ in range(length))

def generate_secure_token(length: int = 32) -> str:
    """Generate secure random token for password reset etc."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

# Email validation
def validate_student_email(email: str) -> tuple[bool, str]:
    """
    Validate if email belongs to a supported university
    Returns (is_valid, error_message)
    """
    # Basic email format validation is handled by EmailStr in Pydantic
    
    # Check if email ends with academic domain
    academic_domains = [
        ".ac.id",  # Indonesian academic domains
        ".edu",    # US academic domains
        ".edu.my", # Malaysian academic domains
        ".edu.sg", # Singapore academic domains
    ]
    
    is_academic = any(email.lower().endswith(domain) for domain in academic_domains)
    
    if not is_academic:
        return False, "Email must be from an academic institution (.ac.id, .edu, etc.)"
    
    # Additional validation for Indonesian universities
    if email.lower().endswith(".ac.id"):
        # Extract university from email domain
        domain_parts = email.lower().split("@")[-1].split(".")
        if len(domain_parts) >= 3:  # e.g., student.ui.ac.id
            university_code = domain_parts[-3]  # 'ui' from student.ui.ac.id
            
            # Map common university codes
            university_codes = {
                "ui": "Universitas Indonesia",
                "itb": "Institut Teknologi Bandung", 
                "ugm": "Universitas Gadjah Mada",
                "its": "Institut Teknologi Sepuluh Nopember",
                "unpad": "Universitas Padjadjaran",
                "undip": "Universitas Diponegoro",
                "unair": "Universitas Airlangga",
                "ub": "Universitas Brawijaya",
                "unhas": "Universitas Hasanuddin",
                "unand": "Universitas Andalas",
                "unsri": "Universitas Sriwijaya",
                "unimed": "Universitas Negeri Medan",
                "uny": "Universitas Negeri Yogyakarta",
                "um": "Universitas Negeri Malang",
                "unj": "Universitas Negeri Jakarta"
            }
            
            if university_code in university_codes:
                return True, university_codes[university_code]
    
    return True, "Academic email accepted"

# Security utilities for account protection
def is_suspicious_activity(
    failed_attempts: int,
    last_login: Optional[datetime],
    current_time: Optional[datetime] = None
) -> bool:
    """Detect suspicious login activity"""
    if current_time is None:
        current_time = datetime.utcnow()
    
    # Too many failed attempts
    if failed_attempts >= settings.MAX_LOGIN_ATTEMPTS:
        return True
    
    # Login from unusual time (implement based on user patterns)
    # This is a simple implementation - in production, use ML-based detection
    if last_login:
        time_diff = current_time - last_login
        # Suspicious if login after being inactive for more than 30 days
        if time_diff.days > 30:
            return True
    
    return False

def should_lock_account(failed_attempts: int) -> bool:
    """Determine if account should be locked"""
    return failed_attempts >= settings.MAX_LOGIN_ATTEMPTS

def calculate_lockout_time() -> datetime:
    """Calculate when account lockout should expire"""
    return datetime.utcnow() + timedelta(minutes=settings.ACCOUNT_LOCKOUT_DURATION)

# Input sanitization
def sanitize_input(input_string: str, max_length: int = 1000) -> str:
    """Basic input sanitization"""
    if not input_string:
        return ""
    
    # Remove or escape potentially dangerous characters
    sanitized = input_string.strip()
    sanitized = sanitized[:max_length]  # Limit length
    
    # Remove null bytes and control characters
    sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in '\t\n\r')
    
    return sanitized

def validate_phone_number(phone: str) -> tuple[bool, str]:
    """Validate Indonesian phone number format"""
    if not phone:
        return True, ""  # Phone is optional
    
    # Remove all non-digit characters for validation
    digits_only = re.sub(r'\D', '', phone)
    
    # Indonesian phone number patterns
    patterns = [
        r'^(\+62|62|0)8[1-9][0-9]{6,10}$',  # Mobile numbers
        r'^(\+62|62|0)2[1-9][0-9]{6,8}$',   # Jakarta area
        r'^(\+62|62|0)[2-9][1-9][0-9]{6,8}$' # Other areas
    ]
    
    # Check if original format matches any pattern
    is_valid = any(re.match(pattern, phone) for pattern in patterns)
    
    if not is_valid:
        return False, "Invalid Indonesian phone number format"
    
    return True, ""

# Rate limiting helpers
def create_rate_limit_key(identifier: str, action: str) -> str:
    """Create consistent rate limiting key"""
    return f"rate_limit:{action}:{identifier}"

def get_client_ip(request) -> str:
    """Extract client IP from request headers"""
    # Check for forwarded headers first (in case of proxy/load balancer)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fall back to direct connection IP
    return request.client.host