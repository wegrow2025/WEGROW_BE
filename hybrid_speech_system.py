import time
import base64
from typing import Dict, Optional
from clova_stt import clova_stt
from template_engine import template_engine
from tts_engine import tts_engine
from ai_analyzer import ai_analyzer

class HybridSpeechSystem:
    def __init__(self):
        self.latency_goal = 2.0  # 2초 이내 응답 목표
        self.privacy_mode = True  # 개인정보 보호 모드
        
    def process_speech_interaction(self, audio_data: bytes, child_age_months: int, 
                                 user_id: int, context: Dict = None) -> Dict:
        """하이브리드 음성 상호작용 처리"""
        start_time = time.time()
        
        try:
            # 1. STT (음성 인식)
            stt_result = self._perform_stt(audio_data)
            if not stt_result['success']:
                return self._create_error_response("STT 실패", start_time)
            
            text = stt_result['text']
            print(f"STT 결과: {text}")
            
            # 2. Template/Policy Engine 처리
            template_result = template_engine.process_text(
                text, child_age_months, context or {}
            )
            
            # 3. OpenAI API로 의도 분석 및 응답 생성
            ai_result = ai_analyzer.analyze_text_message(
                text, child_age_months, user_id, 
                ai_analyzer.get_development_stage(child_age_months)
            )
            
            # 4. 최종 응답 텍스트 생성
            final_response = self._generate_final_response(template_result, ai_result)
            
            # 5. TTS (음성 합성)
            tts_result = tts_engine.synthesize_speech(
                final_response, language="ko", slow=False
            )
            
            if not tts_result['success']:
                return self._create_error_response("TTS 실패", start_time)
            
            # 6. 응답 생성
            processing_time = time.time() - start_time
            latency_status = "good" if processing_time <= self.latency_goal else "slow"
            
            response = {
                'success': True,
                'original_text': text,
                'final_response': final_response,
                'audio_data': base64.b64encode(tts_result['audio_data']).decode('utf-8'),
                'processing_time': round(processing_time, 2),
                'latency_status': latency_status,
                'stt_confidence': stt_result.get('confidence', 0.0),
                'cache_hit': tts_result.get('cache_hit', False),
                'timestamp': int(time.time() * 1000)
            }
            
            # 개인정보 보호: 원본 오디오/텍스트 저장하지 않음
            if self.privacy_mode:
                response['privacy_note'] = "원본 데이터 저장되지 않음"
            
            return response
            
        except Exception as e:
            return self._create_error_response(f"시스템 오류: {str(e)}", start_time)
    
    def _perform_stt(self, audio_data: bytes) -> Dict:
        """STT 수행 (CLOVA만 사용)"""
        # CLOVA STT 사용
        clova_result = clova_stt.transcribe_audio(audio_data)
        
        if clova_result['success'] and clova_result['text'].strip():
            print("CLOVA STT 성공")
            return clova_result
        
        # CLOVA STT 실패
        print("CLOVA STT 실패")
        return {
            'success': False,
            'error': "CLOVA STT 서비스 실패",
            'text': '',
            'confidence': 0.0
        }
    
    def _generate_final_response(self, template_result: Dict, ai_result: Dict) -> str:
        """최종 응답 텍스트 생성"""
        # Template Engine 응답을 기본으로 사용
        template_response = template_result.get('response', '')
        
        # AI 분석 결과가 있으면 결합
        if ai_result.get('parent_suggestion'):
            ai_suggestion = ai_result['parent_suggestion']
            # AI 제안이 더 적절하면 사용
            if len(ai_suggestion) > len(template_response):
                return ai_suggestion
        
        return template_response
    
    def _create_error_response(self, error_message: str, start_time: float) -> Dict:
        """오류 응답 생성"""
        return {
            'success': False,
            'error': error_message,
            'processing_time': round(time.time() - start_time, 2),
            'timestamp': int(time.time() * 1000)
        }
    
    def get_system_status(self) -> Dict:
        """시스템 상태 조회"""
        return {
            'clova_stt_available': bool(clova_stt.client_id and clova_stt.client_secret),
            'tts_cache_stats': tts_engine.get_cache_stats(),
            'latency_goal': self.latency_goal,
            'privacy_mode': self.privacy_mode
        }
    
    def clear_tts_cache(self) -> Dict:
        """TTS 캐시 정리"""
        return tts_engine.clear_cache()

# 하이브리드 음성 시스템 인스턴스
hybrid_speech_system = HybridSpeechSystem()
