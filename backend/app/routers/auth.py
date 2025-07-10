from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from ..services.auth_service import AuthService
from ..schemas.auth_schemas import (
    UserRegister, 
    UserLogin, 
    Token, 
    TokenRefresh,
    ProfileSetup, 
    FinancialSetup,
    UserResponse,
    ChangePassword,
    UpdateProfile,
    ApiResponse
)
from ..utils.security import verify_token
from ..models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()
auth_service = AuthService()

# Dependency untuk mendapatkan current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Dependency untuk mendapatkan user yang sedang login"""
    
    payload = verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak valid",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    user = await auth_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User tidak ditemukan",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

@router.post("/register", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """
    Registrasi user baru
    
    - **username**: Username unik (3-50 karakter, alfanumerik + underscore)
    - **email**: Email valid dan unik
    - **password**: Password minimal 6 karakter dengan huruf dan angka
    - **confirm_password**: Konfirmasi password harus sama
    """
    try:
        new_user = await auth_service.register_user(user_data)
        
        return ApiResponse(
            success=True,
            message="Registrasi berhasil! Silakan login untuk melanjutkan.",
            data={
                "user_id": new_user.id,
                "username": new_user.username,
                "email": new_user.email,
                "created_at": new_user.created_at.isoformat()
            }
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Terjadi kesalahan dalam registrasi: {str(e)}"
        )

@router.post("/login", response_model=ApiResponse)
async def login(login_data: UserLogin):
    """
    Login user
    
    - **email**: Email terdaftar
    - **password**: Password yang sesuai
    
    Mengembalikan access token dan refresh token untuk autentikasi.
    """
    try:
        # Autentikasi user
        user = await auth_service.authenticate_user(login_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email atau password salah"
            )
        
        # Buat tokens
        tokens = await auth_service.create_tokens(user)
        
        # Konversi user ke response format
        user_response = UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            profile=user.profile.dict() if user.profile else None,
            preferences=user.preferences.dict(),
            financial_settings=user.financial_settings.dict() if user.financial_settings else None,
            is_active=user.is_active,
            is_verified=user.is_verified,
            is_premium=user.is_premium,
            profile_setup_completed=user.profile_setup_completed,
            financial_setup_completed=user.financial_setup_completed,
            onboarding_completed=user.onboarding_completed,
            created_at=user.created_at,
            last_login=user.last_login
        )
        
        return ApiResponse(
            success=True,
            message="Login berhasil!",
            data={
                "tokens": tokens,
                "user": user_response.dict()
            }
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Terjadi kesalahan dalam login: {str(e)}"
        )

@router.post("/refresh-token", response_model=ApiResponse)
async def refresh_token(token_data: TokenRefresh):
    """
    Refresh access token menggunakan refresh token
    
    - **refresh_token**: Refresh token yang valid
    """
    try:
        new_token = await auth_service.refresh_access_token(token_data.refresh_token)
        
        return ApiResponse(
            success=True,
            message="Token berhasil diperbarui",
            data=new_token
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Terjadi kesalahan dalam refresh token: {str(e)}"
        )

@router.post("/setup-profile", response_model=ApiResponse)
async def setup_profile(
    profile_data: ProfileSetup,
    current_user: User = Depends(get_current_user)
):
    """
    Setup profil user setelah registrasi
    
    - **full_name**: Nama lengkap (2-100 karakter)
    - **phone_number**: Nomor telepon (opsional)
    - **date_of_birth**: Tanggal lahir (opsional)
    - **occupation**: Pekerjaan (opsional)
    - **city**: Kota tempat tinggal (opsional)
    - **language**: Bahasa (id/en)
    - **currency**: Mata uang (IDR, USD, dll)
    - **notifications_enabled**: Aktifkan notifikasi
    - **voice_enabled**: Aktifkan fitur suara
    - **dark_mode**: Mode gelap
    """
    try:
        updated_user = await auth_service.setup_profile(current_user.id, profile_data)
        
        user_response = UserResponse(
            id=updated_user.id,
            username=updated_user.username,
            email=updated_user.email,
            profile=updated_user.profile.dict() if updated_user.profile else None,
            preferences=updated_user.preferences.dict(),
            financial_settings=updated_user.financial_settings.dict() if updated_user.financial_settings else None,
            is_active=updated_user.is_active,
            is_verified=updated_user.is_verified,
            is_premium=updated_user.is_premium,
            profile_setup_completed=updated_user.profile_setup_completed,
            financial_setup_completed=updated_user.financial_setup_completed,
            onboarding_completed=updated_user.onboarding_completed,
            created_at=updated_user.created_at,
            last_login=updated_user.last_login
        )
        
        return ApiResponse(
            success=True,
            message="Profil berhasil disimpan!",
            data={"user": user_response.dict()}
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Terjadi kesalahan dalam setup profil: {str(e)}"
        )

@router.post("/initial-financial-setup", response_model=ApiResponse)
async def initial_financial_setup(
    financial_data: FinancialSetup,
    current_user: User = Depends(get_current_user)
):
    """
    Setup keuangan awal user
    
    - **monthly_income**: Pendapatan bulanan (wajib, > 0)
    - **monthly_budget**: Budget bulanan (opsional, <= monthly_income)
    - **savings_goal_percentage**: Persentase target tabungan (0-100, default 20%)
    - **emergency_fund_target**: Target dana darurat (opsional)
    - **primary_bank**: Bank utama (opsional)
    """
    try:
        updated_user = await auth_service.setup_financial(current_user.id, financial_data)
        
        user_response = UserResponse(
            id=updated_user.id,
            username=updated_user.username,
            email=updated_user.email,
            profile=updated_user.profile.dict() if updated_user.profile else None,
            preferences=updated_user.preferences.dict(),
            financial_settings=updated_user.financial_settings.dict() if updated_user.financial_settings else None,
            is_active=updated_user.is_active,
            is_verified=updated_user.is_verified,
            is_premium=updated_user.is_premium,
            profile_setup_completed=updated_user.profile_setup_completed,
            financial_setup_completed=updated_user.financial_setup_completed,
            onboarding_completed=updated_user.onboarding_completed,
            created_at=updated_user.created_at,
            last_login=updated_user.last_login
        )
        
        # Hitung target tabungan bulanan berdasarkan persentase
        monthly_savings_target = (
            financial_data.monthly_income * financial_data.savings_goal_percentage / 100
        )
        
        return ApiResponse(
            success=True,
            message="Setup keuangan berhasil! Sekarang Anda dapat mulai menggunakan Lunance.",
            data={
                "user": user_response.dict(),
                "calculations": {
                    "monthly_savings_target": monthly_savings_target,
                    "monthly_income": financial_data.monthly_income,
                    "budget_remaining": (
                        financial_data.monthly_budget - monthly_savings_target 
                        if financial_data.monthly_budget else None
                    )
                }
            }
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Terjadi kesalahan dalam setup keuangan: {str(e)}"
        )

@router.get("/me", response_model=ApiResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Mendapatkan informasi user yang sedang login
    """
    try:
        user_response = UserResponse(
            id=current_user.id,
            username=current_user.username,
            email=current_user.email,
            profile=current_user.profile.dict() if current_user.profile else None,
            preferences=current_user.preferences.dict(),
            financial_settings=current_user.financial_settings.dict() if current_user.financial_settings else None,
            is_active=current_user.is_active,
            is_verified=current_user.is_verified,
            is_premium=current_user.is_premium,
            profile_setup_completed=current_user.profile_setup_completed,
            financial_setup_completed=current_user.financial_setup_completed,
            onboarding_completed=current_user.onboarding_completed,
            created_at=current_user.created_at,
            last_login=current_user.last_login
        )
        
        return ApiResponse(
            success=True,
            message="Data user berhasil diambil",
            data={"user": user_response.dict()}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Terjadi kesalahan: {str(e)}"
        )

@router.post("/logout", response_model=ApiResponse)
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout user (menghapus refresh token)
    """
    try:
        success = await auth_service.logout_user(current_user.id)
        
        if success:
            return ApiResponse(
                success=True,
                message="Logout berhasil"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Gagal logout"
            )
            
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Terjadi kesalahan dalam logout: {str(e)}"
        )

@router.post("/change-password", response_model=ApiResponse)
async def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_user)
):
    """
    Ganti password user
    
    - **current_password**: Password saat ini
    - **new_password**: Password baru (minimal 6 karakter dengan huruf dan angka)
    - **confirm_password**: Konfirmasi password baru
    
    Setelah ganti password, user akan di-logout dari semua device.
    """
    try:
        success = await auth_service.change_password(current_user.id, password_data)
        
        if success:
            return ApiResponse(
                success=True,
                message="Password berhasil diubah. Silakan login kembali."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Gagal mengubah password"
            )
            
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Terjadi kesalahan dalam ganti password: {str(e)}"
        )

@router.put("/update-profile", response_model=ApiResponse)
async def update_profile(
    update_data: UpdateProfile,
    current_user: User = Depends(get_current_user)
):
    """
    Update profil user
    
    Semua field bersifat opsional. Hanya field yang dikirim yang akan diupdate.
    """
    try:
        updated_user = await auth_service.update_profile(current_user.id, update_data)
        
        user_response = UserResponse(
            id=updated_user.id,
            username=updated_user.username,
            email=updated_user.email,
            profile=updated_user.profile.dict() if updated_user.profile else None,
            preferences=updated_user.preferences.dict(),
            financial_settings=updated_user.financial_settings.dict() if updated_user.financial_settings else None,
            is_active=updated_user.is_active,
            is_verified=updated_user.is_verified,
            is_premium=updated_user.is_premium,
            profile_setup_completed=updated_user.profile_setup_completed,
            financial_setup_completed=updated_user.financial_setup_completed,
            onboarding_completed=updated_user.onboarding_completed,
            created_at=updated_user.created_at,
            last_login=updated_user.last_login
        )
        
        return ApiResponse(
            success=True,
            message="Profil berhasil diperbarui",
            data={"user": user_response.dict()}
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Terjadi kesalahan dalam update profil: {str(e)}"
        )