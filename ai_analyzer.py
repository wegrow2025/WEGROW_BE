import openai
import json
import base64
import io
import librosa
import numpy as np
from typing import Dict, List, Optional, Tuple
from config import settings

class AIAnalyzer:
    def __init__(self):
        openai.api_key = settings.openai_api_key
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
    
    def get_development_stage(self, child_age_months: int) -> str:
        """아이 나이에 따른 발달 단계 결정"""
        if child_age_months <= 12:
            return "옹알이"
        elif child_age_months <= 18:
            return "단어_시작"
        elif child_age_months <= 24:
            return "단어_발전"
        elif child_age_months <= 36:
            return "문장_시작"
        else:
            return "문장_발전"
    
    def create_analysis_prompt(self, audio_data: str, child_age_months: int, 
                             development_stage: str) -> str:
        """아이 발달 단계에 따른 맞춤형 분석 프롬프트 생성"""
        
        base_prompt = f"""
당신은 {child_age_months}개월 아이의 언어 발달을 분석하는 전문가입니다.
현재 발달 단계: {development_stage}

다음 JSON 형식으로 분석 결과를 제공해주세요:
{{
    "transcription": "전사된 텍스트",
    "confidence": 0.95,
    "intent": "의도 분석",
    "syllable_combinations": 2,
    "meaningful_attempts": 1,
    "new_words": ["새로운 단어들"],
    "parent_suggestion": "부모 권장 반응",
    "development_notes": "발달 관련 메모"
}}
"""
        
        if development_stage == "옹알이":
            return base_prompt + """
옹알이 단계 분석 지침:
- "까까", "바바", "맘마" 같은 반복음소에 집중
- 의도성 있는 발성인지 판단
- 부모는 아이의 소리를 그대로 따라해주는 것이 좋음
- 의미 있는 시도는 의사소통 의도가 있는 발성
"""
        
        elif development_stage == "단어_시작":
            return base_prompt + """
단어 시작 단계 분석 지침:
- "엄마", "아빠", "물" 같은 첫 단어들 인식
- 발음이 부정확해도 의도를 파악
- 부모는 정확한 발음으로 반복해주기
- 새로운 단어 시도 시 긍정적 반응
"""
        
        elif development_stage == "단어_발전":
            return base_prompt + """
단어 발전 단계 분석 지침:
- 2-3음절 단어 조합 인식
- 문맥을 통한 의도 파악
- 부모는 문장으로 확장해서 응답
- "마마" -> "엄마, 맞아!" 같은 교정
"""
        
        elif development_stage == "문장_시작":
            return base_prompt + """
문장 시작 단계 분석 지침:
- 2-3단어 조합 인식
- 문법적 오류는 자연스럽게 교정
- 부모는 완전한 문장으로 응답
- 질문과 답변 형태의 대화 유도
"""
        
        else:  # 문장_발전
            return base_prompt + """
문장 발전 단계 분석 지침:
- 복잡한 문장 구조 인식
- 추상적 개념 표현 파악
- 부모는 대화를 확장하고 질문하기
- 창의적 표현 격려
"""
    
    def analyze_audio(self, audio_base64: str, child_age_months: int, 
                     user_id: int) -> Dict:
        """음성 데이터 분석"""
        try:
            # Base64 디코딩
            audio_bytes = base64.b64decode(audio_base64)
            
            # 오디오 특성 분석
            audio_features = self._extract_audio_features(audio_bytes)
            
            # 발달 단계 결정
            development_stage = self.get_development_stage(child_age_months)
            
            # AI 분석 프롬프트 생성
            prompt = self.create_analysis_prompt(
                audio_base64, child_age_months, development_stage
            )
            
            # OpenAI API 호출
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "당신은 아동 언어 발달 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            # JSON 파싱
            analysis_result = json.loads(response.choices[0].message.content)
            
            # 오디오 특성 추가
            analysis_result.update({
                "audio_features": audio_features,
                "development_stage": development_stage,
                "user_id": user_id
            })
            
            return analysis_result
            
        except Exception as e:
            return {
                "error": str(e),
                "transcription": "",
                "confidence": 0.0,
                "intent": "분석 실패",
                "syllable_combinations": 0,
                "meaningful_attempts": 0,
                "new_words": [],
                "parent_suggestion": "다시 시도해주세요.",
                "development_notes": "분석 중 오류가 발생했습니다."
            }
    
    def _extract_audio_features(self, audio_bytes: bytes) -> Dict:
        """오디오 특성 추출"""
        try:
            # librosa로 오디오 로드
            audio_data, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
            
            # 기본 특성
            duration = len(audio_data) / sr
            rms_energy = np.sqrt(np.mean(audio_data**2))
            
            # 음성 활동 감지 (VAD)
            frame_length = 2048
            hop_length = 512
            energy = librosa.feature.rms(y=audio_data, frame_length=frame_length, hop_length=hop_length)[0]
            voice_activity = np.sum(energy > np.mean(energy) * 0.1) / len(energy)
            
            # 피치 분석
            pitches, magnitudes = librosa.piptrack(y=audio_data, sr=sr)
            pitch_values = pitches[pitches > 0]
            avg_pitch = np.mean(pitch_values) if len(pitch_values) > 0 else 0
            
            # 스펙트럼 중심
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sr)[0]
            avg_spectral_centroid = np.mean(spectral_centroids)
            
            return {
                "duration": duration,
                "rms_energy": float(rms_energy),
                "voice_activity_ratio": float(voice_activity),
                "average_pitch": float(avg_pitch),
                "spectral_centroid": float(avg_spectral_centroid),
                "sample_rate": sr
            }
            
        except Exception as e:
            return {
                "duration": 0,
                "rms_energy": 0,
                "voice_activity_ratio": 0,
                "average_pitch": 0,
                "spectral_centroid": 0,
                "sample_rate": 16000,
                "error": str(e)
            }
    
    def generate_tts_response(self, transcription: str, development_stage: str, 
                            child_age_months: int) -> str:
        """발달 단계에 따른 TTS 응답 생성"""
        
        if development_stage == "옹알이":
            # 옹알이 단계: 아이 소리 그대로 따라하기
            return transcription
        
        elif development_stage == "단어_시작":
            # 단어 시작: 정확한 발음으로 반복
            if transcription in ["마마", "맘마", "엄마"]:
                return "엄마"
            elif transcription in ["아바", "아빠", "아빠"]:
                return "아빠"
            elif transcription in ["물", "물물", "물"]:
                return "물"
            else:
                return transcription
        
        elif development_stage == "단어_발전":
            # 단어 발전: 문장으로 확장
            if "엄마" in transcription:
                return "엄마, 맞아! 엄마가 여기 있어."
            elif "아빠" in transcription:
                return "아빠, 맞아! 아빠가 여기 있어."
            elif "물" in transcription:
                return "물을 원하는구나! 물을 줄게."
            else:
                return f"{transcription}, 맞아!"
        
        elif development_stage == "문장_시작":
            # 문장 시작: 완전한 문장으로 응답
            if "엄마" in transcription:
                return "엄마가 여기 있어. 무엇을 도와줄까?"
            elif "아빠" in transcription:
                return "아빠가 여기 있어. 무엇을 원해?"
            else:
                return f"네, {transcription}. 더 자세히 말해줄 수 있어?"
        
        else:  # 문장_발전
            # 문장 발전: 대화 확장
            return f"정말 좋은 말이야! {transcription}에 대해 더 이야기해볼까?"

# 전역 AI 분석기 인스턴스
ai_analyzer = AIAnalyzer()
