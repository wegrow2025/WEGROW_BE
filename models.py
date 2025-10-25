from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# 인증 관련 모델
class UserRegister(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    password: str
    child_age: int = Field(alias="childAge")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int

class TokenRefresh(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int

# 사용자 프로필 모델
class UserProfile(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    child_age: Optional[int] = None
    password: Optional[str] = None

# 오디오 샘플 모델
class AudioUpload(BaseModel):
    duration: float
    source: str  # "parent" or "robot"
    notes: Optional[str] = None

class AudioSampleResponse(BaseModel):
    id: int
    timestamp: datetime
    duration: float
    source: str
    status: str
    notes: Optional[str] = None

class AudioSampleList(BaseModel):
    samples: List[AudioSampleResponse]

# 일일 리포트 모델
class DailyReport(BaseModel):
    vocalizations: int
    syllable_combinations: int = Field(alias="syllableCombinations")
    meaningful_attempts: int = Field(alias="meaningfulAttempts")
    new_words: int = Field(alias="newWords")
    previous_day: Optional[Dict[str, Any]] = Field(alias="previousDay", default=None)

class AgeComparison(BaseModel):
    vocalization_score: float = Field(alias="vocalizationScore")
    word_understanding_score: float = Field(alias="wordUnderstandingScore")
    communication_score: float = Field(alias="communicationScore")

# 타임라인 모델
class TimelineItem(BaseModel):
    timestamp: datetime
    child_speech: str = Field(alias="childSpeech")
    intent: str
    parent_suggestion: str = Field(alias="parentSuggestion")

class Timeline(BaseModel):
    timeline: List[TimelineItem]

# 성장 분석 모델
class GrowthAnalysis(BaseModel):
    syllable_growth: str = Field(alias="syllableGrowth")
    meaningful_growth: str = Field(alias="meaningfulGrowth")
    total_interactions: int = Field(alias="totalInteractions")
    highlights: str
    age_comparison: Dict[str, Any] = Field(alias="ageComparison")

# 팁 & 코칭 모델
class Tip(BaseModel):
    id: int
    level: str
    scenario: str
    parent_response: str = Field(alias="parentResponse")
    explanation: str

class TipList(BaseModel):
    tips: List[Tip]

# 설정 모델
class Settings(BaseModel):
    recording_collection: bool = Field(alias="recordingCollection")
    analysis_usage: bool = Field(alias="analysisUsage")
    coaching_recommendations: bool = Field(alias="coachingRecommendations")
    notifications_enabled: bool = Field(alias="notificationsEnabled")
    email_reports: bool = Field(alias="emailReports")

# 알림 모델
class Notification(BaseModel):
    type: str
    message: str
    timestamp: datetime

class NotificationList(BaseModel):
    notifications: List[Notification]

# 통계 모델
class StatsOverview(BaseModel):
    robot_samples: int = Field(alias="robotSamples")
    parent_samples: int = Field(alias="parentSamples")
    analyzed_samples: int = Field(alias="analyzedSamples")

# 에러 모델
class ErrorResponse(BaseModel):
    type: str
    code: str
    message: str
    timestamp: int
