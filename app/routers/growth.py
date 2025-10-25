from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import List, Dict, Any
from app.database import get_db
from app.models import User, AudioSample, WeeklyReport
from app.schemas import WeeklyReport as WeeklyReportSchema, WeeklyReportBase
from app.auth import get_current_active_user

router = APIRouter(prefix="/api/growth", tags=["growth"])


@router.get("/weekly-report", response_model=WeeklyReportBase)
async def get_weekly_report(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """주간 성장 리포트 조회"""
    # 이번 주 시작일 계산
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    week_start_str = week_start.strftime("%Y-%m-%d")
    
    # 이번 주 데이터 수집
    week_samples = db.query(AudioSample).filter(
        AudioSample.user_id == current_user.id,
        func.date(AudioSample.created_at) >= week_start_str
    ).all()
    
    # 실제 분석 데이터 기반 지표 계산
    all_transcriptions = [s.transcription for s in week_samples if s.transcription]
    vocabulary_count = len(set(all_transcriptions))
    
    # 두 단어 이상 문장 분석
    two_word_sentences = 0
    for sample in week_samples:
        if sample.transcription:
            words = sample.transcription.split()
            if len(words) >= 2:
                two_word_sentences += 1
    
    # 대화 지속 시간 (실제 오디오 길이 기반)
    conversation_duration = sum([s.duration for s in week_samples if s.duration]) or 0
    
    # 의도별 분석
    intent_analysis = {}
    for sample in week_samples:
        if sample.intent:
            intent_analysis[sample.intent] = intent_analysis.get(sample.intent, 0) + 1
    
    # 발달 단계별 분석
    stage_analysis = {}
    for sample in week_samples:
        if sample.language_development_stage:
            stage_analysis[sample.language_development_stage] = stage_analysis.get(sample.language_development_stage, 0) + 1
    
    # 감정 분석
    emotion_analysis = {}
    for sample in week_samples:
        if sample.emotion:
            emotion_analysis[sample.emotion] = emotion_analysis.get(sample.emotion, 0) + 1
    
    # 실제 데이터 기반 진행 지표
    age_targets = {
        18: {"vocabulary": 15, "sentences": 2},
        24: {"vocabulary": 50, "sentences": 10},
        30: {"vocabulary": 200, "sentences": 20}
    }
    
    # 아이 나이에 맞는 목표 설정
    child_age = current_user.child_age
    if child_age < 24:
        target_vocab = age_targets[18]["vocabulary"]
        target_sentences = age_targets[18]["sentences"]
    elif child_age < 30:
        target_vocab = age_targets[24]["vocabulary"]
        target_sentences = age_targets[24]["sentences"]
    else:
        target_vocab = age_targets[30]["vocabulary"]
        target_sentences = age_targets[30]["sentences"]
    
    progress_metrics = [
        {
            "label": "활용 어휘",
            "value": f"{vocabulary_count} 단어",
            "helper": f"목표 {target_vocab} 단어",
            "trend": f"이번 주에 {vocabulary_count}개 단어를 사용했어요!",
            "progress": min(100, (vocabulary_count / target_vocab) * 100),
            "color": "#E17AA4"
        },
        {
            "label": "두 단어 말하기",
            "value": f"주간 {two_word_sentences}회",
            "helper": "자연스러운 말 잇기",
            "trend": f"이번 주에 {two_word_sentences}번의 두 단어 문장을 말했어요!",
            "progress": min(100, (two_word_sentences / target_sentences) * 100),
            "color": "#A678E3"
        }
    ]
    
    # 의도별 분석 지표 추가
    if intent_analysis:
        main_intent = max(intent_analysis, key=intent_analysis.get)
        progress_metrics.append({
            "label": "주요 의도",
            "value": f"{main_intent} ({intent_analysis[main_intent]}회)",
            "helper": "가장 많이 사용한 의도",
            "trend": f"'{main_intent}' 의도로 가장 많이 소통했어요!",
            "progress": 100,
            "color": "#4CAF50"
        })
    
    # 일일 순간들
    daily_moments = [
        {
            "time": "놀이 시간(블록)",
            "script": "아이: \"더!\" → 도담: \"더 쌓자. 높은 탑? 낮은 탑? 하나, 둘—올려볼까?\"",
            "focus": "반복 + 선택 질문으로 자발 발화 유도"
        }
    ]
    
    # 단계별 가이드
    stage_guides = [
        {
            "stage": "24개월 포인트",
            "color": "#A678E3",
            "summary": "50개 이상의 단어로 두 단어 문장을 말해요!",
            "actions": [
                "'무슨 색 좋아?'처럼 선택 질문으로 대화 유도하기",
                "아이의 짧은 말을 더 긴 문장으로 이어 말해주기",
                "역할놀이로 감정 단어(기뻐, 속상해 등) 알려주기"
            ],
            "example": "예: \"더 우유\" → \"우유 더 마시고 싶구나~ 컵을 두 손으로 잡아볼까?\""
        }
    ]
    
    # 추천사항
    recommendations = [
        {
            "title": "집 안 단어 탐험",
            "detail": "컵, 의자, 신발 같은 물건에 이름표를 붙여요. 도담이 읽어주면 아이가 말소리로 반응하며 배워요!",
            "tip": "이번 주엔 새로운 단어 6개를 골라 집중해볼까요?"
        }
    ]
    
    # 부모 지원
    parent_assist = [
        "오늘 도담이와 아이의 대화에서 짧은 응답 후에 대화가 자주 멈췄어요. 부모님이 아이의 말 뒤에 한 단어만 더 이어주시면, 문장 길이가 자연스럽게 늘어날 거예요.",
        "아이가 요청형 말(\"더\", \"줘\")을 자주 사용했어요. 이는 언어 이해가 빠르게 성장하는 시기예요.",
        "도담이의 관찰에 따르면, 감정 표현어('좋아', '싫어' 등) 반응이 아직 적어요."
    ]
    
    return WeeklyReportBase(
        week_start_date=week_start_str,
        vocabulary_count=vocabulary_count,
        two_word_sentences=two_word_sentences,
        conversation_duration=conversation_duration,
        progress_metrics=progress_metrics,
        daily_moments=daily_moments,
        stage_guides=stage_guides,
        recommendations=recommendations,
        parent_assist=parent_assist
    )
