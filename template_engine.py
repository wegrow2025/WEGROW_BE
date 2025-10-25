import json
import os
import re
from typing import Dict, List, Optional
from datetime import datetime

class TemplatePolicyEngine:
    def __init__(self, assets_dir: str = "assets"):
        self.assets_dir = assets_dir
        self.lexicon = self._load_lexicon()
        self.templates = self._load_templates()
        self.rules = self._load_rules()
        
    def _load_lexicon(self) -> Dict:
        """한국어 어휘 사전 로드"""
        lexicon_path = os.path.join(self.assets_dir, "lexicon_ko.csv")
        lexicon = {}
        
        if os.path.exists(lexicon_path):
            with open(lexicon_path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) >= 2:
                        word = parts[0]
                        category = parts[1]
                        lexicon[word] = category
        else:
            # 기본 어휘 사전 생성
            lexicon = {
                "엄마": "가족",
                "아빠": "가족", 
                "물": "물건",
                "까까": "음식",
                "안녕": "인사",
                "고마워": "감사",
                "미안": "사과",
                "좋아": "감정",
                "싫어": "감정"
            }
            
        return lexicon
    
    def _load_templates(self) -> Dict:
        """응답 템플릿 로드"""
        templates_path = os.path.join(self.assets_dir, "templates_ko.json")
        
        if os.path.exists(templates_path):
            with open(templates_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 기본 템플릿 생성
            return {
                "greeting": [
                    "안녕! 반가워!",
                    "안녕하세요!",
                    "반가워요!"
                ],
                "family": [
                    "맞아! {word}야!",
                    "정말 좋은 말이야!",
                    "{word}를 잘 말했어!"
                ],
                "object": [
                    "맞아! {word}이야!",
                    "정말 잘 말했어!",
                    "{word}를 정확히 말했구나!"
                ],
                "food": [
                    "맛있는 {word}이구나!",
                    "정말 좋은 음식이야!",
                    "{word}를 좋아하는구나!"
                ],
                "emotion": [
                    "정말 좋은 기분이구나!",
                    "그런 마음이구나!",
                    "정말 좋아하는구나!"
                ],
                "default": [
                    "정말 좋은 말이야!",
                    "잘 말했어!",
                    "정말 대단해!"
                ]
            }
    
    def _load_rules(self) -> Dict:
        """규칙 오버라이드 로드"""
        rules_path = os.path.join(self.assets_dir, "rules_overrides.json")
        
        if os.path.exists(rules_path):
            with open(rules_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 기본 규칙 생성
            return {
                "context_aware": True,
                "age_appropriate": True,
                "encouragement_level": "high",
                "response_length": "short"
            }
    
    def process_text(self, text: str, child_age_months: int, context: Dict = None) -> Dict:
        """텍스트 처리 및 응답 생성"""
        # 1. 형태소 분석
        morphemes = self._analyze_morphemes(text)
        
        # 2. 의도 파악
        intent = self._classify_intent(text, morphemes)
        
        # 3. 컨텍스트 인식 템플릿 선택
        template_category = self._select_template_category(intent, morphemes, child_age_months)
        
        # 4. 응답 생성
        response = self._generate_response(template_category, text, morphemes, child_age_months)
        
        return {
            "original_text": text,
            "morphemes": morphemes,
            "intent": intent,
            "template_category": template_category,
            "response": response,
            "confidence": self._calculate_confidence(text, morphemes, intent)
        }
    
    def _analyze_morphemes(self, text: str) -> List[str]:
        """간단한 형태소 분석"""
        # 기본적인 한국어 형태소 분석
        morphemes = []
        
        # 단어 단위로 분리
        words = re.findall(r'[가-힣]+', text)
        
        for word in words:
            # 어휘 사전에서 카테고리 확인
            category = self.lexicon.get(word, "unknown")
            morphemes.append({
                "word": word,
                "category": category,
                "length": len(word)
            })
        
        return morphemes
    
    def _classify_intent(self, text: str, morphemes: List[Dict]) -> str:
        """의도 분류"""
        # 인사 의도
        if any(word in text for word in ["안녕", "안녕하세요", "안녕하세요"]):
            return "greeting"
        
        # 가족 호칭 의도
        if any(morpheme["category"] == "가족" for morpheme in morphemes):
            return "family"
        
        # 물건 지칭 의도
        if any(morpheme["category"] == "물건" for morpheme in morphemes):
            return "object"
        
        # 음식 의도
        if any(morpheme["category"] == "음식" for morpheme in morphemes):
            return "food"
        
        # 감정 표현 의도
        if any(morpheme["category"] == "감정" for morpheme in morphemes):
            return "emotion"
        
        # 질문 의도
        if "?" in text or "뭐" in text or "어디" in text:
            return "question"
        
        return "general"
    
    def _select_template_category(self, intent: str, morphemes: List[Dict], child_age_months: int) -> str:
        """컨텍스트 인식 템플릿 선택"""
        # 나이에 따른 템플릿 조정
        if child_age_months <= 18:
            # 옹알이/단어 시작 단계
            if intent == "family":
                return "family_simple"
            elif intent == "object":
                return "object_simple"
            else:
                return "encouragement"
        elif child_age_months <= 36:
            # 단어 발전/문장 시작 단계
            return intent
        else:
            # 문장 발전 단계
            return intent
    
    def _generate_response(self, template_category: str, text: str, morphemes: List[Dict], child_age_months: int) -> str:
        """응답 생성"""
        # 템플릿 선택
        templates = self.templates.get(template_category, self.templates["default"])
        
        # 나이에 따른 응답 길이 조정
        if child_age_months <= 18:
            # 짧고 간단한 응답
            response = templates[0] if templates else "정말 좋아!"
        elif child_age_months <= 36:
            # 중간 길이 응답
            response = templates[1] if len(templates) > 1 else templates[0]
        else:
            # 긴 응답
            response = templates[-1] if templates else "정말 좋은 말이야!"
        
        # 템플릿 변수 치환
        if morphemes:
            main_word = morphemes[0]["word"]
            response = response.replace("{word}", main_word)
        
        return response
    
    def _calculate_confidence(self, text: str, morphemes: List[Dict], intent: str) -> float:
        """신뢰도 계산"""
        confidence = 0.5  # 기본 신뢰도
        
        # 어휘 사전에 있는 단어가 많을수록 높은 신뢰도
        known_words = sum(1 for morpheme in morphemes if morpheme["category"] != "unknown")
        if morphemes:
            confidence += (known_words / len(morphemes)) * 0.3
        
        # 의도가 명확할수록 높은 신뢰도
        if intent != "general":
            confidence += 0.2
        
        return min(1.0, confidence)

# Template/Policy Engine 인스턴스
template_engine = TemplatePolicyEngine()
