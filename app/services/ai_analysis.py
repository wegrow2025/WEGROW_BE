import httpx
import json
from typing import Dict, Any, Optional
from app.config import settings
from app.schemas import AudioAnalysisResult


class AIAnalysisService:
    """AI 분석 서비스"""
    
    def __init__(self):
        self.clova_stt_url = settings.clova_stt_api_url
        self.clova_client_id = settings.clova_client_id
        self.clova_client_secret = settings.clova_client_secret
        self.openai_api_key = settings.openai_api_key
    
    async def analyze_audio(self, audio_file_path: str, child_age: int) -> AudioAnalysisResult:
        """오디오 파일 분석"""
        try:
            # 1. 음성 전사 (STT)
            transcription = await self._speech_to_text(audio_file_path)
            
            # 2. 의도 분석
            intent = await self._analyze_intent(transcription, child_age)
            
            # 3. 발달 단계 분석
            stage = await self._analyze_development_stage(transcription, child_age)
            
            # 4. 감정 분석
            emotion = await self._analyze_emotion(transcription, intent)
            
            # 5. 연령 적절성 분석
            age_appropriate = await self._analyze_age_appropriateness(transcription, child_age, stage)
            
            # 6. 부모 코칭 응답 생성
            coaching_response = await self._generate_coaching_response(
                transcription, intent, stage, child_age
            )
            
            result = AudioAnalysisResult(
                transcription=transcription,
                confidence=0.85,  # 실제로는 STT 결과에서 가져옴
                intent=intent,
                emotion=emotion,
                age_appropriate=age_appropriate,
                recommended_response=coaching_response,
                language_development_stage=stage,
                suggestions=[
                    "아이의 의도를 자연스럽게 확장해서 말해주세요",
                    "선택지를 제공하여 대화를 이어가세요"
                ]
            )
            return result
            
        except Exception as e:
            raise Exception(f"AI 분석 중 오류가 발생했습니다: {str(e)}")
    
    async def _speech_to_text(self, audio_file_path: str) -> str:
        """음성 전사 (ClovaSTT 사용)"""
        if not self.clova_client_id or not self.clova_client_secret:
            return "까까"
        
        try:
            async with httpx.AsyncClient() as client:
                with open(audio_file_path, "rb") as audio_file:
                    audio_data = audio_file.read()
                    
                    headers = {
                        'X-NCP-APIGW-API-KEY-ID': self.clova_client_id,
                        'X-NCP-APIGW-API-KEY': self.clova_client_secret,
                        'Content-Type': 'application/octet-stream'
                    }
                    
                    params = {
                        'lang': 'Kor'
                    }
                    
                    response = await client.post(
                        self.clova_stt_url,
                        data=audio_data,
                        headers=headers,
                        params=params
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        return result.get("text", "")
                    else:
                        raise Exception(f"STT API 오류: {response.status_code}")
        except Exception as e:
            # 오류 시 모의 데이터 반환
            return "까까"
    
    async def _analyze_intent(self, transcription: str, child_age: int) -> str:
        """의도 분석"""
        # 유아 친화적 키워드 기반 의도 분석
        intent_keywords = {
            "물품 요청": {
                "keywords": ["까까", "물", "우유", "밥", "과자", "장난감", "주세요", "줘", "먹어", "마셔", "맘마", "음식", "간식", "우유", "물물", "과과"],
                "context": "우리 아가가 맛있는 것, 재미있는 것을 원하는 의도"
            },
            "사람 부르기": {
                "keywords": ["엄마", "아빠", "할머니", "할아버지", "언니", "오빠", "누나", "형", "맘마", "아빠빠", "할머니", "할아버지"],
                "context": "우리 아가가 사랑하는 사람을 부르는 의도"
            },
            "음성 실험": {
                "keywords": ["바바바", "다다다", "가가가", "라라라", "마마마", "나나나", "바바", "다다", "가가", "라라", "마마", "나나", "아아", "어어", "오오"],
                "context": "우리 아가가 소리를 탐험하고 실험하는 단계"
            },
            "감정 표현": {
                "keywords": ["좋아", "싫어", "기뻐", "속상해", "무서워", "재미있어", "아파", "웃어", "하하", "우와", "와", "오", "아이", "예예", "노노"],
                "context": "우리 아가가 기분과 감정을 표현하는 의도"
            },
            "놀이 요청": {
                "keywords": ["놀아", "같이", "더", "놀이", "게임", "책", "그림", "춤", "놀자", "같이놀자", "더놀자", "책책", "그림그림", "춤춤"],
                "context": "우리 아가가 재미있는 놀이를 원하는 의도"
            },
            "부정 표현": {
                "keywords": ["안", "싫어", "하지마", "그만", "싫어해", "안돼", "노노", "싫싫", "안안", "그만그만"],
                "context": "우리 아가가 싫어하거나 그만두고 싶어하는 의도"
            },
            "질문하기": {
                "keywords": ["뭐", "어디", "언제", "왜", "누구", "어떻게", "몇", "뭐뭐", "어디어디", "왜왜", "누구누구"],
                "context": "우리 아가가 궁금한 것을 묻는 의도"
            },
            "도움 요청": {
                "keywords": ["도와", "해줘", "못해", "어려워", "힘들어", "도와줘", "해줘해줘", "못해못해", "어려워어려워"],
                "context": "우리 아가가 도움이나 지원을 요청하는 의도"
            }
        }
        
        # 키워드 매칭 및 컨텍스트 분석
        best_match = None
        max_score = 0
        
        for intent, data in intent_keywords.items():
            score = 0
            keywords = data["keywords"]
            
            # 직접 키워드 매칭
            for keyword in keywords:
                if keyword in transcription:
                    score += 1
            
            # 부분 매칭 (긴 키워드의 경우)
            for keyword in keywords:
                if len(keyword) > 2 and keyword in transcription:
                    score += 0.5
            
            if score > max_score:
                max_score = score
                best_match = intent
        
        # 최소 임계값 이상일 때만 반환
        if max_score >= 0.5:
            return best_match
        
        # 매칭되지 않으면 발달 단계에 따른 기본 의도
        if child_age < 18:
            return "음성 실험"
        elif child_age < 24:
            return "물품 요청"
        else:
            return "놀이 요청"
    
    async def _analyze_development_stage(self, transcription: str, child_age: int) -> str:
        """발달 단계 분석"""
        # 전사된 텍스트의 복잡도 분석
        word_count = len(transcription.split()) if transcription else 0
        syllable_count = len(transcription) if transcription else 0
        
        # 우리 아가 발달 단계별 특성 분석
        if child_age < 12:
            return "옹알이 단계 (우리 아가 소리 탐험 중)"
        elif child_age < 18:
            # 음성 실험과 첫 단어 시기
            if word_count == 0 or syllable_count < 3:
                return "음성 실험 단계 (우리 아가 소리 놀이 중)"
            else:
                return "첫 단어 단계 (우리 아가 첫 말 시작)"
        elif child_age < 24:
            # 단어 이해와 의도 표현
            if word_count <= 1:
                return "단어 이해 단계 (우리 아가 단어 알아가기)"
            else:
                return "의도 표현 단계 (우리 아가 원하는 것 말하기)"
        elif child_age < 30:
            # 두 단어 조합과 문장 구성
            if word_count <= 2:
                return "두 단어 조합 단계 (우리 아가 단어 연결하기)"
            else:
                return "문장 구성 초기 (우리 아가 문장 만들기 시작)"
        elif child_age < 36:
            # 문장 확장과 복잡한 표현
            if word_count <= 3:
                return "문장 구성 단계 (우리 아가 문장 만들기 중)"
            else:
                return "문장 확장 단계 (우리 아가 긴 문장 말하기)"
        else:
            # 고급 언어 능력
            if word_count <= 4:
                return "문장 확장 단계 (우리 아가 긴 문장 말하기)"
            else:
                return "고급 언어 단계 (우리 아가 복잡한 말하기)"
    
    async def _generate_coaching_response(
        self, 
        transcription: str, 
        intent: str, 
        stage: str, 
        child_age: int
    ) -> str:
        """부모 코칭 응답 생성"""
        if not settings.openai_api_key:
            return self._get_default_coaching_response(transcription, intent)
        
        try:
            prompt = f"""
당신은 {child_age}개월 우리 귀여운 아이와 함께 놀고 있는 사랑스러운 엄마/아빠입니다! 아이와 자연스럽고 재미있게 대화해보세요.

## 우리 아이 상황
- 우리 아가 나이: {child_age}개월
- 우리 아가가 말한 것: "{transcription}"
- 우리 아가가 원하는 것: {intent}
- 우리 아가 발달 단계: {stage}

## 엄마/아빠처럼 사랑스럽게 말하는 방법

### 1. 귀엽고 부드러운 톤으로
- "우리 아가~", "귀여운 우리 아이~", "사랑스러운 우리 아가~"
- 높고 밝은 목소리로 "와~", "우와~", "오~" 같은 감탄사
- "맛있겠다~", "좋겠다~", "재미있겠다~" 같은 표현

### 2. 아이처럼 재미있게
- "어떻게 할까요?", "뭐가 좋을까요?", "엄마랑 같이 해볼까요?"
- "더 하고 싶어요?", "또 해볼까요?", "다른 것도 해볼까요?"
- "빨간색? 파란색?", "큰 것? 작은 것?" 같은 선택지

### 3. 감정을 함께 나누기
- "기뻐하는구나~", "신나는구나~", "재미있어하는구나~"
- "궁금해하는구나~", "우리 아가 정말 똑똑하네~"
- "엄마도 기뻐요~", "아빠도 신나요~"

### 4. {child_age}개월 우리 아가 수준에 맞게
- "엄마", "아빠", "맘마", "물", "놀이", "책", "장난감" 같은 기본 단어
- "맛있어요", "좋아요", "싫어요", "더", "또" 같은 쉬운 표현
- 2-3단어로 된 간단한 문장

### 5. 응답 예시
"우리 아가 '{transcription}'라고 말했구나~! [아이의 말을 사랑스럽게 확장]. [재미있는 질문이나 제안]. [사랑스럽게 격려하기]"

이제 우리 귀여운 아이와 자연스럽고 사랑스럽게 대화해보세요:
            """
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.openai_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-3.5-turbo",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 100
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    response_text = result["choices"][0]["message"]["content"].strip()
                    return response_text
                else:
                    return self._get_default_coaching_response(transcription, intent)
                    
        except Exception as e:
            return self._get_default_coaching_response(transcription, intent)
    
    def _get_default_coaching_response(self, transcription: str, intent: str) -> str:
        """기본 코칭 응답"""
        import random
        
        if intent == "물품 요청":
            responses = [
                f"우리 아가~ {transcription} 원하는구나! 엄마가 맛있는 {transcription} 준비해줄게요~ 맛있게 먹을까요?",
                f"와~ {transcription} 주세요? 엄마가 사랑스러운 {transcription} 줄게요~ 어떤 게 더 좋아요?",
                f"좋아요! {transcription} 마시고 싶구나~ 엄마가 컵에 담아줄게요~ 차가운 거? 따뜻한 거?"
            ]
            return random.choice(responses)
        elif intent == "사람 부르기":
            responses = [
                f"우리 아가~ {transcription} 여기 있어요! 반가워요~ 뭐 하고 싶어요?",
                f"와~ {transcription} 부르셨네요! 엄마가 왔어요~ 무슨 일이에요?",
                f"여기 있어요! {transcription}가 왔어요~ 같이 놀까요?"
            ]
            return random.choice(responses)
        elif intent == "놀이 요청":
            responses = [
                f"우와~ 좋아요! 같이 놀자! 블록으로 탑 쌓을까요? 아니면 그림 그릴까요?",
                f"놀이 시간이네요~ 어떤 놀이가 좋아요? 책 읽기? 춤추기?",
                f"재미있는 놀이를 해볼까요~ 뭐 하고 싶어요? 엄마랑 같이 해요!"
            ]
            return random.choice(responses)
        elif intent == "감정 표현":
            responses = [
                f"우리 아가~ {transcription}한 기분이구나! 엄마도 그런 기분 알아요~ 더 이야기해볼까요?",
                f"기분이 {transcription}하구나~ 엄마가 들어줄게요~ 어떤 일이 있었어요?",
                f"우와~ {transcription}한 기분이네요! 정말 좋아요~ 더 자세히 말해줄래요?"
            ]
            return random.choice(responses)
        elif intent == "부정 표현":
            responses = [
                f"우리 아가~ {transcription}라고 하시는구나~ 엄마가 들어줄게요~ 왜 그런 기분이에요?",
                f"그렇구나~ {transcription}한 기분이구나~ 엄마가 도와줄게요~ 어떻게 해주면 좋을까요?",
                f"알겠어요~ {transcription}하시는구나~ 엄마가 함께 있어줄게요~"
            ]
            return random.choice(responses)
        elif intent == "질문하기":
            responses = [
                f"우리 아가~ 궁금한 게 있구나! 좋은 질문이에요~ 엄마가 알려줄게요!",
                f"어떤 걸 궁금해해요? 엄마가 설명해줄게요~",
                f"좋은 질문이네요~ 엄마가 답해줄게요~ 더 궁금한 게 있어요?"
            ]
            return random.choice(responses)
        elif intent == "도움 요청":
            responses = [
                f"우리 아가~ 도움이 필요하구나! 엄마가 도와줄게요~ 어떻게 해주면 좋을까요?",
                f"어려운 일이 있구나~ 엄마가 함께 해줄게요~ 걱정하지 마세요!",
                f"힘들구나~ 엄마가 도와줄게요~ 어떤 걸 도와주면 좋을까요?"
            ]
            return random.choice(responses)
        else:
            responses = [
                f"우와, {transcription}라고 말했네요! 정말 좋아요! 더 이야기해볼까요?",
                f"멋진 말이에요! {transcription}라고 말하는 소리가 정말 귀여워요!",
                f"좋아요! {transcription}라고 말했구나! 엄마가 들어줄게요!"
            ]
            return random.choice(responses)
    
    async def _analyze_emotion(self, transcription: str, intent: str) -> str:
        """감정 분석"""
        # 의도별 기본 감정 매핑
        intent_emotion_map = {
            "물품 요청": "중립",
            "사람 부르기": "긍정적",
            "음성 실험": "호기심",
            "감정 표현": "다양",
            "놀이 요청": "기쁨",
            "부정 표현": "부정적",
            "질문하기": "호기심",
            "도움 요청": "불안"
        }
        
        # 유아 친화적 감정 키워드 분석
        emotion_keywords = {
            "기쁨": ["좋아", "기뻐", "재미있어", "웃어", "하하", "우와", "와", "오", "예예", "하하하", "기쁘다", "좋다"],
            "슬픔": ["울어", "슬퍼", "아파", "속상해", "우우", "아이", "슬프다", "아프다", "속상하다"],
            "화남": ["짜증", "화나", "싫어", "안돼", "노노", "싫싫", "안안", "짜증나", "화나다"],
            "두려움": ["무서워", "겁나", "무서워해", "무서무서", "겁겁", "무섭다", "겁난다"],
            "호기심": ["뭐", "어디", "왜", "어떻게", "궁금", "뭐뭐", "어디어디", "왜왜", "궁금하다", "뭐지"],
            "불안": ["도와", "어려워", "힘들어", "못해", "도와줘", "어려워어려워", "힘들어힘들어", "못해못해"]
        }
        
        # 키워드 매칭으로 감정 분석
        for emotion, keywords in emotion_keywords.items():
            for keyword in keywords:
                if keyword in transcription:
                    return emotion
        
        # 의도 기반 감정 반환
        return intent_emotion_map.get(intent, "중립")
    
    async def _analyze_age_appropriateness(self, transcription: str, child_age: int, stage: str) -> bool:
        """연령 적절성 분석"""
        word_count = len(transcription.split()) if transcription else 0
        
        # 연령별 적절한 발화 수준
        age_appropriate_ranges = {
            (0, 12): (0, 1),      # 옹알이 단계
            (12, 18): (0, 2),     # 첫 단어 단계
            (18, 24): (1, 3),     # 단어 조합 단계
            (24, 30): (2, 4),     # 문장 구성 단계
            (30, 36): (3, 6),     # 문장 확장 단계
            (36, 48): (4, 8)      # 고급 언어 단계
        }
        
        # 연령에 맞는 범위 찾기
        for (min_age, max_age), (min_words, max_words) in age_appropriate_ranges.items():
            if min_age <= child_age < max_age:
                return min_words <= word_count <= max_words
        
        # 기본값: 연령에 맞지 않으면 False
        return False
    
    async def analyze_growth_metrics(self, user_id: str, time_period: str) -> Dict[str, Any]:
        """성장 지표 분석"""
        # 실제로는 데이터베이스에서 사용자 데이터를 가져와서 분석
        return {
            "vocabulary_growth": {
                "current": 42,
                "target": 50,
                "trend": "increasing",
                "weekly_growth": 6
            },
            "sentence_complexity": {
                "two_word_sentences": 9,
                "average_length": 1.8,
                "improvement": 0.3
            },
            "communication_attempts": {
                "daily_average": 14,
                "meaningful_attempts": 5,
                "success_rate": 0.36
            }
        }


# 전역 인스턴스
ai_analysis_service = AIAnalysisService()
