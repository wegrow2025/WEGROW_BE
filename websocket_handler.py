import json
import base64
import asyncio
from typing import Dict, Any
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from database import get_db, AudioSample, User
from ai_analyzer import ai_analyzer
from hybrid_speech_system import hybrid_speech_system
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
            print(f"WebSocket 메시지 수신 (사용자 ID: {user_id}): {data[:100]}...")
            
            message = json.loads(data)
            print(f"파싱된 메시지: {message}")
            
            if message["type"] == "audio_data":
                print(f"오디오 데이터 메시지 처리 시작")
                await handle_audio_data(message, user_id)
            elif message["type"] == "text_message":
                print(f"텍스트 메시지 처리 시작")
                await handle_text_message(message, user_id)
            else:
                print(f"지원하지 않는 메시지 타입: {message['type']}")
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
        print(f"오디오 데이터 수신 (사용자 ID: {user_id})")
        print(f"메시지 타입: {message.get('type', 'unknown')}")
        print(f"메시지 키들: {list(message.keys())}")
        
        # 오디오 데이터를 버퍼에 추가
        audio_data = message["data"]
        timestamp = message.get("timestamp", int(datetime.now().timestamp() * 1000))
        
        print(f"오디오 데이터 크기: {len(audio_data)} bytes")
        print(f"오디오 데이터 타입: {type(audio_data)}")
        
        # 사용자 오디오 버퍼에 추가
        if user_id not in manager.user_audio_buffers:
            manager.user_audio_buffers[user_id] = []
        
        manager.user_audio_buffers[user_id].append({
            "data": audio_data,
            "timestamp": timestamp
        })
        
        print(f"현재 버퍼 크기: {len(manager.user_audio_buffers[user_id])}")
        
        # 오디오 데이터가 있으면 즉시 분석 시작 (실시간 처리)
        if len(manager.user_audio_buffers[user_id]) >= 1:
            print(f"오디오 버퍼 분석 시작 (사용자 ID: {user_id})")
            await process_audio_buffer(user_id)
        else:
            print(f"오디오 버퍼 대기 중... ({len(manager.user_audio_buffers[user_id])}/1)")
            
    except Exception as e:
        print(f"Error handling audio data: {e}")
        print(f"Message content: {message}")
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
        
        print(f"텍스트 메시지 수신: '{text}' (사용자 ID: {user_id})")
        
        # 데이터베이스에서 사용자 정보 가져오기
        db = next(get_db())
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            print(f"사용자를 찾을 수 없습니다: {user_id}")
            await manager.send_error(
                "USER_NOT_FOUND", 
                "사용자를 찾을 수 없습니다.", 
                user_id
            )
            return
        
        print(f"사용자 정보: {user.name}, 아이 나이: {user.child_age_months}개월")
        
        # 발달 단계 확인
        development_stage = ai_analyzer.get_development_stage(user.child_age_months)
        print(f"발달 단계: {development_stage}")
        
        # AI 분석 (텍스트 기반)
        print(f"AI 분석 시작...")
        analysis_result = ai_analyzer.analyze_text_message(
            text, user.child_age_months, user_id, development_stage
        )
        print(f"AI 분석 결과: {analysis_result}")
        
        # 전사 결과 전송 (AI 분석 결과 포함)
        transcription_message = {
            "type": "transcription",
            "text": analysis_result.get("transcription", text),
            "confidence": analysis_result.get("confidence", 1.0),
            "timestamp": timestamp,
            "analysis": {
                "intent": analysis_result.get("intent", ""),
                "syllable_combinations": analysis_result.get("syllable_combinations", 0),
                "meaningful_attempts": analysis_result.get("meaningful_attempts", 0),
                "new_words": analysis_result.get("new_words", []),
                "parent_suggestion": analysis_result.get("parent_suggestion", ""),
                "development_notes": analysis_result.get("development_notes", "")
            }
        }
        await manager.send_personal_message(transcription_message, user_id)
        print(f"전사 결과 전송: {transcription_message}")
        
        # TTS 응답 생성 및 전송
        tts_response = ai_analyzer.generate_tts_response(
            analysis_result.get("transcription", text), 
            development_stage, 
            user.child_age_months
        )
        print(f"TTS 응답 생성: '{tts_response}'")
        
        # TTS 응답 전송
        tts_message = {
            "type": "tts_response",
            "audioData": "",  # 실제 TTS 오디오 데이터
            "text": tts_response,
            "timestamp": timestamp
        }
        await manager.send_personal_message(tts_message, user_id)
        print(f"TTS 응답 전송: {tts_message}")
        
    except Exception as e:
        print(f"Error handling text message: {e}")
        await manager.send_error(
            "TEXT_PROCESSING_FAILED", 
            "텍스트 처리에 실패했습니다.", 
            user_id
        )

async def process_audio_buffer(user_id: int):
    """오디오 버퍼 처리 및 하이브리드 음성 분석"""
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
        
        # 하이브리드 음성 시스템으로 처리
        print(f"하이브리드 음성 시스템 처리 시작 (사용자 ID: {user_id})")
        
        # Base64 디코딩하여 바이트 데이터로 변환
        audio_bytes = base64.b64decode(combined_audio)
        print(f"디코딩된 오디오 크기: {len(audio_bytes)} bytes")
        
        # 하이브리드 시스템으로 음성 상호작용 처리
        speech_result = hybrid_speech_system.process_speech_interaction(
            audio_bytes, user.child_age_months, user_id
        )
        
        if not speech_result.get('success'):
            await manager.send_error(
                "SPEECH_PROCESSING_FAILED", 
                f"음성 처리 실패: {speech_result.get('error', '알 수 없는 오류')}", 
                user_id
            )
            return
        
        # 전사 결과 전송
        transcription_message = {
            "type": "transcription",
            "text": speech_result["original_text"],
            "confidence": speech_result.get("stt_confidence", 0.0),
            "timestamp": speech_result.get("timestamp", int(datetime.now().timestamp() * 1000))
        }
        await manager.send_personal_message(transcription_message, user_id)
        print(f"전사 결과 전송: {transcription_message}")
        
        # TTS 응답 전송 (실제 오디오 데이터 포함)
        tts_message = {
            "type": "tts_response",
            "audioData": speech_result["audio_data"],
            "text": speech_result["final_response"],
            "timestamp": speech_result.get("timestamp", int(datetime.now().timestamp() * 1000)),
            "processing_time": speech_result.get("processing_time", 0),
            "latency_status": speech_result.get("latency_status", "unknown"),
            "cache_hit": speech_result.get("cache_hit", False)
        }
        await manager.send_personal_message(tts_message, user_id)
        print(f"TTS 응답 전송: {speech_result['final_response']} (처리시간: {speech_result.get('processing_time', 0)}초)")
        
        # 오디오 샘플 저장 (개인정보 보호 모드에서는 원본 데이터 저장하지 않음)
        if not hybrid_speech_system.privacy_mode:
            await save_audio_sample(user_id, combined_audio, {
                "transcription": speech_result["original_text"],
                "confidence": speech_result.get("stt_confidence", 0.0),
                "intent": "하이브리드_음성_분석",
                "syllable_combinations": len(speech_result["original_text"]),
                "meaningful_attempts": 1 if speech_result.get("stt_confidence", 0) > 0.5 else 0,
                "new_words": []
            })
        
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
