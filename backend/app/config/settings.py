import os
from typing import List, Optional
from pydantic import  EmailStr, validator, Field
from pydantic_settings import BaseSettings



class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application Settings
    DEBUG: bool = Field(default=False, env="DEBUG")
    APP_NAME: str = Field(default="Lunance Finance Tracker", env="APP_NAME")
    APP_VERSION: str = Field(default="1.0.0", env="APP_VERSION")
    API_V1_STR: str = "/api/v1"
    
    # Database Settings
    MONGODB_URL: str = Field(..., env="MONGODB_URL")
    DATABASE_NAME: str = Field(..., env="DATABASE_NAME")
    
    # Security Settings
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    ALGORITHM: str = "HS256"
    
    # Password Security
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_NUMBERS: bool = True
    PASSWORD_REQUIRE_SPECIAL_CHARS: bool = False
    
    # Account Security
    MAX_LOGIN_ATTEMPTS: int = Field(default=5, env="MAX_LOGIN_ATTEMPTS")
    ACCOUNT_LOCKOUT_DURATION: int = Field(default=30, env="ACCOUNT_LOCKOUT_DURATION")  # minutes
    
    # OTP Settings
    OTP_EXPIRE_MINUTES: int = Field(default=10, env="OTP_EXPIRE_MINUTES")
    OTP_MAX_ATTEMPTS: int = Field(default=3, env="OTP_MAX_ATTEMPTS")
    OTP_LENGTH: int = 6
    
    # Email/SMTP Configuration
    SMTP_SERVER: str = Field(..., env="SMTP_SERVER")
    SMTP_PORT: int = Field(..., env="SMTP_PORT")
    SMTP_USERNAME: str = Field(..., env="SMTP_USERNAME")
    SMTP_PASSWORD: str = Field(..., env="SMTP_PASSWORD")
    EMAIL_FROM: EmailStr = Field(..., env="EMAIL_FROM")
    EMAIL_FROM_NAME: str = Field(default="Lunance Finance", env="EMAIL_FROM_NAME")
    
    # Email Templates
    EMAIL_TEMPLATES_DIR: str = "app/templates/email"
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    
    # File Upload Settings
    UPLOAD_DIR: str = "static/uploads"
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_FILE_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".pdf"]
    
    # API Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 10
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:8000",
        "https://lunance.app",
        "https://app.lunance.com"
    ]
    
    # Student-specific Settings
    SUPPORTED_UNIVERSITIES: List[str] = [
        "Universitas Indonesia",
        "Institut Teknologi Bandung",
        "Universitas Gadjah Mada",
        "Institut Teknologi Sepuluh Nopember",
        "Universitas Padjadjaran",
        "Universitas Diponegoro",
        "Universitas Airlangga",
        "Universitas Brawijaya",
        "Universitas Hasanuddin",
        "Universitas Andalas"
    ]
    
    # Currency Settings
    DEFAULT_CURRENCY: str = "IDR"
    SUPPORTED_CURRENCIES: List[str] = ["IDR", "USD"]
    
    # Gamification Settings
    POINTS_PER_TRANSACTION: int = 1
    POINTS_PER_SAVINGS_GOAL: int = 10
    POINTS_PER_DAILY_LOGIN: int = 5
    POINTS_PER_WEEKLY_STREAK: int = 25
    
    # Achievement Settings
    ACHIEVEMENTS_FILE: str = "data/achievements.json"
    ACADEMIC_CALENDAR_FILE: str = "data/academic_calendar.json"
    PREDICTION_RULES_FILE: str = "data/prediction_rules.json"
    
    # Chat/AI Settings
    CHAT_SESSION_TIMEOUT_MINUTES: int = 30
    MAX_CHAT_HISTORY: int = 100
    
    # Analytics Settings
    ANALYTICS_RETENTION_DAYS: int = 365
    PREDICTION_DAYS_AHEAD: int = 30
    
    # Development Settings
    RELOAD: bool = Field(default=False, env="RELOAD")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # External API Settings (for future integrations)
    BANK_API_KEY: Optional[str] = Field(default=None, env="BANK_API_KEY")
    NOTIFICATION_SERVICE_URL: Optional[str] = Field(default=None, env="NOTIFICATION_SERVICE_URL")
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    @validator("SECRET_KEY")
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v
    
    @validator("SMTP_PORT")
    def validate_smtp_port(cls, v):
        if v not in [25, 465, 587]:
            raise ValueError("SMTP_PORT must be 25, 465, or 587")
        return v
    
    @validator("PASSWORD_MIN_LENGTH")
    def validate_password_min_length(cls, v):
        if v < 6:
            raise ValueError("PASSWORD_MIN_LENGTH must be at least 6")
        return v
    
    @validator("OTP_LENGTH")
    def validate_otp_length(cls, v):
        if v not in [4, 6, 8]:
            raise ValueError("OTP_LENGTH must be 4, 6, or 8")
        return v
    
    @property
    def database_url_sync(self) -> str:
        """Get synchronous MongoDB URL for migrations or CLI tools"""
        return self.MONGODB_URL.replace("mongodb://", "mongodb://").replace("mongodb+srv://", "mongodb+srv://")
    
    @property
    def smtp_config(self) -> dict:
        """Get SMTP configuration as dict"""
        return {
            "hostname": self.SMTP_SERVER,
            "port": self.SMTP_PORT,
            "username": self.SMTP_USERNAME,
            "password": self.SMTP_PASSWORD,
            "use_tls": self.SMTP_PORT in [587, 25],
            "start_tls": self.SMTP_PORT == 587,
        }
    
    @property
    def password_policy(self) -> dict:
        """Get password policy as dict"""
        return {
            "min_length": self.PASSWORD_MIN_LENGTH,
            "require_uppercase": self.PASSWORD_REQUIRE_UPPERCASE,
            "require_lowercase": self.PASSWORD_REQUIRE_LOWERCASE,
            "require_numbers": self.PASSWORD_REQUIRE_NUMBERS,
            "require_special_chars": self.PASSWORD_REQUIRE_SPECIAL_CHARS,
        }
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create global settings instance
settings = Settings()

# Environment-specific configurations
def get_logging_config():
    """Get logging configuration based on environment"""
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s",
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "formatter": "detailed",
                "class": "logging.FileHandler",
                "filename": "lunance.log",
            },
        },
        "root": {
            "level": settings.LOG_LEVEL,
            "handlers": ["default"] if settings.DEBUG else ["default", "file"],
        },
        "loggers": {
            "uvicorn": {
                "level": "INFO",
                "handlers": ["default"],
                "propagate": False,
            },
            "motor": {
                "level": "WARNING",
                "handlers": ["default"],
                "propagate": False,
            },
        },
    }