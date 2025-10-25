from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
import os
import uuid
from datetime import datetime
from app.database import get_db
from app.models import User, AudioSample, TimelineItem
from app.schemas import AudioSample as AudioSampleSchema, TimelineItem as TimelineItemSchema
from app.auth import get_current_active_user
from app.config import settings
from app.services.ai_analysis import ai_analysis_service
from app.services.tts_service import tts_service

router = APIRouter(prefix="/api/audio", tags=["audio"])


@router.post("/upload", response_model=dict)
async def upload_audio(
    audio_file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """오디오 파일 업로드"""
    # 파일 크기 확인
    if audio_file.size > settings.max_file_size:
        raise HTTPException(
            status_code=413,
            detail="파일 크기가 너무 큽니다."
        )
    
    # 파일 형식 확인
    allowed_extensions = ['.mp3', '.wav', '.m4a']
    file_extension = os.path.splitext(audio_file.filename)[1].lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="지원하지 않는 오디오 형식입니다."
        )
    
    # 업로드 디렉토리 생성
    os.makedirs(settings.upload_dir, exist_ok=True)
    
    # 파일 저장
    file_id = str(uuid.uuid4())
    file_extension = os.path.splitext(audio_file.filename)[1]
    file_path = os.path.join(settings.upload_dir, f"{file_id}{file_extension}")
    
    with open(file_path, "wb") as buffer:
        content = await audio_file.read()
        buffer.write(content)
    
    # 데이터베이스에 저장
    audio_sample = AudioSample(
        user_id=current_user.id,
        file_path=file_path,
        duration=0.0,  # 기본값 설정
        source="parent",  # 기본값 설정
        notes=None,  # 기본값 설정
        status="analyzing"
    )
    db.add(audio_sample)
    db.commit()
    db.refresh(audio_sample)
    
    try:
        # AI 분석 수행
        analysis_result = await ai_analysis_service.analyze_audio(file_path, current_user.child_age)
        
        # 분석 결과를 데이터베이스에 저장
        audio_sample.transcription = analysis_result.transcription
        audio_sample.intent = analysis_result.intent
        audio_sample.confidence = analysis_result.confidence
        audio_sample.emotion = analysis_result.emotion
        audio_sample.age_appropriate = analysis_result.age_appropriate
        audio_sample.recommended_response = analysis_result.recommended_response
        audio_sample.language_development_stage = analysis_result.language_development_stage
        audio_sample.status = "completed"
        audio_sample.analyzed_at = datetime.utcnow()
        
        db.commit()
        
        # TTS 오디오 생성
        tts_audio_path = await tts_service.generate_recommended_response_audio(analysis_result.recommended_response)
        if tts_audio_path:
            audio_sample.tts_audio_path = tts_audio_path
            db.commit()
        
        # 타임라인 항목 생성
        timeline_item = TimelineItem(
            user_id=current_user.id,
            audio_sample_id=audio_sample.id,
            date=datetime.now().strftime("%Y-%m-%d"),
            time=datetime.now().strftime("%H:%M"),
            child_utterance=analysis_result.transcription,
            intent=analysis_result.intent,
            parent_response=analysis_result.recommended_response,
            audio_url=f"/api/audio/samples/{audio_sample.id}/play",
            duration=0.0,  # 실제로는 오디오 길이 계산 필요
            confidence=analysis_result.confidence,
            analysis_result={
                "transcription": analysis_result.transcription,
                "intent": analysis_result.intent,
                "confidence": analysis_result.confidence,
                "emotion": analysis_result.emotion,
                "age_appropriate": analysis_result.age_appropriate,
                "recommended_response": analysis_result.recommended_response,
                "language_development_stage": analysis_result.language_development_stage,
                "suggestions": analysis_result.suggestions
            }
        )
        db.add(timeline_item)
        db.commit()
        
        result = {
            "success": True,
            "sample_id": audio_sample.id,
            "status": "분석 완료",
            "analysis_result": {
                "transcription": analysis_result.transcription,
                "intent": analysis_result.intent,
                "confidence": analysis_result.confidence,
                "recommended_response": analysis_result.recommended_response,
                "language_development_stage": analysis_result.language_development_stage
            }
        }
        return result
        
    except Exception as e:
        # 분석 실패 시 상태 업데이트
        audio_sample.status = "failed"
        db.commit()
        
        return {
            "success": False,
            "sample_id": audio_sample.id,
            "status": "분석 실패",
            "error": str(e)
        }


@router.get("/samples", response_model=dict)
async def get_audio_samples(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """오디오 샘플 목록 조회"""
    samples = db.query(AudioSample).filter(
        AudioSample.user_id == current_user.id
    ).order_by(desc(AudioSample.created_at)).all()
    
    # 통계 계산
    robot_collected = len([s for s in samples if s.source == "robot"])
    parent_uploaded = len([s for s in samples if s.source == "parent"])
    analysis_completed = len([s for s in samples if s.status == "completed"])
    
    # 샘플 데이터 변환
    sample_data = []
    for sample in samples:
        sample_data.append({
            "id": sample.id,
            "timestamp": sample.created_at.isoformat(),
            "duration": sample.duration,
            "source": "로봇 자동 수집" if sample.source == "robot" else "부모 업로드",
            "status": "분석 완료" if sample.status == "completed" else "분석 중",
            "notes": sample.notes or "",
            "audio_url": f"/api/audio/samples/{sample.id}/play",
            "tts_audio_url": f"/api/audio/samples/{sample.id}/tts" if sample.tts_audio_path else None,
            "analysis_result": {
                "transcription": sample.transcription,
                "intent": sample.intent,
                "confidence": sample.confidence,
                "recommended_response": sample.recommended_response
            } if sample.status == "completed" else None
        })
    
    return {
        "samples": sample_data,
        "statistics": {
            "robot_collected": robot_collected,
            "parent_uploaded": parent_uploaded,
            "analysis_completed": analysis_completed
        }
    }


@router.delete("/samples/{sample_id}", response_model=dict)
async def delete_audio_sample(
    sample_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """오디오 샘플 삭제"""
    sample = db.query(AudioSample).filter(
        AudioSample.id == sample_id,
        AudioSample.user_id == current_user.id
    ).first()
    
    if not sample:
        raise HTTPException(status_code=404, detail="샘플을 찾을 수 없습니다.")
    
    # 파일 삭제
    if os.path.exists(sample.file_path):
        os.remove(sample.file_path)
    
    # 데이터베이스에서 삭제
    db.delete(sample)
    db.commit()
    
    return {
        "success": True,
        "message": "샘플이 삭제되었습니다."
    }


@router.post("/samples/{sample_id}/reanalyze", response_model=dict)
async def reanalyze_audio_sample(
    sample_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """오디오 샘플 재분석"""
    sample = db.query(AudioSample).filter(
        AudioSample.id == sample_id,
        AudioSample.user_id == current_user.id
    ).first()
    
    if not sample:
        raise HTTPException(status_code=404, detail="샘플을 찾을 수 없습니다.")
    
    # 상태 업데이트
    sample.status = "analyzing"
    db.commit()
    
    try:
        # AI 분석 수행
        analysis_result = await ai_analysis_service.analyze_audio(sample.file_path, current_user.child_age)
        
        # 분석 결과를 데이터베이스에 저장
        sample.transcription = analysis_result.transcription
        sample.intent = analysis_result.intent
        sample.confidence = analysis_result.confidence
        sample.emotion = analysis_result.emotion
        sample.age_appropriate = analysis_result.age_appropriate
        sample.recommended_response = analysis_result.recommended_response
        sample.language_development_stage = analysis_result.language_development_stage
        sample.status = "completed"
        sample.analyzed_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "success": True,
            "status": "분석 완료",
            "analysis_result": {
                "transcription": analysis_result.transcription,
                "intent": analysis_result.intent,
                "confidence": analysis_result.confidence,
                "recommended_response": analysis_result.recommended_response,
                "language_development_stage": analysis_result.language_development_stage
            }
        }
        
    except Exception as e:
        # 분석 실패 시 상태 업데이트
        sample.status = "failed"
        db.commit()
        
        return {
            "success": False,
            "status": "분석 실패",
            "error": str(e)
        }


@router.get("/samples/{sample_id}/play")
async def play_audio_sample(
    sample_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """원본 오디오 샘플 재생"""
    sample = db.query(AudioSample).filter(
        AudioSample.id == sample_id,
        AudioSample.user_id == current_user.id
    ).first()
    
    if not sample:
        raise HTTPException(status_code=404, detail="샘플을 찾을 수 없습니다.")
    
    if not os.path.exists(sample.file_path):
        raise HTTPException(status_code=404, detail="오디오 파일을 찾을 수 없습니다.")
    
    return FileResponse(
        path=sample.file_path,
        media_type="audio/mpeg",
        filename=f"sample_{sample_id}.mp3"
    )


@router.get("/samples/{sample_id}/tts")
async def play_tts_audio(
    sample_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """TTS 오디오 재생"""
    sample = db.query(AudioSample).filter(
        AudioSample.id == sample_id,
        AudioSample.user_id == current_user.id
    ).first()
    
    if not sample:
        raise HTTPException(status_code=404, detail="샘플을 찾을 수 없습니다.")
    
    if not sample.tts_audio_path or not os.path.exists(sample.tts_audio_path):
        raise HTTPException(status_code=404, detail="TTS 오디오 파일을 찾을 수 없습니다.")
    
    return FileResponse(
        path=sample.tts_audio_path,
        media_type="audio/mpeg",
        filename=f"tts_{sample_id}.mp3"
    )


@router.post("/samples/{sample_id}/generate-tts")
async def generate_tts_for_sample(
    sample_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """샘플에 대한 TTS 오디오 생성"""
    sample = db.query(AudioSample).filter(
        AudioSample.id == sample_id,
        AudioSample.user_id == current_user.id
    ).first()
    
    if not sample:
        raise HTTPException(status_code=404, detail="샘플을 찾을 수 없습니다.")
    
    if not sample.recommended_response:
        raise HTTPException(status_code=400, detail="권장 응답이 없습니다.")
    
    try:
        # TTS 오디오 생성
        tts_audio_path = await tts_service.generate_recommended_response_audio(sample.recommended_response)
        
        if tts_audio_path:
            sample.tts_audio_path = tts_audio_path
            db.commit()
            
            return {
                "success": True,
                "tts_audio_url": f"/api/audio/samples/{sample_id}/tts",
                "message": "TTS 오디오가 생성되었습니다."
            }
        else:
            return {
                "success": False,
                "message": "TTS 오디오 생성에 실패했습니다."
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": f"TTS 생성 중 오류가 발생했습니다: {str(e)}"
        }
