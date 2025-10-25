from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

# 인증 관련 모델
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    child_age: int

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# 사용자 프로필 모델
class UserProfile(BaseModel):
    email: Optional[EmailStr] = None
    child_age: Optional[int] = None
    password: Optional[str] = None

# 오디오 샘플 모델
class AudioUpload(BaseModel):
    duration: float
    source: str  # "parent" or "robot"
    notes: Optional[str] = None

class AudioSample(BaseModel):
    id: int
    timestamp: datetime
    duration: float
    source: str
    status: str
    notes: Optional[str] = None

class AudioSampleList(BaseModel):
    samples: List[AudioSample]

# 일일 리포트 모델
class DailyReport(BaseModel):
    vocalizations: int
    syllable_combinations: int
    meaningful_attempts: int
    new_words: int
    previous_day: Optional[Dict[str, Any]] = None

class AgeComparison(BaseModel):
    vocalization_score: float
    word_understanding_score: float
    communication_score: float

# 타임라인 모델
class TimelineItem(BaseModel):
    timestamp: datetime
    child_speech: str
    intent: str
    parent_suggestion: str

class Timeline(BaseModel):
    timeline: List[TimelineItem]

# 성장 분석 모델
class GrowthAnalysis(BaseModel):
    syllable_growth: str
    meaningful_growth: str
    total_interactions: int
    highlights: str
    age_comparison: Dict[str, Any]

# 팁 & 코칭 모델
class Tip(BaseModel):
    id: int
    level: str
    scenario: str
    parent_response: str
    explanation: str

class TipList(BaseModel):
    tips: List[Tip]

# 설정 모델
class Settings(BaseModel):
    recording_collection: bool
    analysis_usage: bool
    coaching_recommendations: bool
    notifications_enabled: bool
    email_reports: bool

# 알림 모델
class Notification(BaseModel):
    type: str
    message: str
    timestamp: datetime

class NotificationList(BaseModel):
    notifications: List[Notification]

# 통계 모델
class StatsOverview(BaseModel):
    robot_samples: int
    parent_samples: int
    analyzed_samples: int

# 에러 모델
class ErrorResponse(BaseModel):
    type: str
    code: str
    message: str
    timestamp: int
