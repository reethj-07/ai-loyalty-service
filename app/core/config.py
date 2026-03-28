from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from typing import Optional

class Settings(BaseSettings):
    # App Configuration
    app_name: str = "Agentic Loyalty AI Service"
    environment: str = os.getenv("ENVIRONMENT", "local")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    debug: bool = False
    
    # Database
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_anon_key: str = os.getenv("SUPABASE_ANON_KEY", "")
    supabase_service_key: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    supabase_jwt_secret: Optional[str] = os.getenv("SUPABASE_JWT_SECRET", None)
    
    # Optional Services
    redis_url: Optional[str] = os.getenv("REDIS_URL", None)
    sendgrid_api_key: Optional[str] = os.getenv("SENDGRID_API_KEY", None)
    anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY", None)
    groq_api_key: Optional[str] = os.getenv("GROQ_API_KEY", None)
    llm_provider: str = os.getenv("LLM_PROVIDER", "groq")
    
    # Feature Flags
    enable_ml_models: bool = os.getenv("ENABLE_ML_MODELS", "true").lower() == "true"
    enable_email: bool = sendgrid_api_key is not None
    enable_ai: bool = anthropic_api_key is not None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )
    
    def __init__(self, **data):
        super().__init__(**data)
        # Set debug based on environment
        self.debug = self.environment != "production"

settings = Settings()
