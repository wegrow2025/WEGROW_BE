from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid


class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: f"user_{uuid.uuid4()}")
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    child_age = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    
    # 관계
    settings = relationship("UserSettings", back_populates="user", uselist=False)
    audio_samples = relationship("AudioSample", back_populates="user")
    timeline_items = relationship("TimelineItem", back_populates="user")


class UserSettings(Base):
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # 기본 설정
    recording_collection = Column(Boolean, default=True)
    analysis_usage = Column(Boolean, default=True)
    coaching_recommendations = Column(Boolean, default=True)
    notifications_enabled = Column(Boolean, default=True)
    email_reports = Column(Boolean, default=True)
    data_retention_days = Column(Integer, default=365)
    language = Column(String, default="ko-KR")
    timezone = Column(String, default="Asia/Seoul")
    
    # 프라이버시 설정
    audio_recording = Column(Boolean, default=True)
    research_participation = Column(Boolean, default=False)
    third_party_sharing = Column(Boolean, default=False)
    anonymized_research = Column(Boolean, default=False)
    family_sharing = Column(Boolean, default=False)
    
    # 관계
    user = relationship("User", back_populates="settings")


class AudioSample(Base):
    __tablename__ = "audio_samples"
    
    id = Column(String, primary_key=True, default=lambda: f"sample_{uuid.uuid4()}")
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # 오디오 정보
    file_path = Column(String, nullable=False)
    duration = Column(Float, nullable=False)
    source = Column(String, nullable=False)  # "parent" | "robot"
    notes = Column(Text)
    
    # 분석 결과
    transcription = Column(Text)
    intent = Column(String)
    confidence = Column(Float)
    emotion = Column(String)
    age_appropriate = Column(Boolean)
    recommended_response = Column(Text)
    language_development_stage = Column(String)
    
    # TTS 오디오
    tts_audio_path = Column(String)
    
    # 메타데이터
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    analyzed_at = Column(DateTime(timezone=True))
    status = Column(String, default="pending")  # "pending" | "analyzing" | "completed" | "failed"
    
    # 관계
    user = relationship("User", back_populates="audio_samples")
    timeline_items = relationship("TimelineItem", back_populates="audio_sample")


class TimelineItem(Base):
    __tablename__ = "timeline_items"
    
    id = Column(String, primary_key=True, default=lambda: f"timeline_{uuid.uuid4()}")
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    audio_sample_id = Column(String, ForeignKey("audio_samples.id"))
    
    # 타임라인 정보
    date = Column(String, nullable=False)  # YYYY-MM-DD
    time = Column(String, nullable=False)  # HH:MM
    child_utterance = Column(Text, nullable=False)
    intent = Column(String, nullable=False)
    parent_response = Column(Text)
    
    # 오디오 정보
    audio_url = Column(String)
    duration = Column(Float)
    confidence = Column(Float)
    
    # 분석 결과
    analysis_result = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계
    user = relationship("User", back_populates="timeline_items")
    audio_sample = relationship("AudioSample", back_populates="timeline_items")


class Tip(Base):
    __tablename__ = "tips"
    
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String, nullable=False)
    age_range = Column(JSON)  # [min_age, max_age]
    scenario = Column(Text, nullable=False)
    parent_response = Column(Text, nullable=False)
    explanation = Column(Text, nullable=False)
    tags = Column(JSON)  # ["확장", "모델링", "대화이어가기"]
    effectiveness = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)


class UserTipFavorite(Base):
    __tablename__ = "user_tip_favorites"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    tip_id = Column(Integer, ForeignKey("tips.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DailyReport(Base):
    __tablename__ = "daily_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    date = Column(String, nullable=False)  # YYYY-MM-DD
    
    # 일일 지표
    vocalizations = Column(Integer, default=0)
    syllable_combinations = Column(Integer, default=0)
    meaningful_attempts = Column(Integer, default=0)
    new_words = Column(Integer, default=0)
    
    # 전일 대비
    previous_day_vocalizations = Column(Integer, default=0)
    
    # 요약 및 추천
    summary = Column(Text)
    recommended_response = Column(Text)
    
    # 성장 지표
    growth_indicators = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class WeeklyReport(Base):
    __tablename__ = "weekly_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    week_start_date = Column(String, nullable=False)  # YYYY-MM-DD
    
    # 주간 지표
    vocabulary_count = Column(Integer, default=0)
    two_word_sentences = Column(Integer, default=0)
    conversation_duration = Column(Float, default=0.0)
    
    # 진행 지표
    progress_metrics = Column(JSON)
    
    # 일일 순간들
    daily_moments = Column(JSON)
    
    # 단계별 가이드
    stage_guides = Column(JSON)
    
    # 추천사항
    recommendations = Column(JSON)
    
    # 부모 지원
    parent_assist = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
