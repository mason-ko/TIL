# Step 2: Supervisor 패턴 (관리자 + 작업자)

## 목표

- Supervisor 패턴 이해
- 작업 분배 메커니즘 구현
- 전문화된 에이전트 활용
- 복잡한 작업 처리

## Supervisor 패턴이란?

**Manager + Workers 구조**

```
        [Supervisor]
        작업 분석 및 할당
              ↓
    ┌─────────┼─────────┐
    ↓         ↓         ↓
[Researcher] [Coder] [Reviewer]
  조사       코딩      검토
```

### 왜 필요한가?

**Sequential (Step 1)의 한계:**
```python
모든 작업을 순차 실행
→ 코딩 작업도 리서치를 거침 (비효율)
→ 단순 질문도 전체 플로우 (시간 낭비)
```

**Supervisor의 해결책:**
```python
작업 유형 분석
→ 코딩 작업 = Coder에게 직행
→ 조사 작업 = Researcher에게 직행
→ 효율적인 라우팅 ✅
```

## 구조 설계

### State 정의

```python
from typing_extensions import TypedDict

class State(TypedDict):
    task: str           # 원본 작업
    assigned_to: str    # 할당된 에이전트
    research: str       # 리서치 결과
    code: str          # 코드 결과
    review: str        # 리뷰 결과
    final_output: str  # 최종 출력
```

### 에이전트 역할

| 에이전트 | 역할 | 입력 | 출력 |
|---------|------|------|------|
| **Supervisor** | 작업 분석 및 라우팅 | task | assigned_to |
| **Researcher** | 정보 조사 | task | research |
| **Coder** | 코드 작성 | task | code |
| **Reviewer** | 결과 검토 | research/code | review |

## 구현

### 1. Supervisor (관리자)

```python
from langchain_community.llms import Ollama

def supervisor(state: State) -> State:
    """작업 분석 및 할당"""
    task = state['task']

    # 간단한 라우팅 로직
    if "코드" in task or "프로그램" in task:
        assigned = "coder"
    elif "분석" in task or "조사" in task:
        assigned = "researcher"
    else:
        assigned = "researcher"  # 기본값

    print(f"[Supervisor] '{task}' → {assigned}에게 할당")

    return {"assigned_to": assigned}
```

**고급 버전 (LLM 사용):**
```python
def supervisor_llm(state: State) -> State:
    """LLM으로 작업 분류"""
    llm = Ollama(model="llama3")

    prompt = f"""다음 작업을 분류하세요:
    작업: {state['task']}

    옵션:
    - researcher: 정보 조사, 분석
    - coder: 코드 작성, 프로그래밍

    한 단어만 답하세요 (researcher 또는 coder):"""

    assigned = llm.invoke(prompt).strip().lower()

    return {"assigned_to": assigned}
```

### 2. Worker Agents (작업자)

```python
def researcher(state: State) -> State:
    """리서치 에이전트"""
    print("[Researcher] 조사 중...")

    llm = Ollama(model="llama3")
    result = llm.invoke(f"{state['task']}에 대해 조사해줘")

    return {"research": result}

def coder(state: State) -> State:
    """코딩 에이전트"""
    print("[Coder] 코드 작성 중...")

    llm = Ollama(model="llama3")
    result = llm.invoke(f"{state['task']} 코드를 작성해줘")

    return {"code": result}

def reviewer(state: State) -> State:
    """리뷰 에이전트"""
    print("[Reviewer] 리뷰 중...")

    # 이전 단계 결과 가져오기
    content = state.get('research') or state.get('code') or ""

    llm = Ollama(model="llama3")
    review = llm.invoke(f"다음 내용을 리뷰해줘:\n{content[:200]}")

    return {
        "review": review,
        "final_output": content
    }
```

### 3. LangGraph 구성

```python
from langgraph.graph import StateGraph, START, END
from typing_extensions import Literal

# 그래프 생성
workflow = StateGraph(State)

# 노드 추가
workflow.add_node("supervisor", supervisor)
workflow.add_node("researcher", researcher)
workflow.add_node("coder", coder)
workflow.add_node("reviewer", reviewer)

# 라우팅 함수
def route_after_supervisor(state: State) -> Literal["researcher", "coder"]:
    """Supervisor 이후 분기"""
    return state['assigned_to']

# 엣지 연결
workflow.add_edge(START, "supervisor")

# Conditional 엣지 (분기)
workflow.add_conditional_edges(
    "supervisor",
    route_after_supervisor,
    {
        "researcher": "researcher",
        "coder": "coder"
    }
)

# 최종 리뷰로 수렴
workflow.add_edge("researcher", "reviewer")
workflow.add_edge("coder", "reviewer")
workflow.add_edge("reviewer", END)

# 컴파일
app = workflow.compile()
```

### 4. 실행

```python
# 테스트 작업
tasks = [
    "Python FastAPI 서버 코드 작성",      # → Coder
    "Vector Database 조사",               # → Researcher
    "GraphRAG가 뭔지 분석해줘",           # → Researcher
]

for task in tasks:
    print(f"\n{'='*60}")
    print(f"Task: {task}")
    print('='*60)

    result = app.invoke({"task": task})

    print(f"\n[할당] {result['assigned_to']}")
    print(f"[리뷰] {result['review'][:100]}...")
```

**출력:**
```
============================================================
Task: Python FastAPI 서버 코드 작성
============================================================
[Supervisor] 'Python FastAPI 서버 코드 작성' → coder에게 할당
[Coder] 코드 작성 중...
[Reviewer] 리뷰 중...

[할당] coder
[리뷰] 작성된 FastAPI 서버 코드는 기본 구조를 잘 갖추고 있습니다...

============================================================
Task: Vector Database 조사
============================================================
[Supervisor] 'Vector Database 조사' → researcher에게 할당
[Researcher] 조사 중...
[Reviewer] 리뷰 중...

[할당] researcher
[리뷰] Vector Database에 대한 조사 내용이 포괄적입니다...
```

## 실행 흐름

```
Task: "FastAPI 서버 코드 작성"
  ↓
[Supervisor] 분석
  → "코드" 키워드 발견
  → assigned_to = "coder"
  ↓
[Coder] 코드 작성
  → code = "from fastapi import FastAPI..."
  ↓
[Reviewer] 리뷰
  → review = "코드 품질: 좋음"
  ↓
END
```

## 장점

### 1. 전문화

```python
# 각 에이전트가 자신의 전문 분야만
Coder → 코드 작성에만 집중
Researcher → 정보 수집에만 집중
Reviewer → 품질 검토에만 집중
```

### 2. 확장성

```python
# 새 에이전트 추가 쉬움
workflow.add_node("translator", translator)
workflow.add_node("tester", tester)

# Supervisor 로직만 수정
if "번역" in task:
    assigned = "translator"
elif "테스트" in task:
    assigned = "tester"
```

### 3. 효율성

```python
# Sequential vs Supervisor
Sequential: 모든 작업 5단계 통과
Supervisor: 필요한 단계만 실행

예: 단순 질문
Sequential: 5단계 (30초)
Supervisor: 2단계 (10초) ✅
```

## 실무 확장

### 1. 에이전트 추가

```python
def data_analyst(state: State) -> State:
    """데이터 분석 에이전트"""
    print("[Data Analyst] 분석 중...")
    # 데이터 처리 로직
    return {"analysis": result}

workflow.add_node("data_analyst", data_analyst)

# Supervisor 수정
if "데이터" in task or "분석" in task:
    assigned = "data_analyst"
```

### 2. 우선순위

```python
class State(TypedDict):
    task: str
    priority: str  # "high", "medium", "low"
    assigned_to: str

def supervisor(state: State) -> State:
    priority = state.get('priority', 'medium')

    if priority == "high":
        # 고품질 에이전트 할당
        assigned = "senior_coder"
    else:
        assigned = "junior_coder"

    return {"assigned_to": assigned}
```

### 3. 병렬 작업

```python
# 여러 에이전트 동시 실행
workflow.add_conditional_edges(
    "supervisor",
    lambda s: ["researcher", "coder"],  # 둘 다 실행
    {
        "researcher": "researcher",
        "coder": "coder"
    }
)
```

## Supervisor vs Sequential

| 특징 | Sequential | Supervisor |
|------|-----------|-----------|
| **구조** | 직선형 | 분기형 |
| **효율** | 모든 단계 실행 | 필요한 단계만 |
| **확장** | 어려움 | 쉬움 |
| **복잡도** | 낮음 | 중간 |
| **사용 사례** | 단순 플로우 | 다양한 작업 유형 |

## 다음 단계

**Step 3: Network 패턴**
- 에이전트 간 직접 통신
- 동적 협업
- 자율적 의사결정

---

**핵심 요약:**
1. Supervisor = 작업 분배자
2. Worker = 전문화된 에이전트
3. Conditional Edge = 동적 라우팅
4. 효율성 ↑ (필요한 작업만 실행)

**Supervisor 패턴 = 실무에서 가장 많이 사용** ✅
