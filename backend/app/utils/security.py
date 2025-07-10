from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

# Konfigurasi JWT
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")  # Provide default for development
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Memverifikasi password dengan hash menggunakan bcrypt"""
    try:
        # Pastikan input dalam format yang benar
        if isinstance(plain_password, str):
            plain_password = plain_password.encode('utf-8')
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('utf-8')
        
        return bcrypt.checkpw(plain_password, hashed_password)
    except Exception as e:
        print(f"Error verifying password: {e}")
        return False

def get_password_hash(password: str) -> str:
    """Membuat hash dari password menggunakan bcrypt"""
    try:
        # Encode password ke bytes jika masih string
        if isinstance(password, str):
            password = password.encode('utf-8')
        
        # Generate salt dan hash
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password, salt)
        
        # Return sebagai string
        return hashed.decode('utf-8')
    except Exception as e:
        print(f"Error hashing password: {e}")
        raise ValueError("Gagal membuat hash password")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Membuat JWT access token"""
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY tidak ditemukan")
    
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        print(f"Error creating access token: {e}")
        raise ValueError("Gagal membuat access token")

def create_refresh_token(data: dict) -> str:
    """Membuat JWT refresh token"""
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY tidak ditemukan")
    
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        print(f"Error creating refresh token: {e}")
        raise ValueError("Gagal membuat refresh token")

def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
    """Memverifikasi JWT token"""
    if not SECRET_KEY:
        print("SECRET_KEY tidak ditemukan")
        return None
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Verifikasi tipe token
        if payload.get("type") != token_type:
            print(f"Token type mismatch: expected {token_type}, got {payload.get('type')}")
            return None
        
        # Verifikasi expiration
        exp = payload.get("exp")
        if exp is None:
            print("Token tidak memiliki expiration")
            return None
            
        if datetime.utcnow() > datetime.fromtimestamp(exp):
            print("Token sudah expired")
            return None
        
        return payload
        
    except JWTError as e:
        print(f"JWT Error: {e}")
        return None
    except Exception as e:
        print(f"Error verifying token: {e}")
        return None

def extract_user_id_from_token(token: str) -> Optional[str]:
    """Mengekstrak user_id dari token"""
    payload = verify_token(token)
    if payload:
        return payload.get("sub")
    return None

def generate_reset_token(email: str) -> str:
    """Membuat token untuk reset password"""
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY tidak ditemukan")
    
    data = {"sub": email, "type": "reset"}
    expire = datetime.utcnow() + timedelta(hours=1)  # Token reset berlaku 1 jam
    
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    
    try:
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    except Exception as e:
        print(f"Error generating reset token: {e}")
        raise ValueError("Gagal membuat reset token")

def verify_reset_token(token: str) -> Optional[str]:
    """Memverifikasi token reset password"""
    if not SECRET_KEY:
        print("SECRET_KEY tidak ditemukan")
        return None
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        if payload.get("type") != "reset":
            return None
            
        email = payload.get("sub")
        return email
        
    except JWTError as e:
        print(f"JWT Error verifying reset token: {e}")
        return None
    except Exception as e:
        print(f"Error verifying reset token: {e}")
        return None