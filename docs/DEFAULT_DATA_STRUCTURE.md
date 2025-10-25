# We:Grow 기본 데이터 구조

## 1. 사용자 기본 설정

### 1.1 신규 사용자 기본값
```json
{
  "user": {
    "id": "user_{uuid}",
    "email": "user@example.com",
    "name": "부모님",
    "childAge": 18,
    "createdAt": "2025-01-25T00:00:00Z",
    "lastLoginAt": null
  },
  "settings": {
    "recordingCollection": true,
    "analysisUsage": true,
    "coachingRecommendations": true,
    "notificationsEnabled": true,
    "emailReports": true,
    "dataRetentionDays": 365,
    "language": "ko-KR",
    "timezone": "Asia/Seoul"
  }
}
```

### 1.2 프라이버시 기본 설정
```json
{
  "privacy": {
    "dataCollection": {
      "audioRecording": true,
      "analysisUsage": true,
      "coachingRecommendations": true,
      "researchParticipation": false
    },
    "dataSharing": {
      "thirdParty": false,
      "anonymizedResearch": false,
      "familySharing": false
    },
    "retention": {
      "audioData": 30,
      "analysisResults": 365,
      "userProfile": "permanent"
    }
  }
}
```

## 2. 성장 단계별 기본 데이터

### 2.1 18개월 기본 데이터
```json
{
  "ageGroup": "18개월",
  "targets": {
    "vocabulary": {
      "minimum": 10,
      "target": 15,
      "excellent": 25
    },
    "sentences": {
      "minimum": 0,
      "target": 0,
      "excellent": 2
    },
    "communicationAttempts": {
      "daily": 8,
      "meaningful": 3
    }
  },
  "focusAreas": [
    "단어 이해",
    "음성 실험", 
    "의도 표현",
    "소리 모방"
  ],
  "milestones": [
    "10-15개 단어 이해",
    "간단한 요청 표현",
    "음절 반복 옹알이",
    "부모 말 따라하기"
  ]
}
```

### 2.2 24개월 기본 데이터
```json
{
  "ageGroup": "24개월",
  "targets": {
    "vocabulary": {
      "minimum": 25,
      "target": 50,
      "excellent": 100
    },
    "sentences": {
      "minimum": 2,
      "target": 5,
      "excellent": 10
    },
    "communicationAttempts": {
      "daily": 15,
      "meaningful": 8
    }
  },
  "focusAreas": [
    "두 단어 조합",
    "감정 표현",
    "선택 질문",
    "역할놀이"
  ],
  "milestones": [
    "50개 이상 단어 사용",
    "두 단어 문장 구성",
    "감정 표현하기",
    "질문에 답하기"
  ]
}
```

### 2.3 30개월 기본 데이터
```json
{
  "ageGroup": "30개월",
  "targets": {
    "vocabulary": {
      "minimum": 100,
      "target": 200,
      "excellent": 300
    },
    "sentences": {
      "minimum": 5,
      "target": 10,
      "excellent": 15
    },
    "communicationAttempts": {
      "daily": 25,
      "meaningful": 15
    }
  },
  "focusAreas": [
    "문장 확장",
    "이야기하기",
    "질문하기",
    "상상놀이"
  ],
  "milestones": [
    "200개 이상 단어 사용",
    "3-4단어 문장 구성",
    "이야기 나누기",
    "상상놀이 참여"
  ]
}
```

## 3. 팁 데이터베이스

### 3.1 발달 단계별 팁
```json
{
  "tips": [
    {
      "id": 1,
      "level": "음성 실험 단계",
      "ageRange": [12, 18],
      "scenario": "아이: \"바바바\"",
      "parentResponse": "엄마(권장): \"바나나? 맛있는 바나나네요. 배? 노란 배?\"",
      "explanation": "음절 반복은 음성 실험입니다. 그 음절로 시작하는 실제 단어들을 여러 개 들려주세요.",
      "tags": ["음성실험", "모델링", "어휘확장"],
      "effectiveness": 0.85
    },
    {
      "id": 2,
      "level": "단어 이해 단계",
      "ageRange": [18, 24],
      "scenario": "아이: \"까까\" (물을 가리키며)",
      "parentResponse": "엄마(권장): \"물 주세요? 엄마가 물 줄까요? 물 시원하지?\"",
      "explanation": "아이가 뭔가를 원하는 의도를 보이면, 그것을 자연스러운 문장으로 확장해 말해주세요.",
      "tags": ["의도표현", "확장", "선택지제공"],
      "effectiveness": 0.92
    },
    {
      "id": 3,
      "level": "두 단어 조합 단계",
      "ageRange": [24, 30],
      "scenario": "아이: \"또!\"",
      "parentResponse": "엄마(권장): \"또 해요? 또 하고 싶어요?\"",
      "explanation": "아이의 한 단어를 길게 확장해서 말해주면, 아이가 자연스럽게 더 긴 표현을 들을 수 있습니다.",
      "tags": ["확장", "모델링", "대화이어가기"],
      "effectiveness": 0.88
    },
    {
      "id": 4,
      "level": "감정 표현 초기",
      "ageRange": [18, 30],
      "scenario": "아이가 웃으면서 옹알이함",
      "parentResponse": "엄마(권장): \"우와, 즐거워? 엄청 재미있어?\"",
      "explanation": "감정 표현이 나타나면, 그 감정을 이름지어서 말해주면 정서 어휘 발달을 돕습니다.",
      "tags": ["감정표현", "정서어휘", "공감"],
      "effectiveness": 0.90
    }
  ]
}
```

### 3.2 상황별 팁
```json
{
  "situationalTips": [
    {
      "situation": "아침 식사",
      "ageRange": [18, 24],
      "script": "아이: \"우유\" → 도담: \"우-유 마실래? 우유 컵을 두 손으로 잡아볼까?\"",
      "focus": "핵심 단어 반복으로 주의 집중",
      "effectiveness": 0.87
    },
    {
      "situation": "놀이 시간(블록)",
      "ageRange": [24, 30],
      "script": "아이: \"더!\" → 도담: \"더 쌓자. 높은 탑? 낮은 탑? 하나, 둘—올려볼까?\"",
      "focus": "반복 + 선택 질문으로 자발 발화 유도",
      "effectiveness": 0.91
    },
    {
      "situation": "책 읽기",
      "ageRange": [18, 30],
      "script": "아이: \"읽어\" → 도담: \"더 읽자. 이 페이지에서 뭐가 보일까? 고양이? 기차?\"",
      "focus": "짧은 확장 발화(모델링)로 어휘 넓히기",
      "effectiveness": 0.89
    },
    {
      "situation": "저녁 정리",
      "ageRange": [24, 30],
      "script": "아이: \"신발\" → 도담: \"신발 정리하자. 신발—여기, 신발장에 쏙! 우리 같이 넣어볼까?\"",
      "focus": "동작과 말 연결(행동 언어화)",
      "effectiveness": 0.86
    }
  ]
}
```

## 4. 일일 리포트 기본 템플릿

### 4.1 기본 리포트 구조
```json
{
  "dailyReport": {
    "date": "2025-01-25",
    "vocalizations": 14,
    "syllableCombinations": 3,
    "meaningfulAttempts": 5,
    "newWords": 1,
    "previousDay": {
      "vocalizations": 12
    },
    "summary": "좋은 소식! 아이가 오늘 처음으로 두 음절을 조합해서 발성했어요.",
    "recommendedResponse": "물? 물 주세요? 엄마가 물 줄까요?",
    "growthIndicators": {
      "vocabularyGrowth": 0.18,
      "communicationImprovement": 0.25,
      "newSkills": ["두 음절 조합"]
    }
  }
}
```

### 4.2 성장 분석 기본 템플릿
```json
{
  "growthAnalysis": {
    "period": "weekly",
    "vocabularyCount": 42,
    "twoWordSentences": 9,
    "conversationDuration": 6,
    "progressMetrics": [
      {
        "label": "활용 어휘",
        "value": "42 단어",
        "helper": "목표 50 단어",
        "trend": "지난주보다 6개 늘었어요!",
        "progress": 84,
        "color": "#E17AA4"
      }
    ],
    "recommendations": [
      {
        "title": "집 안 단어 탐험",
        "detail": "컵, 의자, 신발 같은 물건에 이름표를 붙여요.",
        "tip": "이번 주엔 새로운 단어 6개를 골라 집중해볼까요?"
      }
    ]
  }
}
```

## 5. 타임라인 기본 데이터

### 5.1 타임라인 항목 구조
```json
{
  "timelineItem": {
    "id": "timeline_123",
    "date": "2025-01-25",
    "time": "14:32",
    "childUtterance": "까까",
    "intent": "물품 요청",
    "parentResponse": "물 주세요? 라고 말해주세요",
    "audioUrl": "/api/audio/samples/123/play",
    "duration": 3,
    "confidence": 0.85,
    "analysisResult": {
      "transcription": "까까",
      "intent": "물품 요청",
      "confidence": 0.85,
      "recommendedResponse": "물 주세요? 엄마가 물 줄까요?",
      "languageDevelopmentStage": "두 단어 조합 초기"
    }
  }
}
```

## 6. 설정 기본값

### 6.1 알림 설정
```json
{
  "notifications": {
    "newWords": true,
    "milestones": true,
    "dailyReminders": true,
    "weeklyReports": true,
    "coachingTips": true,
    "soundEnabled": true,
    "vibrationEnabled": true
  }
}
```

### 6.2 분석 설정
```json
{
  "analysis": {
    "autoAnalysis": true,
    "realTimeProcessing": true,
    "confidenceThreshold": 0.7,
    "languageDetection": true,
    "emotionAnalysis": true,
    "developmentTracking": true
  }
}
```

## 7. 에러 메시지 기본값

### 7.1 일반 에러 메시지
```json
{
  "errors": {
    "AUDIO_PROCESSING_FAILED": "오디오 처리에 실패했습니다.",
    "STT_SERVICE_UNAVAILABLE": "음성 인식 서비스를 사용할 수 없습니다.",
    "ANALYSIS_TIMEOUT": "분석 시간이 초과되었습니다.",
    "INVALID_AUDIO_FORMAT": "지원하지 않는 오디오 형식입니다.",
    "FILE_TOO_LARGE": "파일 크기가 너무 큽니다.",
    "NETWORK_ERROR": "네트워크 연결을 확인해주세요."
  }
}
```

### 7.2 성공 메시지
```json
{
  "success": {
    "AUDIO_UPLOADED": "음성 파일이 성공적으로 업로드되었습니다.",
    "ANALYSIS_COMPLETED": "분석이 완료되었습니다.",
    "SETTINGS_SAVED": "설정이 저장되었습니다.",
    "DATA_DELETED": "데이터가 삭제되었습니다."
  }
}
```

## 8. AI 모델 기본 설정

### 8.1 음성 인식 설정
```json
{
  "speechRecognition": {
    "language": "ko-KR",
    "model": "clova-stt",
    "confidenceThreshold": 0.7,
    "maxDuration": 30,
    "sampleRate": 16000
  }
}
```

### 8.2 의도 분석 설정
```json
{
  "intentAnalysis": {
    "model": "bert-base-multilingual-cased",
    "confidenceThreshold": 0.6,
    "maxLength": 512,
    "batchSize": 32
  }
}
```

### 8.3 TTS 설정
```json
{
  "textToSpeech": {
    "voice": "ko-KR-Standard-A",
    "speed": 1.0,
    "pitch": 1.0,
    "volume": 0.8
  }
}
```

이 기본 데이터 구조를 사용하여 백엔드에서 초기값을 설정하고, 사용자가 설정을 변경할 수 있도록 구현하시면 됩니다.
