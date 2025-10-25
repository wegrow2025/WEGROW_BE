import requests
import json
import base64
import time
from typing import Dict, Optional
from config import settings

class ClovaSTT:
    def __init__(self):
        # 공식 문서에 따른 올바른 API URL
        self.api_url = "https://naveropenapi.apigw.ntruss.com/recog/v1/stt"
        self.client_id = getattr(settings, 'clova_client_id', '')
        self.client_secret = getattr(settings, 'clova_client_secret', '')
        
    def transcribe_audio(self, audio_data: bytes, language: str = "ko-KR") -> Dict:
        """CLOVA STT를 사용한 음성 인식 (공식 문서 기준)"""
        try:
            # API 키 확인
            if not self.client_id or not self.client_secret:
                return {
                    'success': False,
                    'error': "CLOVA API 키가 설정되지 않았습니다. .env 파일에 CLOVA_CLIENT_ID와 CLOVA_CLIENT_SECRET을 설정하세요.",
                    'text': '',
                    'confidence': 0.0
                }
            
            # 공식 문서에 따른 올바른 헤더 설정
            headers = {
                'X-NCP-APIGW-API-KEY-ID': self.client_id,
                'X-NCP-APIGW-API-KEY': self.client_secret,
                'Content-Type': 'application/octet-stream'  # 공식 문서에 따른 Content-Type
            }
            
            # 공식 문서에 따른 쿼리 파라미터 (CLOVA STT는 ko만 지원)
            params = {
                'lang': 'Kor'  # CLOVA STT는 ko만 지원
            }
            
            print(f"CLOVA STT 요청 시작 - 오디오 크기: {len(audio_data)} bytes")
            print(f"API URL: {self.api_url}")
            print(f"언어: {language}")
            
            # 오디오 데이터를 직접 전송 (base64 인코딩 없이)
            response = requests.post(
                self.api_url,
                headers=headers,
                params=params,
                data=audio_data,  # 바이너리 데이터 직접 전송
                timeout=30
            )
            
            print(f"CLOVA STT 응답 상태: {response.status_code}")
            print(f"CLOVA STT 응답 헤더: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"CLOVA STT 성공 응답: {result}")
                return {
                    'success': True,
                    'text': result.get('text', ''),
                    'confidence': result.get('confidence', 0.0),
                    'language': language
                }
            else:
                error_text = response.text
                print(f"CLOVA STT 오류 응답: {error_text}")
                return {
                    'success': False,
                    'error': f"CLOVA STT API 오류: {response.status_code} - {error_text}",
                    'text': '',
                    'confidence': 0.0
                }
                
        except Exception as e:
            print(f"CLOVA STT 예외 발생: {str(e)}")
            return {
                'success': False,
                'error': f"CLOVA STT 처리 오류: {str(e)}",
                'text': '',
                'confidence': 0.0
            }

# CLOVA STT 인스턴스
clova_stt = ClovaSTT()
