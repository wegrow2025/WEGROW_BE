from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import asyncio
from app.services.ai_analysis import ai_analysis_service


class ConnectionManager:
    """WebSocket 연결 관리자"""
    
    def __init__(self):
        # 활성 연결 저장
        self.active_connections: Dict[str, WebSocket] = {}
        # 사용자별 연결 저장
        self.user_connections: Dict[str, List[str]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str, connection_id: str):
        """WebSocket 연결"""
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        self.user_connections[user_id].append(connection_id)
    
    def disconnect(self, connection_id: str, user_id: str):
        """WebSocket 연결 해제"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        if user_id in self.user_connections:
            if connection_id in self.user_connections[user_id]:
                self.user_connections[user_id].remove(connection_id)
    
    async def send_personal_message(self, message: dict, connection_id: str):
        """개별 연결에 메시지 전송"""
        if connection_id in self.active_connections:
            try:
                await self.active_connections[connection_id].send_text(json.dumps(message))
            except:
                # 연결이 끊어진 경우 제거
                del self.active_connections[connection_id]
    
    async def send_to_user(self, message: dict, user_id: str):
        """특정 사용자의 모든 연결에 메시지 전송"""
        if user_id in self.user_connections:
            for connection_id in self.user_connections[user_id]:
                await self.send_personal_message(message, connection_id)
    
    async def broadcast(self, message: dict):
        """모든 연결에 메시지 전송"""
        for connection_id in list(self.active_connections.keys()):
            await self.send_personal_message(message, connection_id)


# 전역 연결 관리자
manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket 엔드포인트"""
    connection_id = f"{user_id}_{asyncio.get_event_loop().time()}"
    
    await manager.connect(websocket, user_id, connection_id)
    
    try:
        while True:
            # 클라이언트로부터 메시지 수신
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # 메시지 타입에 따른 처리
            if message["type"] == "audio_data":
                await handle_audio_data(message, user_id, connection_id)
            elif message["type"] == "text_message":
                await handle_text_message(message, user_id, connection_id)
            else:
                await manager.send_personal_message({
                    "type": "error",
                    "message": "알 수 없는 메시지 타입입니다.",
                    "timestamp": asyncio.get_event_loop().time()
                }, connection_id)
                
    except WebSocketDisconnect:
        manager.disconnect(connection_id, user_id)
    except Exception as e:
        await manager.send_personal_message({
            "type": "error",
            "message": f"오류가 발생했습니다: {str(e)}",
            "timestamp": asyncio.get_event_loop().time()
        }, connection_id)
        manager.disconnect(connection_id, user_id)


async def handle_audio_data(message: dict, user_id: str, connection_id: str):
    """오디오 데이터 처리"""
    try:
        # 오디오 데이터를 임시 파일로 저장
        import base64
        import os
        from datetime import datetime
        
        audio_data = base64.b64decode(message["data"])
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_file = f"temp_audio_{user_id}_{timestamp}.wav"
        
        with open(temp_file, "wb") as f:
            f.write(audio_data)
        
        # AI 분석 수행
        analysis_result = await ai_analysis_service.analyze_audio(temp_file, 18)  # 실제로는 사용자 나이 가져오기
        
        # 분석 결과 전송
        await manager.send_personal_message({
            "type": "transcription",
            "text": analysis_result.transcription,
            "confidence": analysis_result.confidence,
            "intent": analysis_result.intent,
            "recommended_response": analysis_result.recommended_response,
            "timestamp": message.get("timestamp", asyncio.get_event_loop().time())
        }, connection_id)
        
        # TTS 응답 생성 (실제로는 TTS 서비스 호출)
        await manager.send_personal_message({
            "type": "tts_response",
            "audio_data": "",  # 실제로는 TTS 오디오 데이터
            "text": analysis_result.recommended_response,
            "timestamp": asyncio.get_event_loop().time()
        }, connection_id)
        
        # 임시 파일 삭제
        if os.path.exists(temp_file):
            os.remove(temp_file)
            
    except Exception as e:
        await manager.send_personal_message({
            "type": "error",
            "message": f"오디오 처리 중 오류가 발생했습니다: {str(e)}",
            "timestamp": asyncio.get_event_loop().time()
        }, connection_id)


async def handle_text_message(message: dict, user_id: str, connection_id: str):
    """텍스트 메시지 처리"""
    try:
        # 간단한 텍스트 응답 생성
        response_text = f"'{message['text']}'라고 말씀하셨네요. 아이와 함께 대화를 나누어보세요!"
        
        await manager.send_personal_message({
            "type": "text_response",
            "text": response_text,
            "timestamp": asyncio.get_event_loop().time()
        }, connection_id)
        
    except Exception as e:
        await manager.send_personal_message({
            "type": "error",
            "message": f"텍스트 처리 중 오류가 발생했습니다: {str(e)}",
            "timestamp": asyncio.get_event_loop().time()
        }, connection_id)
