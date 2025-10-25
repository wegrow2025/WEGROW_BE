import json
import base64
import asyncio
from typing import Dict, Any
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from database import get_db, AudioSample, User
from ai_analyzer import ai_analyzer
import io
import wave
import tempfile
import os
from datetime import datetime

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}
        self.user_audio_buffers: Dict[int, list] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.user_audio_buffers[user_id] = []
        print(f"User {user_id} connected to WebSocket")
    
    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.user_audio_buffers:
            del self.user_audio_buffers[user_id]
        print(f"User {user_id} disconnected from WebSocket")
    
    async def send_personal_message(self, message: dict, user_id: int):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(json.dumps(message))
            except Exception as e:
                print(f"Error sending message to user {user_id}: {e}")
    
    async def send_error(self, error_code: str, error_message: str, user_id: int):
        error_message = {
            "type": "error",
            "code": error_code,
            "message": error_message,
            "timestamp": int(datetime.now().timestamp() * 1000)
        }
        await self.send_personal_message(error_message, user_id)

# 전역 WebSocket 매니저
manager = WebSocketManager()

async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            # 클라이언트로부터 메시지 수신
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "audio_data":
                await handle_audio_data(message, user_id)
            elif message["type"] == "text_message":
                await handle_text_message(message, user_id)
            else:
                await manager.send_error(
                    "INVALID_MESSAGE_TYPE", 
                    "지원하지 않는 메시지 타입입니다.", 
                    user_id
                )
                
    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        await manager.send_error(
            "WEBSOCKET_ERROR", 
            "연결 중 오류가 발생했습니다.", 
            user_id
        )
        manager.disconnect(user_id)

async def handle_audio_data(message: dict, user_id: int):
    """오디오 데이터 처리"""
    try:
        # 오디오 데이터를 버퍼에 추가
        audio_data = message["data"]
        timestamp = message.get("timestamp", int(datetime.now().timestamp() * 1000))
        
        # 사용자 오디오 버퍼에 추가
        if user_id not in manager.user_audio_buffers:
            manager.user_audio_buffers[user_id] = []
        
        manager.user_audio_buffers[user_id].append({
            "data": audio_data,
            "timestamp": timestamp
        })
        
        # 버퍼가 충분히 쌓이면 분석 시작 (예: 3초 분량)
        if len(manager.user_audio_buffers[user_id]) >= 3:
            await process_audio_buffer(user_id)
            
    except Exception as e:
        print(f"Error handling audio data: {e}")
        await manager.send_error(
            "AUDIO_PROCESSING_FAILED", 
            "오디오 처리에 실패했습니다.", 
            user_id
        )

async def handle_text_message(message: dict, user_id: int):
    """텍스트 메시지 처리"""
    try:
        text = message["text"]
        timestamp = message.get("timestamp", int(datetime.now().timestamp() * 1000))
        
        # 데이터베이스에서 사용자 정보 가져오기
        db = next(get_db())
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            await manager.send_error(
                "USER_NOT_FOUND", 
                "사용자를 찾을 수 없습니다.", 
                user_id
            )
            return
        
        # AI 분석
        analysis_result = ai_analyzer.analyze_audio(
            "", user.child_age_months, user_id
        )
        
        # 전사 결과 전송
        transcription_message = {
            "type": "transcription",
            "text": text,
            "confidence": 1.0,
            "timestamp": timestamp
        }
        await manager.send_personal_message(transcription_message, user_id)
        
        # TTS 응답 생성 및 전송
        development_stage = ai_analyzer.get_development_stage(user.child_age_months)
        tts_response = ai_analyzer.generate_tts_response(
            text, development_stage, user.child_age_months
        )
        
        # TTS 응답 전송 (실제로는 TTS 서비스 호출 필요)
        tts_message = {
            "type": "tts_response",
            "audioData": "",  # 실제 TTS 오디오 데이터
            "text": tts_response,
            "timestamp": timestamp
        }
        await manager.send_personal_message(tts_message, user_id)
        
    except Exception as e:
        print(f"Error handling text message: {e}")
        await manager.send_error(
            "TEXT_PROCESSING_FAILED", 
            "텍스트 처리에 실패했습니다.", 
            user_id
        )

async def process_audio_buffer(user_id: int):
    """오디오 버퍼 처리 및 분석"""
    try:
        if user_id not in manager.user_audio_buffers:
            return
        
        # 버퍼에서 오디오 데이터 결합
        audio_buffer = manager.user_audio_buffers[user_id]
        combined_audio = combine_audio_buffer(audio_buffer)
        
        # 데이터베이스에서 사용자 정보 가져오기
        db = next(get_db())
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            await manager.send_error(
                "USER_NOT_FOUND", 
                "사용자를 찾을 수 없습니다.", 
                user_id
            )
            return
        
        # AI 분석
        analysis_result = ai_analyzer.analyze_audio(
            combined_audio, user.child_age_months, user_id
        )
        
        if "error" in analysis_result:
            await manager.send_error(
                "AI_ANALYSIS_FAILED", 
                "AI 분석에 실패했습니다.", 
                user_id
            )
            return
        
        # 전사 결과 전송
        transcription_message = {
            "type": "transcription",
            "text": analysis_result["transcription"],
            "confidence": analysis_result["confidence"],
            "timestamp": int(datetime.now().timestamp() * 1000)
        }
        await manager.send_personal_message(transcription_message, user_id)
        
        # TTS 응답 생성
        development_stage = analysis_result["development_stage"]
        tts_response = ai_analyzer.generate_tts_response(
            analysis_result["transcription"], 
            development_stage, 
            user.child_age_months
        )
        
        # TTS 응답 전송
        tts_message = {
            "type": "tts_response",
            "audioData": "",  # 실제 TTS 오디오 데이터
            "text": tts_response,
            "timestamp": int(datetime.now().timestamp() * 1000)
        }
        await manager.send_personal_message(tts_message, user_id)
        
        # 오디오 샘플 저장
        await save_audio_sample(user_id, combined_audio, analysis_result)
        
        # 버퍼 초기화
        manager.user_audio_buffers[user_id] = []
        
    except Exception as e:
        print(f"Error processing audio buffer: {e}")
        await manager.send_error(
            "AUDIO_BUFFER_PROCESSING_FAILED", 
            "오디오 버퍼 처리에 실패했습니다.", 
            user_id
        )

def combine_audio_buffer(audio_buffer: list) -> str:
    """오디오 버퍼를 하나의 base64 문자열로 결합"""
    try:
        combined_data = b""
        for audio_chunk in audio_buffer:
            audio_bytes = base64.b64decode(audio_chunk["data"])
            combined_data += audio_bytes
        
        # 결합된 오디오를 base64로 인코딩
        return base64.b64encode(combined_data).decode('utf-8')
        
    except Exception as e:
        print(f"Error combining audio buffer: {e}")
        return ""

async def save_audio_sample(user_id: int, audio_data: str, analysis_result: dict):
    """오디오 샘플을 데이터베이스에 저장"""
    try:
        db = next(get_db())
        
        # 임시 파일로 오디오 저장
        audio_bytes = base64.b64decode(audio_data)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file.write(audio_bytes)
            temp_file_path = temp_file.name
        
        # 오디오 샘플 생성
        audio_sample = AudioSample(
            user_id=user_id,
            file_path=temp_file_path,
            duration=analysis_result.get("audio_features", {}).get("duration", 0),
            source="robot",  # 실시간 수집
            status="분석 완료",
            transcription=analysis_result.get("transcription", ""),
            confidence=analysis_result.get("confidence", 0),
            intent=analysis_result.get("intent", ""),
            syllable_combinations=analysis_result.get("syllable_combinations", 0),
            meaningful_attempts=analysis_result.get("meaningful_attempts", 0),
            new_words=json.dumps(analysis_result.get("new_words", []))
        )
        
        db.add(audio_sample)
        db.commit()
        
        print(f"Audio sample saved for user {user_id}")
        
    except Exception as e:
        print(f"Error saving audio sample: {e}")
