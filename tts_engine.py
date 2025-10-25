import os
import hashlib
import time
from typing import Dict, Optional
from gtts import gTTS
import io

class TTSEngine:
    def __init__(self, cache_dir: str = "cache/tts"):
        self.cache_dir = cache_dir
        self.supported_languages = {
            "ko": "ko-KR",
            "en": "en-US"
        }
        
        # 캐시 디렉토리 생성
        os.makedirs(cache_dir, exist_ok=True)
    
    def synthesize_speech(self, text: str, language: str = "ko", slow: bool = False) -> Dict:
        """텍스트를 음성으로 변환"""
        try:
            # 캐시 키 생성
            cache_key = self._generate_cache_key(text, language, slow)
            cache_path = os.path.join(self.cache_dir, f"{cache_key}.mp3")
            
            # 캐시된 파일이 있는지 확인
            if os.path.exists(cache_path):
                print(f"캐시된 TTS 사용: {cache_key}")
                with open(cache_path, 'rb') as f:
                    audio_data = f.read()
                return {
                    'success': True,
                    'audio_data': audio_data,
                    'cache_hit': True,
                    'text': text,
                    'language': language
                }
            
            # gTTS로 음성 생성
            tts = gTTS(text=text, lang=language, slow=slow)
            
            # 메모리에 오디오 데이터 생성
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_data = audio_buffer.getvalue()
            
            # 캐시에 저장
            with open(cache_path, 'wb') as f:
                f.write(audio_data)
            
            print(f"새로운 TTS 생성 및 캐시 저장: {cache_key}")
            
            return {
                'success': True,
                'audio_data': audio_data,
                'cache_hit': False,
                'text': text,
                'language': language,
                'file_size': len(audio_data)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"TTS 생성 오류: {str(e)}",
                'audio_data': None
            }
    
    def _generate_cache_key(self, text: str, language: str, slow: bool) -> str:
        """캐시 키 생성"""
        content = f"{text}_{language}_{slow}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def get_cache_stats(self) -> Dict:
        """캐시 통계 조회"""
        if not os.path.exists(self.cache_dir):
            return {"total_files": 0, "total_size": 0}
        
        total_files = 0
        total_size = 0
        
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.mp3'):
                file_path = os.path.join(self.cache_dir, filename)
                total_files += 1
                total_size += os.path.getsize(file_path)
        
        return {
            "total_files": total_files,
            "total_size": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }
    
    def clear_cache(self) -> Dict:
        """캐시 정리"""
        if not os.path.exists(self.cache_dir):
            return {"cleared_files": 0}
        
        cleared_files = 0
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.mp3'):
                file_path = os.path.join(self.cache_dir, filename)
                os.remove(file_path)
                cleared_files += 1
        
        return {"cleared_files": cleared_files}

# TTS 엔진 인스턴스
tts_engine = TTSEngine()
