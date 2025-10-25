import httpx
import base64
import os
from typing import Optional
from app.config import settings


class TTSService:
    """Google TTS 서비스"""
    
    def __init__(self):
        self.google_tts_url = "https://texttospeech.googleapis.com/v1/text:synthesize"
        self.google_api_key = getattr(settings, 'google_tts_api_key', None)
    
    def _preprocess_text_for_tts(self, text: str) -> str:
        """TTS용 텍스트 전처리"""
        # ~ 기호를 제거하고 자연스러운 톤으로 변환
        processed_text = text.replace("~", "")
        
        # 연속된 느낌표나 물음표 정리
        processed_text = processed_text.replace("!!", "!")
        processed_text = processed_text.replace("??", "?")
        
        # 유아 친화적인 표현으로 변환
        processed_text = processed_text.replace("우리 아가", "우리 아가")
        processed_text = processed_text.replace("와", "와")
        processed_text = processed_text.replace("우와", "우와")
        
        return processed_text.strip()

    async def generate_speech(self, text: str, language: str = "ko-KR", voice: str = "ko-KR-Standard-A") -> Optional[str]:
        """텍스트를 음성으로 변환"""
        # TTS용 텍스트 전처리
        processed_text = self._preprocess_text_for_tts(text)
        
        if not self.google_api_key:
            return self._generate_mock_audio(processed_text)
        
        try:
            request_data = {
                "input": {"text": processed_text},
                "voice": {
                    "languageCode": language,
                    "name": voice,
                    "ssmlGender": "FEMALE"
                },
                "audioConfig": {
                    "audioEncoding": "MP3",
                    "speakingRate": 0.8,  # 조금 더 천천히 (유아가 따라하기 좋게)
                    "pitch": 2.0,  # 높은 톤 (유아가 좋아하는 밝은 목소리)
                    "volumeGainDb": 2.0  # 조금 더 큰 소리
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.google_tts_url}?key={self.google_api_key}",
                    json=request_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    audio_content = result.get("audioContent")
                    if audio_content:
                        # Base64 디코딩하여 오디오 파일로 저장
                        audio_data = base64.b64decode(audio_content)
                        return await self._save_audio_file(audio_data, processed_text)
                    else:
                        return None
                else:
                    return self._generate_mock_audio(processed_text)
                    
        except Exception as e:
            return self._generate_mock_audio(processed_text)
    
    async def _save_audio_file(self, audio_data: bytes, text: str) -> str:
        """오디오 데이터를 파일로 저장"""
        import uuid
        from datetime import datetime
        
        # TTS 오디오 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_id = str(uuid.uuid4())[:8]
        filename = f"tts_{timestamp}_{file_id}.mp3"
        
        # TTS 전용 디렉토리 생성
        tts_dir = os.path.join(settings.upload_dir, "tts")
        os.makedirs(tts_dir, exist_ok=True)
        
        file_path = os.path.join(tts_dir, filename)
        
        with open(file_path, "wb") as f:
            f.write(audio_data)
        
        return file_path
    
    def _generate_mock_audio(self, text: str) -> str:
        """개발 환경용 모의 오디오 생성"""
        import uuid
        from datetime import datetime
        
        # 모의 TTS 오디오 파일 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_id = str(uuid.uuid4())[:8]
        filename = f"mock_tts_{timestamp}_{file_id}.mp3"
        
        # TTS 전용 디렉토리 생성
        tts_dir = os.path.join(settings.upload_dir, "tts")
        os.makedirs(tts_dir, exist_ok=True)
        
        file_path = os.path.join(tts_dir, filename)
        
        # 모의 오디오 파일 생성 (실제로는 빈 파일)
        with open(file_path, "wb") as f:
            f.write(b"mock_audio_data")
        
        return file_path
    
    async def generate_recommended_response_audio(self, recommended_response: str) -> Optional[str]:
        """권장 응답을 TTS로 변환"""
        if not recommended_response:
            return None
        
        # 따옴표 제거
        clean_text = recommended_response.strip('"\'')
        return await self.generate_speech(clean_text)
    
    async def generate_transcription_audio(self, transcription: str) -> Optional[str]:
        """전사된 텍스트를 TTS로 변환"""
        if not transcription:
            return None
        
        return await self.generate_speech(transcription)


# 전역 인스턴스
tts_service = TTSService()
