# 멀티모달 튜토리얼

텍스트, 이미지, 오디오를 처리하는 AI 시스템 구축

## 개요

**여러 모달리티**(텍스트, 이미지, 오디오, 비디오)를 이해하고 생성하는 AI 시스템을 학습합니다.

## 멀티모달이란?

### 단일 모달 (텍스트만)
```python
Q: "강아지가 뭐야?"
A: "강아지는 개의 새끼입니다..."
```

### 멀티모달 (텍스트 + 이미지)
```python
Q: [이미지 업로드] "이 강아지 품종은?"
A: "이 사진 속 강아지는 골든 리트리버로 보입니다..."
```

## 주요 모달리티

### 1. Vision (이미지)
```python
# Vision Language Model (VLM)
- GPT-4V
- Claude 3
- Gemini Pro Vision
- LLaVA (오픈소스)
```

**사용 사례:**
- 이미지 설명 생성
- 시각적 질문 답변 (VQA)
- OCR (텍스트 추출)
- 객체 인식

### 2. Audio (오디오)
```python
# Speech-to-Text
- Whisper (OpenAI)
- Google Speech-to-Text

# Text-to-Speech
- ElevenLabs
- Google Text-to-Speech
```

**사용 사례:**
- 음성 비서
- 회의 녹음 → 요약
- 팟캐스트 자동 자막

### 3. Video (비디오)
```python
# Video Understanding
- Gemini 1.5 Pro (네이티브 비디오 지원)
- 프레임 추출 + VLM
```

**사용 사례:**
- 비디오 요약
- 동영상 검색
- 이상 탐지

## 학습 목차

**Step 1**: Vision - 이미지 이해 (GPT-4V, Claude 3)
**Step 2**: Audio - 음성 처리 (Whisper)
**Step 3**: Vision + Text - RAG with Images
**Step 4**: Audio + Text - 음성 챗봇
**Step 5**: Video - 영상 분석
**Step 6**: 멀티모달 에이전트

## 실무 예시

### 1. 시각적 Q&A 챗봇
```python
사용자: [제품 사진] "이거 얼마예요?"
봇: "사진 속 나이키 에어맥스는 129,000원입니다."
```

### 2. 문서 분석
```python
입력: [PDF 스캔본]
출력:
- 텍스트 추출 (OCR)
- 표 데이터 구조화
- 요약 생성
```

### 3. 음성 회의 비서
```python
입력: [회의 녹음 파일]
처리:
1. 음성 → 텍스트 (Whisper)
2. 화자 분리
3. 요약 생성
4. 액션 아이템 추출
```

### 4. 제품 추천
```python
사용자: [스타일 사진] "이런 느낌의 옷 추천해줘"
시스템:
1. 이미지 분석 (색상, 스타일)
2. 유사 상품 벡터 검색
3. 추천 목록 생성
```

## 주요 모델

| 모델 | 모달리티 | 특징 |
|------|---------|------|
| **GPT-4V** | Text + Image | 높은 정확도, 비쌈 |
| **Claude 3** | Text + Image | 긴 컨텍스트 |
| **Gemini Pro Vision** | Text + Image + Video | 비디오 네이티브 |
| **LLaVA** | Text + Image | 오픈소스 |
| **Whisper** | Audio → Text | 다국어, 정확 |

## 기술적 도전

### 1. 모달리티 정렬
```python
# 문제: 서로 다른 형식의 데이터
이미지: [픽셀 배열]
텍스트: [토큰 시퀀스]
오디오: [파형]

# 해결: 공통 임베딩 공간
→ 모두 벡터로 변환
```

### 2. 컨텍스트 길이
```python
텍스트: 1 토큰 = 4자
이미지: 1 이미지 = 수백~수천 토큰
비디오: 1분 = 수만 토큰

→ 효율적 압축 필요
```

### 3. 처리 속도
```python
텍스트: 빠름
이미지: 느림 (인코딩 필요)
비디오: 매우 느림 (프레임 추출 + 인코딩)
```

## 빠른 시작

```python
from langchain_google_genai import ChatGoogleGenerativeAI
import base64

# Vision 모델
llm = ChatGoogleGenerativeAI(model="gemini-pro-vision")

# 이미지 + 텍스트 질문
with open("image.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode()

response = llm.invoke([
    {"type": "text", "text": "이 이미지를 설명해주세요"},
    {"type": "image_url", "image_url": f"data:image/jpeg;base64,{image_data}"}
])

print(response.content)
```

---

**학습 목표**: 텍스트, 이미지, 오디오를 통합하여 처리하는 멀티모달 AI 시스템을 구축할 수 있다.
