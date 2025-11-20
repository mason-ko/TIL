# Step 5: 조건부 엣지와 라우팅

## 개요
지금까지는 노드들이 순차적으로 실행되었습니다.
이번 단계에서는 조건에 따라 다른 경로로 분기하고, 루프를 만드는 방법을 배웁니다.
이것이 바로 에이전트가 "결정"을 내리는 핵심 메커니즘입니다!

## 사전 준비

### 필요한 패키지 설치
```bash
pip install langgraph langchain-google-genai
```

### 실행
```bash
python tutorials/step5.py
```

## 엣지의 두 가지 종류

### 1. 일반 엣지 (Normal Edge)
```python
workflow.add_edge("node_a", "node_b")
# node_a는 항상 node_b로 이동
```

- 고정된 경로
- 조건 없이 항상 다음 노드로 이동

### 2. 조건부 엣지 (Conditional Edge)
```python
workflow.add_conditional_edges(
    "node_a",           # 시작 노드
    routing_function,   # 라우팅 함수
    {
        "path1": "node_b",
        "path2": "node_c"
    }
)
```

- 동적 경로
- 라우팅 함수의 반환값에 따라 다음 노드 결정

## 핵심 개념: 라우팅 함수

**라우팅 함수의 역할:**
- 현재 State를 보고 다음에 갈 노드를 결정
- 문자열 (노드 이름 또는 경로 키)을 반환

**시그니처:**
```python
def routing_function(state: State) -> str:
    # state를 분석
    # 조건에 따라 경로 키 반환
    return "path_key"
```

**반환값:**
- 매핑 딕셔너리의 키와 일치해야 함
- Literal 타입으로 명시하면 타입 안정성 향상

## 코드 설명

### 1. 단순 조건 분기 (`simple_conditional_example`)

**그래프 구조:**
```
                  ┌─→ even → END
START → check ─┤
                  └─→ odd → END
```

**라우팅 함수:**
```python
def route_based_on_number(state: State) -> Literal["even", "odd"]:
    if state["number"] % 2 == 0:
        return "even"
    else:
        return "odd"
```

- 짝수면 "even" 반환 → even 노드로
- 홀수면 "odd" 반환 → odd 노드로

**조건부 엣지 추가:**
```python
workflow.add_conditional_edges(
    "check",                    # 이 노드 이후에
    route_based_on_number,      # 이 함수로 판단해서
    {
        "even": "even",         # "even" 반환 시 even 노드로
        "odd": "odd"            # "odd" 반환 시 odd 노드로
    }
)
```

**Literal 타입의 장점:**
```python
from typing import Literal

def route(...) -> Literal["even", "odd"]:
    ...
```

- 타입 체커가 오타를 잡아줌
- IDE 자동완성 지원
- 가능한 경로를 명확히 문서화

### 2. 루프 (`loop_example`)

**그래프 구조:**
```
         ┌──────────┐
         ↓          │
START → increment ─┤
                    │
                    └─→ END
```

**루프 생성 방법:**
```python
workflow.add_conditional_edges(
    "increment",
    should_continue,
    {
        "continue": "increment",  # 자기 자신으로! (루프)
        "end": END
    }
)
```

**종료 조건:**
```python
def should_continue(state: State) -> Literal["continue", "end"]:
    if state["count"] < state["max_count"]:
        return "continue"  # 루프 계속
    else:
        return "end"       # 루프 종료
```

**중요:**
- 루프는 무한히 반복될 수 있습니다!
- 반드시 종료 조건이 있어야 합니다
- LangGraph는 기본적으로 최대 반복 횟수 제한이 있습니다 (25회)

### 3. LLM 기반 의사결정 (`llm_decision_example`)

**그래프 구조:**
```
                   ┌─→ code → END
START → classify ─┼─→ explanation → END
                   └─→ debug → END
```

**LLM으로 분류:**
```python
def classify_question(state: State) -> State:
    # LLM에게 질문 분류 요청
    response = llm.invoke([...])
    question_type = response.content.strip().lower()
    return {"question_type": question_type}
```

**LLM 응답 기반 라우팅:**
```python
def route_by_question_type(state: State) -> Literal["code", "explanation", "debug"]:
    return state["question_type"]
```

**핵심:**
- LLM이 상황을 판단하고 결정합니다
- 에이전트의 "사고" 과정
- 각 경로마다 전문화된 처리 가능

**안전장치:**
```python
if question_type not in ["code", "explanation", "debug"]:
    question_type = "explanation"  # 기본값
```

LLM 출력이 예상과 다를 수 있으므로 검증 필요!

### 4. 다중 경로 (`multi_path_example`)

**실용적인 워크플로우 패턴:**

1. 입력 분석
2. 조건에 따라 분류
3. 각 분류별로 다른 처리
4. 결과 반환

**예시: 이슈 트래킹 시스템**
- 우선순위 분석 → 고/중/저 분류
- 고: 시니어 개발자에게 즉시 할당
- 중: 팀 대기열에 추가
- 저: 백로그에 추가

### 5. 최대 반복 제한 (`max_iterations_example`)

**무한 루프 방지 패턴:**

```python
def should_retry(state: State) -> Literal["retry", "success", "failed"]:
    if state["success"]:
        return "success"  # 성공 시 종료
    elif state["attempts"] >= state["max_attempts"]:
        return "failed"   # 최대 시도 초과
    else:
        return "retry"    # 재시도
```

**3가지 출구:**
1. 성공 → 성공 핸들러
2. 최대 시도 초과 → 실패 핸들러
3. 재시도 가능 → 다시 시도 (루프)

**실용 사례:**
- API 호출 재시도
- 데이터 검증 반복
- 에이전트의 자가 수정

## 조건부 엣지 패턴

### 패턴 1: 이진 분기
```python
# 예: 성공/실패, 예/아니오
def route(state) -> Literal["yes", "no"]:
    return "yes" if condition else "no"
```

### 패턴 2: 다중 분기
```python
# 예: 여러 카테고리
def route(state) -> Literal["cat1", "cat2", "cat3"]:
    if ...:
        return "cat1"
    elif ...:
        return "cat2"
    else:
        return "cat3"
```

### 패턴 3: 루프
```python
# 예: 계속/종료
def route(state) -> Literal["continue", "end"]:
    return "continue" if not_done else "end"
```

### 패턴 4: 루프 + 출구
```python
# 예: 재시도/성공/실패
def route(state) -> Literal["retry", "success", "failed"]:
    if state["success"]:
        return "success"
    elif state["attempts"] < max:
        return "retry"
    else:
        return "failed"
```

## 디버깅 팁

### 1. 라우팅 로깅
```python
def route(state: State) -> str:
    decision = "path_a" if condition else "path_b"
    print(f"라우팅 결정: {decision}")  # 어느 경로로 가는지 확인
    return decision
```

### 2. State 검사
```python
def route(state: State) -> str:
    print(f"현재 상태: {state}")  # State 전체 출력
    # 의사결정 로직
    return result
```

### 3. 스트림으로 중간 과정 보기
```python
for step in app.stream(initial_state):
    print(f"현재 단계: {step}")
```

## 고급: 동적 엣지

**경로 매핑 없이 직접 노드 이름 반환:**

```python
workflow.add_conditional_edges(
    "node_a",
    lambda state: "node_b" if condition else "node_c"
    # 매핑 딕셔너리 없음
)
```

라우팅 함수가 직접 노드 이름을 반환하면 됩니다.

## LangGraph의 루프 제한

**기본 제한:**
- 최대 재귀 깊이: 25회
- 무한 루프 방지 메커니즘

**제한 변경:**
```python
app = workflow.compile()
result = app.invoke(
    initial_state,
    {"recursion_limit": 50}  # 제한 늘리기
)
```

**주의:**
- 너무 높은 값은 위험
- 의도하지 않은 무한 루프 주의
- 명확한 종료 조건 필수

## 실전 예제: 에이전트 루프

```python
def should_continue(state):
    """에이전트가 계속 작업할지 결정"""
    if "FINAL ANSWER" in state["messages"][-1].content:
        return "end"
    elif state["steps"] > 10:
        return "max_steps"
    else:
        return "continue"

workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "agent",      # 계속 사고
        "end": "finalize",        # 답변 완성
        "max_steps": "fallback"   # 너무 오래 걸림
    }
)
```

## 핵심 개념 정리

### 1. 조건부 엣지는 의사결정의 핵심
- 에이전트가 "생각"하는 메커니즘
- 상황에 따라 다른 행동 선택

### 2. 라우팅 함수
- State를 분석하여 경로 결정
- 반환값은 문자열 (경로 키 또는 노드 이름)
- Literal 타입 사용 권장

### 3. 루프 = 자기 참조
- 조건부 엣지로 자기 자신을 가리킴
- 반드시 종료 조건 필요
- 최대 반복 제한 주의

### 4. 안전장치 필수
- LLM 출력 검증
- 최대 반복 횟수 제한
- 기본값/fallback 경로

## 다음 단계

조건부 분기와 루프를 마스터했습니다!
이제 에이전트가 스스로 결정을 내릴 수 있습니다.

다음 단계(Step 6)에서는 이 모든 것을 종합하여 **실용적인 에이전트**를 만듭니다!

**Step 6에서 배울 내용:**
- Tool 사용 에이전트
- ReAct 패턴
- 실제 문제 해결 에이전트
- 에이전트 디버깅과 최적화
