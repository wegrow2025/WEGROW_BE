# We:Grow RealTime Audio API

아이의 언어 발달을 위한 실시간 음성 분석 및 AI 기반 맞춤형 코칭 API입니다.

## 주요 기능

- **실시간 음성 분석**: WebSocket을 통한 실시간 음성 데이터 처리
- **AI 기반 분석**: OpenAI GPT-4를 활용한 정확한 음성 인식 및 의도 분석
- **발달 단계별 맞춤형 처리**: 아이의 월령에 따른 개인화된 분석 및 응답
- **종합적인 대시보드**: 일일 리포트, 성장 분석, 타임라인 제공
- **스마트 코칭**: 발달 단계별 맞춤형 팁과 권장사항 제공

## 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   클라이언트     │    │   FastAPI       │    │   AI 분석기     │
│   (WebSocket)   │◄──►│   서버          │◄──►│   (OpenAI)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   SQLite DB     │
                       │   (음성 데이터)  │
                       └─────────────────┘
```

## 요구사항

- Python 3.8+
- OpenAI API Key
- Redis (선택사항, 캐싱용)

## 설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 다음 내용을 추가하세요:

```env
# OpenAI API Key (필수)
OPENAI_API_KEY=your_openai_api_key_here

# 데이터베이스
DATABASE_URL=sqlite:///./wegrow.db

# JWT 시크릿 키
SECRET_KEY=your_secret_key_here

# 서버 설정
HOST=0.0.0.0
PORT=8000
```

### 3. 서버 실행

```bash
python run.py
```

또는

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API 엔드포인트

### WebSocket 연결
```
ws://localhost:8000/ws?user_id={user_id}
```

### REST API
- **인증**: `/api/auth/register`, `/api/auth/login`, `/api/auth/refresh`, `/api/auth/logout`, `/api/auth/verify`
- **음성 관리**: `/api/audio/upload`, `/api/audio/samples`
- **대시보드**: `/api/dashboard/daily-report`, `/api/dashboard/age-comparison`
- **타임라인**: `/api/timeline`
- **성장 분석**: `/api/growth/analysis`
- **팁 & 코칭**: `/api/tips`
- **설정**: `/api/settings`
- **통계**: `/api/stats/overview`

## 인증 시스템

### 회원가입
```bash
POST /api/auth/register
{
  "email": "user@example.com",
  "name": "사용자명",
  "password": "password123",
  "childAge": 18
}
```

**응답:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "IwgYRhdr9TqnebdxdM0AciM7p728duTWTzinv3mvsAM",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### 로그인
```bash
POST /api/auth/login
{
  "email": "user@example.com",
  "password": "password123"
}
```

### 토큰 갱신
```bash
POST /api/auth/refresh
{
  "refresh_token": "your_refresh_token"
}
```

### 토큰 검증
```bash
GET /api/auth/verify
Authorization: Bearer your_access_token
```

### 로그아웃
```bash
POST /api/auth/logout
{
  "refresh_token": "your_refresh_token"
}
```

## WebSocket 메시지 형식

### 클라이언트 → 서버

**오디오 데이터 전송**
```json
{
  "type": "audio_data",
  "data": "base64_encoded_audio_data",
  "timestamp": 1640995200000
}
```

**텍스트 메시지 전송**
```json
{
  "type": "text_message",
  "text": "안녕하세요",
  "timestamp": 1640995200000
}
```

### 서버 → 클라이언트

**전사 결과**
```json
{
  "type": "transcription",
  "text": "전사된 텍스트",
  "confidence": 0.95,
  "timestamp": 1640995200000
}
```

**TTS 응답**
```json
{
  "type": "tts_response",
  "audioData": "base64_encoded_audio_data",
  "text": "음성으로 변환된 텍스트",
  "timestamp": 1640995200000
}
```

## AI 분석 로직

### 발달 단계별 처리

1. **옹알이 단계 (0-12개월)**
   - 반복음소 인식 ("까까", "바바", "맘마")
   - 의도성 있는 발성 판단
   - 부모는 아이 소리 그대로 따라하기

2. **단어 시작 단계 (12-18개월)**
   - 첫 단어 인식 ("엄마", "아빠", "물")
   - 부정확한 발음도 의도 파악
   - 정확한 발음으로 교정

3. **단어 발전 단계 (18-24개월)**
   - 2-3음절 단어 조합 인식
   - 문맥을 통한 의도 파악
   - 문장으로 확장해서 응답

4. **문장 시작 단계 (24-36개월)**
   - 2-3단어 조합 인식
   - 문법적 오류 자연스럽게 교정
   - 완전한 문장으로 응답

5. **문장 발전 단계 (36개월+)**
   - 복잡한 문장 구조 인식
   - 추상적 개념 표현 파악
   - 대화 확장 및 질문 유도

## 핵심 특징

### 1. 정확한 음성 인식
- OpenAI GPT-4 기반 고정밀 전사
- 아이 발달 단계별 맞춤형 프롬프트
- 오디오 특성 분석 (피치, 에너지, 스펙트럼)

### 2. 지능형 의도 분석
- "마마" → "엄마" 교정
- 의사소통 의도 파악
- 발달 단계별 적절한 응답 생성

### 3. 실시간 처리
- WebSocket 기반 실시간 통신
- 오디오 버퍼링 및 배치 처리
- 백그라운드 AI 분석

### 4. 개인화된 코칭
- 아이 나이별 맞춤형 팁
- 발달 단계별 권장사항
- 성장 추적 및 분석

### 5. 토큰 기반 인증 시스템
- JWT Access Token (24시간 유효)
- Refresh Token (30일 유효)
- 자동 토큰 갱신
- 보안 강화된 인증

## 테스트

### WebSocket 테스트
브라우저에서 `http://localhost:8000/ws/test` 접속하여 WebSocket 연결을 테스트할 수 있습니다.

### API 문서
`http://localhost:8000/docs`에서 자동 생성된 API 문서를 확인할 수 있습니다.

## 데이터베이스 스키마

- **users**: 사용자 정보
- **user_settings**: 사용자 설정
- **audio_samples**: 음성 샘플 및 분석 결과
- **notifications**: 알림

## 설정

### 환경 변수
- `OPENAI_API_KEY`: OpenAI API 키 (필수)
- `DATABASE_URL`: 데이터베이스 연결 URL
- `SECRET_KEY`: JWT 토큰 시크릿 키
- `HOST`, `PORT`: 서버 주소 및 포트

### 오디오 처리 설정
- 최대 오디오 길이: 5분
- 샘플링 레이트: 16kHz
- 채널: 모노

## 배포

### Docker (권장)
```bash
docker build -t wegrow-api .
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key wegrow-api
```

### 일반 배포
```bash
pip install -r requirements.txt
python run.py
```

## 라이선스

MIT License
