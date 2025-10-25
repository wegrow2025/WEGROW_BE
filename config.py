from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # CLOVA Configuration
    clova_client_id: str = os.getenv("CLOVA_CLIENT_ID", "")
    clova_client_secret: str = os.getenv("CLOVA_CLIENT_SECRET", "")
    
    # Database Configuration
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./wegrow.db")
    
    # Redis Configuration
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # JWT Configuration
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24시간 (1440분)
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Audio Processing Configuration
    max_audio_duration: int = 300  # 5 minutes
    audio_sample_rate: int = 16000
    audio_channels: int = 1
    
    class Config:
        env_file = ".env"

settings = Settings()
