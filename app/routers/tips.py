from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta
from app.database import get_db
from app.models import User, Tip, UserTipFavorite, AudioSample, TimelineItem
from app.schemas import Tip as TipSchema, TipWithFavorite
from app.auth import get_current_active_user

router = APIRouter(prefix="/api/tips", tags=["tips"])


@router.get("", response_model=dict)
async def get_tips(
    level: Optional[str] = None,
    favorites: Optional[bool] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """팁 목록 조회"""
    query = db.query(Tip).filter(Tip.is_active == True)
    
    # 발달 단계 필터
    if level:
        query = query.filter(Tip.level == level)
    
    tips = query.all()
    
    # 즐겨찾기 정보 추가
    user_favorites = db.query(UserTipFavorite).filter(
        UserTipFavorite.user_id == current_user.id
    ).all()
    favorite_tip_ids = {f.tip_id for f in user_favorites}
    
    # 즐겨찾기 필터
    if favorites is not None:
        if favorites:
            tips = [tip for tip in tips if tip.id in favorite_tip_ids]
        else:
            tips = [tip for tip in tips if tip.id not in favorite_tip_ids]
    
    # 데이터 변환
    tip_data = []
    for tip in tips:
        tip_data.append({
            "id": tip.id,
            "level": tip.level,
            "scenario": tip.scenario,
            "parent_response": tip.parent_response,
            "explanation": tip.explanation,
            "is_favorite": tip.id in favorite_tip_ids
        })
    
    # 사용자 분석 데이터 기반 맞춤형 추천
    user_analysis = await get_user_analysis_data(current_user.id, db)
    
    # 교육 콘텐츠
    education_content = {
        "modeling": "아이의 발화를 바로 수정하지 마세요. 대신 아이가 말한 것을 더 완성된 형태로 자연스럽게 다시 말해주세요.",
        "expansion": "아이의 한 단어에 의미 있는 단어들을 더해서 더 긴 표현으로 확장해 들려주세요.",
        "repetition": "같은 개념을 여러 단어와 상황으로 반복 노출하면 학습이 강화됩니다."
    }
    
    # 맞춤형 추천 팁
    personalized_tips = get_personalized_tips(user_analysis, tip_data)
    
    return {
        "tips": tip_data,
        "personalized_tips": personalized_tips,
        "user_analysis": user_analysis,
        "education_content": education_content
    }


@router.post("/{tip_id}/favorite", response_model=dict)
async def toggle_tip_favorite(
    tip_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """팁 즐겨찾기 토글"""
    # 팁 존재 확인
    tip = db.query(Tip).filter(Tip.id == tip_id).first()
    if not tip:
        raise HTTPException(status_code=404, detail="팁을 찾을 수 없습니다.")
    
    # 기존 즐겨찾기 확인
    existing_favorite = db.query(UserTipFavorite).filter(
        UserTipFavorite.user_id == current_user.id,
        UserTipFavorite.tip_id == tip_id
    ).first()
    
    if existing_favorite:
        # 즐겨찾기 제거
        db.delete(existing_favorite)
        is_favorite = False
    else:
        # 즐겨찾기 추가
        new_favorite = UserTipFavorite(
            user_id=current_user.id,
            tip_id=tip_id
        )
        db.add(new_favorite)
        is_favorite = True
    
    db.commit()
    
    return {
        "success": True,
        "is_favorite": is_favorite
    }


async def get_user_analysis_data(user_id: str, db: Session) -> dict:
    """사용자 분석 데이터 조회"""
    # 최근 7일간의 데이터 수집
    week_ago = datetime.now() - timedelta(days=7)
    
    recent_samples = db.query(AudioSample).filter(
        AudioSample.user_id == user_id,
        AudioSample.created_at >= week_ago
    ).all()
    
    # 의도별 분석
    intent_analysis = {}
    for sample in recent_samples:
        if sample.intent:
            intent_analysis[sample.intent] = intent_analysis.get(sample.intent, 0) + 1
    
    # 발달 단계별 분석
    stage_analysis = {}
    for sample in recent_samples:
        if sample.language_development_stage:
            stage_analysis[sample.language_development_stage] = stage_analysis.get(sample.language_development_stage, 0) + 1
    
    # 감정 분석
    emotion_analysis = {}
    for sample in recent_samples:
        if sample.emotion:
            emotion_analysis[sample.emotion] = emotion_analysis.get(sample.emotion, 0) + 1
    
    # 어휘 분석
    all_words = []
    for sample in recent_samples:
        if sample.transcription:
            words = sample.transcription.split()
            all_words.extend(words)
    
    unique_words = len(set(all_words))
    word_frequency = {}
    for word in all_words:
        word_frequency[word] = word_frequency.get(word, 0) + 1
    
    # 가장 많이 사용된 단어
    most_used_words = sorted(word_frequency.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        "total_samples": len(recent_samples),
        "intent_distribution": intent_analysis,
        "stage_distribution": stage_analysis,
        "emotion_distribution": emotion_analysis,
        "vocabulary_count": unique_words,
        "most_used_words": most_used_words,
        "analysis_period": "최근 7일"
    }


def get_personalized_tips(user_analysis: dict, all_tips: list) -> list:
    """사용자 분석 데이터 기반 맞춤형 팁 추천"""
    personalized_tips = []
    
    # 의도별 맞춤 팁
    if user_analysis["intent_distribution"]:
        main_intent = max(user_analysis["intent_distribution"], key=user_analysis["intent_distribution"].get)
        
        # 해당 의도와 관련된 팁 찾기
        intent_related_tips = []
        for tip in all_tips:
            if main_intent in tip["scenario"] or main_intent in tip["explanation"]:
                intent_related_tips.append({
                    **tip,
                    "recommendation_reason": f"'{main_intent}' 의도를 {user_analysis['intent_distribution'][main_intent]}번 사용했어요"
                })
        
        personalized_tips.extend(intent_related_tips[:2])  # 상위 2개만
    
    # 발달 단계별 맞춤 팁
    if user_analysis["stage_distribution"]:
        main_stage = max(user_analysis["stage_distribution"], key=user_analysis["stage_distribution"].get)
        
        stage_related_tips = []
        for tip in all_tips:
            if main_stage in tip["level"]:
                stage_related_tips.append({
                    **tip,
                    "recommendation_reason": f"현재 '{main_stage}' 단계에 있어요"
                })
        
        personalized_tips.extend(stage_related_tips[:2])  # 상위 2개만
    
    # 어휘 발달 맞춤 팁
    if user_analysis["vocabulary_count"] < 20:  # 어휘가 부족한 경우
        vocabulary_tips = []
        for tip in all_tips:
            if "어휘" in tip["explanation"] or "단어" in tip["explanation"]:
                vocabulary_tips.append({
                    **tip,
                    "recommendation_reason": f"현재 {user_analysis['vocabulary_count']}개 단어를 사용하고 있어요"
                })
        
        personalized_tips.extend(vocabulary_tips[:1])  # 1개만
    
    return personalized_tips[:5]  # 최대 5개 추천
