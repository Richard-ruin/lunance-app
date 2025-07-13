# app/routers/auth.py (Enhanced Version with Financial Integration)
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
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
    Registrasi mahasiswa baru
    
    - **username**: Username unik (3-50 karakter, alfanumerik + underscore)
    - **email**: Email valid dan unik
    - **password**: Password minimal 6 karakter dengan huruf dan angka
    - **confirm_password**: Konfirmasi password harus sama
    """
    try:
        new_user = await auth_service.register_user(user_data)
        
        return ApiResponse(
            success=True,
            message="Registrasi berhasil! Silakan login untuk melanjutkan setup profil.",
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
    Login mahasiswa
    
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
        
        # 🆕 Get financial overview if setup completed
        financial_overview = None
        if user.onboarding_completed:
            try:
                financial_overview = await auth_service.get_user_financial_overview(user.id)
            except Exception as e:
                print(f"Warning: Could not get financial overview: {e}")
        
        return ApiResponse(
            success=True,
            message="Login berhasil!",
            data={
                "tokens": tokens,
                "user": user_response.dict(),
                "financial_overview": financial_overview
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
    Setup profil mahasiswa setelah registrasi
    
    - **full_name**: Nama lengkap (2-100 karakter) *wajib*
    - **phone_number**: Nomor telepon (opsional)
    - **university**: Nama universitas (2-200 karakter) *wajib*
    - **city**: Kota/kecamatan tempat tinggal (2-100 karakter) *wajib*
    - **occupation**: Pekerjaan sampingan (opsional)
    - **notifications_enabled**: Aktifkan notifikasi
    - **voice_enabled**: Aktifkan fitur suara
    - **dark_mode**: Mode gelap
    
    Note: Bahasa sudah fixed ke Bahasa Indonesia dan mata uang ke Rupiah
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
            message="Profil berhasil disimpan! Silakan lanjutkan setup keuangan.",
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
    Setup keuangan awal mahasiswa dengan integrasi savings goals
    
    - **current_savings**: Total tabungan saat ini (>= 0) *wajib*
    - **monthly_savings_target**: Target tabungan bulanan (> 0) *wajib*
    - **primary_bank**: Bank atau e-wallet utama *wajib*
    
    Disesuaikan untuk kebutuhan mahasiswa Indonesia dengan fokus pada tabungan.
    Otomatis membuat initial savings goals berdasarkan data yang diinput.
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
        
        # 🆕 Get financial dashboard after setup
        financial_overview = await auth_service.get_user_financial_overview(updated_user.id)
        
        # Hitung proyeksi tabungan untuk insight
        projected_6_months = financial_data.current_savings + (financial_data.monthly_savings_target * 6)
        projected_1_year = financial_data.current_savings + (financial_data.monthly_savings_target * 12)
        
        return ApiResponse(
            success=True,
            message="Setup keuangan berhasil! Selamat datang di Lunance - AI finansial untuk mahasiswa Indonesia!",
            data={
                "user": user_response.dict(),
                "financial_overview": financial_overview,
                "projections": {
                    "current_savings": financial_data.current_savings,
                    "monthly_target": financial_data.monthly_savings_target,
                    "projected_6_months": projected_6_months,
                    "projected_1_year": projected_1_year
                },
                "next_steps": [
                    "Mulai chat dengan Luna AI untuk tracking keuangan otomatis",
                    "Buat target tabungan untuk barang yang ingin dibeli",
                    "Input transaksi harian melalui chat natural",
                    "Pantau progress bulanan di dashboard"
                ]
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
    Mendapatkan informasi mahasiswa yang sedang login dengan financial overview
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
        
        # 🆕 Get financial overview if setup completed
        financial_overview = None
        if current_user.onboarding_completed:
            financial_overview = await auth_service.get_user_financial_overview(current_user.id)
        
        return ApiResponse(
            success=True,
            message="Data user berhasil diambil",
            data={
                "user": user_response.dict(),
                "financial_overview": financial_overview
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Terjadi kesalahan: {str(e)}"
        )

@router.post("/logout", response_model=ApiResponse)
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout mahasiswa (menghapus refresh token)
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
    Ganti password mahasiswa
    
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
    Update profil mahasiswa
    
    Semua field bersifat opsional. Hanya field yang dikirim yang akan diupdate.
    Bahasa dan mata uang tidak bisa diubah (fixed untuk Indonesia).
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

# 🆕 NEW ENDPOINTS: Financial Settings Management

@router.put("/financial-settings", response_model=ApiResponse)
async def update_financial_settings(
    financial_data: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Update financial settings dengan sinkronisasi savings goals
    
    - **current_savings**: Update total tabungan saat ini
    - **monthly_savings_target**: Update target tabungan bulanan  
    - **primary_bank**: Update bank/e-wallet utama
    
    Akan otomatis sinkronisasi dengan data savings goals.
    """
    try:
        updated_user = await auth_service.update_financial_settings(current_user.id, financial_data)
        
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
        
        # Get updated financial overview
        financial_overview = await auth_service.get_user_financial_overview(updated_user.id)
        
        return ApiResponse(
            success=True,
            message="Financial settings berhasil diperbarui dan disinkronisasi",
            data={
                "user": user_response.dict(),
                "financial_overview": financial_overview
            }
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Terjadi kesalahan dalam update financial settings: {str(e)}"
        )

@router.get("/financial-overview", response_model=ApiResponse)
async def get_financial_overview(
    current_user: User = Depends(get_current_user)
):
    """
    Mendapatkan overview keuangan lengkap user
    
    Menampilkan:
    - Financial settings user
    - Dashboard keuangan real-time
    - Sync status antara settings dan data aktual
    - Monthly progress
    - Active savings goals
    """
    try:
        financial_overview = await auth_service.get_user_financial_overview(current_user.id)
        
        return ApiResponse(
            success=True,
            message="Financial overview berhasil diambil",
            data=financial_overview
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Terjadi kesalahan mengambil financial overview: {str(e)}"
        )

@router.post("/sync-financial-data", response_model=ApiResponse)
async def sync_financial_data(
    current_user: User = Depends(get_current_user)
):
    """
    Sinkronisasi manual antara user financial settings dengan data savings goals
    
    Berguna jika ada perbedaan antara:
    - current_savings di user settings vs total current_amount di savings goals
    - Data tidak sinkron karena import atau perubahan manual
    """
    try:
        # Import finance service
        from ..services.finance_service import FinanceService
        finance_service = FinanceService()
        
        # Sync financial settings
        sync_result = await finance_service.sync_user_financial_settings(current_user.id)
        
        # Get updated overview
        financial_overview = await auth_service.get_user_financial_overview(current_user.id)
        
        return ApiResponse(
            success=True,
            message="Sinkronisasi financial data berhasil dilakukan",
            data={
                "sync_result": sync_result,
                "financial_overview": financial_overview
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Terjadi kesalahan dalam sinkronisasi: {str(e)}"
        )

@router.get("/onboarding-status", response_model=ApiResponse)
async def get_onboarding_status(
    current_user: User = Depends(get_current_user)
):
    """
    Cek status onboarding user dan langkah yang belum selesai
    """
    try:
        status_data = {
            "user_id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "profile_setup_completed": current_user.profile_setup_completed,
            "financial_setup_completed": current_user.financial_setup_completed,
            "onboarding_completed": current_user.onboarding_completed,
            "next_steps": []
        }
        
        # Determine next steps
        if not current_user.profile_setup_completed:
            status_data["next_steps"].append({
                "step": "profile_setup",
                "title": "Setup Profil",
                "description": "Lengkapi profil dengan nama, universitas, dan kota",
                "endpoint": "/api/v1/auth/setup-profile",
                "priority": 1
            })
        
        if not current_user.financial_setup_completed:
            status_data["next_steps"].append({
                "step": "financial_setup", 
                "title": "Setup Keuangan",
                "description": "Atur tabungan awal dan target bulanan",
                "endpoint": "/api/v1/auth/initial-financial-setup",
                "priority": 2
            })
        
        if current_user.onboarding_completed:
            status_data["next_steps"].append({
                "step": "start_using",
                "title": "Mulai Gunakan Lunance",
                "description": "Chat dengan Luna AI untuk tracking keuangan otomatis",
                "endpoint": "/api/v1/chat/ws/{user_id}",
                "priority": 3
            })
        
        return ApiResponse(
            success=True,
            message="Status onboarding berhasil diambil",
            data=status_data
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Terjadi kesalahan mengambil status onboarding: {str(e)}"
        )