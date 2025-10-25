from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, HTMLResponse
import uvicorn
import os
from typing import Dict, Any

from api_routes import api_router
from websocket_handler import websocket_endpoint
from config import settings

# FastAPI 앱 생성
app = FastAPI(
    title="We:Grow RealTime Audio API",
    description="아이의 언어 발달을 위한 실시간 음성 분석 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경에서 모든 도메인 허용
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(api_router, prefix="/api")

# WebSocket 엔드포인트
@app.websocket("/ws")
async def websocket_route(websocket: WebSocket, user_id: int):
    """WebSocket 연결 처리"""
    await websocket_endpoint(websocket, user_id)

# 정적 파일 서빙 (업로드된 오디오 파일용)
if not os.path.exists("uploads"):
    os.makedirs("uploads")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# WebSocket 테스트 페이지 서빙
if not os.path.exists("ws"):
    os.makedirs("ws")
app.mount("/ws", StaticFiles(directory="ws"), name="ws")

# 루트 엔드포인트
@app.get("/")
async def root():
    """API 상태 확인"""
    return {
        "message": "We:Grow RealTime Audio API",
        "version": "1.0.0",
        "status": "running",
        "websocket_url": f"ws://{settings.host}:{settings.port}/ws",
        "endpoints": {
            "auth": "/api/auth",
            "audio": "/api/audio",
            "dashboard": "/api/dashboard",
            "timeline": "/api/timeline",
            "growth": "/api/growth",
            "tips": "/api/tips",
            "settings": "/api/settings",
            "stats": "/api/stats"
        }
    }

# 헬스 체크
@app.get("/health")
async def health_check():
    """서버 상태 확인"""
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

# 에러 핸들러
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "type": "error",
            "code": "NOT_FOUND",
            "message": "요청한 리소스를 찾을 수 없습니다.",
            "timestamp": 1640995200000
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "type": "error",
            "code": "INTERNAL_SERVER_ERROR",
            "message": "서버 내부 오류가 발생했습니다.",
            "timestamp": 1640995200000
        }
    )

# WebSocket 연결 테스트 엔드포인트
@app.get("/ws/test")
async def websocket_test():
    """WebSocket 연결 테스트용 HTML 페이지"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>We:Grow WebSocket Test</title>
        <meta charset="utf-8">
    </head>
    <body>
        <h1>We:Grow WebSocket Test</h1>
        <div id="status">연결 대기 중...</div>
        <div id="messages"></div>
        <button onclick="connect()">연결</button>
        <button onclick="disconnect()">연결 해제</button>
        <button onclick="sendTestMessage()">테스트 메시지 전송</button>
        
        <script>
            let ws = null;
            const status = document.getElementById('status');
            const messages = document.getElementById('messages');
            
            function connect() {
                ws = new WebSocket('ws://localhost:8000/ws?user_id=1');
                
                ws.onopen = function() {
                    status.textContent = '연결됨';
                    status.style.color = 'green';
                };
                
                ws.onmessage = function(event) {
                    const message = JSON.parse(event.data);
                    messages.innerHTML += '<div>' + JSON.stringify(message, null, 2) + '</div>';
                };
                
                ws.onclose = function() {
                    status.textContent = '연결 해제됨';
                    status.style.color = 'red';
                };
                
                ws.onerror = function(error) {
                    status.textContent = '오류: ' + error;
                    status.style.color = 'red';
                };
            }
            
            function disconnect() {
                if (ws) {
                    ws.close();
                }
            }
            
            function sendTestMessage() {
                if (ws) {
                    const message = {
                        type: 'text_message',
                        text: '안녕하세요',
                        timestamp: Date.now()
                    };
                    ws.send(JSON.stringify(message));
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
