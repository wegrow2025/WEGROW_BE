from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from app.database import get_db
from app.models import User, AudioSample, DailyReport, TimelineItem
from app.schemas import DashboardDailyReport, AgeComparison
from app.auth import get_current_active_user

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/daily-report", response_model=DashboardDailyReport)
async def get_daily_report(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """일일 리포트 조회"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 오늘의 오디오 샘플 통계
    today_samples = db.query(AudioSample).filter(
        AudioSample.user_id == current_user.id,
        func.date(AudioSample.created_at) == today
    ).all()
    
    # 어제의 발화 수
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    yesterday_samples = db.query(AudioSample).filter(
        AudioSample.user_id == current_user.id,
        func.date(AudioSample.created_at) == yesterday
    ).count()
    
    # 실제 분석 데이터 기반 통계 계산
    vocalizations = len(today_samples)
    
    # 음절 조합 분석 (실제 전사 데이터 기반)
    syllable_combinations = 0
    for sample in today_samples:
        if sample.transcription:
            words = sample.transcription.split()
            if len(words) >= 2:
                syllable_combinations += 1
    
    # 의미 있는 시도 분석 (실제 의도 분석 기반)
    meaningful_attempts = 0
    intent_distribution = {}
    for sample in today_samples:
        if sample.intent and sample.intent != "음성 실험":
            meaningful_attempts += 1
            intent_distribution[sample.intent] = intent_distribution.get(sample.intent, 0) + 1
    
    # 새로운 단어 분석 (실제 전사 데이터 기반)
    unique_words = set()
    for sample in today_samples:
        if sample.transcription:
            words = sample.transcription.split()
            unique_words.update(words)
    new_words = len(unique_words)
    
    # 발달 단계 분석
    development_stages = {}
    for sample in today_samples:
        if sample.language_development_stage:
            development_stages[sample.language_development_stage] = development_stages.get(sample.language_development_stage, 0) + 1
    
    # 감정 분석
    emotion_distribution = {}
    for sample in today_samples:
        if sample.emotion:
            emotion_distribution[sample.emotion] = emotion_distribution.get(sample.emotion, 0) + 1
    
    # 요약 생성 (실제 데이터 기반)
    if vocalizations > yesterday_samples:
        improvement = vocalizations - yesterday_samples
        summary = f"좋은 소식! 아이가 오늘 {vocalizations}번의 발화를 했어요. 어제보다 {improvement}번 더 많이 말했어요."
    elif vocalizations == yesterday_samples:
        summary = f"아이가 오늘 {vocalizations}번의 발화를 했어요. 어제와 같은 수준이에요."
    else:
        summary = f"아이가 오늘 {vocalizations}번의 발화를 했어요."
    
    # 발달 단계별 인사이트 추가
    if development_stages:
        main_stage = max(development_stages, key=development_stages.get)
        summary += f" 현재 주요 발달 단계는 '{main_stage}'입니다."
    
    # 권장 응답 (실제 분석 결과 기반)
    if meaningful_attempts > 0:
        main_intent = max(intent_distribution, key=intent_distribution.get) if intent_distribution else "의사소통"
        recommended_response = f"아이가 '{main_intent}' 의도로 {meaningful_attempts}번의 의미 있는 시도를 했어요. 이 의도를 자연스럽게 확장해서 대화를 이어가세요."
    else:
        recommended_response = "아이와 더 많은 대화를 나누어보세요. 간단한 단어부터 시작해보세요."
    
    return DashboardDailyReport(
        vocalizations=vocalizations,
        syllable_combinations=syllable_combinations,
        meaningful_attempts=meaningful_attempts,
        new_words=new_words,
        previous_day={"vocalizations": yesterday_samples},
        summary=summary,
        recommended_response=recommended_response,
        date=today
    )


@router.get("/age-comparison", response_model=AgeComparison)
async def get_age_comparison(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """월령별 비교 데이터 조회"""
    # 최근 7일간의 데이터 수집
    week_ago = datetime.now() - timedelta(days=7)
    
    recent_samples = db.query(AudioSample).filter(
        AudioSample.user_id == current_user.id,
        AudioSample.created_at >= week_ago
    ).all()
    
    # 점수 계산 (간단한 예시)
    total_samples = len(recent_samples)
    meaningful_samples = len([s for s in recent_samples if s.intent and s.intent != "음성 실험"])
    
    # 점수 계산 (0-100)
    vocalization_score = min(100, (total_samples / 7) * 10)  # 일일 평균 기준
    word_understanding_score = min(100, (meaningful_samples / max(total_samples, 1)) * 100)
    communication_score = (vocalization_score + word_understanding_score) / 2
    
    # 해석 생성
    if communication_score >= 80:
        interpretation = "우리 아이는 대부분의 영역에서 또래 평균과 함께 성장 중입니다. 특히 음성 표현에 강점이 있습니다."
    elif communication_score >= 60:
        interpretation = "우리 아이는 평균적인 발달 속도를 보이고 있습니다. 꾸준한 상호작용으로 더욱 발전할 수 있어요."
    else:
        interpretation = "아이의 언어 발달을 위해 더 많은 대화와 상호작용이 필요합니다."
    
    return AgeComparison(
        vocalization_score=int(vocalization_score),
        word_understanding_score=int(word_understanding_score),
        communication_score=int(communication_score),
        interpretation=interpretation,
        child_age=current_user.child_age
    )
