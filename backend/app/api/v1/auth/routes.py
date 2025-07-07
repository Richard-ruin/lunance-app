from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, Field
from typing import Optional
from app.services.auth_service import AuthService
from app.utils.helpers import create_response
from app.middleware.auth_middleware import get_current_user
from app.models.user import User

router = APIRouter()

# Request/Response Models
class RegisterStep1Request(BaseModel):
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.ac\.id$')
    nama_lengkap: str = Field(..., min_length=3, max_length=100)
    no_telepon: str = Field(..., min_length=8, max_length=20)

class RegisterStep2Request(BaseModel):
    email: str
    university_id: str
    fakultas_id: str
    prodi_id: str

class RegisterStep3Request(BaseModel):
    email: str
    otp_code: str = Field(..., min_length=6, max_length=6, pattern=r'^\d{6}$')

class RegisterStep4Request(BaseModel):
    email: str
    tabungan_awal: float = Field(..., ge=0)

class RegisterStep5Request(BaseModel):
    email: str
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)
    nama_lengkap: str = Field(..., min_length=3, max_length=100)
    no_telepon: str = Field(..., min_length=8, max_length=20)
    university_id: str
    fakultas_id: str
    prodi_id: str
    tabungan_awal: float = Field(..., ge=0)

class LoginRequest(BaseModel):
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.ac\.id$')
    password: str = Field(..., min_length=1)

class VerifyOTPRequest(BaseModel):
    email: str
    otp_code: str = Field(..., min_length=6, max_length=6, pattern=r'^\d{6}$')

class ForgotPasswordRequest(BaseModel):
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.ac\.id$')

class ResetPasswordRequest(BaseModel):
    email: str
    otp_code: str = Field(..., min_length=6, max_length=6, pattern=r'^\d{6}$')
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)

class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)

class RefreshTokenRequest(BaseModel):
    refresh_token: str

# Authentication Routes
@router.post("/register/step1")
async def register_step1(request: RegisterStep1Request):
    """Step 1: Basic information and email validation"""
    try:
        result = AuthService.register_step1(
            email=request.email,
            nama_lengkap=request.nama_lengkap,
            no_telepon=request.no_telepon
        )
        
        return create_response(
            data=result,
            message="Data berhasil divalidasi. Silakan lanjut ke step 2."
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Terjadi kesalahan sistem")

@router.post("/register/step2")
async def register_step2(request: RegisterStep2Request):
    """Step 2: University information validation"""
    try:
        result = AuthService.register_step2(
            email=request.email,
            university_id=request.university_id,
            fakultas_id=request.fakultas_id,
            prodi_id=request.prodi_id
        )
        
        return create_response(
            data=result,
            message="Informasi universitas berhasil divalidasi. Silakan lanjut ke step 3."
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Terjadi kesalahan sistem")

@router.post("/register/step3")
async def register_step3(request: RegisterStep3Request):
    """Step 3: OTP verification"""
    try:
        result = AuthService.register_step3(
            email=request.email,
            otp_code=request.otp_code
        )
        
        return create_response(
            data=result,
            message="OTP berhasil diverifikasi. Silakan lanjut ke step 4."
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Terjadi kesalahan sistem")

@router.post("/register/step4")
async def register_step4(request: RegisterStep4Request):
    """Step 4: Set initial savings"""
    try:
        result = AuthService.register_step4(
            email=request.email,
            tabungan_awal=request.tabungan_awal
        )
        
        return create_response(
            data=result,
            message="Tabungan awal berhasil diset. Silakan lanjut ke step 5."
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Terjadi kesalahan sistem")

@router.post("/register/step5")
async def register_step5(request: RegisterStep5Request):
    """Step 5: Complete registration"""
    try:
        result = AuthService.register_step5(
            email=request.email,
            password=request.password,
            confirm_password=request.confirm_password,
            nama_lengkap=request.nama_lengkap,
            no_telepon=request.no_telepon,
            university_id=request.university_id,
            fakultas_id=request.fakultas_id,
            prodi_id=request.prodi_id,
            tabungan_awal=request.tabungan_awal
        )
        
        return create_response(
            data=result,
            message="Registrasi berhasil! Akun Anda sedang menunggu persetujuan admin."
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Terjadi kesalahan sistem")

@router.post("/login")
async def login(request: LoginRequest):
    """Login user"""
    try:
        result = AuthService.login(
            email=request.email,
            password=request.password
        )
        
        return create_response(
            data=result,
            message="Login berhasil"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Terjadi kesalahan sistem")

@router.post("/refresh")
async def refresh_token(request: RefreshTokenRequest):
    """Refresh access token"""
    try:
        result = AuthService.refresh_token(request.refresh_token)
        
        return create_response(
            data=result,
            message="Token berhasil diperbarui"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Terjadi kesalahan sistem")

@router.post("/verify-otp")
async def verify_otp(request: VerifyOTPRequest):
    """Verify OTP (general purpose)"""
    try:
        result = AuthService.register_step3(
            email=request.email,
            otp_code=request.otp_code
        )
        
        return create_response(
            data=result,
            message="OTP berhasil diverifikasi"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Terjadi kesalahan sistem")

@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    """Request password reset OTP"""
    try:
        result = AuthService.forgot_password(request.email)
        
        return create_response(
            data=result,
            message="Jika email terdaftar, OTP akan dikirim ke email Anda"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Terjadi kesalahan sistem")

@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """Reset password with OTP"""
    try:
        result = AuthService.reset_password(
            email=request.email,
            otp_code=request.otp_code,
            new_password=request.new_password,
            confirm_password=request.confirm_password
        )
        
        return create_response(
            data=result,
            message="Password berhasil direset"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Terjadi kesalahan sistem")

@router.post("/change-password")
async def change_password(request: ChangePasswordRequest, current_user: User = Depends(get_current_user)):
    """Change password for authenticated user"""
    try:
        result = AuthService.change_password(
            user_id=str(current_user.id),
            old_password=request.old_password,
            new_password=request.new_password,
            confirm_password=request.confirm_password
        )
        
        return create_response(
            data=result,
            message="Password berhasil diubah"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Terjadi kesalahan sistem")

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout user (client should remove tokens)"""
    return create_response(
        data={"user_id": str(current_user.id)},
        message="Logout berhasil"
    )

@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return create_response(
        data=current_user.to_dict_safe(),
        message="Berhasil mengambil informasi user"
    )

@router.get("/check-email/{email}")
async def check_email_availability(email: str):
    """Check if email is available for registration"""
    try:
        # Validate email format
        if not email.endswith('.ac.id'):
            raise HTTPException(status_code=400, detail="Email harus menggunakan domain .ac.id")
        
        user = User.find_by_email(email)
        is_available = user is None
        
        return create_response(
            data={
                "email": email,
                "is_available": is_available
            },
            message="Berhasil memeriksa ketersediaan email"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Terjadi kesalahan sistem")