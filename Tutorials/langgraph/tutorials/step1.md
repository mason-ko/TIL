# Step 1: 기본 LLM 호출

## 개요
LangGraph를 배우기 전에 가장 기본적인 LLM(Large Language Model) API 호출을 이해하는 단계입니다.
Google Gemini API를 직접 사용하여 LLM과 상호작용하는 방법을 배웁니다.

## 사전 준비

### 1. 필요한 패키지 설치
```bash
pip install google-generativeai
```

### 2. API 키 설정
Google Gemini API 키를 환경변수로 설정합니다.
[Google AI Studio](https://aistudio.google.com/app/apikey)에서 발급받으세요.

**Linux/Mac:**
```bash
export GOOGLE_API_KEY='your-api-key-here'
```

**Windows (PowerShell):**
```powershell
$env:GOOGLE_API_KEY='your-api-key-here'
```

**Windows (CMD):**
```cmd
set GOOGLE_API_KEY=your-api-key-here
```

### 3. 실행
```bash
python tutorials/step1.py
```

## 코드 설명

### 1. 기본 LLM 호출 (`basic_llm_call`)

#### 주요 구성 요소:

**Gemini API 설정**
```python
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')
```
- Gemini API와 통신하기 위한 설정
- API 키는 환경변수에서 읽어옵니다 (보안상 코드에 직접 작성하지 않음)
- gemini-2.5-flash는 최신 고성능 모델

**콘텐츠 생성 요청**
```python
response = model.generate_content(
    user_message,
    generation_config=genai.types.GenerationConfig(
        temperature=0.7,
        max_output_tokens=500
    )
)
```

- `model`: 사용할 LLM 모델 (gemini-2.5-flash는 빠르고 강력한 모델)
- `temperature`: 응답의 창의성/무작위성 (0.0 = 결정적, 2.0 = 매우 창의적)
- `max_output_tokens`: 생성할 최대 토큰 수

**응답 처리**
```python
assistant_message = response.text
```
- Gemini의 응답은 `response.text`로 바로 접근할 수 있습니다
- 에러 처리를 위해 `response.candidates`를 확인할 수 있습니다
- 토큰 사용량은 `response.usage_metadata`에서 확인 가능합니다

### 2. 대화 이력 유지 (`conversation_example`)

**메시지 역할의 종류:**
- `system`: LLM의 행동 방식을 지정 (예: "당신은 친절한 Python 튜터입니다")
- `user`: 사용자의 질문이나 입력
- `assistant`: LLM의 이전 응답

**대화 이력 관리:**
```python
# Gemini의 채팅 세션 사용
chat = model.start_chat(history=[])
response_1 = chat.send_message("안녕하세요! Python을 배우고 싶어요.")
response_2 = chat.send_message("그럼 먼저 변수에 대해 알려주세요.")
```

- Gemini는 `start_chat()`으로 채팅 세션을 시작합니다
- `send_message()`로 메시지를 보내면 자동으로 이력이 관리됩니다
- `chat.history`로 전체 대화 이력을 확인할 수 있습니다

**중요:** LLM 자체는 상태를 저장하지 않습니다. 채팅 세션 객체가 이력을 관리합니다!

### 3. 스트리밍 응답 (`streaming_example`)

**스트리밍의 장점:**
- 응답을 실시간으로 받아 사용자에게 즉시 표시할 수 있습니다
- 긴 응답의 경우 사용자 경험이 크게 향상됩니다
- ChatGPT 웹사이트처럼 글자가 하나씩 나타나는 효과

**스트리밍 사용법:**
```python
response = model.generate_content(user_message, stream=True)

for chunk in response:
    if chunk.text:
        print(chunk.text, end="", flush=True)
```

- `stream=True`로 설정
- 응답이 청크(chunk) 단위로 하나씩 전달됩니다
- `chunk.text`에 새로운 텍스트 조각이 들어있습니다
- `flush=True`로 즉시 출력되도록 합니다

## 핵심 개념 정리

### 1. LLM은 상태가 없다 (Stateless)
- LLM은 이전 대화를 자동으로 기억하지 않습니다
- 매 요청마다 필요한 모든 문맥을 함께 보내야 합니다
- 대화 이력 관리는 개발자의 책임입니다

### 2. 토큰 (Token)
- LLM은 텍스트를 토큰 단위로 처리합니다
- 대략 1토큰 ≈ 0.75 단어 (영어 기준)
- API 비용은 사용한 토큰 수에 비례합니다
- `max_tokens`로 응답 길이를 제한할 수 있습니다

### 3. 메시지 역할 (Roles)
- `system`: LLM의 페르소나/행동 방식 정의
- `user`: 사용자 입력
- `assistant`: LLM 응답

### 4. Temperature
- 0.0에 가까울수록: 결정적, 일관적, 예측 가능
- 2.0에 가까울수록: 창의적, 다양한, 무작위적
- 일반적으로 0.7~1.0 사이 값을 많이 사용

## 다음 단계

이제 기본적인 LLM 호출을 이해했습니다!
다음 단계(Step 2)에서는 LangChain을 사용하여 이러한 작업을 더 쉽고 구조적으로 수행하는 방법을 배웁니다.

**Step 2에서 배울 내용:**
- LangChain의 ChatOpenAI 래퍼 사용
- 프롬프트 템플릿
- 출력 파서
- 체인 구성
