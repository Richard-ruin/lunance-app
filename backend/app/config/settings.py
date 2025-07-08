# app/config/settings.py (Enhanced untuk WebSocket)
"""Konfigurasi aplikasi dengan dukungan WebSocket dan fitur real-time."""

from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Konfigurasi aplikasi dengan fitur real-time."""
    
    # Konfigurasi Aplikasi
    app_name: str = "Lunance Backend"
    app_version: str = "1.0.0"
    app_description: str = "Sistem Manajemen Keuangan Pintar untuk Mahasiswa Indonesia"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Konfigurasi MongoDB
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "lunance_db"
    mongodb_test_db_name: str = "lunance_test_db"
    
    # Konfigurasi JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_minutes: int = 10080  # 7 hari
    
    # Konfigurasi Email SMTP
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str
    smtp_password: str
    smtp_from_email: str
    smtp_from_name: str = "Tim Lunance"
    
    # Konfigurasi AI
    huggingface_api_key: str
    openai_api_key: Optional[str] = None
    
    # Konfigurasi File Upload
    max_file_size_mb: int = 10
    allowed_image_extensions: str = "jpg,jpeg,png,gif,webp"
    allowed_document_extensions: str = "pdf,doc,docx,txt"
    
    # Konfigurasi CORS
    cors_origins: List[str] = [
        "http://localhost:3000", 
        "http://localhost:3001", 
        "https://lunance.vercel.app",
        "http://192.168.190.195:8000"
    ]
    
    # Konfigurasi Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_minutes: int = 1
    
    # Konfigurasi WebSocket
    websocket_max_connections_per_user: int = 5
    websocket_heartbeat_interval: int = 30  # detik
    websocket_connection_timeout: int = 300  # 5 menit
    websocket_message_max_size: int = 65536  # 64KB
    websocket_rate_limit_messages_per_minute: int = 60
    websocket_rate_limit_messages_per_hour: int = 1000
    websocket_auto_cleanup_interval: int = 300  # 5 menit
    
    # Konfigurasi Real-time Features
    realtime_dashboard_update_interval: int = 5  # detik
    realtime_notification_batch_size: int = 100
    realtime_broadcast_retry_attempts: int = 3
    realtime_offline_message_retention_hours: int = 24
    
    # Konfigurasi Notifications
    notification_email_enabled: bool = True
    notification_push_enabled: bool = True
    notification_websocket_enabled: bool = True
    notification_digest_enabled: bool = True
    notification_cleanup_days: int = 30
    notification_max_unread: int = 1000
    
    # Konfigurasi Broadcasting
    broadcast_max_recipients: int = 10000
    broadcast_email_batch_size: int = 50
    broadcast_retry_delay_seconds: int = 5
    broadcast_history_retention_days: int = 90
    
    # Konfigurasi Kebijakan Password
    password_min_length: int = 8
    password_max_length: int = 128
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_numbers: bool = True
    password_require_special_chars: bool = True
    
    # Konfigurasi OTP
    otp_length: int = 6
    otp_expire_minutes: int = 5
    otp_max_attempts: int = 3
    otp_daily_limit: int = 10
    otp_resend_cooldown_seconds: int = 60
    
    # Validasi Domain Email
    allowed_email_domains: List[str] = ["ac.id"]
    
    # Konfigurasi Keamanan
    token_blacklist_cleanup_hours: int = 24
    failed_login_max_attempts: int = 5
    failed_login_lockout_minutes: int = 15
    session_cleanup_hours: int = 72
    
    # Konfigurasi Logging
    log_level: str = "INFO"
    log_file: str = "app.log"
    log_websocket_file: str = "logs/websocket.log"
    log_notification_file: str = "logs/notifications.log"
    log_broadcast_file: str = "logs/broadcast.log"
    log_max_file_size_mb: int = 50
    log_backup_count: int = 5
    
    # Konfigurasi Performance
    database_connection_pool_size: int = 100
    database_max_idle_time_ms: int = 30000
    cache_default_ttl_seconds: int = 300
    api_response_cache_enabled: bool = True
    
    # Konfigurasi Monitoring
    health_check_interval_seconds: int = 30
    metrics_collection_enabled: bool = True
    performance_logging_enabled: bool = True
    error_tracking_enabled: bool = True
    
    # Konfigurasi Localization
    default_language: str = "id"  # Indonesian
    supported_languages: List[str] = ["id", "en"]
    timezone: str = "Asia/Jakarta"
    date_format: str = "%d/%m/%Y"
    time_format: str = "%H:%M"
    currency_symbol: str = "Rp"
    currency_decimal_places: int = 0
    
    # Konfigurasi Features Toggle
    feature_ai_chat_enabled: bool = True
    feature_predictions_enabled: bool = True
    feature_websocket_enabled: bool = True
    feature_notifications_enabled: bool = True
    feature_broadcasting_enabled: bool = True
    feature_email_notifications_enabled: bool = True
    feature_admin_panel_enabled: bool = True
    
    # Konfigurasi Business Logic
    max_savings_targets_per_user: int = 20
    max_transactions_per_day: int = 100
    max_categories_per_user: int = 50
    transaction_amount_min: float = 0.01
    transaction_amount_max: float = 999999999.99
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins dari string atau list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @field_validator('allowed_email_domains', mode='before')
    @classmethod
    def parse_email_domains(cls, v):
        """Parse domain email yang diizinkan."""
        if isinstance(v, str):
            return [domain.strip() for domain in v.split(',')]
        return v
    
    @field_validator('supported_languages', mode='before')
    @classmethod
    def parse_supported_languages(cls, v):
        """Parse bahasa yang didukung."""
        if isinstance(v, str):
            return [lang.strip() for lang in v.split(',')]
        return v
    
    @property
    def allowed_image_extensions_list(self) -> List[str]:
        """Daftar ekstensi gambar yang diizinkan."""
        return [ext.strip().lower() for ext in self.allowed_image_extensions.split(',')]
    
    @property
    def allowed_document_extensions_list(self) -> List[str]:
        """Daftar ekstensi dokumen yang diizinkan."""
        return [ext.strip().lower() for ext in self.allowed_document_extensions.split(',')]
    
    @property
    def max_file_size_bytes(self) -> int:
        """Ukuran maksimal file dalam bytes."""
        return self.max_file_size_mb * 1024 * 1024
    
    @property
    def websocket_message_max_size_bytes(self) -> int:
        """Ukuran maksimal pesan WebSocket dalam bytes."""
        return self.websocket_message_max_size
    
    @property
    def password_regex_pattern(self) -> str:
        """Generate regex pattern untuk validasi password."""
        pattern_parts = []
        
        if self.password_require_uppercase:
            pattern_parts.append(r'(?=.*[A-Z])')
        if self.password_require_lowercase:
            pattern_parts.append(r'(?=.*[a-z])')
        if self.password_require_numbers:
            pattern_parts.append(r'(?=.*\d)')
        if self.password_require_special_chars:
            pattern_parts.append(r'(?=.*[!@#$%^&*()_+\-=\[\]{}|;:,.<>?])')
        
        pattern = ''.join(pattern_parts)
        pattern += f'.{{{self.password_min_length},{self.password_max_length}}}'
        
        return f'^{pattern}$'
    
    def validate_email_domain(self, email: str) -> bool:
        """Validasi apakah domain email diizinkan."""
        email_lower = email.lower()
        return any(email_lower.endswith(f'.{domain}') for domain in self.allowed_email_domains)
    
    def format_currency(self, amount: float) -> str:
        """Format mata uang sesuai konfigurasi."""
        if self.currency_decimal_places == 0:
            return f"{self.currency_symbol} {amount:,.0f}"
        else:
            return f"{self.currency_symbol} {amount:,.{self.currency_decimal_places}f}"
    
    def get_websocket_settings(self) -> dict:
        """Dapatkan konfigurasi WebSocket."""
        return {
            "max_connections_per_user": self.websocket_max_connections_per_user,
            "heartbeat_interval": self.websocket_heartbeat_interval,
            "connection_timeout": self.websocket_connection_timeout,
            "message_max_size": self.websocket_message_max_size,
            "rate_limit_per_minute": self.websocket_rate_limit_messages_per_minute,
            "rate_limit_per_hour": self.websocket_rate_limit_messages_per_hour,
            "auto_cleanup_interval": self.websocket_auto_cleanup_interval
        }
    
    def get_notification_settings(self) -> dict:
        """Dapatkan konfigurasi notifikasi."""
        return {
            "email_enabled": self.notification_email_enabled,
            "push_enabled": self.notification_push_enabled,
            "websocket_enabled": self.notification_websocket_enabled,
            "digest_enabled": self.notification_digest_enabled,
            "cleanup_days": self.notification_cleanup_days,
            "max_unread": self.notification_max_unread
        }
    
    def get_broadcast_settings(self) -> dict:
        """Dapatkan konfigurasi broadcasting."""
        return {
            "max_recipients": self.broadcast_max_recipients,
            "email_batch_size": self.broadcast_email_batch_size,
            "retry_delay_seconds": self.broadcast_retry_delay_seconds,
            "history_retention_days": self.broadcast_history_retention_days
        }
    
    def get_localization_settings(self) -> dict:
        """Dapatkan konfigurasi lokalisasi."""
        return {
            "default_language": self.default_language,
            "supported_languages": self.supported_languages,
            "timezone": self.timezone,
            "date_format": self.date_format,
            "time_format": self.time_format,
            "currency_symbol": self.currency_symbol,
            "currency_decimal_places": self.currency_decimal_places
        }
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        """Periksa apakah fitur tertentu diaktifkan."""
        feature_attr = f"feature_{feature_name}_enabled"
        return getattr(self, feature_attr, False)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Buat instance settings
settings = Settings()


# Buat direktori upload dan log
def create_required_directories():
    """Buat direktori yang diperlukan jika belum ada."""
    directories = [
        "uploads/profile_pictures",
        "uploads/receipts",
        "logs",
        "temp",
        "backups"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


# Inisialisasi direktori
create_required_directories()


# Fungsi utilitas
def validate_academic_email(email: str) -> bool:
    """
    Validasi email akademik.
    
    Args:
        email: Alamat email yang akan divalidasi
        
    Returns:
        True jika email akademik valid
    """
    return settings.validate_email_domain(email)


def get_smtp_settings() -> dict:
    """
    Dapatkan konfigurasi SMTP untuk layanan email.
    
    Returns:
        Dictionary dengan konfigurasi SMTP
    """
    return {
        "SMTP_HOST": settings.smtp_host,
        "SMTP_PORT": settings.smtp_port,
        "SMTP_USERNAME": settings.smtp_username,
        "SMTP_PASSWORD": settings.smtp_password,
        "SMTP_FROM_EMAIL": settings.smtp_from_email,
        "SMTP_FROM_NAME": settings.smtp_from_name
    }


def get_app_info() -> dict:
    """
    Dapatkan informasi aplikasi.
    
    Returns:
        Dictionary dengan informasi aplikasi
    """
    return {
        "nama": settings.app_name,
        "versi": settings.app_version,
        "deskripsi": settings.app_description,
        "bahasa_default": settings.default_language,
        "mata_uang": settings.currency_symbol,
        "zona_waktu": settings.timezone,
        "fitur_aktif": {
            "ai_chat": settings.feature_ai_chat_enabled,
            "prediksi": settings.feature_predictions_enabled,
            "websocket": settings.feature_websocket_enabled,
            "notifikasi": settings.feature_notifications_enabled,
            "broadcasting": settings.feature_broadcasting_enabled,
            "email_notifikasi": settings.feature_email_notifications_enabled,
            "panel_admin": settings.feature_admin_panel_enabled
        }
    }


# Konstanta untuk pesan dalam bahasa Indonesia
INDONESIAN_MESSAGES = {
    "validation": {
        "required": "Field ini wajib diisi",
        "email_invalid": "Format email tidak valid",
        "email_domain": "Email harus menggunakan domain akademik (.ac.id)",
        "password_weak": "Password tidak memenuhi syarat keamanan",
        "phone_invalid": "Format nomor telepon tidak valid",
        "amount_invalid": "Jumlah tidak valid",
        "date_invalid": "Format tanggal tidak valid"
    },
    "auth": {
        "login_success": "Login berhasil",
        "login_failed": "Email atau password salah",
        "logout_success": "Logout berhasil",
        "register_success": "Registrasi berhasil",
        "token_expired": "Token sudah kadaluarsa",
        "token_invalid": "Token tidak valid",
        "access_denied": "Akses ditolak"
    },
    "websocket": {
        "connected": "Terhubung",
        "disconnected": "Terputus",
        "connection_failed": "Koneksi gagal",
        "message_sent": "Pesan terkirim",
        "message_failed": "Pesan gagal dikirim",
        "rate_limited": "Terlalu banyak pesan, mohon tunggu"
    },
    "notifications": {
        "new_transaction": "Transaksi baru ditambahkan",
        "savings_goal_achieved": "Target tabungan tercapai!",
        "budget_warning": "Anggaran hampir habis",
        "budget_exceeded": "Anggaran terlampaui",
        "system_maintenance": "Pemeliharaan sistem",
        "feature_update": "Fitur baru tersedia"
    },
    "errors": {
        "internal_error": "Terjadi kesalahan internal",
        "not_found": "Data tidak ditemukan",
        "permission_denied": "Izin ditolak",
        "validation_error": "Data tidak valid",
        "rate_limit_exceeded": "Batas permintaan terlampaui",
        "service_unavailable": "Layanan tidak tersedia"
    }
}