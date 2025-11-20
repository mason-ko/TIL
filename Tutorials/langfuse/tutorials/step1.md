# Step 1: Langfuse 설치 및 기본 트레이싱

## 목표

- Langfuse Self-hosted 설치
- Ollama와 연동하여 첫 트레이싱 실행
- UI에서 추적 데이터 확인

## Langfuse란?

**오픈소스 LLM Observability 플랫폼**으로 로컬 LLM에 최적화되어 있습니다.

### 핵심 장점

1. **완전 무료**: Self-hosted 시 비용 $0
2. **데이터 프라이버시**: 모든 데이터가 내 서버에
3. **로컬 LLM 친화적**: Ollama, vLLM 완벽 지원
4. **오픈소스**: 코드 수정 및 커스터마이징 자유

## 설치 방법

### 1. Docker로 Langfuse 설치

```bash
# Langfuse 저장소 클론
git clone https://github.com/langfuse/langfuse.git
cd langfuse

# 환경 변수 설정
cp .env.example .env

# Docker Compose로 실행
docker compose up -d

# 실행 확인
docker compose ps
```

### 2. 초기 설정

```bash
# 브라우저에서 접속
http://localhost:3000

# 1. 계정 생성
# 2. 프로젝트 생성
# 3. API Keys 발급
```

### 3. API Keys 확인

```
Settings → API Keys → Create new keys

Public Key: pk-lf-...
Secret Key: sk-lf-...
```

## Ollama 설치 (로컬 LLM)

```bash
# Ollama 설치 (Mac/Linux)
curl -fsSL https://ollama.com/install.sh | sh

# Windows는 https://ollama.com/download 에서 다운로드

# Llama 3 모델 다운로드
ollama pull llama3

# 실행 확인
ollama run llama3 "Hello"
```

## 코드 예제

### 예제 1: 기본 트레이싱 (Ollama)

**가장 간단한 예제**

```python
import os
from dotenv import load_dotenv
from langfuse import Langfuse
from langchain_community.llms import Ollama

load_dotenv()

# Langfuse 초기화
langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST", "http://localhost:3000")
)

# Ollama 모델
llm = Ollama(model="llama3")

# 트레이싱 시작
trace = langfuse.trace(name="first-trace")

# LLM 호출
generation = trace.generation(
    name="ollama-call",
    model="llama3",
    input="Langfuse에 대해 한 문장으로 설명해주세요."
)

response = llm.invoke("Langfuse에 대해 한 문장으로 설명해주세요.")

generation.end(output=response)

print(f"응답: {response}\n")
print(f"✅ Langfuse UI에서 확인: {trace.get_trace_url()}")
```

**실행 후:**
1. http://localhost:3000 접속
2. Traces 탭에서 방금 실행한 trace 확인!

### 예제 2: LangChain 통합

**LangChain과 자동 연동**

```python
from langfuse.callback import CallbackHandler
from langchain_community.llms import Ollama
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Langfuse Callback
langfuse_handler = CallbackHandler(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST")
)

# 프롬프트 템플릿
prompt = PromptTemplate(
    input_variables=["topic"],
    template="다음 주제에 대해 3줄로 설명해주세요: {topic}"
)

llm = Ollama(model="llama3")
chain = LLMChain(llm=llm, prompt=prompt)

# 자동 트레이싱
response = chain.invoke(
    {"topic": "Vector Database"},
    config={"callbacks": [langfuse_handler]}
)

print(response["text"])
```

**Langfuse UI에서 볼 수 있는 것:**
```
Chain Run
  ├─ Prompt Template
  │   Input: {topic: "Vector Database"}
  │   Output: "다음 주제에 대해 3줄로 설명해주세요: Vector Database"
  │
  └─ Ollama LLM Call
      Input: "다음 주제에 대해..."
      Output: "Vector Database는..."
      Latency: 2.3s
```

### 예제 3: 메타데이터 추가

**추가 정보 기록**

```python
from langfuse.decorators import langfuse_context, observe

@observe()
def translate_text(text: str, target_lang: str) -> str:
    """텍스트 번역 함수"""
    llm = Ollama(model="llama3")

    # 현재 trace에 메타데이터 추가
    langfuse_context.update_current_trace(
        metadata={
            "source_text": text,
            "target_language": target_lang,
            "model": "llama3",
            "environment": "development"
        },
        tags=["translation", "ollama"]
    )

    prompt = f"Translate to {target_lang}: {text}"
    response = llm.invoke(prompt)

    return response

# 사용
result = translate_text("Hello, world!", "Korean")
print(f"번역 결과: {result}")
```

### 예제 4: 에러 추적

**에러도 자동으로 기록됨**

```python
trace = langfuse.trace(name="error-example")

try:
    llm = Ollama(model="nonexistent-model")
    generation = trace.generation(name="bad-call")

    response = llm.invoke("This will fail")
    generation.end(output=response)

except Exception as e:
    # 에러 기록
    generation.end(
        output=None,
        metadata={"error": str(e)},
        level="ERROR"
    )
    print(f"❌ 에러 발생: {e}")
    print(f"Langfuse에서 에러 확인: {trace.get_trace_url()}")
```

## UI 살펴보기

### 메인 대시보드

```
┌─────────────────────────────────┐
│ Project: my-ollama-project      │
├─────────────────────────────────┤
│ Total Traces: 25                │
│ Success Rate: 96%               │
│ Avg Latency: 2.1s               │
│ Models: llama3, mistral         │
└─────────────────────────────────┘

Recent Traces:
- translate_text (10초 전) ✅ 2.3s
- first-trace (1분 전) ✅ 1.8s
- error-example (5분 전) ❌ Error
```

### Trace 상세 화면

```
Trace Details
─────────────
Name: translate_text
Status: ✅ Success
Duration: 2.3s
Model: llama3 (Ollama)

Metadata:
source_text: "Hello, world!"
target_language: "Korean"
environment: "development"

Tags: translation, ollama

Timeline:
├─ Start (0.0s)
├─ Ollama Call (0.1s - 2.2s)
└─ End (2.3s)

Input:
"Translate to Korean: Hello, world!"

Output:
"안녕하세요, 세상!"
```

## 로컬 vs 클라우드

### Self-hosted (로컬)

**장점:**
- ✅ 완전 무료
- ✅ 데이터 프라이버시
- ✅ 커스터마이징 가능
- ✅ 무제한 traces

**단점:**
- ❌ 서버 관리 필요
- ❌ 초기 설정 복잡

### Langfuse Cloud

**장점:**
- ✅ 빠른 시작 (5분)
- ✅ 관리 불필요
- ✅ 자동 업데이트

**단점:**
- ❌ 무료 플랜 제한 (50K traces/월)
- ❌ 데이터 외부 저장

**권장:**
- 개발: Cloud (빠른 시작)
- 프로덕션: Self-hosted (무제한 + 프라이버시)

## 실습 과제

### 1. Langfuse 설치 및 실행

```bash
# TODO: Docker로 Langfuse 실행
# 1. docker compose up -d
# 2. http://localhost:3000 접속
# 3. 계정 및 프로젝트 생성
```

### 2. Ollama 첫 트레이싱

```python
# TODO: Ollama + Langfuse 연동
# 1. 간단한 질문-답변
# 2. UI에서 trace 확인
# 3. 지연시간 확인
```

### 3. LangChain 통합

```python
# TODO: LangChain 체인 트레이싱
# 1. CallbackHandler 사용
# 2. 전체 체인 과정 확인
```

## 다음 단계

**Step 2: 고급 트레이싱**에서는:
- 멀티턴 대화 트레이싱
- RAG 파이프라인 추적
- 성능 최적화
- 비용 분석 (API 사용 시)

## 핵심 요약

1. **Langfuse = 오픈소스 LLM Observability**
2. **Self-hosted로 완전 무료**
3. **Ollama와 완벽한 조합**
4. **모든 LLM 호출이 자동 기록**
5. **에러, 메타데이터까지 추적**

---

**다음**: `step2.md` - RAG 파이프라인 트레이싱 및 고급 기능
