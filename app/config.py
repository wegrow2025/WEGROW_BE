from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # 데이터베이스 설정
    database_url: str = "sqlite:///./wegrow.db"
    
    # JWT 설정
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Redis 설정
    redis_url: str = "redis://localhost:6379"
    
    # AI 서비스 설정
    clova_client_id: Optional[str] = None
    clova_client_secret: Optional[str] = None
    clova_stt_api_url: str = "https://naveropenapi.apigw.ntruss.com/recog/v1/stt"
    
    # OpenAI 설정
    openai_api_key: Optional[str] = None
    
    # Google TTS 설정
    google_tts_api_key: Optional[str] = None
    
    # 파일 업로드 설정
    max_file_size: int = 10485760  # 10MB
    upload_dir: str = "./uploads"
    
    # 개발 설정
    debug: bool = True
    environment: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
