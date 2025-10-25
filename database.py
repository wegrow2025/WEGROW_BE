from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from typing import Optional

# Database setup
engine = create_engine("sqlite:///./wegrow.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    hashed_password = Column(String)
    child_age_months = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    audio_samples = relationship("AudioSample", back_populates="user")
    settings = relationship("UserSettings", back_populates="user", uselist=False)

class UserSettings(Base):
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    recording_collection = Column(Boolean, default=True)
    analysis_usage = Column(Boolean, default=True)
    coaching_recommendations = Column(Boolean, default=True)
    notifications_enabled = Column(Boolean, default=True)
    email_reports = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="settings")

class AudioSample(Base):
    __tablename__ = "audio_samples"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    file_path = Column(String)
    duration = Column(Float)
    source = Column(String)  # "parent" or "robot"
    notes = Column(Text, nullable=True)
    status = Column(String, default="분석 중")  # "분석 중" or "분석 완료"
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Analysis results
    transcription = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)
    intent = Column(String, nullable=True)  # "요청", "부르기", "모방"
    syllable_combinations = Column(Integer, default=0)
    meaningful_attempts = Column(Integer, default=0)
    new_words = Column(Text, nullable=True)  # JSON string of new words
    
    # Relationships
    user = relationship("User", back_populates="audio_samples")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String, unique=True, index=True)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_revoked = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User")

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String)
    message = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    read = Column(Boolean, default=False)

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
