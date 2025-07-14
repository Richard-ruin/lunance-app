# app/services/auth_service_fixed.py - Fixed logic untuk tabungan awal
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from bson import ObjectId

from ..config.database import get_database
from ..models.user import User, UserProfile, UserPreferences, FinancialSettings
from ..utils.security import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_refresh_token,
    verify_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from ..schemas.auth_schemas import (
    UserRegister, 
    UserLogin, 
    ProfileSetup, 
    FinancialSetup,
    ChangePassword,
    UpdateProfile
)

class AuthService:
    def __init__(self):
        self.db = get_database()
        self.users_collection = self.db.users
    
    async def register_user(self, user_data: UserRegister) -> User:
        """Registrasi mahasiswa baru"""
        
        # Cek apakah email sudah terdaftar
        existing_user = self.users_collection.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email sudah terdaftar"
            )
        
        # Cek apakah username sudah digunakan
        existing_username = self.users_collection.find_one({"username": user_data.username})
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username sudah digunakan"
            )
        
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        # Buat user baru dengan enhanced preferences untuk mahasiswa Indonesia
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            preferences=UserPreferences(),  # Default preferences (ID, IDR, student-optimized)
            is_student=True,  # Default untuk app mahasiswa
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Simpan ke database
        user_dict = new_user.to_mongo()
        
        try:
            result = self.users_collection.insert_one(user_dict)
            
            # Ambil user yang baru dibuat
            created_user = self.users_collection.find_one({"_id": result.inserted_id})
            
            if not created_user:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Gagal membuat user baru"
                )
                
            return User.from_mongo(created_user)
            
        except Exception as e:
            print(f"Error creating user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal menyimpan user: {str(e)}"
            )
    
    async def authenticate_user(self, login_data: UserLogin) -> Optional[User]:
        """Autentikasi mahasiswa dengan email dan password"""
        
        try:
            user_doc = self.users_collection.find_one({"email": login_data.email})
            if not user_doc:
                return None
            
            user = User.from_mongo(user_doc)
            
            # Verifikasi password
            if not verify_password(login_data.password, user.hashed_password):
                return None
            
            # Cek apakah akun aktif
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Akun tidak aktif"
                )
            
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error authenticating user: {e}")
            return None
    
    async def create_tokens(self, user: User) -> dict:
        """Membuat access token dan refresh token"""
        
        try:
            # Data untuk token
            token_data = {"sub": str(user.id), "email": user.email}
            
            # Buat tokens
            access_token = create_access_token(token_data)
            refresh_token = create_refresh_token(token_data)
            
            # Update refresh token di database
            self.users_collection.update_one(
                {"_id": ObjectId(user.id)},
                {
                    "$set": {
                        "refresh_token": refresh_token,
                        "last_login": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }
            
        except Exception as e:
            print(f"Error creating tokens: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gagal membuat token"
            )
    
    async def setup_profile(self, user_id: str, profile_data: ProfileSetup) -> User:
        """Setup profil mahasiswa dengan enhanced fields"""
        
        try:
            # Buat profile object untuk mahasiswa dengan enhanced fields
            profile = UserProfile(
                full_name=profile_data.full_name,
                phone_number=profile_data.phone_number,
                university=profile_data.university,  # Universitas (wajib)
                city=profile_data.city,  # Kota (wajib)
                occupation=profile_data.occupation  # Pekerjaan sampingan (opsional)
            )
            
            # Update preferences (enhanced untuk mahasiswa)
            preferences = UserPreferences(
                language="id",  # Fixed Bahasa Indonesia
                currency="IDR",  # Fixed Rupiah
                notifications_enabled=profile_data.notifications_enabled,
                voice_enabled=profile_data.voice_enabled,
                dark_mode=profile_data.dark_mode,
                auto_categorization=True  # Enable untuk mahasiswa
            )
            
            # Update user di database
            update_data = {
                "profile": profile.dict(),
                "preferences": preferences.dict(),
                "profile_setup_completed": True,
                "is_student": True,  # Ensure student flag
                "updated_at": datetime.utcnow()
            }
            
            result = self.users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            
            if result.modified_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User tidak ditemukan"
                )
            
            # Ambil user yang sudah diupdate
            updated_user = self.users_collection.find_one({"_id": ObjectId(user_id)})
            return User.from_mongo(updated_user)
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error setting up profile: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gagal setup profil"
            )
    
    async def setup_financial(self, user_id: str, financial_data: FinancialSetup) -> User:
        """
        FIXED: Setup keuangan awal mahasiswa dengan logika yang diperbaiki
        - current_savings = tabungan awal, TIDAK berubah otomatis
        - TIDAK membuat savings goal untuk tabungan awal
        - Total tabungan real-time dihitung di finance service
        """
        
        try:
            # Buat financial settings dengan enhanced categories untuk mahasiswa
            financial_settings = FinancialSettings(
                current_savings=financial_data.current_savings,  # Simpan sebagai tabungan AWAL saja
                monthly_savings_target=financial_data.monthly_savings_target,
                emergency_fund=financial_data.emergency_fund,
                primary_bank=financial_data.primary_bank,
                # Categories sudah ada di default FinancialSettings untuk mahasiswa
                semester_system=True,  # Default untuk mahasiswa
                academic_year_start=7  # Juli (tahun akademik Indonesia)
            )
            
            # Update user di database
            update_data = {
                "financial_settings": financial_settings.dict(),
                "financial_setup_completed": True,
                "updated_at": datetime.utcnow()
            }
            
            # Cek apakah profile setup sudah selesai untuk menentukan onboarding
            user_doc = self.users_collection.find_one({"_id": ObjectId(user_id)})
            if user_doc and user_doc.get("profile_setup_completed", False):
                update_data["onboarding_completed"] = True
            
            result = self.users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            
            if result.modified_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User tidak ditemukan"
                )
            
            # FIXED: TIDAK membuat initial savings goals
            # Tabungan awal tetap sebagai current_savings di financial_settings
            # Total tabungan real-time akan dihitung di finance service
            
            print(f"✅ Financial setup completed for user {user_id}")
            print(f"💰 Initial savings: Rp {financial_data.current_savings:,.0f}")
            print(f"🎯 Monthly target: Rp {financial_data.monthly_savings_target:,.0f}")
            print(f"🚨 Emergency fund: Rp {financial_data.emergency_fund:,.0f}")
            print(f"🏦 Primary bank: {financial_data.primary_bank}")
            print(f"📝 Logic: Tabungan awal tersimpan, tidak dibuat savings goal")
            
            # Ambil user yang sudah diupdate
            updated_user = self.users_collection.find_one({"_id": ObjectId(user_id)})
            return User.from_mongo(updated_user)
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error setting up financial: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gagal setup keuangan"
            )
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Mendapatkan user berdasarkan ID"""
        try:
            user_doc = self.users_collection.find_one({"_id": ObjectId(user_id)})
            if user_doc:
                return User.from_mongo(user_doc)
            return None
        except Exception as e:
            print(f"Error getting user by id: {e}")
            return None
    
    async def logout_user(self, user_id: str) -> bool:
        """Logout user dengan menghapus refresh token"""
        try:
            result = self.users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$unset": {"refresh_token": ""},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error logging out user: {e}")
            return False
    
    async def change_password(self, user_id: str, password_data: ChangePassword) -> bool:
        """Ganti password user"""
        
        try:
            # Ambil user saat ini
            user_doc = self.users_collection.find_one({"_id": ObjectId(user_id)})
            if not user_doc:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User tidak ditemukan"
                )
            
            user = User.from_mongo(user_doc)
            
            # Verifikasi password lama
            if not verify_password(password_data.current_password, user.hashed_password):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Password lama tidak sesuai"
                )
            
            # Hash password baru
            new_hashed_password = get_password_hash(password_data.new_password)
            
            # Update password di database
            result = self.users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "hashed_password": new_hashed_password,
                        "updated_at": datetime.utcnow()
                    },
                    "$unset": {"refresh_token": ""}  # Logout dari semua device
                }
            )
            
            return result.modified_count > 0
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error changing password: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gagal mengubah password"
            )
    
    async def update_profile(self, user_id: str, update_data: UpdateProfile) -> User:
        """Update profil mahasiswa"""
        
        try:
            update_dict = {}
            
            # Update profile fields
            profile_updates = {}
            if update_data.full_name is not None:
                profile_updates["profile.full_name"] = update_data.full_name
            if update_data.phone_number is not None:
                profile_updates["profile.phone_number"] = update_data.phone_number
            if update_data.university is not None:
                profile_updates["profile.university"] = update_data.university
            if update_data.city is not None:
                profile_updates["profile.city"] = update_data.city
            if update_data.occupation is not None:
                profile_updates["profile.occupation"] = update_data.occupation
            
            # Update preferences (language dan currency tetap tidak bisa diubah)
            if update_data.notifications_enabled is not None:
                profile_updates["preferences.notifications_enabled"] = update_data.notifications_enabled
            if update_data.voice_enabled is not None:
                profile_updates["preferences.voice_enabled"] = update_data.voice_enabled
            if update_data.dark_mode is not None:
                profile_updates["preferences.dark_mode"] = update_data.dark_mode
            if update_data.auto_categorization is not None:
                profile_updates["preferences.auto_categorization"] = update_data.auto_categorization
            
            if profile_updates:
                profile_updates["updated_at"] = datetime.utcnow()
                
                result = self.users_collection.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$set": profile_updates}
                )
                
                if result.modified_count == 0:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="User tidak ditemukan atau tidak ada perubahan"
                    )
            
            # Ambil user yang sudah diupdate
            updated_user = self.users_collection.find_one({"_id": ObjectId(user_id)})
            return User.from_mongo(updated_user)
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error updating profile: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gagal update profil"
            )
    
    # === ENHANCED METHODS: Financial Settings Management ===
    
    async def update_financial_settings(self, user_id: str, financial_data: Dict[str, Any]) -> User:
        """Update financial settings mahasiswa"""
        try:
            financial_updates = {}
            
            # Update financial settings fields
            if "current_savings" in financial_data:
                # FIXED: current_savings tetap sebagai tabungan awal
                financial_updates["financial_settings.current_savings"] = financial_data["current_savings"]
                print(f"⚠️  Updated initial savings to: Rp {financial_data['current_savings']:,.0f}")
                print(f"📝 Note: Ini mengubah tabungan AWAL, bukan total real-time")
                
            if "monthly_savings_target" in financial_data:
                financial_updates["financial_settings.monthly_savings_target"] = financial_data["monthly_savings_target"]
            if "emergency_fund" in financial_data:
                financial_updates["financial_settings.emergency_fund"] = financial_data["emergency_fund"]
            if "primary_bank" in financial_data:
                financial_updates["financial_settings.primary_bank"] = financial_data["primary_bank"]
            
            if financial_updates:
                financial_updates["updated_at"] = datetime.utcnow()
                
                result = self.users_collection.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$set": financial_updates}
                )
                
                if result.modified_count == 0:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="User tidak ditemukan atau tidak ada perubahan"
                    )
            
            # Ambil user yang sudah diupdate
            updated_user = self.users_collection.find_one({"_id": ObjectId(user_id)})
            return User.from_mongo(updated_user)
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error updating financial settings: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gagal update financial settings"
            )
    
    async def get_user_financial_overview(self, user_id: str) -> Dict[str, Any]:
        """Mendapatkan overview keuangan lengkap mahasiswa dengan logika yang diperbaiki"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user or not user.financial_settings:
                return {
                    "has_financial_setup": False,
                    "message": "Financial setup belum dilakukan"
                }
            
            # Get REAL financial dashboard dari finance service
            from ..services.finance_service import FinanceService
            finance_service = FinanceService()
            dashboard = await finance_service.get_financial_dashboard(user_id)
            
            # Calculate student-specific insights
            student_context = user.get_student_context()
            financial_tips = user.get_student_financial_tips()
            
            return {
                "has_financial_setup": True,
                "user_profile": {
                    "full_name": user.profile.full_name if user.profile else "",
                    "university": user.profile.university if user.profile else "",
                    "city": user.profile.city if user.profile else "",
                    "is_student": user.is_student
                },
                "financial_overview": dashboard,
                "student_context": student_context,
                "student_tips": financial_tips,
                "logic_explanation": {
                    "initial_savings": "Tabungan awal saat setup (tidak berubah otomatis)",
                    "real_total_savings": "Tabungan awal + total pemasukan - total pengeluaran",
                    "monthly_progress": "Pemasukan - pengeluaran bulan ini",
                    "savings_goals": "Target tabungan untuk barang spesifik (terpisah dari total tabungan)"
                }
            }
            
        except Exception as e:
            print(f"Error getting financial overview: {e}")
            return {
                "has_financial_setup": False,
                "error": str(e)
            }
    
    async def refresh_access_token(self, refresh_token: str) -> dict:
        """Refresh access token menggunakan refresh token"""
        
        # Verifikasi refresh token
        payload = verify_token(refresh_token, "refresh")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token tidak valid"
            )
        
        user_id = payload.get("sub")
        
        try:
            user_doc = self.users_collection.find_one({"_id": ObjectId(user_id)})
            
            if not user_doc:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User tidak ditemukan"
                )
            
            user = User.from_mongo(user_doc)
            
            # Cek apakah refresh token masih valid
            if user.refresh_token != refresh_token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh token sudah tidak berlaku"
                )
            
            # Buat access token baru
            token_data = {"sub": str(user.id), "email": user.email}
            new_access_token = create_access_token(token_data)
            
            return {
                "access_token": new_access_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error refreshing token: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gagal refresh token"
            )