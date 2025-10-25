# We:Grow 백엔드 API 명세서

## 1. 사용자 관리 API

### POST /api/auth/register
**요청 데이터:**
```json
{
  "email": "parent@example.com",
  "password": "password123",
  "childAge": 18,
  "name": "부모님 이름"
}
```

**응답 데이터:**
```json
{
  "success": true,
  "user": {
    "id": "user_123",
    "email": "parent@example.com",
    "name": "부모님 이름",
    "childAge": 18,
    "createdAt": "2025-01-25T00:00:00Z"
  },
  "token": "jwt_token_here"
}
```

### POST /api/auth/login
**요청 데이터:**
```json
{
  "email": "parent@example.com",
  "password": "password123",
  "rememberMe": true
}
```

**응답 데이터:**
```json
{
  "success": true,
  "user": {
    "id": "user_123",
    "email": "parent@example.com",
    "name": "부모님 이름",
    "childAge": 18
  },
  "token": "jwt_token_here"
}
```

### PUT /api/user/profile
**요청 데이터:**
```json
{
  "email": "new_email@example.com",
  "childAge": 20,
  "password": "new_password"
}
```

## 2. 대시보드 API

### GET /api/dashboard/daily-report
**응답 데이터:**
```json
{
  "vocalizations": 14,
  "syllableCombinations": 3,
  "meaningfulAttempts": 5,
  "newWords": 1,
  "previousDay": {
    "vocalizations": 12
  },
  "summary": "좋은 소식! 아이가 오늘 처음으로 두 음절을 조합해서 발성했어요.",
  "recommendedResponse": "물? 물 주세요? 엄마가 물 줄까요?",
  "date": "2025-01-25"
}
```

### GET /api/dashboard/age-comparison
**응답 데이터:**
```json
{
  "vocalizationScore": 75,
  "wordUnderstandingScore": 55,
  "communicationScore": 65,
  "interpretation": "우리 아이는 대부분의 영역에서 또래 평균과 함께 성장 중입니다. 특히 음성 표현에 강점이 있습니다.",
  "childAge": 18
}
```

## 3. 성장 분석 API

### GET /api/growth/weekly-report
**응답 데이터:**
```json
{
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
    },
    {
      "label": "두 단어 말하기",
      "value": "1일 9회",
      "helper": "자연스러운 말 잇기",
      "trend": "3번 더 늘었어요!",
      "progress": 72,
      "color": "#A678E3"
    }
  ],
  "dailyMoments": [
    {
      "time": "놀이 시간(블록)",
      "script": "아이: \"더!\" → 도담: \"더 쌓자. 높은 탑? 낮은 탑? 하나, 둘—올려볼까?\"",
      "focus": "반복 + 선택 질문으로 자발 발화 유도"
    }
  ],
  "stageGuides": [
    {
      "stage": "24개월 포인트",
      "color": "#A678E3",
      "summary": "50개 이상의 단어로 두 단어 문장을 말해요!",
      "actions": [
        "'무슨 색 좋아?'처럼 선택 질문으로 대화 유도하기",
        "아이의 짧은 말을 더 긴 문장으로 이어 말해주기",
        "역할놀이로 감정 단어(기뻐, 속상해 등) 알려주기"
      ],
      "example": "예: \"더 우유\" → \"우유 더 마시고 싶구나~ 컵을 두 손으로 잡아볼까?\""
    }
  ],
  "recommendations": [
    {
      "title": "집 안 단어 탐험",
      "detail": "컵, 의자, 신발 같은 물건에 이름표를 붙여요. 도담이 읽어주면 아이가 말소리로 반응하며 배워요!",
      "tip": "이번 주엔 새로운 단어 6개를 골라 집중해볼까요?"
    }
  ],
  "parentAssist": [
    "오늘 도담이와 아이의 대화에서 짧은 응답 후에 대화가 자주 멈췄어요. 부모님이 아이의 말 뒤에 한 단어만 더 이어주시면, 문장 길이가 자연스럽게 늘어날 거예요.",
    "아이가 요청형 말(\"더\", \"줘\")을 자주 사용했어요. 이는 언어 이해가 빠르게 성장하는 시기예요.",
    "도담이의 관찰에 따르면, 감정 표현어('좋아', '싫어' 등) 반응이 아직 적어요."
  ]
}
```

## 4. 타임라인 API

### GET /api/timeline
**쿼리 파라미터:**
- `date`: 날짜 필터 (YYYY-MM-DD)
- `intent`: 의도 필터 ("요청", "부르기", "모방", "음성실험")

**응답 데이터:**
```json
{
  "timeline": [
    {
      "id": "timeline_123",
      "date": "2025-01-25",
      "time": "14:32",
      "childUtterance": "까까",
      "intent": "물품 요청",
      "parentResponse": "물 주세요? 라고 말해주세요",
      "audioUrl": "/api/audio/samples/123/play",
      "duration": 3,
      "confidence": 0.85
    }
  ],
  "totalCount": 17,
  "hasMore": false
}
```

## 5. 음성 데이터 관리 API

### POST /api/audio/upload
**요청 데이터 (multipart/form-data):**
- `audio_file`: 음성 파일 (MP3, WAV, M4A) - 필수

**응답 데이터:**
```json
{
  "success": true,
  "sample_id": "sample_123",
  "status": "분석 완료",
  "analysis_result": {
    "transcription": "까까",
    "intent": "물품 요청",
    "confidence": 0.85,
    "recommended_response": "물 주세요? 엄마가 물 줄까요?",
    "language_development_stage": "두 단어 조합 초기"
  }
}
```

**에러 응답:**
```json
{
  "success": false,
  "sample_id": "sample_123",
  "status": "분석 실패",
  "error": "AI 분석 중 오류가 발생했습니다."
}
```

**에러 응답:**
- `413`: 파일 크기가 너무 큼 (10MB 초과)
- `400`: 지원하지 않는 오디오 형식

### GET /api/audio/samples
**응답 데이터:**
```json
{
  "samples": [
    {
      "id": "sample_123",
      "timestamp": "2025-01-25T14:32:00Z",
      "duration": 3,
      "source": "로봇 자동 수집",
      "status": "분석 완료",
      "notes": "",
      "audioUrl": "/api/audio/samples/123/play",
      "ttsAudioUrl": "/api/audio/samples/123/tts",
      "analysisResult": {
        "transcription": "까까",
        "intent": "물품 요청",
        "confidence": 0.85,
        "recommendedResponse": "물 주세요? 엄마가 물 줄까요?"
      }
    }
  ],
  "statistics": {
    "robotCollected": 14,
    "parentUploaded": 3,
    "analysisCompleted": 16
  }
}
```

### DELETE /api/audio/samples/:id
**응답 데이터:**
```json
{
  "success": true,
  "message": "샘플이 삭제되었습니다."
}
```

### POST /api/audio/samples/:id/reanalyze
**응답 데이터:**
```json
{
  "success": true,
  "status": "분석 완료",
  "analysis_result": {
    "transcription": "까까",
    "intent": "물품 요청",
    "confidence": 0.85,
    "recommended_response": "물 주세요? 엄마가 물 줄까요?",
    "language_development_stage": "두 단어 조합 초기"
  }
}
```

**에러 응답:**
```json
{
  "success": false,
  "status": "분석 실패",
  "error": "AI 분석 중 오류가 발생했습니다."
}
```

### GET /api/audio/samples/:id/play
**설명:** 원본 오디오 샘플 재생
**응답:** MP3 오디오 파일 스트림

### GET /api/audio/samples/:id/tts
**설명:** TTS로 생성된 권장 응답 오디오 재생
**응답:** MP3 오디오 파일 스트림

### POST /api/audio/samples/:id/generate-tts
**설명:** 샘플에 대한 TTS 오디오 생성
**응답 데이터:**
```json
{
  "success": true,
  "tts_audio_url": "/api/audio/samples/123/tts",
  "message": "TTS 오디오가 생성되었습니다."
}
```

**에러 응답:**
```json
{
  "success": false,
  "message": "TTS 오디오 생성에 실패했습니다."
}
```

## 6. 팁 & 코칭 API

### GET /api/tips
**쿼리 파라미터:**
- `level`: 발달 단계 필터
- `favorites`: 즐겨찾기만 보기 (true/false)

**응답 데이터:**
```json
{
  "tips": [
    {
      "id": 1,
      "level": "두 단어 조합 초기 단계",
      "scenario": "아이: \"또!\"",
      "parentResponse": "엄마(권장): \"또 해요? 또 하고 싶어요?\"",
      "explanation": "아이의 한 단어를 길게 확장해서 말해주면, 아이가 자연스럽게 더 긴 표현을 들을 수 있습니다.",
      "isFavorite": false
    }
  ],
  "educationContent": {
    "modeling": "아이의 발화를 바로 수정하지 마세요. 대신 아이가 말한 것을 더 완성된 형태로 자연스럽게 다시 말해주세요.",
    "expansion": "아이의 한 단어에 의미 있는 단어들을 더해서 더 긴 표현으로 확장해 들려주세요.",
    "repetition": "같은 개념을 여러 단어와 상황으로 반복 노출하면 학습이 강화됩니다."
  }
}
```

### POST /api/tips/:id/favorite
**응답 데이터:**
```json
{
  "success": true,
  "isFavorite": true
}
```

## 7. 설정 API

### GET /api/settings
**응답 데이터:**
```json
{
  "recordingCollection": true,
  "analysisUsage": true,
  "coachingRecommendations": true,
  "notificationsEnabled": true,
  "emailReports": true,
  "user": {
    "email": "parent@example.com",
    "childAge": 18
  }
}
```

### PUT /api/settings
**요청 데이터:**
```json
{
  "recordingCollection": true,
  "analysisUsage": true,
  "coachingRecommendations": true,
  "notificationsEnabled": true,
  "emailReports": true
}
```

## 8. 실시간 음성 통신 API (WebSocket)

### WebSocket 연결
```
ws://localhost:8080/ws
```

### 클라이언트 → 서버 메시지

**오디오 데이터 전송:**
```json
{
  "type": "audio_data",
  "data": "base64_encoded_audio_data",
  "timestamp": 1640995200000,
  "userId": "user_123"
}
```

**텍스트 메시지 전송:**
```json
{
  "type": "text_message",
  "text": "안녕하세요",
  "timestamp": 1640995200000,
  "userId": "user_123"
}
```

### 서버 → 클라이언트 메시지

**오디오 응답:**
```json
{
  "type": "audio_response",
  "audioData": "base64_encoded_audio_data",
  "text": "음성으로 변환된 텍스트",
  "timestamp": 1640995200000
}
```

**전사 결과:**
```json
{
  "type": "transcription",
  "text": "전사된 텍스트",
  "confidence": 0.95,
  "intent": "물품 요청",
  "recommendedResponse": "물 주세요? 엄마가 물 줄까요?",
  "timestamp": 1640995200000
}
```

**TTS 응답:**
```json
{
  "type": "tts_response",
  "audioData": "base64_encoded_audio_data",
  "text": "음성으로 변환된 텍스트",
  "timestamp": 1640995200000
}
```

## 9. AI 분석 결과 데이터 구조

### 음성 분석 결과
```json
{
  "transcription": "까까",
  "confidence": 0.85,
  "intent": "물품 요청",
  "emotion": "중립",
  "ageAppropriate": true,
  "recommendedResponse": "물 주세요? 엄마가 물 줄까요?",
  "languageDevelopmentStage": "두 단어 조합 초기",
  "suggestions": [
    "아이의 의도를 자연스럽게 확장해서 말해주세요",
    "선택지를 제공하여 대화를 이어가세요"
  ]
}
```

### 성장 지표 분석
```json
{
  "vocabularyGrowth": {
    "current": 42,
    "target": 50,
    "trend": "increasing",
    "weeklyGrowth": 6
  },
  "sentenceComplexity": {
    "twoWordSentences": 9,
    "averageLength": 1.8,
    "improvement": 0.3
  },
  "communicationAttempts": {
    "dailyAverage": 14,
    "meaningfulAttempts": 5,
    "successRate": 0.36
  }
}
```

## 10. 에러 응답 형식

```json
{
  "success": false,
  "error": {
    "code": "AUDIO_PROCESSING_FAILED",
    "message": "오디오 처리에 실패했습니다.",
    "details": "지원하지 않는 오디오 형식입니다."
  },
  "timestamp": "2025-01-25T00:00:00Z"
}
```

## 11. 기본값 데이터 정의

### 사용자 기본 설정
```json
{
  "recordingCollection": true,
  "analysisUsage": true,
  "coachingRecommendations": true,
  "notificationsEnabled": true,
  "emailReports": true
}
```

### 성장 단계별 기본 데이터
```json
{
  "18개월": {
    "targetVocabulary": 15,
    "expectedSentences": 0,
    "communicationAttempts": 8,
    "focusAreas": ["단어 이해", "음성 실험", "의도 표현"]
  },
  "24개월": {
    "targetVocabulary": 50,
    "expectedSentences": 5,
    "communicationAttempts": 15,
    "focusAreas": ["두 단어 조합", "감정 표현", "선택 질문"]
  }
}
```

### 팁 데이터베이스
```json
{
  "tips": [
    {
      "id": 1,
      "level": "두 단어 조합 초기 단계",
      "scenario": "아이: \"또!\"",
      "parentResponse": "엄마(권장): \"또 해요? 또 하고 싶어요?\"",
      "explanation": "아이의 한 단어를 길게 확장해서 말해주면, 아이가 자연스럽게 더 긴 표현을 들을 수 있습니다.",
      "ageRange": [18, 24],
      "tags": ["확장", "모델링"]
    }
  ]
}
```

이 명세서를 바탕으로 백엔드 API를 구현하시면 됩니다. 각 API는 실제 AI 분석 결과를 반환하도록 구현되어야 하며, WebSocket을 통한 실시간 음성 통신도 지원해야 합니다.
