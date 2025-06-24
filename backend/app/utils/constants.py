"""
Constants for the Lunance Finance Tracker application
"""

from enum import Enum
from typing import Dict, List, Any

# Application Constants
APP_NAME = "Lunance Finance Tracker"
APP_DESCRIPTION = "Personal Finance Tracker for Indonesian Students"
API_VERSION = "v1"

# Student Academic Constants
class Semester(Enum):
    SEMESTER_1 = 1
    SEMESTER_2 = 2
    SEMESTER_3 = 3
    SEMESTER_4 = 4
    SEMESTER_5 = 5
    SEMESTER_6 = 6
    SEMESTER_7 = 7
    SEMESTER_8 = 8
    SEMESTER_9 = 9
    SEMESTER_10 = 10
    SEMESTER_11 = 11
    SEMESTER_12 = 12
    SEMESTER_13 = 13
    SEMESTER_14 = 14

class AcademicYear(Enum):
    YEAR_1 = 1
    YEAR_2 = 2
    YEAR_3 = 3
    YEAR_4 = 4
    YEAR_5 = 5
    YEAR_6 = 6
    YEAR_7 = 7

class EducationLevel(Enum):
    S1 = "S1"  # Sarjana (Bachelor's)
    S2 = "S2"  # Magister (Master's)
    S3 = "S3"  # Doktor (PhD)
    D3 = "D3"  # Diploma 3
    D4 = "D4"  # Diploma 4

# Transaction Constants
class TransactionType(Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"

class TransactionCategory(Enum):
    # Student-specific categories
    ACADEMIC = "academic"
    FOOD = "food"
    TRANSPORTATION = "transportation"
    ENTERTAINMENT = "entertainment"
    HEALTH = "health"
    TECHNOLOGY = "technology"
    CLOTHING = "clothing"
    SOCIAL = "social"
    EMERGENCY = "emergency"
    SAVINGS = "savings"
    OTHER = "other"

class PaymentMethod(Enum):
    CASH = "cash"
    DEBIT_CARD = "debit_card"
    CREDIT_CARD = "credit_card"
    E_WALLET = "e_wallet"
    BANK_TRANSFER = "bank_transfer"
    OTHER = "other"

# Indonesian E-Wallet Providers
INDONESIAN_E_WALLETS = [
    "GoPay", "OVO", "DANA", "LinkAja", "ShopeePay", 
    "Jenius", "Sakuku", "TrueMoney", "Doku"
]

# Indonesian Banks
INDONESIAN_BANKS = [
    "Bank Central Asia (BCA)", "Bank Rakyat Indonesia (BRI)", 
    "Bank Negara Indonesia (BNI)", "Bank Mandiri", "Bank CIMB Niaga",
    "Bank Permata", "Bank Danamon", "Bank OCBC NISP", "Bank Maybank",
    "Bank BTN", "Bank BJB", "Jenius", "Bank Neo Commerce",
    "Bank Jago", "Bank Seabank"
]

# Expense Categories with Subcategories
EXPENSE_CATEGORIES = {
    "academic": {
        "name": "Akademik",
        "icon": "📚",
        "color": "#3B82F6",
        "subcategories": [
            "uang_kuliah", "buku", "alat_tulis", "fotokopi", "print",
            "lab", "praktikum", "seminar", "conference", "research",
            "thesis", "skripsi", "software", "subscription_academic"
        ]
    },
    "food": {
        "name": "Makanan & Minuman",
        "icon": "🍽️",
        "color": "#10B981",
        "subcategories": [
            "sarapan", "makan_siang", "makan_malam", "snack", "kopi",
            "bubble_tea", "jajan", "groceries", "bahan_masak", "delivery",
            "restaurant", "cafe", "kantin", "warteg", "street_food"
        ]
    },
    "transportation": {
        "name": "Transportasi",
        "icon": "🚗",
        "color": "#F59E0B",
        "subcategories": [
            "ojol", "grab", "gojek", "bus", "angkot", "kereta", "krl",
            "mrt", "lrt", "bensin", "parkir", "tol", "taxi",
            "bike_sharing", "car_sharing"
        ]
    },
    "entertainment": {
        "name": "Hiburan",
        "icon": "🎮",
        "color": "#8B5CF6",
        "subcategories": [
            "nonton", "bioskop", "streaming", "game", "musik", "spotify",
            "netflix", "youtube_premium", "hobi", "olahraga", "gym",
            "traveling", "liburan", "concert", "festival"
        ]
    },
    "health": {
        "name": "Kesehatan",
        "icon": "🏥",
        "color": "#EF4444",
        "subcategories": [
            "obat", "vitamin", "suplemen", "dokter", "checkup",
            "dental", "glasses", "contact_lens", "therapy",
            "consultation", "emergency_medical"
        ]
    },
    "technology": {
        "name": "Teknologi",
        "icon": "📱",
        "color": "#06B6D4",
        "subcategories": [
            "internet", "wifi", "pulsa", "paket_data", "aplikasi",
            "subscription", "cloud_storage", "gadget", "accessories",
            "repair", "upgrade", "software_license"
        ]
    },
    "clothing": {
        "name": "Pakaian",
        "icon": "👕",
        "color": "#EC4899",
        "subcategories": [
            "baju", "celana", "sepatu", "jaket", "tas", "aksesoris",
            "underwear", "socks", "belt", "watch", "jewelry", "laundry"
        ]
    },
    "social": {
        "name": "Sosial",
        "icon": "👥",
        "color": "#84CC16",
        "subcategories": [
            "hang_out", "dating", "kado", "gift", "donasi", "charity",
            "organisasi", "event", "party", "wedding", "family",
            "friends", "social_activities"
        ]
    },
    "emergency": {
        "name": "Darurat",
        "icon": "🚨",
        "color": "#DC2626",
        "subcategories": [
            "medical_emergency", "family_emergency", "repair_urgent",
            "replacement", "unexpected", "crisis"
        ]
    }
}

# Income Categories
INCOME_CATEGORIES = {
    "allowance": {
        "name": "Uang Saku",
        "icon": "💰",
        "color": "#059669"
    },
    "part_time": {
        "name": "Kerja Paruh Waktu",
        "icon": "💼",
        "color": "#0D9488"
    },
    "freelance": {
        "name": "Freelance",
        "icon": "💻",
        "color": "#0891B2"
    },
    "scholarship": {
        "name": "Beasiswa",
        "icon": "🎓",
        "color": "#7C3AED"
    },
    "investment": {
        "name": "Investasi",
        "icon": "📈",
        "color": "#C026D3"
    },
    "business": {
        "name": "Bisnis",
        "icon": "🏪",
        "color": "#EA580C"
    },
    "gift": {
        "name": "Hadiah",
        "icon": "🎁",
        "color": "#DC2626"
    },
    "other": {
        "name": "Lainnya",
        "icon": "❓",
        "color": "#6B7280"
    }
}

# Savings Goal Categories
SAVINGS_GOAL_CATEGORIES = {
    "emergency": {
        "name": "Dana Darurat",
        "icon": "🆘",
        "color": "#DC2626",
        "priority": "high"
    },
    "gadget": {
        "name": "Gadget",
        "icon": "📱",
        "color": "#3B82F6",
        "priority": "medium"
    },
    "travel": {
        "name": "Liburan",
        "icon": "✈️",
        "color": "#10B981",
        "priority": "low"
    },
    "education": {
        "name": "Pendidikan",
        "icon": "📚",
        "color": "#8B5CF6",
        "priority": "high"
    },
    "investment": {
        "name": "Investasi",
        "icon": "📈",
        "color": "#F59E0B",
        "priority": "medium"
    },
    "wedding": {
        "name": "Pernikahan",
        "icon": "💍",
        "color": "#EC4899",
        "priority": "high"
    },
    "vehicle": {
        "name": "Kendaraan",
        "icon": "🚗",
        "color": "#84CC16",
        "priority": "medium"
    },
    "house": {
        "name": "Rumah",
        "icon": "🏠",
        "color": "#06B6D4",
        "priority": "high"
    }
}

# Achievement Categories
ACHIEVEMENT_CATEGORIES = {
    "starter": {
        "name": "Pemula",
        "description": "Achievement untuk pengguna baru",
        "color": "#10B981"
    },
    "consistency": {
        "name": "Konsistensi",
        "description": "Achievement untuk kebiasaan baik",
        "color": "#3B82F6"
    },
    "savings": {
        "name": "Menabung",
        "description": "Achievement untuk pencapaian tabungan",
        "color": "#F59E0B"
    },
    "social": {
        "name": "Sosial",
        "description": "Achievement untuk aktivitas sosial",
        "color": "#8B5CF6"
    },
    "milestone": {
        "name": "Pencapaian",
        "description": "Achievement untuk milestone penting",
        "color": "#EF4444"
    }
}

# Indonesian Regions and Major Cities
INDONESIAN_REGIONS = {
    "jawa": [
        "Jakarta", "Surabaya", "Bandung", "Bekasi", "Medan", "Tangerang",
        "Depok", "Semarang", "Palembang", "Makassar", "South Tangerang",
        "Batam", "Bogor", "Pekanbaru", "Bandar Lampung"
    ],
    "sumatra": [
        "Medan", "Palembang", "Batam", "Pekanbaru", "Bandar Lampung",
        "Padang", "Jambi", "Bengkulu", "Banda Aceh", "Dumai"
    ],
    "kalimantan": [
        "Balikpapan", "Samarinda", "Pontianak", "Banjarmasin", "Palangka Raya"
    ],
    "sulawesi": [
        "Makassar", "Manado", "Kendari", "Palu", "Gorontalo"
    ],
    "bali_nusa_tenggara": [
        "Denpasar", "Mataram", "Kupang"
    ],
    "maluku_papua": [
        "Ambon", "Jayapura", "Sorong", "Merauke"
    ]
}

# Indonesian Public Holidays (common ones)
INDONESIAN_HOLIDAYS = [
    "Tahun Baru", "Imlek", "Hari Raya Nyepi", "Wafat Isa Almasih",
    "Hari Buruh", "Kenaikan Isa Almasih", "Hari Lahir Pancasila",
    "Idul Fitri", "Hari Kemerdekaan RI", "Idul Adha", "Tahun Baru Islam",
    "Maulid Nabi Muhammad SAW", "Hari Natal"
]

# Academic Calendar Events
ACADEMIC_EVENTS = {
    "semester_start": "Awal Semester",
    "semester_end": "Akhir Semester", 
    "midterm_exam": "UTS",
    "final_exam": "UAS",
    "registration": "Registrasi",
    "orientation": "Orientasi",
    "graduation": "Wisuda",
    "thesis_defense": "Sidang Skripsi/Tesis",
    "holiday": "Libur",
    "study_break": "Libur Belajar"
}

# Expense Prediction Rules
PREDICTION_RULES = {
    "academic_start": {
        "trigger": "semester_start",
        "categories": ["academic", "technology", "clothing"],
        "multiplier": 1.5,
        "description": "Peningkatan pengeluaran di awal semester"
    },
    "exam_period": {
        "trigger": "exam_week",
        "categories": ["food", "health", "entertainment"],
        "multiplier": 1.2,
        "description": "Peningkatan pengeluaran selama ujian"
    },
    "holiday_period": {
        "trigger": "holiday",
        "categories": ["transportation", "entertainment", "social"],
        "multiplier": 1.8,
        "description": "Peningkatan pengeluaran selama liburan"
    },
    "ramadan": {
        "trigger": "ramadan",
        "categories": ["food"],
        "multiplier": 1.3,
        "description": "Perubahan pola pengeluaran selama Ramadan"
    }
}

# Gamification Constants
EXPERIENCE_POINTS = {
    "daily_login": 5,
    "first_transaction": 15,
    "complete_profile": 50,
    "set_budget": 25,
    "achieve_savings_goal": 100,
    "share_expense": 20,
    "weekly_streak": 40,
    "monthly_streak": 150,
    "budget_adherence": 30,
    "expense_categorization": 10
}

LEVEL_THRESHOLDS = [
    0,      # Level 1: 0-99 points
    100,    # Level 2: 100-299 points
    300,    # Level 3: 300-599 points
    600,    # Level 4: 600-999 points
    1000,   # Level 5: 1000-1499 points
    1500,   # Level 6: 1500+ points (then +500 for each level)
]

# Default Budget Allocations for Students (percentages)
DEFAULT_BUDGET_ALLOCATION = {
    "food": 40,           # 40% for food
    "transportation": 15,  # 15% for transportation
    "academic": 10,       # 10% for academic expenses
    "entertainment": 10,   # 10% for entertainment
    "health": 5,          # 5% for health
    "clothing": 5,        # 5% for clothing
    "social": 5,          # 5% for social activities
    "emergency": 10       # 10% for emergency fund
}

# Financial Health Indicators
FINANCIAL_HEALTH_THRESHOLDS = {
    "emergency_fund_months": 3,  # 3 months of expenses
    "savings_rate_minimum": 10,  # 10% of income
    "debt_to_income_maximum": 30,  # 30% of income
    "budget_variance_acceptable": 10  # 10% variance from budget
}

# Notification Templates
NOTIFICATION_TEMPLATES = {
    "budget_warning": "Hati-hati! Pengeluaran {category} sudah mencapai {percentage}% dari budget bulan ini.",
    "budget_exceeded": "Budget {category} telah terlampaui! Sudah {amount} lebih dari target.",
    "savings_goal_achieved": "Selamat! Target tabungan '{goal_name}' telah tercapai!",
    "daily_reminder": "Jangan lupa catat pengeluaran hari ini untuk tracking yang lebih baik.",
    "weekly_summary": "Minggu ini kamu sudah menghabiskan {amount} dengan kategori terbanyak: {category}.",
    "achievement_unlocked": "Achievement baru terbuka: {achievement_name}! Kamu mendapat {points} poin."
}

# API Response Messages
API_MESSAGES = {
    "success": {
        "created": "Data berhasil dibuat",
        "updated": "Data berhasil diperbarui", 
        "deleted": "Data berhasil dihapus",
        "retrieved": "Data berhasil diambil"
    },
    "error": {
        "not_found": "Data tidak ditemukan",
        "unauthorized": "Tidak memiliki akses",
        "forbidden": "Akses ditolak",
        "validation": "Data tidak valid",
        "server_error": "Terjadi kesalahan server"
    }
}

# File Upload Constants
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif']
ALLOWED_DOCUMENT_EXTENSIONS = ['.pdf', '.doc', '.docx', '.txt']
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_DOCUMENT_SIZE = 10 * 1024 * 1024  # 10MB

# Rate Limiting
RATE_LIMITS = {
    "auth": "10/minute",
    "otp": "5/minute", 
    "general": "100/minute",
    "upload": "20/minute"
}

# Cache Keys
CACHE_KEYS = {
    "user_profile": "user_profile:{user_id}",
    "user_transactions": "user_transactions:{user_id}:{date}",
    "exchange_rates": "exchange_rates:{date}",
    "university_list": "university_list",
    "achievements": "achievements"
}

# Timeouts (in seconds)
TIMEOUTS = {
    "jwt_access": 30 * 60,      # 30 minutes
    "jwt_refresh": 7 * 24 * 60 * 60,  # 7 days
    "otp": 10 * 60,             # 10 minutes
    "password_reset": 24 * 60 * 60,   # 24 hours
    "cache_short": 5 * 60,      # 5 minutes
    "cache_medium": 30 * 60,    # 30 minutes
    "cache_long": 24 * 60 * 60  # 24 hours
}