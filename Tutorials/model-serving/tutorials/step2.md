# Step 2: Ollama API 서버 활용

## 목표

- Ollama REST API 이해
- Chat API로 대화형 서비스 구현
- 스트리밍 응답 활용
- 모델 관리 방법

## Ollama API란?

Ollama는 **HTTP 서버**로 실행되며, REST API를 제공합니다.

```
ollama serve → http://localhost:11434
```

### API 구조

```
GET  /api/tags         # 설치된 모델 목록
POST /api/generate     # 텍스트 생성
POST /api/chat         # 대화형 생성
POST /api/pull         # 모델 다운로드
```

## 1. REST API로 직접 호출

### Generate API (일반 프롬프트)

```python
import requests

url = "http://localhost:11434/api/generate"

data = {
    "model": "llama3",
    "prompt": "LangGraph를 한 문장으로 설명해줘",
    "stream": False  # 한 번에 응답
}

response = requests.post(url, json=data)
result = response.json()

print(result['response'])
```

**응답 형식:**
```json
{
  "model": "llama3",
  "response": "LangGraph는 상태 기반 워크플로우...",
  "done": true
}
```

## 2. Chat API (대화형)

**대화 히스토리 유지**

```python
url = "http://localhost:11434/api/chat"

messages = [
    {"role": "system", "content": "너는 친절한 AI 어시스턴트야"},
    {"role": "user", "content": "안녕! 너는 누구야?"},
]

data = {
    "model": "llama3",
    "messages": messages,
    "stream": False
}

response = requests.post(url, json=data)
result = response.json()

print(result['message']['content'])
```

**다음 대화 추가:**
```python
# 이전 응답을 messages에 추가
messages.append(result['message'])
messages.append({"role": "user", "content": "Python을 설명해줘"})

# 다시 요청 → 컨텍스트 유지됨
```

## 3. 스트리밍 (실시간 응답)

**ChatGPT처럼 실시간으로 출력**

```python
from langchain_community.llms import Ollama

llm = Ollama(model="llama3")

question = "Ollama의 장점 3가지를 알려줘"

# 스트리밍 출력
for chunk in llm.stream(question):
    print(chunk, end="", flush=True)
```

**왜 스트리밍?**
- 사용자 경험 향상 (기다림 해소)
- 긴 응답도 즉시 시작
- 웹/앱 서비스 필수 기능

## 4. 모델 관리

### 설치된 모델 확인

```python
response = requests.get("http://localhost:11434/api/tags")
models = response.json()

for model in models['models']:
    name = model['name']
    size = model['size'] / (1024**3)  # GB로 변환
    print(f"{name} ({size:.1f} GB)")
```

**출력 예:**
```
llama3:8b (4.7 GB)
mistral:7b (4.1 GB)
gemma:7b (5.0 GB)
```

### 새 모델 다운로드

```bash
# CLI로 다운로드
ollama pull mistral
ollama pull gemma:7b
ollama pull phi3:mini

# API로 다운로드 (비동기)
POST /api/pull
{
  "name": "mistral:7b"
}
```

## API vs LangChain 비교

### REST API (직접)
```python
response = requests.post(
    "http://localhost:11434/api/generate",
    json={"model": "llama3", "prompt": "Hello"}
)
```

**장점:**
- 어떤 언어에서든 사용 가능 (Python, JS, Go, ...)
- 세밀한 제어

**단점:**
- 코드가 길어짐
- 에러 처리 직접 구현

### LangChain (추상화)
```python
from langchain_community.llms import Ollama

llm = Ollama(model="llama3")
response = llm.invoke("Hello")
```

**장점:**
- 간결한 코드
- LangChain 에코시스템 활용

**단점:**
- Python만 지원

## 실무 활용

### 1. FastAPI 서버 (다른 언어에서 호출)

```python
from fastapi import FastAPI
from langchain_community.llms import Ollama

app = FastAPI()
llm = Ollama(model="llama3")

@app.post("/chat")
def chat(message: str):
    response = llm.invoke(message)
    return {"response": response}
```

**다른 언어에서:**
```javascript
// JavaScript
fetch('http://localhost:8000/chat', {
  method: 'POST',
  body: JSON.stringify({message: 'Hello'})
})
```

### 2. 스트리밍 웹 서비스

```python
from fastapi.responses import StreamingResponse

@app.post("/chat/stream")
def chat_stream(message: str):
    def generate():
        for chunk in llm.stream(message):
            yield chunk

    return StreamingResponse(generate(), media_type="text/plain")
```

### 3. 모델 동적 선택

```python
@app.post("/chat")
def chat(message: str, model: str = "llama3"):
    llm = Ollama(model=model)  # 동적 선택
    return {"response": llm.invoke(message)}
```

**요청:**
```bash
curl -X POST http://localhost:8000/chat \
  -d '{"message": "Hello", "model": "mistral"}'
```

## 오류 처리

### Ollama 서버 미실행

```python
try:
    response = requests.post(url, json=data, timeout=5)
except requests.exceptions.ConnectionError:
    print("❌ Ollama 서버가 실행되지 않았습니다")
    print("   실행: ollama serve")
```

### 모델 없음

```python
try:
    llm = Ollama(model="llama3")
    result = llm.invoke("test")
except Exception as e:
    if "not found" in str(e):
        print("❌ 모델을 다운로드하세요")
        print("   ollama pull llama3")
```

## 핵심 요약

| 방식 | 용도 | 코드 |
|------|------|------|
| **Generate API** | 단발성 생성 | `POST /api/generate` |
| **Chat API** | 대화형 (히스토리 유지) | `POST /api/chat` |
| **스트리밍** | 실시간 UI | `llm.stream()` |
| **모델 관리** | 설치/삭제 | `GET /api/tags`, `ollama pull` |

## 다음 단계

**Step 3: 모델 비교 및 선택**
- 여러 모델 성능 비교
- 용도별 모델 추천
- 하드웨어 요구사항

---

**실습 체크리스트:**
- [ ] REST API로 텍스트 생성
- [ ] Chat API로 대화 구현
- [ ] 스트리밍 응답 확인
- [ ] 설치된 모델 목록 확인
- [ ] 새 모델 다운로드 (mistral, gemma)

**어디에든 사용 가능한 REST API = Ollama의 핵심 강점** ✅
