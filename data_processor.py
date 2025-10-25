import os
import re
import json
from typing import List, Dict, Tuple
from collections import Counter

class ChildLanguageDataProcessor:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.child_utterances = []
        self.mother_utterances = []
        self.conversation_pairs = []
        
    def load_data(self) -> Dict:
        """데이터셋 로드 및 전처리"""
        print("데이터셋 로딩 시작...")
        
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.txt'):
                file_path = os.path.join(self.data_dir, filename)
                self._process_file(file_path)
        
        print(f"총 {len(self.child_utterances)}개의 아동 발화 수집")
        print(f"총 {len(self.mother_utterances)}개의 어머니 발화 수집")
        
        return {
            "child_utterances": self.child_utterances,
            "mother_utterances": self.mother_utterances,
            "conversation_pairs": self.conversation_pairs
        }
    
    def _process_file(self, file_path: str):
        """개별 파일 처리"""
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        current_mother = ""
        current_child = ""
        
        for line in lines:
            line = line.strip()
            if line.startswith('MOT:'):
                if current_child:
                    # 이전 대화 쌍 저장
                    self.conversation_pairs.append({
                        "mother": current_mother,
                        "child": current_child,
                        "file": os.path.basename(file_path)
                    })
                    current_mother = ""
                    current_child = ""
                
                current_mother = line[4:].strip()
                self.mother_utterances.append(current_mother)
                
            elif line.startswith('CHI:'):
                current_child = line[4:].strip()
                self.child_utterances.append(current_child)
    
    def analyze_child_utterances(self) -> Dict:
        """아동 발화 분석"""
        print("아동 발화 분석 중...")
        
        # 발화 길이 분석
        utterance_lengths = [len(utterance) for utterance in self.child_utterances]
        
        # 단어 빈도 분석
        all_words = []
        for utterance in self.child_utterances:
            words = re.findall(r'[가-힣]+', utterance)
            all_words.extend(words)
        
        word_freq = Counter(all_words)
        
        # 발화 패턴 분석
        patterns = {
            "single_syllable": len([u for u in self.child_utterances if len(u) == 1]),
            "two_syllable": len([u for u in self.child_utterances if len(u) == 2]),
            "three_syllable": len([u for u in self.child_utterances if len(u) == 3]),
            "long_utterances": len([u for u in self.child_utterances if len(u) > 3])
        }
        
        return {
            "total_utterances": len(self.child_utterances),
            "average_length": sum(utterance_lengths) / len(utterance_lengths) if utterance_lengths else 0,
            "word_frequency": dict(word_freq.most_common(20)),
            "patterns": patterns,
            "sample_utterances": self.child_utterances[:10]
        }
    
    def generate_development_insights(self) -> Dict:
        """발달 인사이트 생성"""
        analysis = self.analyze_child_utterances()
        
        insights = {
            "language_development_stage": self._determine_development_stage(analysis),
            "key_observations": self._generate_observations(analysis),
            "recommendations": self._generate_recommendations(analysis)
        }
        
        return insights
    
    def _determine_development_stage(self, analysis: Dict) -> str:
        """발달 단계 결정"""
        avg_length = analysis["average_length"]
        patterns = analysis["patterns"]
        
        if avg_length <= 1.5:
            return "옹알이_단계"
        elif avg_length <= 2.5:
            return "단어_시작_단계"
        elif avg_length <= 3.5:
            return "단어_발전_단계"
        else:
            return "문장_시작_단계"
    
    def _generate_observations(self, analysis: Dict) -> List[str]:
        """관찰사항 생성"""
        observations = []
        
        if analysis["patterns"]["single_syllable"] > analysis["patterns"]["long_utterances"]:
            observations.append("단음절 발화가 많아 옹알이 단계에 해당")
        
        if "엄마" in analysis["word_frequency"] or "아빠" in analysis["word_frequency"]:
            observations.append("가족 호칭어 사용이 활발함")
        
        if analysis["average_length"] > 2:
            observations.append("2음절 이상의 발화가 증가하여 언어 발달이 진행 중")
        
        return observations
    
    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """권장사항 생성"""
        recommendations = []
        
        stage = self._determine_development_stage(analysis)
        
        if stage == "옹알이_단계":
            recommendations.append("아이의 옹알이를 그대로 따라해주세요")
            recommendations.append("단순한 소리 놀이를 통해 발성 연습을 도와주세요")
        elif stage == "단어_시작_단계":
            recommendations.append("정확한 발음으로 단어를 반복해주세요")
            recommendations.append("일상적인 물건의 이름을 자주 말해주세요")
        elif stage == "단어_발전_단계":
            recommendations.append("아이의 말을 문장으로 확장해서 응답해주세요")
            recommendations.append("질문과 답변 형태의 대화를 유도해주세요")
        
        return recommendations

# 데이터 처리기 인스턴스
data_processor = ChildLanguageDataProcessor()
