# app/models/user_updated.py - Updated untuk metode 50/30/20
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from bson import ObjectId
from enum import Enum

class UserPreferences(BaseModel):
    """Model untuk preferensi user - disesuaikan untuk mahasiswa Indonesia"""
    language: str = "id"  # Fixed Bahasa Indonesia
    currency: str = "IDR"  # Fixed Rupiah
    date_format: str = "DD/MM/YYYY"
    time_format: str = "24h"
    notifications_enabled: bool = True
    voice_enabled: bool = True
    dark_mode: bool = False
    auto_categorization: bool = True

class FinancialSettings(BaseModel):
    """
    Model untuk pengaturan keuangan mahasiswa dengan metode 50/30/20 Elizabeth Warren
    
    Metode 50/30/20:
    - 50% Needs (Kebutuhan): Kos, makan, transport, pendidikan  
    - 30% Wants (Keinginan): Hiburan, jajan, shopping, target tabungan barang
    - 20% Savings (Tabungan): Tabungan umum untuk masa depan
    
    Budget di-reset setiap tanggal 1
    """
    # Core settings
    current_savings: Optional[float] = None  # Tabungan awal (tidak berubah otomatis)
    monthly_income: Optional[float] = None   # Pemasukan bulanan (wajib untuk calculate budget)
    primary_bank: Optional[str] = None       # Bank atau e-wallet utama
    
    # Auto-calculated budget allocation (50/30/20)
    needs_budget: Optional[float] = None     # 50% dari monthly_income
    wants_budget: Optional[float] = None     # 30% dari monthly_income  
    savings_budget: Optional[float] = None   # 20% dari monthly_income
    
    # Budget tracking
    budget_method: str = "50/30/20"          # Metode budgeting yang digunakan
    last_budget_reset: Optional[datetime] = None  # Terakhir budget di-reset (tanggal 1)
    budget_cycle: str = "monthly"            # Siklus budget (monthly)
    
    # Enhanced categories untuk mahasiswa Indonesia dengan klasifikasi 50/30/20
    needs_categories: list = Field(default_factory=lambda: [
        # 50% NEEDS - Kebutuhan pokok mahasiswa
        "Makanan Pokok",               # Makan sehari-hari, groceries
        "Kos/Tempat Tinggal",         # Sewa kos, listrik, air
        "Transportasi Wajib",          # Transport ke kampus, pulang
        "Pendidikan",                  # Buku, alat tulis, UKT, praktikum
        "Internet & Komunikasi",       # Pulsa, paket data (kebutuhan)
        "Kesehatan & Kebersihan",      # Obat, vitamin, sabun, pasta gigi
    ])
    
    wants_categories: list = Field(default_factory=lambda: [
        # 30% WANTS - Keinginan dan lifestyle mahasiswa
        "Hiburan & Sosial",           # Nongkrong, cinema, game
        "Jajan & Snack",              # Jajan di luar kebutuhan pokok
        "Pakaian & Aksesoris",        # Baju, sepatu, tas (non-essential)
        "Organisasi & Event",         # UKM, himpunan, event kampus
        "Target Tabungan Barang",     # Nabung untuk laptop, HP, dll (dari wants)
        "Lainnya (Wants)",            # Keinginan lainnya
    ])
    
    savings_categories: list = Field(default_factory=lambda: [
        # 20% SAVINGS - Tabungan untuk masa depan
        "Tabungan Umum",              # Tabungan tanpa tujuan spesifik
        "Dana Darurat",               # Untuk situasi mendesak
        "Investasi Masa Depan",       # Reksadana, saham (untuk yang sudah advanced)
        "Tabungan Jangka Panjang",    # Untuk setelah lulus, modal usaha, dll
    ])
    
    income_categories: list = Field(default_factory=lambda: [
        "Uang Saku/Kiriman Ortu",     # Support dari keluarga
        "Part-time Job",              # Kerja sampingan
        "Freelance/Project",          # Freelance online
        "Beasiswa",                   # Beasiswa pendidikan
        "Hadiah/Bonus",               # Hadiah, THR, bonus
        "Lainnya",                    # Pemasukan lain
    ])
    
    # Student-specific settings
    semester_system: bool = True              # Menggunakan sistem semester
    academic_year_start: Optional[int] = None # Tahun akademik dimulai (bulan)
    university_location: Optional[str] = None # Lokasi universitas untuk context
    
    def calculate_budget_allocation(self, monthly_income: float) -> Dict[str, float]:
        """Calculate budget allocation berdasarkan metode 50/30/20"""
        return {
            "monthly_income": monthly_income,
            "needs_budget": monthly_income * 0.50,    # 50% untuk kebutuhan
            "wants_budget": monthly_income * 0.30,    # 30% untuk keinginan
            "savings_budget": monthly_income * 0.20,  # 20% untuk tabungan
            "needs_percentage": 50.0,
            "wants_percentage": 30.0,
            "savings_percentage": 20.0
        }
    
    def update_budget_allocation(self, monthly_income: float):
        """Update budget allocation dan set ke field"""
        if monthly_income > 0:
            self.monthly_income = monthly_income
            self.needs_budget = monthly_income * 0.50
            self.wants_budget = monthly_income * 0.30
            self.savings_budget = monthly_income * 0.20
    
    def get_category_type(self, category: str) -> str:
        """Tentukan apakah kategori masuk needs, wants, atau savings"""
        if category in self.needs_categories:
            return "needs"
        elif category in self.wants_categories:
            return "wants"
        elif category in self.savings_categories:
            return "savings"
        else:
            return "unknown"
    
    def should_reset_budget(self) -> bool:
        """Cek apakah budget perlu di-reset (sudah lewat tanggal 1)"""
        if not self.last_budget_reset:
            return True
        
        now = datetime.utcnow()
        # Reset jika sudah lewat tanggal 1 bulan ini
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return self.last_budget_reset < current_month_start

class UserProfile(BaseModel):
    """Model untuk profil mahasiswa Indonesia"""
    full_name: str
    phone_number: Optional[str] = None
    university: Optional[str] = None  # Universitas (wajib untuk mahasiswa)
    city: Optional[str] = None  # Kota/kecamatan tempat tinggal (wajib)
    occupation: Optional[str] = None  # Pekerjaan sampingan (opsional)
    profile_picture: Optional[str] = None
    
    # Additional student-specific fields
    student_id: Optional[str] = None  # NIM/Student ID (opsional)
    major: Optional[str] = None  # Jurusan (opsional)
    semester: Optional[int] = None  # Semester saat ini (opsional)
    graduation_year: Optional[int] = None  # Target lulus (opsional)

class User(BaseModel):
    """Model utama untuk User mahasiswa Indonesia dengan sistem 50/30/20"""
    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }
    )
    
    id: Optional[str] = Field(default=None, alias="_id")
    username: str
    email: EmailStr
    hashed_password: str
    
    # Profile information
    profile: Optional[UserProfile] = None
    
    # App preferences (fixed untuk Indonesia)
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    
    # Financial settings (enhanced dengan metode 50/30/20)
    financial_settings: Optional[FinancialSettings] = None
    
    # Account status
    is_active: bool = True
    is_verified: bool = False
    is_premium: bool = False
    
    # Setup status
    profile_setup_completed: bool = False
    financial_setup_completed: bool = False
    onboarding_completed: bool = False
    
    # Student-specific status
    is_student: bool = True  # Default true untuk app mahasiswa
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    # Session management
    refresh_token: Optional[str] = None
    
    @classmethod
    def from_mongo(cls, data: Dict[str, Any]) -> "User":
        """Mengkonversi data dari MongoDB ke User model"""
        if data is None:
            return None
            
        # Konversi ObjectId ke string
        if "_id" in data and data["_id"] is not None:
            data["_id"] = str(data["_id"])
        elif "_id" not in data:
            data["_id"] = None
            
        return cls(**data)
    
    def to_mongo(self) -> Dict[str, Any]:
        """Mengkonversi User model ke format MongoDB"""
        data = self.model_dump(by_alias=True, exclude_unset=True)
        
        # Hapus _id jika None (untuk insert baru)
        if "_id" in data and data["_id"] is None:
            del data["_id"]
            
        return data
    
    def update_last_login(self):
        """Update timestamp last login"""
        self.last_login = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def complete_profile_setup(self):
        """Menandai profile setup sebagai selesai"""
        self.profile_setup_completed = True
        self.updated_at = datetime.utcnow()
    
    def complete_financial_setup(self):
        """Menandai financial setup sebagai selesai"""
        self.financial_setup_completed = True
        self.updated_at = datetime.utcnow()
        
        # Check jika semua setup sudah selesai
        if self.profile_setup_completed and self.financial_setup_completed:
            self.onboarding_completed = True
    
    def is_setup_complete(self) -> bool:
        """Mengecek apakah setup user sudah lengkap"""
        return self.profile_setup_completed and self.financial_setup_completed
    
    # === ENHANCED METHODS untuk sistem 50/30/20 ===
    
    def get_current_budget_allocation(self) -> Dict[str, Any]:
        """Dapatkan alokasi budget 50/30/20 saat ini"""
        if not self.financial_settings or not self.financial_settings.monthly_income:
            return {
                "has_budget": False,
                "message": "Belum setup budget bulanan"
            }
        
        monthly_income = self.financial_settings.monthly_income
        allocation = self.financial_settings.calculate_budget_allocation(monthly_income)
        
        return {
            "has_budget": True,
            "method": "50/30/20 Elizabeth Warren",
            "allocation": allocation,
            "reset_date": "Tanggal 1 setiap bulan",
            "last_reset": self.financial_settings.last_budget_reset,
            "needs_budget_remaining": allocation["needs_budget"],  # Will be calculated in service
            "wants_budget_remaining": allocation["wants_budget"],
            "savings_budget_remaining": allocation["savings_budget"]
        }
    
    def update_budget_if_needed(self):
        """Update budget allocation jika perlu (dipanggil saat login/activity)"""
        if not self.financial_settings:
            return False
        
        if self.financial_settings.should_reset_budget():
            # Reset budget untuk bulan baru
            if self.financial_settings.monthly_income:
                self.financial_settings.update_budget_allocation(self.financial_settings.monthly_income)
                self.financial_settings.last_budget_reset = datetime.utcnow()
                self.updated_at = datetime.utcnow()
                return True
        
        return False
    
    def get_real_total_savings(self) -> float:
        """
        Hitung total tabungan real-time = tabungan_awal + akumulasi_savings
        Note: Untuk total real-time, gunakan FinanceService._calculate_real_total_savings()
        """
        if self.financial_settings:
            return self.financial_settings.current_savings or 0.0
        return 0.0
    
    def get_student_context(self) -> Dict[str, Any]:
        """Dapatkan context mahasiswa untuk personalisasi dengan metode 50/30/20"""
        context = {
            "is_student": self.is_student,
            "university": self.profile.university if self.profile else None,
            "city": self.profile.city if self.profile else None,
            "semester": self.profile.semester if self.profile else None,
            "major": self.profile.major if self.profile else None,
            "has_financial_setup": self.financial_setup_completed,
            "primary_bank": self.financial_settings.primary_bank if self.financial_settings else None,
            "budget_method": "50/30/20",
            "budget_allocation": self.get_current_budget_allocation()
        }
        
        # Add financial capacity context dengan metode 50/30/20
        if self.financial_settings:
            context.update({
                "initial_savings": self.financial_settings.current_savings or 0,
                "monthly_income": self.financial_settings.monthly_income or 0,
                "needs_budget": self.financial_settings.needs_budget or 0,
                "wants_budget": self.financial_settings.wants_budget or 0,
                "savings_budget": self.financial_settings.savings_budget or 0,
                "financial_health_level": self._calculate_financial_health_level()
            })
        
        return context
    
    def _calculate_financial_health_level(self) -> str:
        """Hitung level kesehatan keuangan mahasiswa berdasarkan metode 50/30/20"""
        if not self.financial_settings or not self.financial_settings.monthly_income:
            return "unknown"
        
        monthly_income = self.financial_settings.monthly_income
        initial_savings = self.financial_settings.current_savings or 0
        
        # Simple scoring untuk mahasiswa dengan metode 50/30/20
        score = 0
        
        # Monthly income score (max 40 points)
        if monthly_income >= 3000000:  # 3 juta ke atas
            score += 40
        elif monthly_income >= 2000000:  # 2 juta
            score += 30
        elif monthly_income >= 1000000:  # 1 juta
            score += 20
        elif monthly_income >= 500000:   # 500k
            score += 10
        
        # Initial savings score (max 35 points)
        if initial_savings >= 5000000:  # 5 juta
            score += 35
        elif initial_savings >= 2000000:  # 2 juta
            score += 25
        elif initial_savings >= 1000000:  # 1 juta
            score += 15
        elif initial_savings >= 500000:  # 500k
            score += 10
        
        # Budget discipline score (max 25 points) - jika sudah menggunakan sistem 50/30/20
        if self.financial_settings.last_budget_reset:
            score += 25  # Bonus untuk yang sudah konsisten pakai budget
        elif self.financial_setup_completed:
            score += 15  # Bonus untuk yang sudah setup
        
        # Determine level
        if score >= 80:
            return "excellent"
        elif score >= 60:
            return "good"
        elif score >= 40:
            return "fair"
        else:
            return "needs_improvement"
    
    def get_student_financial_tips(self) -> List[str]:
        """Tips keuangan khusus mahasiswa dengan metode 50/30/20"""
        tips = []
        
        if not self.financial_setup_completed:
            tips.append("Setup keuangan dengan metode 50/30/20 untuk budgeting yang lebih terstruktur")
            return tips
        
        health_level = self._calculate_financial_health_level()
        budget_allocation = self.get_current_budget_allocation()
        
        if health_level == "needs_improvement":
            tips.extend([
                "Mulai disiplin dengan metode 50/30/20: 50% kebutuhan, 30% keinginan, 20% tabungan",
                "Focus pada kategori NEEDS dulu: kos, makan, transport, pendidikan", 
                "Batasi pengeluaran WANTS maksimal 30% dari pemasukan bulanan"
            ])
        elif health_level == "fair":
            tips.extend([
                "Pertahankan disiplin budget 50/30/20 yang sudah berjalan",
                "Manfaatkan 30% WANTS untuk target tabungan barang yang diinginkan",
                "Tingkatkan 20% SAVINGS untuk dana darurat minimal 3 bulan pengeluaran"
            ])
        elif health_level == "good":
            tips.extend([
                "Excellent! Budget 50/30/20 sudah berjalan dengan baik",
                "Pertimbangkan untuk investasi sederhana dari 20% SAVINGS",
                "Gunakan surplus WANTS untuk target tabungan barang impian"
            ])
        else:  # excellent
            tips.extend([
                "🎉 Budget management Anda sudah sangat baik!",
                "Pertimbangkan untuk belajar investasi jangka panjang", 
                "Bagikan tips budgeting 50/30/20 ke teman-teman mahasiswa"
            ])
        
        # City-specific tips tetap sama
        city = self.profile.city if self.profile else ""
        if "jakarta" in city.lower():
            tips.append("Jakarta: Maksimalkan transportasi umum untuk menghemat budget NEEDS")
        elif "bandung" in city.lower():
            tips.append("Bandung: Manfaatkan tempat makan murah untuk menjaga budget NEEDS 50%")
        elif "yogya" in city.lower() or "jogja" in city.lower():
            tips.append("Yogyakarta: Gunakan sepeda/jalan kaki untuk menghemat budget transportasi")
        elif "surabaya" in city.lower():
            tips.append("Surabaya: Manfaatkan Suroboyo Bus untuk transport hemat")
        
        return tips
    
    def format_for_api_response(self) -> Dict[str, Any]:
        """Format user data untuk API response dengan context 50/30/20"""
        response_data = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "profile": self.profile.dict() if self.profile else None,
            "preferences": self.preferences.dict(),
            "financial_settings": self.financial_settings.dict() if self.financial_settings else None,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "is_premium": self.is_premium,
            "is_student": self.is_student,
            "profile_setup_completed": self.profile_setup_completed,
            "financial_setup_completed": self.financial_setup_completed,
            "onboarding_completed": self.onboarding_completed,
            "created_at": self.created_at,
            "last_login": self.last_login,
            
            # Enhanced context dengan metode 50/30/20
            "student_context": self.get_student_context(),
            "budget_allocation": self.get_current_budget_allocation(),
            "financial_health_level": self._calculate_financial_health_level(),
            "student_tips": self.get_student_financial_tips(),
            "budget_method": "50/30/20 Elizabeth Warren"
        }
        
        return response_data

class UserInDB(User):
    """Model untuk user yang disimpan di database"""
    pass