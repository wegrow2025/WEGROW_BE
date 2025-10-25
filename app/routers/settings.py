from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, UserSettings
from app.schemas import UserSettings as UserSettingsSchema
from app.auth import get_current_active_user

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("", response_model=dict)
async def get_settings(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """사용자 설정 조회"""
    settings = db.query(UserSettings).filter(
        UserSettings.user_id == current_user.id
    ).first()
    
    if not settings:
        raise HTTPException(status_code=404, detail="설정을 찾을 수 없습니다.")
    
    return {
        "recording_collection": settings.recording_collection,
        "analysis_usage": settings.analysis_usage,
        "coaching_recommendations": settings.coaching_recommendations,
        "notifications_enabled": settings.notifications_enabled,
        "email_reports": settings.email_reports,
        "user": {
            "email": current_user.email,
            "child_age": current_user.child_age
        }
    }


@router.put("", response_model=dict)
async def update_settings(
    settings_update: UserSettingsSchema,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """사용자 설정 업데이트"""
    settings = db.query(UserSettings).filter(
        UserSettings.user_id == current_user.id
    ).first()
    
    if not settings:
        raise HTTPException(status_code=404, detail="설정을 찾을 수 없습니다.")
    
    # 설정 업데이트
    settings.recording_collection = settings_update.recording_collection
    settings.analysis_usage = settings_update.analysis_usage
    settings.coaching_recommendations = settings_update.coaching_recommendations
    settings.notifications_enabled = settings_update.notifications_enabled
    settings.email_reports = settings_update.email_reports
    
    db.commit()
    
    return {
        "success": True,
        "message": "설정이 저장되었습니다."
    }
