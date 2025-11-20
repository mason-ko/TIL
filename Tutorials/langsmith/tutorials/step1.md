# Step 1: LangSmith 기본 설정

## 목표

- LangSmith 설정 및 첫 트레이싱 실행
- UI에서 추적 데이터 확인
- 트레이싱 데이터 구조 이해

## LangSmith란?

LangSmith는 LangChain 팀이 만든 **LLM 애플리케이션 모니터링 플랫폼**입니다.

### 주요 기능

1. **자동 트레이싱**: 모든 LLM 호출 자동 기록
2. **시각화**: 체인 실행 과정을 그래프로 표시
3. **디버깅**: 각 단계의 입력/출력 확인
4. **평가**: 모델 출력 품질 측정

## 설정 방법

### 1. LangSmith 가입

1. https://smith.langchain.com/ 접속
2. GitHub 또는 이메일로 가입
3. 무료 플랜 시작 (월 5,000 traces)

### 2. API Key 발급

```
1. Settings 클릭
2. API Keys 탭
3. "Create API Key" 클릭
4. Key 이름 입력
5. 복사하여 저장
```

### 3. 환경 변수 설정

`.env` 파일:

```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_pt_your_key_here
LANGCHAIN_PROJECT=my-first-project
```

## 코드 예제

### 예제 1: 첫 트레이싱

**가장 간단한 예제**

```python
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# LangSmith 자동 활성화 (환경변수가 설정되어 있으면)
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")

# 이 호출이 자동으로 LangSmith에 기록됨!
response = llm.invoke("안녕하세요!")
print(response.content)
```

**실행 후:**
1. https://smith.langchain.com/ 접속
2. 프로젝트 선택 (my-first-project)
3. 방금 실행한 trace 확인!

### 예제 2: 체인 트레이싱

**더 복잡한 예제**

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

# 프롬프트 템플릿
prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 {role} 전문가입니다."),
    ("human", "{question}")
])

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")
chain = prompt | llm

# 체인 실행 - 전체 과정이 트레이싱됨
response = chain.invoke({
    "role": "Python",
    "question": "리스트 컴프리헨션이 뭔가요?"
})

print(response.content)
```

**LangSmith UI에서 볼 수 있는 것:**
```
Chain Run
  ├─ Prompt Run (템플릿 렌더링)
  │   Input: {role: "Python", question: "..."}
  │   Output: "당신은 Python 전문가입니다. 리스트 컴프리헨션이..."
  │
  └─ LLM Run (LLM 호출)
      Input: "당신은 Python 전문가입니다..."
      Output: "리스트 컴프리헨션은..."
      Tokens: 120
      Latency: 1.2s
```

### 예제 3: 커스텀 메타데이터

**추가 정보 기록**

```python
from langsmith import traceable

@traceable(
    name="번역기",
    metadata={"version": "1.0", "language": "ko"}
)
def translate_text(text: str, target_lang: str) -> str:
    """텍스트 번역 함수"""
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")

    prompt = f"Translate to {target_lang}: {text}"
    response = llm.invoke(prompt)

    return response.content

# 사용
result = translate_text("Hello, world!", "Korean")
print(result)
```

**메타데이터 활용:**
- 버전 관리
- 환경 구분 (dev/prod)
- 사용자 정보
- 실험 ID

## UI 살펴보기

### 메인 대시보드

```
┌─────────────────────────────────┐
│ Project: my-first-project       │
├─────────────────────────────────┤
│ Total Runs: 15                  │
│ Success Rate: 93%               │
│ Avg Latency: 1.5s               │
│ Total Tokens: 12,500            │
└─────────────────────────────────┘

Recent Runs:
- 번역기 (2초 전) ✅
- Chain Run (1분 전) ✅
- LLM Run (5분 전) ❌ Error
```

### Trace 상세 화면

```
Run Details
─────────────
Name: 번역기
Status: ✅ Success
Duration: 1.2s
Tokens: 120 (100 prompt, 20 completion)
Cost: $0.0012

Timeline:
├─ Start (0.0s)
├─ LLM Call (0.1s - 1.1s)
└─ End (1.2s)

Input:
text: "Hello, world!"
target_lang: "Korean"

Output:
"안녕하세요, 세상!"

Metadata:
version: 1.0
language: ko
```

## 트레이싱 데이터 구조

### Run 타입

| 타입 | 설명 | 예시 |
|------|------|------|
| **Chain** | 여러 단계의 체인 | prompt \| llm |
| **LLM** | LLM API 호출 | ChatGoogleGenerativeAI.invoke() |
| **Tool** | 도구 실행 | Search, Calculator |
| **Retriever** | 검색 | VectorStore.search() |

### Run 속성

```python
{
    "id": "run-123",
    "name": "번역기",
    "run_type": "chain",
    "start_time": "2024-01-15T10:30:00Z",
    "end_time": "2024-01-15T10:30:01.2Z",
    "inputs": {"text": "Hello", "target_lang": "Korean"},
    "outputs": {"output": "안녕하세요"},
    "error": null,
    "metadata": {"version": "1.0"},
    "tags": ["translation", "ko"],
    "parent_run_id": null,
    "child_runs": [...]
}
```

## 트레이싱 제어

### 트레이싱 비활성화

```python
# 방법 1: 환경 변수
os.environ["LANGCHAIN_TRACING_V2"] = "false"

# 방법 2: 특정 함수만 비활성화
from langsmith import tracing_v2_enabled

with tracing_v2_enabled(False):
    # 이 블록 안의 호출은 트레이싱 안 됨
    llm.invoke("비밀 질문")
```

### 프로젝트 변경

```python
# 방법 1: 환경 변수
os.environ["LANGCHAIN_PROJECT"] = "production"

# 방법 2: 컨텍스트 매니저
from langsmith import tracing_context

with tracing_context(project_name="experiment-1"):
    llm.invoke("실험 질문")
```

## 실습 과제

### 1. 기본 트레이싱

```python
# TODO: LangSmith 설정 후 다음 코드 실행
# 1. 간단한 질문-답변
# 2. UI에서 trace 확인
# 3. 입력/출력/토큰 확인
```

### 2. 체인 트레이싱

```python
# TODO: 프롬프트 템플릿 + LLM 체인 만들기
# 1. 시스템 프롬프트 포함
# 2. UI에서 각 단계 확인
```

### 3. 메타데이터 추가

```python
# TODO: @traceable 데코레이터 사용
# 1. 커스텀 메타데이터 추가
# 2. UI에서 메타데이터 확인
```

## 다음 단계

**Step 2: 프로덕션 모니터링**에서는:
- 실시간 모니터링
- 에러 추적
- 필터링 및 검색
- 성능 분석

## 핵심 요약

1. **LangSmith = LLM 애플리케이션 모니터링 플랫폼**
2. **환경 변수만 설정하면 자동 트레이싱**
3. **모든 LLM 호출이 UI에 기록됨**
4. **입력/출력/토큰/지연시간 모두 확인 가능**

---

**다음**: `step2.md` - 프로덕션 환경에서의 실시간 모니터링
