# app/models/user_updated.py - Updated untuk mahasiswa Indonesia
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
    """Model untuk pengaturan keuangan mahasiswa - FIXED LOGIC"""
    # FIXED: current_savings = tabungan awal saat setup, TIDAK berubah otomatis
    current_savings: Optional[float] = None  # Tabungan awal (tidak berubah)
    monthly_savings_target: Optional[float] = None  # Target tabungan bulanan
    emergency_fund: Optional[float] = None  # Dana darurat saat setup
    primary_bank: Optional[str] = None  # Bank atau e-wallet utama
    
    # Enhanced categories untuk mahasiswa Indonesia
    expense_categories: list = Field(default_factory=lambda: [
        "Makanan & Minuman",        # Makan, minum, jajan
        "Transportasi",             # Ojol, angkot, bensin
        "Pendidikan",              # Buku, alat tulis, fotocopy, print
        "Kos/Tempat Tinggal",      # Sewa kos, listrik kos
        "Internet & Komunikasi",    # Pulsa, paket data, WiFi
        "Hiburan & Sosial",        # Nongkrong, cinema, game
        "Kesehatan & Kebersihan",   # Obat, vitamin, sabun, shampo
        "Pakaian & Aksesoris",     # Baju, sepatu, tas
        "Organisasi & Kegiatan",    # UKM, himpunan, event kampus
        "Lainnya"                  # Kategori lain
    ])
    
    income_categories: list = Field(default_factory=lambda: [
        "Uang Saku/Kiriman Ortu",  # Support dari keluarga
        "Part-time Job",           # Kerja sampingan
        "Freelance/Project",       # Freelance online
        "Beasiswa",               # Beasiswa pendidikan
        "Hadiah/Bonus",           # Hadiah, THR, bonus
        "Lainnya"                 # Pemasukan lain
    ])
    
    # Student-specific settings
    semester_system: bool = True  # Menggunakan sistem semester
    academic_year_start: Optional[int] = None  # Tahun akademik dimulai (bulan)
    university_location: Optional[str] = None  # Lokasi universitas untuk context

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
    """Model utama untuk User mahasiswa Indonesia"""
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
    
    # Financial settings (enhanced untuk mahasiswa)
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
    
    # === ENHANCED METHODS untuk mahasiswa ===
    
    def get_real_total_savings(self) -> float:
        """
        CATATAN: Method ini hanya mengembalikan tabungan awal dari financial settings.
        Untuk total tabungan real-time, gunakan FinanceService._calculate_real_total_savings()
        yang menghitung: tabungan_awal + total_pemasukan - total_pengeluaran
        """
        if self.financial_settings:
            return self.financial_settings.current_savings or 0.0
        return 0.0
    
    def get_student_context(self) -> Dict[str, Any]:
        """Dapatkan context mahasiswa untuk personalisasi"""
        context = {
            "is_student": self.is_student,
            "university": self.profile.university if self.profile else None,
            "city": self.profile.city if self.profile else None,
            "semester": self.profile.semester if self.profile else None,
            "major": self.profile.major if self.profile else None,
            "has_financial_setup": self.financial_setup_completed,
            "primary_bank": self.financial_settings.primary_bank if self.financial_settings else None
        }
        
        # Add financial capacity context
        if self.financial_settings:
            context.update({
                "initial_savings": self.financial_settings.current_savings or 0,
                "monthly_target": self.financial_settings.monthly_savings_target or 0,
                "emergency_fund": self.financial_settings.emergency_fund or 0,
                "financial_health_level": self._calculate_financial_health_level()
            })
        
        return context
    
    def _calculate_financial_health_level(self) -> str:
        """Hitung level kesehatan keuangan mahasiswa"""
        if not self.financial_settings:
            return "unknown"
        
        initial_savings = self.financial_settings.current_savings or 0
        monthly_target = self.financial_settings.monthly_savings_target or 0
        emergency_fund = self.financial_settings.emergency_fund or 0
        
        # Simple scoring untuk mahasiswa
        score = 0
        
        # Emergency fund score (max 40 points)
        if emergency_fund >= 1000000:  # 1 juta
            score += 40
        elif emergency_fund >= 500000:  # 500k
            score += 25
        elif emergency_fund >= 200000:  # 200k
            score += 15
        
        # Initial savings score (max 35 points)
        if initial_savings >= 5000000:  # 5 juta
            score += 35
        elif initial_savings >= 2000000:  # 2 juta
            score += 25
        elif initial_savings >= 1000000:  # 1 juta
            score += 15
        elif initial_savings >= 500000:  # 500k
            score += 10
        
        # Monthly target score (max 25 points)
        if monthly_target >= 1000000:  # 1 juta per bulan
            score += 25
        elif monthly_target >= 500000:  # 500k per bulan
            score += 20
        elif monthly_target >= 200000:  # 200k per bulan
            score += 15
        elif monthly_target >= 100000:  # 100k per bulan
            score += 10
        
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
        """Dapatkan tips keuangan khusus mahasiswa berdasarkan profile"""
        tips = []
        
        if not self.financial_setup_completed:
            tips.append("Lengkapi setup keuangan untuk mendapatkan insight yang lebih baik")
            return tips
        
        health_level = self._calculate_financial_health_level()
        city = self.profile.city if self.profile else ""
        
        if health_level == "needs_improvement":
            tips.extend([
                "Mulai dengan dana darurat minimal Rp 200.000 untuk situasi mendesak",
                "Catat semua pengeluaran harian untuk mengetahui pola spending",
                "Cari cara menghemat seperti masak sendiri atau berbagi ongkos transport"
            ])
        elif health_level == "fair":
            tips.extend([
                "Tingkatkan dana darurat menjadi Rp 500.000 - 1 juta",
                "Buat target tabungan spesifik untuk barang yang diinginkan",
                "Pertimbangkan part-time job yang fleksibel dengan jadwal kuliah"
            ])
        elif health_level == "good":
            tips.extend([
                "Pertahankan kebiasaan menabung yang sudah baik",
                "Mulai pelajari investasi sederhana untuk mahasiswa",
                "Buat rencana keuangan jangka panjang untuk setelah lulus"
            ])
        else:  # excellent
            tips.extend([
                "Keuangan Anda sudah sangat baik untuk ukuran mahasiswa!",
                "Pertimbangkan untuk membantu teman-teman mengelola keuangan",
                "Mulai belajar investasi jangka panjang dan perencanaan karir"
            ])
        
        # City-specific tips
        if "jakarta" in city.lower():
            tips.append("Manfaatkan TransJakarta dan KRL untuk menghemat ongkos transport di Jakarta")
        elif "bandung" in city.lower():
            tips.append("Bandung punya banyak tempat makan murah untuk mahasiswa, eksplorasi untuk hemat")
        elif "yogya" in city.lower() or "jogja" in city.lower():
            tips.append("Manfaatkan Trans Jogja dan jalur sepeda untuk transport hemat di Yogyakarta")
        elif "surabaya" in city.lower():
            tips.append("Gunakan Suroboyo Bus dan cari tempat makan lesehan untuk hemat di Surabaya")
        
        return tips
    
    def format_for_api_response(self) -> Dict[str, Any]:
        """Format user data untuk API response dengan context mahasiswa"""
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
            
            # Enhanced context
            "student_context": self.get_student_context(),
            "financial_health_level": self._calculate_financial_health_level(),
            "student_tips": self.get_student_financial_tips()
        }
        
        return response_data

class UserInDB(User):
    """Model untuk user yang disimpan di database"""
    pass