from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os
from datetime import datetime

# 라우터 임포트
from app.routers import auth, dashboard, audio, timeline, tips, settings as settings_router, growth, websocket
from app.config import settings

# FastAPI 앱 생성
app = FastAPI(
    title="We:Grow API",
    description="아이 언어 발달 지원 AI 서비스 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:3000", "http://localhost:3001"],  # 프론트엔드 도메인
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 정적 파일 서빙 (업로드된 파일)
if not os.path.exists(settings.upload_dir):
    os.makedirs(settings.upload_dir)
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

# 라우터 등록
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(audio.router)
app.include_router(timeline.router)
app.include_router(tips.router)
app.include_router(settings_router.router)
app.include_router(growth.router)
app.include_router(websocket.router)


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "We:Grow API 서버가 실행 중입니다.",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


# 전역 예외 처리
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.status_code,
                "message": exc.detail
            },
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "서버 내부 오류가 발생했습니다."
            },
            "timestamp": datetime.now().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
