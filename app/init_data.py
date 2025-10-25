from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Base, Tip
from app.config import settings


def init_database():
    """데이터베이스 테이블 생성"""
    Base.metadata.create_all(bind=engine)


def init_tips_data():
    """팁 데이터 초기화"""
    db = SessionLocal()
    
    try:
        # 기존 팁 데이터 확인
        existing_tips = db.query(Tip).count()
        if existing_tips > 0:
            return
        
        # 기본 팁 데이터
        tips_data = [
            {
                "level": "음성 실험 단계",
                "age_range": [12, 18],
                "scenario": "아이: \"바바바\"",
                "parent_response": "엄마(권장): \"바나나? 맛있는 바나나네요. 배? 노란 배?\"",
                "explanation": "음절 반복은 음성 실험입니다. 그 음절로 시작하는 실제 단어들을 여러 개 들려주세요.",
                "tags": ["음성실험", "모델링", "어휘확장"],
                "effectiveness": 0.85
            },
            {
                "level": "단어 이해 단계",
                "age_range": [18, 24],
                "scenario": "아이: \"까까\" (물을 가리키며)",
                "parent_response": "엄마(권장): \"물 주세요? 엄마가 물 줄까요? 물 시원하지?\"",
                "explanation": "아이가 뭔가를 원하는 의도를 보이면, 그것을 자연스러운 문장으로 확장해 말해주세요.",
                "tags": ["의도표현", "확장", "선택지제공"],
                "effectiveness": 0.92
            },
            {
                "level": "두 단어 조합 단계",
                "age_range": [24, 30],
                "scenario": "아이: \"또!\"",
                "parent_response": "엄마(권장): \"또 해요? 또 하고 싶어요?\"",
                "explanation": "아이의 한 단어를 길게 확장해서 말해주면, 아이가 자연스럽게 더 긴 표현을 들을 수 있습니다.",
                "tags": ["확장", "모델링", "대화이어가기"],
                "effectiveness": 0.88
            },
            {
                "level": "감정 표현 초기",
                "age_range": [18, 30],
                "scenario": "아이가 웃으면서 옹알이함",
                "parent_response": "엄마(권장): \"우와, 즐거워? 엄청 재미있어?\"",
                "explanation": "감정 표현이 나타나면, 그 감정을 이름지어서 말해주면 정서 어휘 발달을 돕습니다.",
                "tags": ["감정표현", "정서어휘", "공감"],
                "effectiveness": 0.90
            },
            {
                "level": "아침 식사",
                "age_range": [18, 24],
                "scenario": "아이: \"우유\"",
                "parent_response": "도담: \"우-유 마실래? 우유 컵을 두 손으로 잡아볼까?\"",
                "explanation": "핵심 단어 반복으로 주의 집중",
                "tags": ["반복", "주의집중", "일상활동"],
                "effectiveness": 0.87
            },
            {
                "level": "놀이 시간(블록)",
                "age_range": [24, 30],
                "scenario": "아이: \"더!\"",
                "parent_response": "도담: \"더 쌓자. 높은 탑? 낮은 탑? 하나, 둘—올려볼까?\"",
                "explanation": "반복 + 선택 질문으로 자발 발화 유도",
                "tags": ["놀이", "선택질문", "자발발화"],
                "effectiveness": 0.91
            },
            {
                "level": "책 읽기",
                "age_range": [18, 30],
                "scenario": "아이: \"읽어\"",
                "parent_response": "도담: \"더 읽자. 이 페이지에서 뭐가 보일까? 고양이? 기차?\"",
                "explanation": "짧은 확장 발화(모델링)로 어휘 넓히기",
                "tags": ["책읽기", "어휘확장", "모델링"],
                "effectiveness": 0.89
            },
            {
                "level": "저녁 정리",
                "age_range": [24, 30],
                "scenario": "아이: \"신발\"",
                "parent_response": "도담: \"신발 정리하자. 신발—여기, 신발장에 쏙! 우리 같이 넣어볼까?\"",
                "explanation": "동작과 말 연결(행동 언어화)",
                "tags": ["정리", "행동언어화", "일상활동"],
                "effectiveness": 0.86
            }
        ]
        
        # 팁 데이터 삽입
        for tip_data in tips_data:
            tip = Tip(**tip_data)
            db.add(tip)
        
        db.commit()
        
    except Exception as e:
        db.rollback()
    finally:
        db.close()


def init_all_data():
    """모든 초기 데이터 설정"""
    # 데이터베이스 테이블 생성
    init_database()
    
    # 팁 데이터 초기화
    init_tips_data()


if __name__ == "__main__":
    init_all_data()
