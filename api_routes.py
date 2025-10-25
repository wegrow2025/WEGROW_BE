from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import json
import os
import tempfile
import base64

from database import get_db, User, AudioSample, UserSettings, Notification
from models import *
from auth import get_current_user, get_password_hash, create_access_token
from ai_analyzer import ai_analyzer

# API 라우터
api_router = APIRouter()

# 1. 사용자 관리 API
@api_router.post("/auth/register", response_model=Token)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """사용자 회원가입"""
    # 이메일 중복 확인
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered."
        )
    
    # 사용자 생성
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        child_age_months=user_data.child_age
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 사용자 설정 생성
    user_settings = UserSettings(user_id=user.id)
    db.add(user_settings)
    db.commit()
    
    # 토큰 생성
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@api_router.post("/auth/login", response_model=Token)
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """사용자 로그인"""
    from auth import authenticate_user
    
    user = authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@api_router.put("/user/profile")
async def update_profile(
    profile_data: UserProfile,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """사용자 프로필 업데이트"""
    if profile_data.email:
        # 이메일 중복 확인
        existing_user = db.query(User).filter(
            User.email == profile_data.email,
            User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use."
            )
        current_user.email = profile_data.email
    
    if profile_data.child_age:
        current_user.child_age_months = profile_data.child_age
    
    if profile_data.password:
        current_user.hashed_password = get_password_hash(profile_data.password)
    
    db.commit()
    return {"message": "Profile updated successfully."}

# 2. 음성 데이터 관리 API
@api_router.post("/audio/upload")
async def upload_audio(
    audio_file: UploadFile = File(...),
    duration: float = Query(...),
    source: str = Query(...),
    notes: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """음성 파일 업로드"""
    # 파일 형식 확인
    allowed_extensions = ['.mp3', '.wav', '.m4a']
    file_extension = os.path.splitext(audio_file.filename)[1].lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Only MP3, WAV, M4A are supported."
        )
    
    # 임시 파일로 저장
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
        content = await audio_file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name
    
    # 오디오 샘플 생성
    audio_sample = AudioSample(
        user_id=current_user.id,
        file_path=temp_file_path,
        duration=duration,
        source=source,
        notes=notes,
        status="분석 중"
    )
    db.add(audio_sample)
    db.commit()
    db.refresh(audio_sample)
    
    # 백그라운드에서 AI 분석 실행
    await analyze_audio_background(audio_sample.id, temp_file_path, current_user.child_age_months)
    
    return {"message": "Audio file uploaded successfully.", "sample_id": audio_sample.id}

@api_router.get("/audio/samples", response_model=AudioSampleList)
async def get_audio_samples(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """음성 샘플 목록 조회"""
    samples = db.query(AudioSample).filter(AudioSample.user_id == current_user.id).all()
    
    sample_list = []
    for sample in samples:
        sample_list.append(AudioSample(
            id=sample.id,
            timestamp=sample.created_at,
            duration=sample.duration,
            source=sample.source,
            status=sample.status,
            notes=sample.notes
        ))
    
    return AudioSampleList(samples=sample_list)

@api_router.delete("/audio/samples/{sample_id}")
async def delete_audio_sample(
    sample_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """음성 샘플 삭제"""
    sample = db.query(AudioSample).filter(
        AudioSample.id == sample_id,
        AudioSample.user_id == current_user.id
    ).first()
    
    if not sample:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio sample not found."
        )
    
    # 파일 삭제
    if os.path.exists(sample.file_path):
        os.remove(sample.file_path)
    
    db.delete(sample)
    db.commit()
    
    return {"message": "Audio sample deleted successfully."}

@api_router.post("/audio/samples/{sample_id}/reanalyze")
async def reanalyze_audio_sample(
    sample_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """음성 샘플 재분석"""
    sample = db.query(AudioSample).filter(
        AudioSample.id == sample_id,
        AudioSample.user_id == current_user.id
    ).first()
    
    if not sample:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio sample not found."
        )
    
    # 재분석 실행
    await analyze_audio_background(sample_id, sample.file_path, current_user.child_age_months)
    
    return {"message": "Reanalysis started."}

# 3. 일일 리포트 API
@api_router.get("/dashboard/daily-report", response_model=DailyReport)
async def get_daily_report(
    date: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """일일 리포트 조회"""
    if date:
        target_date = datetime.fromisoformat(date)
    else:
        target_date = datetime.now().date()
    
    # 당일 데이터
    today_samples = db.query(AudioSample).filter(
        AudioSample.user_id == current_user.id,
        AudioSample.created_at >= target_date,
        AudioSample.created_at < target_date + timedelta(days=1)
    ).all()
    
    # 전일 데이터
    yesterday = target_date - timedelta(days=1)
    yesterday_samples = db.query(AudioSample).filter(
        AudioSample.user_id == current_user.id,
        AudioSample.created_at >= yesterday,
        AudioSample.created_at < target_date
    ).all()
    
    # 통계 계산
    vocalizations = len(today_samples)
    syllable_combinations = sum(sample.syllable_combinations for sample in today_samples)
    meaningful_attempts = sum(sample.meaningful_attempts for sample in today_samples)
    new_words = sum(len(json.loads(sample.new_words or "[]")) for sample in today_samples)
    
    # 전일 비교 데이터
    previous_day = {
        "vocalizations": len(yesterday_samples),
        "syllable_combinations": sum(sample.syllable_combinations for sample in yesterday_samples),
        "meaningful_attempts": sum(sample.meaningful_attempts for sample in yesterday_samples),
        "new_words": sum(len(json.loads(sample.new_words or "[]")) for sample in yesterday_samples)
    }
    
    return DailyReport(
        vocalizations=vocalizations,
        syllable_combinations=syllable_combinations,
        meaningful_attempts=meaningful_attempts,
        new_words=new_words,
        previous_day=previous_day
    )

@api_router.get("/dashboard/age-comparison", response_model=AgeComparison)
async def get_age_comparison(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """월령별 비교 데이터"""
    # 최근 7일 데이터
    week_ago = datetime.now() - timedelta(days=7)
    recent_samples = db.query(AudioSample).filter(
        AudioSample.user_id == current_user.id,
        AudioSample.created_at >= week_ago,
        AudioSample.status == "분석 완료"
    ).all()
    
    # 점수 계산 (예시)
    total_samples = len(recent_samples)
    if total_samples == 0:
        return AgeComparison(
            vocalization_score=0.0,
            word_understanding_score=0.0,
            communication_score=0.0
        )
    
    # 발성 점수 (옹알이 수 기반)
    vocalization_score = min(100.0, (total_samples / 10) * 100)
    
    # 단어 이해 점수 (의미 있는 시도 기반)
    meaningful_total = sum(sample.meaningful_attempts for sample in recent_samples)
    word_understanding_score = min(100.0, (meaningful_total / 5) * 100)
    
    # 의사소통 점수 (전체적인 상호작용 기반)
    communication_score = (vocalization_score + word_understanding_score) / 2
    
    return AgeComparison(
        vocalization_score=vocalization_score,
        word_understanding_score=word_understanding_score,
        communication_score=communication_score
    )

# 4. 타임라인 API
@api_router.get("/timeline", response_model=Timeline)
async def get_timeline(
    date: Optional[str] = Query(None),
    intent: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """타임라인 조회"""
    query = db.query(AudioSample).filter(AudioSample.user_id == current_user.id)
    
    if date:
        target_date = datetime.fromisoformat(date)
        query = query.filter(
            AudioSample.created_at >= target_date,
            AudioSample.created_at < target_date + timedelta(days=1)
        )
    
    if intent:
        query = query.filter(AudioSample.intent == intent)
    
    samples = query.order_by(AudioSample.created_at.desc()).all()
    
    timeline_items = []
    for sample in samples:
        timeline_items.append(TimelineItem(
            timestamp=sample.created_at,
            child_speech=sample.transcription or "",
            intent=sample.intent or "",
            parent_suggestion="아이의 발화에 긍정적으로 반응해주세요."
        ))
    
    return Timeline(timeline=timeline_items)

# 5. 성장 분석 API
@api_router.get("/growth/analysis", response_model=GrowthAnalysis)
async def get_growth_analysis(
    period: str = Query("week"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """성장 분석 조회"""
    if period == "week":
        days = 7
    else:  # month
        days = 30
    
    start_date = datetime.now() - timedelta(days=days)
    previous_start = start_date - timedelta(days=days)
    
    # 현재 기간 데이터
    current_samples = db.query(AudioSample).filter(
        AudioSample.user_id == current_user.id,
        AudioSample.created_at >= start_date,
        AudioSample.status == "분석 완료"
    ).all()
    
    # 이전 기간 데이터
    previous_samples = db.query(AudioSample).filter(
        AudioSample.user_id == current_user.id,
        AudioSample.created_at >= previous_start,
        AudioSample.created_at < start_date,
        AudioSample.status == "분석 완료"
    ).all()
    
    # 성장률 계산
    current_syllables = sum(sample.syllable_combinations for sample in current_samples)
    previous_syllables = sum(sample.syllable_combinations for sample in previous_samples)
    syllable_growth = f"+{((current_syllables - previous_syllables) / max(previous_syllables, 1)) * 100:.0f}%"
    
    current_meaningful = sum(sample.meaningful_attempts for sample in current_samples)
    previous_meaningful = sum(sample.meaningful_attempts for sample in previous_samples)
    meaningful_growth = f"+{((current_meaningful - previous_meaningful) / max(previous_meaningful, 1)) * 100:.0f}%"
    
    # 하이라이트 생성
    highlights = f"이번 {period} 동안 {len(current_samples)}개의 음성 샘플을 수집했습니다."
    
    return GrowthAnalysis(
        syllable_growth=syllable_growth,
        meaningful_growth=meaningful_growth,
        total_interactions=len(current_samples),
        highlights=highlights,
        age_comparison={"percentile": 75}
    )

# 6. 팁 & 코칭 API
@api_router.get("/tips", response_model=TipList)
async def get_tips(
    level: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """팁 목록 조회"""
    # 발달 단계에 따른 팁 생성
    development_stage = ai_analyzer.get_development_stage(current_user.child_age_months)
    
    tips = []
    if development_stage == "옹알이":
        tips = [
            {
                "id": 1,
                "level": "옹알이",
                "scenario": "아이가 '까까'라고 옹알이할 때",
                "parent_response": "까까, 맞아! 정말 좋은 소리야!",
                "explanation": "아이의 옹알이를 그대로 따라해주세요. 이는 언어 발달의 첫 단계입니다."
            }
        ]
    elif development_stage == "단어_시작":
        tips = [
            {
                "id": 2,
                "level": "단어 시작",
                "scenario": "아이가 '마마'라고 말할 때",
                "parent_response": "엄마, 맞아! 엄마가 여기 있어.",
                "explanation": "부정확한 발음을 정확한 단어로 교정해주세요."
            }
        ]
    
    return TipList(tips=[Tip(**tip) for tip in tips])

# 7. 설정 API
@api_router.get("/settings", response_model=Settings)
async def get_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """설정 조회"""
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    if not settings:
        # 기본 설정 생성
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return Settings(
        recording_collection=settings.recording_collection,
        analysis_usage=settings.analysis_usage,
        coaching_recommendations=settings.coaching_recommendations,
        notifications_enabled=settings.notifications_enabled,
        email_reports=settings.email_reports
    )

@api_router.put("/settings")
async def update_settings(
    settings_data: Settings,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """설정 업데이트"""
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)
    
    settings.recording_collection = settings_data.recording_collection
    settings.analysis_usage = settings_data.analysis_usage
    settings.coaching_recommendations = settings_data.coaching_recommendations
    settings.notifications_enabled = settings_data.notifications_enabled
    settings.email_reports = settings_data.email_reports
    
    db.commit()
    return {"message": "Settings updated successfully."}

# 8. 통계 API
@api_router.get("/stats/overview", response_model=StatsOverview)
async def get_stats_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """통계 개요 조회"""
    robot_samples = db.query(AudioSample).filter(
        AudioSample.user_id == current_user.id,
        AudioSample.source == "robot"
    ).count()
    
    parent_samples = db.query(AudioSample).filter(
        AudioSample.user_id == current_user.id,
        AudioSample.source == "parent"
    ).count()
    
    analyzed_samples = db.query(AudioSample).filter(
        AudioSample.user_id == current_user.id,
        AudioSample.status == "분석 완료"
    ).count()
    
    return StatsOverview(
        robot_samples=robot_samples,
        parent_samples=parent_samples,
        analyzed_samples=analyzed_samples
    )

# 백그라운드 작업
async def analyze_audio_background(sample_id: int, file_path: str, child_age_months: int):
    """백그라운드에서 오디오 분석"""
    try:
        # 오디오 파일을 base64로 인코딩
        with open(file_path, 'rb') as f:
            audio_bytes = f.read()
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        # AI 분석
        analysis_result = ai_analyzer.analyze_audio(audio_base64, child_age_months, 0)
        
        # 데이터베이스 업데이트
        from database import SessionLocal
        db = SessionLocal()
        try:
            sample = db.query(AudioSample).filter(AudioSample.id == sample_id).first()
            if sample:
                sample.status = "분석 완료"
                sample.transcription = analysis_result.get("transcription", "")
                sample.confidence = analysis_result.get("confidence", 0)
                sample.intent = analysis_result.get("intent", "")
                sample.syllable_combinations = analysis_result.get("syllable_combinations", 0)
                sample.meaningful_attempts = analysis_result.get("meaningful_attempts", 0)
                sample.new_words = json.dumps(analysis_result.get("new_words", []))
                db.commit()
        finally:
            db.close()
            
    except Exception as e:
        print(f"Error in background analysis: {e}")
