# app/routers/auth.py - UPDATED untuk metode 50/30/20 Elizabeth Warren
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
    UpdateFinancialSettings,
    ApiResponse,
    BudgetAllocationResponse,
    MonthlyBudgetStatus
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
                "is_student": new_user.is_student,
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
    Login mahasiswa dengan auto budget reset
    
    - **email**: Email terdaftar
    - **password**: Password yang sesuai
    
    Mengembalikan access token, refresh token, dan budget allocation 50/30/20.
    Budget otomatis di-reset jika sudah lewat tanggal 1.
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
        
        # Get financial overview with budget 50/30/20 if setup completed
        financial_overview = None
        budget_status = None
        if user.onboarding_completed:
            try:
                financial_overview = await auth_service.get_user_financial_overview(user.id)
                budget_status = await auth_service.get_budget_status(user.id)
            except Exception as e:
                print(f"Warning: Could not get financial overview: {e}")
        
        return ApiResponse(
            success=True,
            message="Login berhasil! Budget 50/30/20 siap digunakan." if user.onboarding_completed else "Login berhasil!",
            data={
                "tokens": tokens,
                "user": user_response.dict(),
                "financial_overview": financial_overview,
                "budget_status": budget_status
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
            message="Profil berhasil disimpan! Silakan lanjutkan setup keuangan dengan metode 50/30/20.",
            data={"user": user_response.dict()}
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Terjadi kesalahan dalam setup profil: {str(e)}"
        )

@router.post("/setup-financial-50-30-20", response_model=ApiResponse)
async def setup_financial_50_30_20(
    financial_data: FinancialSetup,
    current_user: User = Depends(get_current_user)
):
    """
    Setup keuangan awal mahasiswa dengan metode 50/30/20 Elizabeth Warren
    
    - **current_savings**: Total tabungan awal saat ini (>= 0) *wajib*
    - **monthly_income**: Pemasukan bulanan (uang saku/gaji) (> 100.000) *wajib*
    - **primary_bank**: Bank atau e-wallet utama *wajib*
    
    Metode 50/30/20:
    - 50% NEEDS: Kos, makan, transport, pendidikan
    - 30% WANTS: Hiburan, jajan, shopping, target tabungan barang
    - 20% SAVINGS: Tabungan umum untuk masa depan
    
    Budget otomatis di-reset setiap tanggal 1.
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
        
        # Get financial overview after setup
        financial_overview = await auth_service.get_user_financial_overview(updated_user.id)
        
        # Calculate budget allocation
        budget_allocation = updated_user.get_current_budget_allocation()
        
        return ApiResponse(
            success=True,
            message="Setup keuangan 50/30/20 berhasil! Selamat datang di Lunance - AI finansial untuk mahasiswa Indonesia!",
            data={
                "user": user_response.dict(),
                "financial_overview": financial_overview,
                "budget_allocation": budget_allocation,
                "method_explanation": {
                    "method": "50/30/20 Elizabeth Warren",
                    "needs_50": "Kebutuhan pokok: kos, makan, transport, pendidikan",
                    "wants_30": "Keinginan & lifestyle: hiburan, jajan, target tabungan barang",
                    "savings_20": "Tabungan masa depan: dana darurat, investasi, modal usaha",
                    "reset_schedule": "Budget di-reset setiap tanggal 1",
                    "categories": {
                        "needs": updated_user.financial_settings.needs_categories,
                        "wants": updated_user.financial_settings.wants_categories,
                        "savings": updated_user.financial_settings.savings_categories
                    }
                },
                "next_steps": [
                    "Mulai chat dengan Luna AI untuk tracking keuangan otomatis",
                    "Input transaksi harian sesuai kategori 50/30/20",
                    "Monitor budget usage di dashboard", 
                    "Atur target tabungan untuk barang yang diinginkan (dari budget WANTS 30%)",
                    "Pantau kesehatan keuangan bulanan"
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
    Mendapatkan informasi mahasiswa yang sedang login dengan budget 50/30/20 overview
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
        
        # Get financial overview and budget status if setup completed
        financial_overview = None
        budget_status = None
        student_context = None
        
        if current_user.onboarding_completed:
            financial_overview = await auth_service.get_user_financial_overview(current_user.id)
            budget_status = await auth_service.get_budget_status(current_user.id)
            student_context = current_user.get_student_context()
        
        return ApiResponse(
            success=True,
            message="Data user berhasil diambil",
            data={
                "user": user_response.dict(),
                "financial_overview": financial_overview,
                "budget_status": budget_status,
                "student_context": student_context
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

# === NEW ENDPOINTS: Financial Settings Management untuk 50/30/20 ===

@router.put("/financial-settings", response_model=ApiResponse)
async def update_financial_settings(
    financial_data: UpdateFinancialSettings,
    current_user: User = Depends(get_current_user)
):
    """
    Update financial settings dengan recalculate budget 50/30/20
    
    - **current_savings**: Update tabungan awal saat ini
    - **monthly_income**: Update pemasukan bulanan (akan recalculate budget 50/30/20)
    - **primary_bank**: Update bank/e-wallet utama
    
    Jika monthly_income berubah, budget allocation akan otomatis di-recalculate.
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
        
        # Get updated financial overview and budget allocation
        financial_overview = await auth_service.get_user_financial_overview(updated_user.id)
        budget_allocation = updated_user.get_current_budget_allocation()
        
        return ApiResponse(
            success=True,
            message="Financial settings berhasil diperbarui dan budget 50/30/20 telah di-recalculate",
            data={
                "user": user_response.dict(),
                "financial_overview": financial_overview,
                "budget_allocation": budget_allocation
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
    Mendapatkan overview keuangan lengkap dengan metode 50/30/20
    
    Menampilkan:
    - Budget allocation 50/30/20
    - Dashboard keuangan real-time
    - Student context dan tips
    - Financial health level
    - Method explanation
    """
    try:
        financial_overview = await auth_service.get_user_financial_overview(current_user.id)
        
        return ApiResponse(
            success=True,
            message="Financial overview 50/30/20 berhasil diambil",
            data=financial_overview
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Terjadi kesalahan mengambil financial overview: {str(e)}"
        )

@router.get("/budget-status", response_model=ApiResponse)
async def get_budget_status(
    current_user: User = Depends(get_current_user)
):
    """
    Cek status budget 50/30/20 untuk bulan ini
    
    Menampilkan:
    - Budget allocation vs actual spending
    - Remaining budget per kategori (needs/wants/savings)
    - Percentage used per kategori
    - Budget health status
    - Recommendations untuk optimasi budget
    """
    try:
        budget_status = await auth_service.get_budget_status(current_user.id)
        
        return ApiResponse(
            success=True,
            message="Budget status 50/30/20 berhasil diambil",
            data=budget_status
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Terjadi kesalahan mengambil budget status: {str(e)}"
        )

@router.post("/reset-monthly-budget", response_model=ApiResponse)
async def reset_monthly_budget(
    current_user: User = Depends(get_current_user)
):
    """
    Manual reset budget bulanan 50/30/20 (untuk testing atau emergency)
    
    Normally budget otomatis reset setiap tanggal 1, tapi endpoint ini
    bisa digunakan untuk force reset manual.
    """
    try:
        reset_result = await auth_service.reset_monthly_budget(current_user.id)
        
        return ApiResponse(
            success=reset_result["success"],
            message=reset_result["message"],
            data=reset_result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Terjadi kesalahan dalam reset budget: {str(e)}"
        )

@router.get("/budget-categories", response_model=ApiResponse)
async def get_budget_categories(
    current_user: User = Depends(get_current_user)
):
    """
    Mendapatkan daftar kategori budget 50/30/20 untuk mahasiswa Indonesia
    
    Menampilkan:
    - NEEDS categories (50%)
    - WANTS categories (30%)
    - SAVINGS categories (20%)
    - Income categories
    """
    try:
        if not current_user.financial_settings:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Financial settings belum di-setup"
            )
        
        categories = {
            "needs_categories": current_user.financial_settings.needs_categories,
            "wants_categories": current_user.financial_settings.wants_categories,
            "savings_categories": current_user.financial_settings.savings_categories,
            "income_categories": current_user.financial_settings.income_categories,
            "method": "50/30/20 Elizabeth Warren",
            "explanation": {
                "needs_50": "Kebutuhan pokok yang wajib dipenuhi",
                "wants_30": "Keinginan dan lifestyle yang bisa dikontrol",
                "savings_20": "Tabungan untuk masa depan dan investasi"
            }
        }
        
        return ApiResponse(
            success=True,
            message="Kategori budget 50/30/20 berhasil diambil",
            data=categories
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Terjadi kesalahan mengambil kategori budget: {str(e)}"
        )

@router.get("/student-financial-tips", response_model=ApiResponse)
async def get_student_financial_tips(
    current_user: User = Depends(get_current_user)
):
    """
    Mendapatkan tips keuangan khusus mahasiswa dengan metode 50/30/20
    
    Tips disesuaikan berdasarkan:
    - Financial health level user
    - University location
    - Budget allocation status
    """
    try:
        tips = current_user.get_student_financial_tips()
        student_context = current_user.get_student_context()
        
        return ApiResponse(
            success=True,
            message="Tips keuangan mahasiswa berhasil diambil",
            data={
                "tips": tips,
                "student_context": student_context,
                "method": "50/30/20 Elizabeth Warren"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Terjadi kesalahan mengambil tips: {str(e)}"
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
            "budget_method": "50/30/20 Elizabeth Warren",
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
                "title": "Setup Keuangan 50/30/20",
                "description": "Atur pemasukan bulanan dan tabungan awal untuk budget 50/30/20",
                "endpoint": "/api/v1/auth/setup-financial-50-30-20",
                "priority": 2
            })
        
        if current_user.onboarding_completed:
            status_data["next_steps"].append({
                "step": "start_using",
                "title": "Mulai Gunakan Lunance",
                "description": "Chat dengan Luna AI untuk tracking keuangan otomatis dengan budget 50/30/20",
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