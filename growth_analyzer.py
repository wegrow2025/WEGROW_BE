import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from database import AudioSample, User

class GrowthAnalyzer:
    def __init__(self):
        self.milestones = {
            "옹알이": {"age_range": (0, 12), "key_indicators": ["반복음소", "의도성 발성"]},
            "단어_시작": {"age_range": (12, 18), "key_indicators": ["첫 단어", "가족 호칭"]},
            "단어_발전": {"age_range": (18, 24), "key_indicators": ["2-3음절", "물건 이름"]},
            "문장_시작": {"age_range": (24, 36), "key_indicators": ["단어 조합", "질문"]},
            "문장_발전": {"age_range": (36, 60), "key_indicators": ["복잡한 문장", "추상적 개념"]}
        }
    
    def analyze_user_progress(self, user_id: int, db: Session) -> Dict:
        """사용자별 성장 분석"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "사용자를 찾을 수 없습니다"}
        
        # 최근 30일 데이터
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_samples = db.query(AudioSample).filter(
            AudioSample.user_id == user_id,
            AudioSample.created_at >= thirty_days_ago,
            AudioSample.status == "분석 완료"
        ).all()
        
        if not recent_samples:
            return self._generate_empty_report(user)
        
        # 발달 지표 분석
        progress_indicators = self._analyze_development_indicators(recent_samples, user.child_age_months)
        
        # 성장 트렌드 분석
        growth_trends = self._analyze_growth_trends(recent_samples)
        
        # 다음 단계 예측
        next_milestones = self._predict_next_milestones(user.child_age_months, progress_indicators)
        
        return {
            "user_info": {
                "name": user.name,
                "age_months": user.child_age_months,
                "current_stage": self._get_current_stage(user.child_age_months)
            },
            "progress_indicators": progress_indicators,
            "growth_trends": growth_trends,
            "next_milestones": next_milestones,
            "recommendations": self._generate_recommendations(progress_indicators, user.child_age_months)
        }
    
    def _analyze_development_indicators(self, samples: List, age_months: int) -> Dict:
        """발달 지표 분석"""
        total_samples = len(samples)
        if total_samples == 0:
            return {}
        
        # 기본 통계
        total_syllables = sum(s.syllable_combinations or 0 for s in samples)
        total_meaningful = sum(s.meaningful_attempts or 0 for s in samples)
        
        # 새로운 단어 추출
        all_new_words = []
        for sample in samples:
            if sample.new_words:
                try:
                    words = json.loads(sample.new_words)
                    all_new_words.extend(words)
                except:
                    pass
        
        # 발화 패턴 분석
        utterance_patterns = self._analyze_utterance_patterns(samples)
        
        return {
            "total_interactions": total_samples,
            "average_syllables_per_day": total_syllables / 30,
            "meaningful_attempts_rate": total_meaningful / total_samples if total_samples > 0 else 0,
            "new_words_learned": len(set(all_new_words)),
            "utterance_patterns": utterance_patterns,
            "confidence_trend": self._analyze_confidence_trend(samples)
        }
    
    def _analyze_utterance_patterns(self, samples: List) -> Dict:
        """발화 패턴 분석"""
        patterns = {
            "question_attempts": 0,
            "naming_attempts": 0,
            "imitation_attempts": 0,
            "spontaneous_attempts": 0
        }
        
        for sample in samples:
            intent = sample.intent or ""
            if "질문" in intent or "?" in intent:
                patterns["question_attempts"] += 1
            elif "이름" in intent or "지칭" in intent:
                patterns["naming_attempts"] += 1
            elif "모방" in intent or "따라" in intent:
                patterns["imitation_attempts"] += 1
            else:
                patterns["spontaneous_attempts"] += 1
        
        return patterns
    
    def _analyze_confidence_trend(self, samples: List) -> Dict:
        """신뢰도 트렌드 분석"""
        if len(samples) < 2:
            return {"trend": "stable", "average_confidence": 0}
        
        # 시간순 정렬
        sorted_samples = sorted(samples, key=lambda x: x.created_at)
        
        # 신뢰도 변화 계산
        confidences = [s.confidence or 0 for s in sorted_samples]
        if len(confidences) >= 2:
            trend = "improving" if confidences[-1] > confidences[0] else "stable"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "average_confidence": sum(confidences) / len(confidences),
            "confidence_history": confidences
        }
    
    def _analyze_growth_trends(self, samples: List) -> Dict:
        """성장 트렌드 분석"""
        if len(samples) < 7:  # 최소 1주일 데이터 필요
            return {"trend": "insufficient_data"}
        
        # 주간별 그룹화
        weekly_data = {}
        for sample in samples:
            week = sample.created_at.isocalendar()[1]
            if week not in weekly_data:
                weekly_data[week] = []
            weekly_data[week].append(sample)
        
        # 주간 성장률 계산
        weekly_growth = []
        weeks = sorted(weekly_data.keys())
        
        for i in range(1, len(weeks)):
            prev_week = weekly_data[weeks[i-1]]
            curr_week = weekly_data[weeks[i]]
            
            prev_syllables = sum(s.syllable_combinations or 0 for s in prev_week)
            curr_syllables = sum(s.syllable_combinations or 0 for s in curr_week)
            
            if prev_syllables > 0:
                growth_rate = ((curr_syllables - prev_syllables) / prev_syllables) * 100
                weekly_growth.append(growth_rate)
        
        if weekly_growth:
            avg_growth = sum(weekly_growth) / len(weekly_growth)
            trend = "positive" if avg_growth > 0 else "stable"
        else:
            avg_growth = 0
            trend = "stable"
        
        return {
            "trend": trend,
            "average_weekly_growth": avg_growth,
            "weekly_data": {week: len(samples) for week, samples in weekly_data.items()}
        }
    
    def _predict_next_milestones(self, age_months: int, indicators: Dict) -> List[Dict]:
        """다음 발달 단계 예측"""
        current_stage = self._get_current_stage(age_months)
        next_stages = []
        
        for stage, info in self.milestones.items():
            if info["age_range"][0] <= age_months <= info["age_range"][1]:
                # 현재 단계
                next_stages.append({
                    "stage": stage,
                    "status": "current",
                    "progress": self._calculate_stage_progress(indicators, stage),
                    "key_indicators": info["key_indicators"]
                })
            elif info["age_range"][0] > age_months:
                # 다음 단계
                next_stages.append({
                    "stage": stage,
                    "status": "upcoming",
                    "expected_age": info["age_range"][0],
                    "key_indicators": info["key_indicators"]
                })
                break
        
        return next_stages
    
    def _get_current_stage(self, age_months: int) -> str:
        """현재 발달 단계 결정"""
        for stage, info in self.milestones.items():
            if info["age_range"][0] <= age_months <= info["age_range"][1]:
                return stage
        return "문장_발전"
    
    def _calculate_stage_progress(self, indicators: Dict, stage: str) -> float:
        """단계별 진행률 계산"""
        if not indicators:
            return 0.0
        
        # 단계별 기준에 따른 진행률 계산
        if stage == "옹알이":
            return min(1.0, indicators.get("meaningful_attempts_rate", 0) * 2)
        elif stage == "단어_시작":
            return min(1.0, indicators.get("new_words_learned", 0) / 10)
        elif stage == "단어_발전":
            return min(1.0, indicators.get("average_syllables_per_day", 0) / 5)
        else:
            return min(1.0, indicators.get("utterance_patterns", {}).get("spontaneous_attempts", 0) / 10)
    
    def _generate_recommendations(self, indicators: Dict, age_months: int) -> List[str]:
        """개인화된 권장사항 생성"""
        recommendations = []
        
        if indicators.get("meaningful_attempts_rate", 0) < 0.3:
            recommendations.append("아이의 발화에 더 자주 반응해주세요")
        
        if indicators.get("new_words_learned", 0) < 5:
            recommendations.append("일상적인 물건의 이름을 자주 말해주세요")
        
        if indicators.get("utterance_patterns", {}).get("question_attempts", 0) < 2:
            recommendations.append("아이에게 질문을 자주 해주세요")
        
        if age_months > 18 and indicators.get("average_syllables_per_day", 0) < 3:
            recommendations.append("2음절 이상의 단어를 사용해주세요")
        
        return recommendations
    
    def _generate_empty_report(self, user: User) -> Dict:
        """데이터가 없을 때의 기본 리포트"""
        return {
            "user_info": {
                "name": user.name,
                "age_months": user.child_age_months,
                "current_stage": self._get_current_stage(user.child_age_months)
            },
            "progress_indicators": {},
            "growth_trends": {"trend": "no_data"},
            "next_milestones": [],
            "recommendations": ["더 많은 상호작용을 통해 데이터를 수집해주세요"]
        }

# 성장 분석기 인스턴스
growth_analyzer = GrowthAnalyzer()
