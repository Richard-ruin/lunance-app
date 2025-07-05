from fastapi import APIRouter, HTTPException, status, Depends, Body
from fastapi.responses import JSONResponse
from typing import Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
from ..database import get_database
from ..models.user import User, UserCreate, UserResponse
from ..auth.password_utils import verify_password, get_password_hash
from ..auth.jwt_handler import create_access_token, create_refresh_token, verify_token
from ..auth.otp_handler import generate_otp, is_otp_valid, get_otp_expiry
from ..utils.email_service import email_service
from ..utils.validators import validate_academic_email, validate_phone_number, validate_password_strength
from ..middleware.auth_middleware import get_current_user, get_current_verified_user
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Request/Response Models
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    nama_lengkap: str
    nomor_telepon: str
    universitas_id: str
    fakultas: str
    prodi: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp_code: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp_code: str
    new_password: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse

# Rate limiting storage (in production, use Redis)
otp_requests = {}

def check_rate_limit(email: str) -> bool:
    """Check OTP rate limit"""
    now = datetime.utcnow()
    if email in otp_requests:
        requests = otp_requests[email]
        # Remove old requests (older than 1 hour)
        requests = [req for req in requests if now - req < timedelta(hours=1)]
        otp_requests[email] = requests
        
        if len(requests) >= 5:  # Max 5 requests per hour
            return False
    
    if email not in otp_requests:
        otp_requests[email] = []
    
    otp_requests[email].append(now)
    return True

@router.post("/register", response_model=Dict[str, Any])
async def register(request: RegisterRequest):
    """Register new user with OTP verification"""
    db = await get_database()
    
    # Validate email domain
    if not validate_academic_email(request.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email harus menggunakan domain kampus (.ac.id)"
        )
    
    # Validate phone number
    if not validate_phone_number(request.nomor_telepon):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format nomor telepon tidak valid"
        )
    
    # Validate password strength
    is_valid, error_message = validate_password_strength(request.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    # Check if user already exists
    existing_user = await db.users.find_one({"email": request.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email sudah terdaftar"
        )
    
    # Check if university exists
    university = await db.universities.find_one({"_id": ObjectId(request.universitas_id)})
    if not university:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Universitas tidak ditemukan"
        )
    
    # Check rate limit
    if not check_rate_limit(request.email):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Terlalu banyak permintaan OTP. Coba lagi nanti."
        )
    
    # Generate OTP
    otp_code = generate_otp()
    otp_expires = get_otp_expiry()
    
    # Create user
    user_data = {
        "email": request.email,
        "password_hash": get_password_hash(request.password),
        "nama_lengkap": request.nama_lengkap,
        "nomor_telepon": request.nomor_telepon,
        "universitas_id": ObjectId(request.universitas_id),
        "fakultas": request.fakultas,
        "prodi": request.prodi,
        "role": "mahasiswa",
        "is_verified": False,
        "otp_code": otp_code,
        "otp_expires": otp_expires,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await db.users.insert_one(user_data)
    
    # Send OTP email with retry mechanism
    try:
        email_sent = await email_service.send_otp_email(
            request.email, 
            otp_code, 
            "registration"
        )
        
        if not email_sent:
            # Remove user if email failed
            await db.users.delete_one({"_id": result.inserted_id})
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gagal mengirim email OTP. Silakan coba lagi atau periksa email Anda."
            )
    except Exception as e:
        # Remove user if email failed
        await db.users.delete_one({"_id": result.inserted_id})
        print(f"Email error: {str(e)}")  # For debugging
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal mengirim email OTP. Silakan periksa email dan coba lagi."
        )
    
    return {
        "message": "Registrasi berhasil. Silakan cek email untuk kode OTP.",
        "email": request.email
    }
@router.post("/verify-register", response_model=AuthResponse)
async def verify_register(request: VerifyOTPRequest):
    """Verify OTP for registration"""
    db = await get_database()
    
    user = await db.users.find_one({"email": request.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User tidak ditemukan"
        )
    
    if user.get("is_verified"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email sudah terverifikasi"
        )
    
    # Check OTP
    if not user.get("otp_code") or user["otp_code"] != request.otp_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kode OTP tidak valid"
        )
    
    if not is_otp_valid(user.get("otp_expires")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kode OTP sudah kedaluwarsa"
        )
    
    # Update user verification
    await db.users.update_one(
        {"_id": user["_id"]},
        {
            "$set": {
                "is_verified": True,
                "updated_at": datetime.utcnow()
            },
            "$unset": {
                "otp_code": "",
                "otp_expires": ""
            }
        }
    )
    
    # Generate tokens
    access_token = create_access_token(data={"sub": str(user["_id"])})
    refresh_token = create_refresh_token(data={"sub": str(user["_id"])})
    
    # Get updated user
    updated_user = await db.users.find_one({"_id": user["_id"]})
    
    # Use the new from_db_user method
    user_response = UserResponse.from_db_user(updated_user)
    
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user_response
    )

# Update di fungsi login
@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """Login user"""
    db = await get_database()
    
    user = await db.users.find_one({"email": request.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email atau password salah"
        )
    
    if not user.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Akun tidak aktif"
        )
    
    if not verify_password(request.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email atau password salah"
        )
    
    if not user.get("is_verified"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email belum terverifikasi"
        )
    
    # Generate tokens
    access_token = create_access_token(data={"sub": str(user["_id"])})
    refresh_token = create_refresh_token(data={"sub": str(user["_id"])})
    
    # Use the new from_db_user method
    user_response = UserResponse.from_db_user(user)
    
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user_response
    )

# Update di fungsi get_current_user_info
@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_verified_user)):
    """Get current user information"""
    # Convert User model to dict
    user_dict = {
        "_id": current_user.id,
        "email": current_user.email,
        "nama_lengkap": current_user.nama_lengkap,
        "nomor_telepon": current_user.nomor_telepon,
        "universitas_id": current_user.universitas_id,
        "fakultas": current_user.fakultas,
        "prodi": current_user.prodi,
        "role": current_user.role,
        "is_verified": current_user.is_verified,
        "is_active": current_user.is_active,
        "profile_picture": getattr(current_user, 'profile_picture', None),
        "tabungan_awal": getattr(current_user, 'tabungan_awal', None),
        "notification_settings": getattr(current_user, 'notification_settings', NotificationSettings().model_dump()),
        "preferences": getattr(current_user, 'preferences', UserPreferences().model_dump()),
        "created_at": current_user.created_at
    }
    
    return UserResponse.from_db_user(user_dict)

@router.post("/forgot-password", response_model=Dict[str, Any])
async def forgot_password(request: ForgotPasswordRequest):
    """Request password reset OTP"""
    db = await get_database()
    
    user = await db.users.find_one({"email": request.email})
    if not user:
        # Don't reveal if email exists
        return {"message": "Jika email terdaftar, kode OTP akan dikirim."}
    
    # Check rate limit
    if not check_rate_limit(request.email):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Terlalu banyak permintaan OTP. Coba lagi nanti."
        )
    
    # Generate OTP
    otp_code = generate_otp()
    otp_expires = get_otp_expiry()
    
    # Update user with OTP
    await db.users.update_one(
        {"_id": user["_id"]},
        {
            "$set": {
                "otp_code": otp_code,
                "otp_expires": otp_expires,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    # Send OTP email
    await email_service.send_otp_email(
        request.email,
        otp_code,
        "reset password"
    )
    
    return {"message": "Jika email terdaftar, kode OTP akan dikirim."}

@router.post("/verify-otp", response_model=Dict[str, Any])
async def verify_otp(request: VerifyOTPRequest):
    """Verify OTP for password reset"""
    db = await get_database()
    
    user = await db.users.find_one({"email": request.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User tidak ditemukan"
        )
    
    # Check OTP
    if not user.get("otp_code") or user["otp_code"] != request.otp_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kode OTP tidak valid"
        )
    
    if not is_otp_valid(user.get("otp_expires")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kode OTP sudah kedaluwarsa"
        )
    
    return {"message": "OTP valid. Silakan reset password."}

@router.post("/reset-password", response_model=Dict[str, Any])
async def reset_password(request: ResetPasswordRequest):
    """Reset password with OTP"""
    db = await get_database()
    
    user = await db.users.find_one({"email": request.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User tidak ditemukan"
        )
    
    # Check OTP
    if not user.get("otp_code") or user["otp_code"] != request.otp_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kode OTP tidak valid"
        )
    
    if not is_otp_valid(user.get("otp_expires")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kode OTP sudah kedaluwarsa"
        )
    
    # Validate new password
    is_valid, error_message = validate_password_strength(request.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    # Update password
    await db.users.update_one(
        {"_id": user["_id"]},
        {
            "$set": {
                "password_hash": get_password_hash(request.new_password),
                "updated_at": datetime.utcnow()
            },
            "$unset": {
                "otp_code": "",
                "otp_expires": ""
            }
        }
    )
    
    return {"message": "Password berhasil direset"}

@router.post("/change-password", response_model=Dict[str, Any])
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_verified_user)
):
    """Change password for authenticated user"""
    db = await get_database()
    
    # Verify current password
    user = await db.users.find_one({"_id": current_user.id})
    if not verify_password(request.current_password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password saat ini salah"
        )
    
    # Validate new password
    is_valid, error_message = validate_password_strength(request.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    # Update password
    await db.users.update_one(
        {"_id": current_user.id},
        {
            "$set": {
                "password_hash": get_password_hash(request.new_password),
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    return {"message": "Password berhasil diubah"}

@router.post("/refresh-token", response_model=Dict[str, Any])
async def refresh_token(request: RefreshTokenRequest):
    """Refresh access token"""
    payload = verify_token(request.refresh_token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user ID"
        )
    
    # Verify user still exists and is active
    db = await get_database()
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    
    if not user or not user.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Generate new access token
    new_access_token = create_access_token(data={"sub": user_id})
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }
