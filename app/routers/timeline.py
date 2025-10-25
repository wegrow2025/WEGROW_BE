from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
from datetime import datetime, timedelta
from app.database import get_db
from app.models import User, TimelineItem, AudioSample
from app.schemas import TimelineItem as TimelineItemSchema
from app.auth import get_current_active_user

router = APIRouter(prefix="/api/timeline", tags=["timeline"])


@router.get("", response_model=dict)
async def get_timeline(
    date: Optional[str] = Query(None, description="날짜 필터 (YYYY-MM-DD)"),
    intent: Optional[str] = Query(None, description="의도 필터"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """타임라인 조회"""
    query = db.query(TimelineItem).filter(TimelineItem.user_id == current_user.id)
    
    # 날짜 필터
    if date:
        query = query.filter(TimelineItem.date == date)
    
    # 의도 필터
    if intent:
        query = query.filter(TimelineItem.intent == intent)
    
    # 최신순 정렬
    timeline_items = query.order_by(desc(TimelineItem.created_at)).all()
    
    # 통계 계산
    total_items = len(timeline_items)
    intent_counts = {}
    daily_counts = {}
    
    for item in timeline_items:
        # 의도별 통계
        intent_counts[item.intent] = intent_counts.get(item.intent, 0) + 1
        
        # 일별 통계
        daily_counts[item.date] = daily_counts.get(item.date, 0) + 1
    
    # 데이터 변환
    timeline_data = []
    for item in timeline_items:
        # 오디오 샘플 정보 가져오기
        audio_sample = None
        if item.audio_sample_id:
            audio_sample = db.query(AudioSample).filter(
                AudioSample.id == item.audio_sample_id
            ).first()
        
        timeline_data.append({
            "id": item.id,
            "date": item.date,
            "time": item.time,
            "child_utterance": item.child_utterance,
            "intent": item.intent,
            "parent_response": item.parent_response,
            "audio_url": item.audio_url,
            "tts_audio_url": f"/api/audio/samples/{item.audio_sample_id}/tts" if audio_sample and audio_sample.tts_audio_path else None,
            "duration": item.duration,
            "confidence": item.confidence,
            "analysis_result": item.analysis_result,
            "language_development_stage": audio_sample.language_development_stage if audio_sample else None,
            "emotion": audio_sample.emotion if audio_sample else None,
            "age_appropriate": audio_sample.age_appropriate if audio_sample else None
        })
    
    return {
        "timeline": timeline_data,
        "total_count": total_items,
        "statistics": {
            "intent_distribution": intent_counts,
            "daily_activity": daily_counts,
            "total_days": len(daily_counts),
            "average_daily_utterances": round(total_items / max(len(daily_counts), 1), 2)
        },
        "has_more": False  # 페이지네이션 구현 시 수정
    }
