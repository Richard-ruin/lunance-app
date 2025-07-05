# app/config.py (updated untuk AI features)
from pydantic_settings import BaseSettings
from typing import Optional, List
import json

class Settings(BaseSettings):
    model_config = {"env_file": ".env"}
    
    # Database
    mongodb_url: str
    
    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    
    # SMTP Settings (gunakan nama yang konsisten)
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str
    smtp_password: str
    smtp_from_email: str = ""
    smtp_from_name: str = "Student Finance"
    
    # OTP Settings
    otp_expire_minutes: int = 10
    max_otp_requests: int = 5
    
    # AI Configuration
    ai_enabled: bool = True
    indobert_model: str = "indolem/indobert-base-uncased"
    sentiment_model: str = "w11wo/indonesian-roberta-base-sentiment-classifier"
    ai_confidence_threshold: float = 0.7
    ai_processing_timeout: int = 30
    ai_cache_models: bool = True
    ai_max_context_length: int = 512
    
    # WebSocket Configuration
    ws_max_connections_per_user: int = 5
    ws_heartbeat_interval: int = 30
    ws_message_rate_limit: int = 60
    
    # Chat Configuration
    chat_session_timeout_hours: int = 24
    chat_max_messages_per_session: int = 1000
    chat_context_expire_minutes: int = 30
    
    # Luna AI Personality & Behavior
    luna_personality: str = "friendly"  # friendly, professional, casual
    luna_language_preference: str = "mixed"  # indonesian, english, mixed
    luna_response_style: str = "informative"  # brief, informative, detailed
    
    # AI Model Paths (for local models if needed)
    ai_models_cache_dir: str = "./ai_models"
    ai_enable_model_download: bool = True
    ai_model_download_timeout: int = 300  # seconds
    
    # Rate Limiting for AI
    ai_requests_per_minute: int = 60
    ai_requests_per_hour: int = 1000
    ai_enable_rate_limiting: bool = True
    
    # Logging Configuration
    log_level: str = "INFO"
    log_ai_conversations: bool = True
    log_ai_performance: bool = True
    
    # Feature Flags
    enable_dashboard: bool = True
    enable_ai_chatbot: bool = True
    enable_websocket: bool = True
    enable_analytics: bool = True
    enable_export_import: bool = True
    
    # Security Settings - Updated CORS configuration
    cors_origins: str = '["*"]'  # JSON string that will be parsed
    max_upload_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: list = [".jpg", ".jpeg", ".png", ".pdf"]
    
    # Development Settings
    debug_mode: bool = False
    reload_on_change: bool = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set default from_email if not provided
        if not self.smtp_from_email:
            self.smtp_from_email = self.smtp_username
        
        # Validate AI configuration
        if self.ai_enabled:
            self._validate_ai_config()
    
    def _validate_ai_config(self):
        """Validate AI configuration settings"""
        if self.ai_confidence_threshold < 0.0 or self.ai_confidence_threshold > 1.0:
            raise ValueError("ai_confidence_threshold must be between 0.0 and 1.0")
        
        if self.ai_processing_timeout < 1:
            raise ValueError("ai_processing_timeout must be at least 1 second")
        
        if self.chat_max_messages_per_session < 1:
            raise ValueError("chat_max_messages_per_session must be at least 1")
    
    @property
    def parsed_cors_origins(self) -> List[str]:
        """Parse CORS origins from JSON string"""
        try:
            return json.loads(self.cors_origins)
        except json.JSONDecodeError:
            # Fallback to wildcard if parsing fails
            return ["*"]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return not self.debug_mode and self.parsed_cors_origins != ["*"]
    
    @property
    def ai_models_config(self) -> dict:
        """Get AI models configuration"""
        return {
            "language_model": self.indobert_model,
            "sentiment_model": self.sentiment_model,
            "cache_dir": self.ai_models_cache_dir,
            "enable_download": self.ai_enable_model_download,
            "download_timeout": self.ai_model_download_timeout
        }
    
    @property
    def websocket_config(self) -> dict:
        """Get WebSocket configuration"""
        return {
            "max_connections_per_user": self.ws_max_connections_per_user,
            "heartbeat_interval": self.ws_heartbeat_interval,
            "message_rate_limit": self.ws_message_rate_limit
        }
    
    @property
    def luna_config(self) -> dict:
        """Get Luna AI personality configuration"""
        return {
            "personality": self.luna_personality,
            "language_preference": self.luna_language_preference,
            "response_style": self.luna_response_style,
            "confidence_threshold": self.ai_confidence_threshold
        }
    
    @property
    def rate_limiting_config(self) -> dict:
        """Get rate limiting configuration"""
        return {
            "ai_requests_per_minute": self.ai_requests_per_minute,
            "ai_requests_per_hour": self.ai_requests_per_hour,
            "enable_rate_limiting": self.ai_enable_rate_limiting
        }

settings = Settings()