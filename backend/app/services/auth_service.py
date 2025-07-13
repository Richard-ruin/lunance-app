# app/services/auth_service.py (Enhanced Version)
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
        """Registrasi user baru"""
        
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
        
        # Buat user baru dengan default preferences untuk mahasiswa Indonesia
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            preferences=UserPreferences(),  # Default preferences (ID, IDR)
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
            # Log error for debugging
            print(f"Error creating user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal menyimpan user: {str(e)}"
            )
    
    async def authenticate_user(self, login_data: UserLogin) -> Optional[User]:
        """Autentikasi user dengan email dan password"""
        
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
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60  # dalam detik
            }
            
        except Exception as e:
            print(f"Error creating tokens: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gagal membuat token"
            )
    
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
    
    async def setup_profile(self, user_id: str, profile_data: ProfileSetup) -> User:
        """Setup profil mahasiswa setelah registrasi"""
        
        try:
            # Buat profile object untuk mahasiswa
            profile = UserProfile(
                full_name=profile_data.full_name,
                phone_number=profile_data.phone_number,
                university=profile_data.university,  # Field baru untuk universitas
                city=profile_data.city,  # Sekarang wajib
                occupation=profile_data.occupation  # Pekerjaan sampingan (opsional)
            )
            
            # Update preferences (language dan currency sudah fix di default)
            preferences = UserPreferences(
                language="id",  # Fixed Bahasa Indonesia
                currency="IDR",  # Fixed Rupiah
                notifications_enabled=profile_data.notifications_enabled,
                voice_enabled=profile_data.voice_enabled,
                dark_mode=profile_data.dark_mode
            )
            
            # Update user di database
            update_data = {
                "profile": profile.dict(),
                "preferences": preferences.dict(),
                "profile_setup_completed": True,
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
        """Setup keuangan awal mahasiswa dengan integrasi savings goal"""
        
        try:
            # Buat financial settings object untuk mahasiswa
            financial_settings = FinancialSettings(
                current_savings=financial_data.current_savings,
                monthly_savings_target=financial_data.monthly_savings_target,
                primary_bank=financial_data.primary_bank
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
            
            # 🆕 INTEGRASI FINANCIAL: Buat initial savings goal untuk monthly target
            await self._create_initial_financial_goals(user_id, financial_data)
            
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
    
    async def _create_initial_financial_goals(self, user_id: str, financial_data: FinancialSetup):
        """Buat initial savings goals berdasarkan financial setup"""
        try:
            # Import di sini untuk menghindari circular import
            from .finance_service import FinanceService
            finance_service = FinanceService()
            
            # 1. Buat initial savings goal jika user sudah punya tabungan
            if financial_data.current_savings > 0:
                await self._create_current_savings_goal(
                    user_id, 
                    financial_data.current_savings, 
                    finance_service
                )
            
            # 2. Buat monthly savings goal untuk bulan ini
            if financial_data.monthly_savings_target > 0:
                await finance_service.create_monthly_savings_goal(user_id)
            
            print(f"✅ Initial financial goals created for user {user_id}")
            
        except Exception as e:
            print(f"⚠️ Warning: Failed to create initial financial goals: {e}")
            # Don't raise error karena ini optional
    
    async def _create_current_savings_goal(self, user_id: str, current_savings: float, finance_service):
        """Buat savings goal untuk current savings yang sudah ada"""
        try:
            goal_data = {
                "item_name": "Tabungan Awal",
                "target_amount": current_savings,
                "current_amount": current_savings,  # Sudah tercapai
                "description": f"Tabungan awal sebesar Rp {current_savings:,.0f} yang sudah dimiliki saat setup",
                "status": "completed"
            }
            
            # Create savings goal
            await finance_service.create_savings_goal(
                user_id,
                goal_data,
                {"source": "initial_setup"}
            )
            
            # Mark as completed since it's already achieved
            # Note: The service will handle the completion logic
            
        except Exception as e:
            print(f"Error creating current savings goal: {e}")
    
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
            
            # Update preferences (language dan currency tidak bisa diubah)
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
    
    # 🆕 NEW METHODS: Financial Settings Management
    
    async def update_financial_settings(self, user_id: str, financial_data: Dict[str, Any]) -> User:
        """Update financial settings dengan sinkronisasi savings goals"""
        try:
            financial_updates = {}
            
            # Update financial settings fields
            if "current_savings" in financial_data:
                financial_updates["financial_settings.current_savings"] = financial_data["current_savings"]
            if "monthly_savings_target" in financial_data:
                financial_updates["financial_settings.monthly_savings_target"] = financial_data["monthly_savings_target"]
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
                
                # Sync dengan finance service jika ada perubahan
                from .finance_service import FinanceService
                finance_service = FinanceService()
                await finance_service.sync_user_financial_settings(user_id)
            
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
        """Mendapatkan overview keuangan user"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user or not user.financial_settings:
                return {
                    "has_financial_setup": False,
                    "message": "Financial setup belum dilakukan"
                }
            
            # Get financial dashboard dari finance service
            from .finance_service import FinanceService
            finance_service = FinanceService()
            dashboard = await finance_service.get_financial_dashboard(user_id)
            
            return {
                "has_financial_setup": True,
                "user_profile": {
                    "full_name": user.profile.full_name if user.profile else "",
                    "university": user.profile.university if user.profile else "",
                    "city": user.profile.city if user.profile else ""
                },
                "financial_overview": dashboard
            }
            
        except Exception as e:
            print(f"Error getting financial overview: {e}")
            return {
                "has_financial_setup": False,
                "error": str(e)
            }