from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import get_db
from app.models import User, UserSettings
from app.schemas import UserCreate, UserUpdate, Token, User as UserSchema
from app.auth import get_password_hash, create_access_token, authenticate_user, get_current_active_user
from app.config import settings
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/api/auth", tags=["auth"])


# 로그인용 스키마
class LoginRequest(BaseModel):
    email: str
    password: str
    rememberMe: bool = False


@router.post("/register", response_model=dict)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """사용자 회원가입"""
    # 이메일 중복 확인
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 이메일입니다."
        )
    
    # 사용자 생성
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        password_hash=hashed_password,
        name=user.name,
        child_age=user.child_age
    )
    db.add(db_user)
    db.flush()  # ID 생성을 위해 flush
    
    # 기본 설정 생성
    default_settings = UserSettings(
        user_id=db_user.id,
        recording_collection=True,
        analysis_usage=True,
        coaching_recommendations=True,
        notifications_enabled=True,
        email_reports=True,
        data_retention_days=365,
        language="ko-KR",
        timezone="Asia/Seoul",
        audio_recording=True,
        research_participation=False,
        third_party_sharing=False,
        anonymized_research=False,
        family_sharing=False
    )
    db.add(default_settings)
    db.commit()
    db.refresh(db_user)
    
    # JWT 토큰 생성
    access_token = create_access_token(data={"sub": user.email})
    
    return {
        "success": True,
        "user": {
            "id": db_user.id,
            "email": db_user.email,
            "name": db_user.name,
            "childAge": db_user.child_age,
            "createdAt": db_user.created_at.isoformat() if db_user.created_at else None
        },
        "token": access_token
    }


@router.post("/login", response_model=dict)
async def login(
    login_data: LoginRequest = Body(...),
    db: Session = Depends(get_db)
):
    """사용자 로그인"""
    user = authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 로그인 시간 업데이트
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    # JWT 토큰 생성
    expire_minutes = settings.access_token_expire_minutes
    if login_data.rememberMe:
        expire_minutes = 7 * 24 * 60  # 7일
    
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=expire_minutes)
    )
    
    return {
        "success": True,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "childAge": user.child_age
        },
        "token": access_token
    }


@router.get("/me", response_model=UserSchema)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """현재 사용자 정보 조회"""
    return current_user


@router.put("/profile", response_model=UserSchema)
async def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """사용자 프로필 업데이트"""
    if user_update.email and user_update.email != current_user.email:
        # 이메일 중복 확인
        existing_user = db.query(User).filter(User.email == user_update.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 사용 중인 이메일입니다."
            )
        current_user.email = user_update.email
    
    if user_update.name:
        current_user.name = user_update.name
    
    if user_update.child_age:
        current_user.child_age = user_update.child_age
    
    if user_update.password:
        current_user.password_hash = get_password_hash(user_update.password)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user
