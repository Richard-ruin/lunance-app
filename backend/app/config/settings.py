from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import Optional, List


class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Lunance API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # Database Settings
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "lunance_db"

    # JWT Settings
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 1
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Email Settings
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: str = "noreply@lunance.id"
    SMTP_FROM_NAME: str = "Lunance"

    # Security Settings
    MAX_LOGIN_ATTEMPTS: int = 5
    LOGIN_ATTEMPT_TIMEOUT_MINUTES: int = 15
    OTP_EXPIRE_MINUTES: int = 5
    PASSWORD_RESET_OTP_EXPIRE_MINUTES: int = 10
    OTP_MAX_REQUESTS_PER_HOUR: int = 3

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 10

    # File Upload
    MAX_FILE_SIZE_MB: int = 10
    UPLOAD_DIR: str = "uploads/"
    ALLOWED_FILE_TYPES: List[str] = Field(default_factory=lambda: [".jpg", ".jpeg", ".png", ".pdf", ".doc", ".docx"])

    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = Field(default_factory=lambda: [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://lunance.id",
        "https://app.lunance.id"
    ])

    # Pagination
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: str = "logs/app.log"
    ERROR_LOG_FILE: str = "logs/error.log"

    # Redis
    REDIS_URL: Optional[str] = None
    REDIS_PASSWORD: Optional[str] = None
    CACHE_EXPIRE_SECONDS: int = 3600

    # Frontend URLs
    FRONTEND_URL: str = "http://localhost:3000"
    EMAIL_VERIFICATION_URL: str = "http://localhost:3000/verify-email"
    PASSWORD_RESET_URL: str = "http://localhost:3000/reset-password"

    # Feature Flags
    ENABLE_EMAIL_VERIFICATION: bool = True
    ENABLE_OTP_EMAIL: bool = True
    ENABLE_RATE_LIMITING: bool = True
    ENABLE_REGISTRATION: bool = True
    ENABLE_MAINTENANCE_MODE: bool = False

    # Third Party APIs
    GOOGLE_OAUTH_CLIENT_ID: Optional[str] = None
    GOOGLE_OAUTH_CLIENT_SECRET: Optional[str] = None

    # Monitoring
    SENTRY_DSN: Optional[str] = None
    ENABLE_METRICS: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    # Parse comma-separated env vars to lists
    @field_validator("ALLOWED_FILE_TYPES", "CORS_ORIGINS", mode="before")
    @classmethod
    def parse_comma_separated(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v


# Global instance
Config = Settings()
