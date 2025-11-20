# Step 1: Vision - 이미지 이해하기

## 목표

- Vision Language Model (VLM) 이해
- Gemini Pro Vision 사용
- 이미지 + 텍스트 질의응답

## VLM이란?

**이미지를 이해하고 설명하는 LLM**

```python
입력: [사진] + "이게 뭐야?"
출력: "강아지 사진입니다. 골든 리트리버로 보입니다."
```

## 주요 모델

| 모델 | 특징 | 비용 |
|------|------|------|
| GPT-4V | 최고 정확도 | 높음 |
| Claude 3 | 긴 컨텍스트 | 중간 |
| **Gemini Pro Vision** | 무료 티어 | 낮음 ✅ |
| LLaVA | 오픈소스 | 무료 |

## 사용 예제

```python
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="gemini-pro-vision")

response = llm.invoke([
    {"type": "text", "text": "이 이미지를 설명해줘"},
    {"type": "image_url", "image_url": "path/to/image.jpg"}
])
```

## 실무 활용

```python
1. 제품 이미지 분석
   → 자동 태깅, 검색

2. 문서 OCR
   → 이미지에서 텍스트 추출

3. 시각적 Q&A
   → "이 차트가 의미하는 건?"
```

## 핵심 요약

- **VLM = 이미지 이해 LLM**
- **Gemini Pro Vision 추천**
- **OCR, 분석, Q&A 가능**

---

**다음**: step2 - Audio (Whisper)
