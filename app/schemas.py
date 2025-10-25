from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# 사용자 관련 스키마
class UserBase(BaseModel):
    email: EmailStr
    name: str
    child_age: int = Field(alias="childAge")

    class Config:
        populate_by_name = True


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    child_age: Optional[int] = None
    password: Optional[str] = None


class User(UserBase):
    id: str
    created_at: datetime
    last_login_at: Optional[datetime] = None
    is_active: bool

    class Config:
        from_attributes = True


# 인증 관련 스키마
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


# 설정 관련 스키마
class UserSettingsBase(BaseModel):
    recording_collection: bool = True
    analysis_usage: bool = True
    coaching_recommendations: bool = True
    notifications_enabled: bool = True
    email_reports: bool = True
    data_retention_days: int = 365
    language: str = "ko-KR"
    timezone: str = "Asia/Seoul"
    audio_recording: bool = True
    research_participation: bool = False
    third_party_sharing: bool = False
    anonymized_research: bool = False
    family_sharing: bool = False


class UserSettings(UserSettingsBase):
    id: int
    user_id: str

    class Config:
        from_attributes = True


# 오디오 샘플 관련 스키마
class AudioSampleBase(BaseModel):
    duration: float
    source: str
    notes: Optional[str] = None


class AudioSampleCreate(AudioSampleBase):
    pass


class AudioSample(AudioSampleBase):
    id: str
    user_id: str
    file_path: str
    transcription: Optional[str] = None
    intent: Optional[str] = None
    confidence: Optional[float] = None
    emotion: Optional[str] = None
    age_appropriate: Optional[bool] = None
    recommended_response: Optional[str] = None
    language_development_stage: Optional[str] = None
    created_at: datetime
    analyzed_at: Optional[datetime] = None
    status: str
    audio_url: Optional[str] = Field(None, alias="audioUrl")
    tts_audio_url: Optional[str] = Field(None, alias="ttsAudioUrl")
    analysis_result: Optional[Dict[str, Any]] = Field(None, alias="analysisResult")

    class Config:
        from_attributes = True


# 타임라인 관련 스키마
class TimelineItemBase(BaseModel):
    date: str
    time: str
    child_utterance: str
    intent: str
    parent_response: Optional[str] = None
    audio_url: Optional[str] = None
    duration: Optional[float] = None
    confidence: Optional[float] = None
    analysis_result: Optional[Dict[str, Any]] = None


class TimelineItem(TimelineItemBase):
    id: str
    user_id: str
    audio_sample_id: Optional[str] = None
    created_at: datetime
    audio_url: Optional[str] = Field(None, alias="audioUrl")

    class Config:
        from_attributes = True


# 팁 관련 스키마
class TipBase(BaseModel):
    level: str
    age_range: List[int]
    scenario: str
    parent_response: str
    explanation: str
    tags: List[str]
    effectiveness: float = 0.0


class Tip(TipBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True


class TipWithFavorite(Tip):
    is_favorite: bool = False


# 일일 리포트 관련 스키마
class DailyReportBase(BaseModel):
    date: str
    vocalizations: int = 0
    syllable_combinations: int = 0
    meaningful_attempts: int = 0
    new_words: int = 0
    previous_day_vocalizations: int = 0
    summary: Optional[str] = None
    recommended_response: Optional[str] = None
    growth_indicators: Optional[Dict[str, Any]] = None


class DailyReport(DailyReportBase):
    id: int
    user_id: str
    created_at: datetime
    syllable_combinations: int = Field(0, alias="syllableCombinations")
    meaningful_attempts: int = Field(0, alias="meaningfulAttempts")
    new_words: int = Field(0, alias="newWords")
    previous_day_vocalizations: int = Field(0, alias="previousDayVocalizations")

    class Config:
        from_attributes = True


# 주간 리포트 관련 스키마
class WeeklyReportBase(BaseModel):
    week_start_date: str
    vocabulary_count: int = 0
    two_word_sentences: int = 0
    conversation_duration: float = 0.0
    progress_metrics: Optional[List[Dict[str, Any]]] = None
    daily_moments: Optional[List[Dict[str, Any]]] = None
    stage_guides: Optional[List[Dict[str, Any]]] = None
    recommendations: Optional[List[Dict[str, Any]]] = None
    parent_assist: Optional[List[str]] = None


class WeeklyReport(WeeklyReportBase):
    id: int
    user_id: str
    created_at: datetime
    vocabulary_count: int = Field(0, alias="vocabularyCount")
    two_word_sentences: int = Field(0, alias="twoWordSentences")
    conversation_duration: float = Field(0.0, alias="conversationDuration")
    progress_metrics: Optional[List[Dict[str, Any]]] = Field(None, alias="progressMetrics")
    daily_moments: Optional[List[Dict[str, Any]]] = Field(None, alias="dailyMoments")
    stage_guides: Optional[List[Dict[str, Any]]] = Field(None, alias="stageGuides")
    parent_assist: Optional[List[str]] = Field(None, alias="parentAssist")

    class Config:
        from_attributes = True


# 대시보드 관련 스키마
class DashboardDailyReport(BaseModel):
    vocalizations: int
    syllable_combinations: int = Field(alias="syllableCombinations")
    meaningful_attempts: int = Field(alias="meaningfulAttempts")
    new_words: int = Field(alias="newWords")
    previous_day: Dict[str, int] = Field(alias="previousDay")
    summary: str
    recommended_response: str = Field(alias="recommendedResponse")
    date: str

    class Config:
        populate_by_name = True


class AgeComparison(BaseModel):
    vocalization_score: int = Field(alias="vocalizationScore")
    word_understanding_score: int = Field(alias="wordUnderstandingScore")
    communication_score: int = Field(alias="communicationScore")
    interpretation: str
    child_age: int = Field(alias="childAge")

    class Config:
        populate_by_name = True


# AI 분석 결과 스키마
class AudioAnalysisResult(BaseModel):
    transcription: str
    confidence: float
    intent: str
    emotion: str
    age_appropriate: bool = Field(alias="ageAppropriate")
    recommended_response: str = Field(alias="recommendedResponse")
    language_development_stage: str = Field(alias="languageDevelopmentStage")
    suggestions: List[str]

    class Config:
        populate_by_name = True


class GrowthMetrics(BaseModel):
    vocabulary_growth: Dict[str, Any] = Field(alias="vocabularyGrowth")
    sentence_complexity: Dict[str, Any] = Field(alias="sentenceComplexity")
    communication_attempts: Dict[str, Any] = Field(alias="communicationAttempts")

    class Config:
        populate_by_name = True


# 에러 응답 스키마
class ErrorResponse(BaseModel):
    success: bool = False
    error: Dict[str, str]
    timestamp: datetime


# 성공 응답 스키마
class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    timestamp: datetime


# API 응답용 스키마들
class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    child_age: int = Field(alias="childAge")
    created_at: Optional[datetime] = Field(None, alias="createdAt")

    class Config:
        from_attributes = True
        populate_by_name = True


class LoginResponse(BaseModel):
    success: bool = True
    user: UserResponse
    token: str


class RegisterResponse(BaseModel):
    success: bool = True
    user: UserResponse
    token: str


class AudioUploadResponse(BaseModel):
    success: bool
    sample_id: str = Field(alias="sampleId")
    status: str
    analysis_result: Optional[Dict[str, Any]] = Field(None, alias="analysisResult")
    error: Optional[str] = None

    class Config:
        populate_by_name = True


class AudioSampleResponse(BaseModel):
    id: str
    timestamp: str
    duration: float
    source: str
    status: str
    notes: str
    audio_url: str = Field(alias="audioUrl")
    tts_audio_url: Optional[str] = Field(None, alias="ttsAudioUrl")
    analysis_result: Optional[Dict[str, Any]] = Field(None, alias="analysisResult")

    class Config:
        populate_by_name = True


class AudioSamplesResponse(BaseModel):
    samples: List[AudioSampleResponse]
    statistics: Dict[str, int]


class TimelineItemResponse(BaseModel):
    id: str
    date: str
    time: str
    child_utterance: str = Field(alias="childUtterance")
    intent: str
    parent_response: Optional[str] = Field(None, alias="parentResponse")
    audio_url: Optional[str] = Field(None, alias="audioUrl")
    duration: Optional[float] = None
    confidence: Optional[float] = None

    class Config:
        populate_by_name = True


class TimelineResponse(BaseModel):
    timeline: List[TimelineItemResponse]
    total_count: int = Field(alias="totalCount")
    has_more: bool = Field(alias="hasMore")

    class Config:
        populate_by_name = True


class TipResponse(BaseModel):
    id: int
    level: str
    scenario: str
    parent_response: str = Field(alias="parentResponse")
    explanation: str
    is_favorite: bool = Field(alias="isFavorite")

    class Config:
        populate_by_name = True


class TipsResponse(BaseModel):
    tips: List[TipResponse]
    education_content: Dict[str, str] = Field(alias="educationContent")

    class Config:
        populate_by_name = True


class SettingsResponse(BaseModel):
    recording_collection: bool = Field(alias="recordingCollection")
    analysis_usage: bool = Field(alias="analysisUsage")
    coaching_recommendations: bool = Field(alias="coachingRecommendations")
    notifications_enabled: bool = Field(alias="notificationsEnabled")
    email_reports: bool = Field(alias="emailReports")
    user: Dict[str, Any]

    class Config:
        populate_by_name = True


class WeeklyReportResponse(BaseModel):
    vocabulary_count: int = Field(alias="vocabularyCount")
    two_word_sentences: int = Field(alias="twoWordSentences")
    conversation_duration: float = Field(alias="conversationDuration")
    progress_metrics: List[Dict[str, Any]] = Field(alias="progressMetrics")
    daily_moments: List[Dict[str, Any]] = Field(alias="dailyMoments")
    stage_guides: List[Dict[str, Any]] = Field(alias="stageGuides")
    recommendations: List[Dict[str, Any]]
    parent_assist: List[str] = Field(alias="parentAssist")

    class Config:
        populate_by_name = True
