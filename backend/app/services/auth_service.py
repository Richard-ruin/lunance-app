# app/services/auth_service.py - UPDATED untuk metode 50/30/20
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
    UpdateProfile,
    UpdateFinancialSettings
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
            
            # Update budget jika perlu (reset tanggal 1)
            budget_updated = user.update_budget_if_needed()
            if budget_updated:
                # Save updated budget to database
                self.users_collection.update_one(
                    {"_id": ObjectId(user.id)},
                    {"$set": {
                        "financial_settings": user.financial_settings.dict() if user.financial_settings else None,
                        "updated_at": datetime.utcnow()
                    }}
                )
                print(f"✅ Budget 50/30/20 reset untuk user {user.id}")
            
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
        Setup keuangan awal mahasiswa dengan metode 50/30/20 Elizabeth Warren
        
        Input:
        - current_savings: Tabungan awal
        - monthly_income: Pemasukan bulanan (untuk calculate budget 50/30/20)
        - primary_bank: Bank/e-wallet utama
        
        Output: Otomatis calculate budget allocation 50/30/20
        """
        
        try:
            # Buat financial settings dengan metode 50/30/20
            financial_settings = FinancialSettings(
                current_savings=financial_data.current_savings,
                monthly_income=financial_data.monthly_income,
                primary_bank=financial_data.primary_bank,
                budget_method="50/30/20",
                last_budget_reset=datetime.utcnow(),
                budget_cycle="monthly",
                semester_system=True,
                academic_year_start=7,  # Juli (tahun akademik Indonesia)
            )
            
            # Calculate dan set budget allocation 50/30/20
            financial_settings.update_budget_allocation(financial_data.monthly_income)
            
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
            
            print(f"✅ Financial setup 50/30/20 completed for user {user_id}")
            print(f"💰 Monthly Income: Rp {financial_data.monthly_income:,.0f}")
            print(f"🟢 Needs Budget (50%): Rp {financial_settings.needs_budget:,.0f}")
            print(f"🟡 Wants Budget (30%): Rp {financial_settings.wants_budget:,.0f}")
            print(f"🔵 Savings Budget (20%): Rp {financial_settings.savings_budget:,.0f}")
            print(f"🏦 Primary Bank: {financial_data.primary_bank}")
            print(f"📅 Budget reset setiap tanggal 1")
            
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
    
    # === NEW METHODS: Financial Settings Management untuk 50/30/20 ===
    
    async def update_financial_settings(self, user_id: str, financial_data: UpdateFinancialSettings) -> User:
        """Update financial settings dengan recalculate budget 50/30/20"""
        try:
            # Get current user
            user_doc = self.users_collection.find_one({"_id": ObjectId(user_id)})
            if not user_doc:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User tidak ditemukan"
                )
            
            user = User.from_mongo(user_doc)
            
            if not user.financial_settings:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Financial settings belum di-setup"
                )
            
            financial_updates = {}
            recalculate_budget = False
            
            # Update financial settings fields
            if financial_data.current_savings is not None:
                financial_updates["financial_settings.current_savings"] = financial_data.current_savings
                print(f"💰 Updated initial savings to: Rp {financial_data.current_savings:,.0f}")
                
            if financial_data.monthly_income is not None:
                financial_updates["financial_settings.monthly_income"] = financial_data.monthly_income
                # Recalculate budget allocation jika monthly income berubah
                new_allocation = user.financial_settings.calculate_budget_allocation(financial_data.monthly_income)
                financial_updates["financial_settings.needs_budget"] = new_allocation["needs_budget"]
                financial_updates["financial_settings.wants_budget"] = new_allocation["wants_budget"]
                financial_updates["financial_settings.savings_budget"] = new_allocation["savings_budget"]
                recalculate_budget = True
                
                print(f"📊 Updated monthly income & budget allocation:")
                print(f"   Monthly Income: Rp {financial_data.monthly_income:,.0f}")
                print(f"   Needs (50%): Rp {new_allocation['needs_budget']:,.0f}")
                print(f"   Wants (30%): Rp {new_allocation['wants_budget']:,.0f}")
                print(f"   Savings (20%): Rp {new_allocation['savings_budget']:,.0f}")
                
            if financial_data.primary_bank is not None:
                financial_updates["financial_settings.primary_bank"] = financial_data.primary_bank
            
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
        """Mendapatkan overview keuangan lengkap mahasiswa dengan metode 50/30/20"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user or not user.financial_settings:
                return {
                    "has_financial_setup": False,
                    "message": "Financial setup belum dilakukan"
                }
            
            # Get budget allocation 50/30/20
            budget_allocation = user.get_current_budget_allocation()
            
            # Get financial dashboard dari finance service
            try:
                from ..services.finance_service import FinanceService
                finance_service = FinanceService()
                dashboard = await finance_service.get_financial_dashboard_50_30_20(user_id)
            except Exception as e:
                print(f"Error getting dashboard: {e}")
                dashboard = {"error": "Could not load dashboard"}
            
            # Calculate student-specific insights
            student_context = user.get_student_context()
            financial_tips = user.get_student_financial_tips()
            
            return {
                "has_financial_setup": True,
                "budget_method": "50/30/20 Elizabeth Warren",
                "user_profile": {
                    "full_name": user.profile.full_name if user.profile else "",
                    "university": user.profile.university if user.profile else "",
                    "city": user.profile.city if user.profile else "",
                    "is_student": user.is_student
                },
                "budget_allocation": budget_allocation,
                "financial_dashboard": dashboard,
                "student_context": student_context,
                "student_tips": financial_tips,
                "method_explanation": {
                    "needs_50": "Kebutuhan pokok: kos, makan, transport, pendidikan",
                    "wants_30": "Keinginan & lifestyle: hiburan, jajan, target tabungan barang",
                    "savings_20": "Tabungan masa depan: dana darurat, investasi, modal usaha",
                    "reset_schedule": "Budget di-reset setiap tanggal 1",
                    "flexibility": "Proporsi bisa disesuaikan tapi maintain 50/30/20 ratio"
                }
            }
            
        except Exception as e:
            print(f"Error getting financial overview: {e}")
            return {
                "has_financial_setup": False,
                "error": str(e)
            }
    
    async def reset_monthly_budget(self, user_id: str) -> Dict[str, Any]:
        """Manual reset budget bulanan (untuk testing atau emergency)"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user or not user.financial_settings:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Financial settings belum di-setup"
                )
            
            # Force reset budget
            user.financial_settings.last_budget_reset = datetime.utcnow()
            
            # Update di database
            result = self.users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {
                    "financial_settings.last_budget_reset": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }}
            )
            
            if result.modified_count > 0:
                return {
                    "success": True,
                    "message": "Budget berhasil di-reset untuk bulan baru",
                    "reset_time": datetime.utcnow().isoformat(),
                    "budget_allocation": user.get_current_budget_allocation()
                }
            else:
                return {
                    "success": False,
                    "message": "Gagal reset budget"
                }
                
        except Exception as e:
            print(f"Error resetting monthly budget: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_budget_status(self, user_id: str) -> Dict[str, Any]:
        """Cek status budget 50/30/20 current month"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user or not user.financial_settings:
                return {
                    "has_budget": False,
                    "message": "Budget belum di-setup"
                }
            
            # Calculate budget status untuk bulan ini
            from ..services.finance_service import FinanceService
            finance_service = FinanceService()
            
            current_month_spending = await finance_service.get_current_month_spending_by_budget_type(user_id)
            budget_allocation = user.get_current_budget_allocation()
            
            if not budget_allocation["has_budget"]:
                return budget_allocation
            
            allocation = budget_allocation["allocation"]
            
            # Calculate remaining budget
            remaining_budget = {
                "needs": max(allocation["needs_budget"] - current_month_spending["needs"], 0),
                "wants": max(allocation["wants_budget"] - current_month_spending["wants"], 0),
                "savings": max(allocation["savings_budget"] - current_month_spending["savings"], 0)
            }
            
            # Calculate percentage used
            percentage_used = {
                "needs": (current_month_spending["needs"] / allocation["needs_budget"] * 100) if allocation["needs_budget"] > 0 else 0,
                "wants": (current_month_spending["wants"] / allocation["wants_budget"] * 100) if allocation["wants_budget"] > 0 else 0,
                "savings": (current_month_spending["savings"] / allocation["savings_budget"] * 100) if allocation["savings_budget"] > 0 else 0
            }
            
            # Determine overall budget health
            avg_usage = (percentage_used["needs"] + percentage_used["wants"] + percentage_used["savings"]) / 3
            
            if avg_usage <= 70:
                budget_health = "excellent"
            elif avg_usage <= 90:
                budget_health = "good"
            elif avg_usage <= 100:
                budget_health = "warning"
            else:
                budget_health = "over_budget"
            
            # Generate recommendations
            recommendations = []
            if percentage_used["needs"] > 90:
                recommendations.append("⚠️ Budget NEEDS hampir habis. Review pengeluaran kebutuhan pokok.")
            if percentage_used["wants"] > 100:
                recommendations.append("🚨 Budget WANTS sudah over. Kurangi pengeluaran hiburan dan jajan.")
            if percentage_used["savings"] < 50:
                recommendations.append("💡 Budget SAVINGS masih banyak. Pertimbangkan untuk menabung lebih atau investasi.")
            
            if not recommendations:
                recommendations.append("✅ Budget management Anda sudah baik! Pertahankan pola ini.")
            
            return {
                "has_budget": True,
                "method": "50/30/20 Elizabeth Warren",
                "current_month": datetime.now().strftime("%B %Y"),
                "budget_allocation": allocation,
                "current_spending": current_month_spending,
                "remaining_budget": remaining_budget,
                "percentage_used": percentage_used,
                "budget_health": budget_health,
                "recommendations": recommendations,
                "reset_date": "Tanggal 1 setiap bulan"
            }
            
        except Exception as e:
            print(f"Error getting budget status: {e}")
            return {
                "has_budget": False,
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