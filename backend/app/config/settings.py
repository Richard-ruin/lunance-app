"""
Application Settings Configuration
Menggunakan pydantic-settings untuk environment configuration
"""

from typing import List, Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings dengan validasi lengkap"""
    
    # Application Configuration
    app_name: str = Field(default="Lunance Backend API", description="Nama aplikasi")
    app_version: str = Field(default="1.0.0", description="Versi aplikasi")
    debug: bool = Field(default=False, description="Mode debug")
    api_v1_prefix: str = Field(default="/api/v1", description="API v1 prefix")
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Host server")
    port: int = Field(default=8000, description="Port server")
    
    # MongoDB Configuration
    mongodb_url: str = Field(..., description="MongoDB connection URL")
    database_name: str = Field(default="lunance_db", description="Nama database")
    
    # Security Configuration
    secret_key: str = Field(..., description="Secret key untuk JWT")
    algorithm: str = Field(default="HS256", description="Algorithm untuk JWT")
    access_token_expire_minutes: int = Field(
        default=30, 
        description="Durasi token dalam menit"
    )
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(
        default=60, 
        description="Rate limit per menit"
    )
    
    # Email Configuration
    smtp_server: Optional[str] = Field(default=None, description="SMTP server")
    smtp_port: Optional[int] = Field(default=587, description="SMTP port")
    smtp_username: Optional[str] = Field(default=None, description="SMTP username")
    smtp_password: Optional[str] = Field(default=None, description="SMTP password")
    
    # AI Model Configuration
    ai_model_name: str = Field(
        default="indolem/indobert-base-uncased",
        description="Nama model AI"
    )
    ai_model_cache_dir: str = Field(
        default="./models",
        description="Directory cache model AI"
    )
    
    # File Upload Configuration
    max_file_size: int = Field(
        default=5242880,  # 5MB
        description="Maksimum ukuran file upload"
    )
    upload_dir: str = Field(
        default="./uploads",
        description="Directory untuk file upload"
    )
    
    # Logging Configuration
    log_level: str = Field(default="INFO", description="Level logging")
    log_file: str = Field(default="./logs/app.log", description="File log")
    
    # CORS Configuration
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="Origins yang diizinkan"
    )
    allowed_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "PATCH"],
        description="HTTP methods yang diizinkan"
    )
    allowed_headers: List[str] = Field(
        default=["*"],
        description="Headers yang diizinkan"
    )
    
    # University Domain Validation
    valid_university_domains: List[str] = Field(
        default=["ac.id"],
        description="Domain universitas yang valid"
    )
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @validator("mongodb_url")
    def validate_mongodb_url(cls, v):
        """Validasi format MongoDB URL"""
        if not v.startswith("mongodb://") and not v.startswith("mongodb+srv://"):
            raise ValueError("MongoDB URL harus dimulai dengan mongodb:// atau mongodb+srv://")
        return v
    
    @validator("secret_key")
    def validate_secret_key(cls, v):
        """Validasi secret key minimal 32 karakter"""
        if len(v) < 32:
            raise ValueError("Secret key harus minimal 32 karakter")
        return v
    
    @validator("port")
    def validate_port(cls, v):
        """Validasi port range"""
        if not 1 <= v <= 65535:
            raise ValueError("Port harus antara 1-65535")
        return v
    
    @validator("access_token_expire_minutes")
    def validate_token_expire(cls, v):
        """Validasi durasi token"""
        if v <= 0:
            raise ValueError("Durasi token harus lebih dari 0")
        return v
    
    @validator("rate_limit_per_minute")
    def validate_rate_limit(cls, v):
        """Validasi rate limit"""
        if v <= 0:
            raise ValueError("Rate limit harus lebih dari 0")
        return v
    
    @validator("max_file_size")
    def validate_file_size(cls, v):
        """Validasi maksimum file size"""
        if v <= 0:
            raise ValueError("Maksimum file size harus lebih dari 0")
        return v
    
    @validator("log_level")
    def validate_log_level(cls, v):
        """Validasi log level"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level harus salah satu dari: {valid_levels}")
        return v.upper()


# Instance global settings
settings = Settings()


# Utility functions
def get_database_url() -> str:
    """Get full database URL dengan database name"""
    return f"{settings.mongodb_url}/{settings.database_name}"


def is_development() -> bool:
    """Check apakah dalam mode development"""
    return settings.debug


def is_production() -> bool:
    """Check apakah dalam mode production"""
    return not settings.debug


def get_cors_config() -> dict:
    """Get CORS configuration dictionary"""
    return {
        "allow_origins": settings.allowed_origins,
        "allow_methods": settings.allowed_methods,
        "allow_headers": settings.allowed_headers,
        "allow_credentials": True,
    }