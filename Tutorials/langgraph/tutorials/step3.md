# Step 3: LangGraph 기본 구조

## 개요
드디어 LangGraph입니다! LangGraph는 복잡한 AI 워크플로우를 그래프 구조로 표현할 수 있게 해주는 라이브러리입니다.
상태 기반 그래프를 사용하여 에이전트와 복잡한 워크플로우를 구축합니다.

## 사전 준비

### 필요한 패키지 설치
```bash
pip install langgraph langchain-google-genai
```

### 실행
```bash
python tutorials/step3.py
```

## LangGraph가 필요한 이유

**LangChain의 한계:**
- 체인은 선형적입니다 (A → B → C)
- 조건부 분기가 복잡합니다
- 루프나 사이클을 만들기 어렵습니다
- 복잡한 에이전트 로직을 표현하기 어렵습니다

**LangGraph의 장점:**
- 그래프 구조로 복잡한 흐름 표현
- 조건부 분기 쉽게 구현
- 루프와 사이클 지원
- 상태 기반 워크플로우
- 병렬 처리 지원

## 핵심 개념

### 1. 그래프 구성 요소

**State (상태):**
- 그래프 내에서 전달되는 데이터
- TypedDict로 정의
- 각 노드가 상태를 읽고 수정

**Node (노드):**
- 실제 작업을 수행하는 함수
- State를 입력으로 받음
- State의 일부를 반환 (업데이트할 부분만)

**Edge (엣지):**
- 노드들 사이의 연결
- 실행 순서를 정의
- 일반 엣지와 조건부 엣지가 있음

**START와 END:**
- START: 그래프의 진입점
- END: 그래프의 종료점

### 2. 그래프 생성 과정

```python
# 1. State 정의
class State(TypedDict):
    message: str
    count: int

# 2. 노드 함수 정의
def my_node(state: State) -> State:
    return {"message": "updated"}

# 3. 그래프 생성
workflow = StateGraph(State)

# 4. 노드 추가
workflow.add_node("node_name", my_node)

# 5. 엣지 추가
workflow.add_edge(START, "node_name")
workflow.add_edge("node_name", END)

# 6. 컴파일
app = workflow.compile()

# 7. 실행
result = app.invoke({"message": "hello", "count": 0})
```

## 코드 설명

### 1. 간단한 그래프 (`simple_graph_example`)

**State 정의:**
```python
class State(TypedDict):
    message: str
    count: int
```

TypedDict를 사용하여 상태의 구조를 명확히 합니다.

**노드 함수:**
```python
def node_1(state: State) -> State:
    return {
        "message": state["message"] + " -> 노드1",
        "count": state["count"] + 1
    }
```

- 현재 상태를 읽습니다
- 새로운 값을 딕셔너리로 반환합니다
- 반환한 값이 기존 상태에 병합됩니다 (덮어쓰기)

**실행 흐름:**
```
START → step1 → step2 → step3 → END
```

각 노드가 순차적으로 실행되며, 상태가 계속 업데이트됩니다.

**중요:** 노드는 전체 상태를 반환할 필요가 없습니다. 변경할 필드만 반환하면 됩니다!

### 2. LLM 사용 그래프 (`llm_graph_example`)

**실제 사용 패턴:**
1. 사용자 질문을 받음
2. LLM에게 질문
3. 응답을 포맷팅
4. 결과 반환

**노드 분리의 장점:**
- 각 단계를 독립적으로 테스트 가능
- 노드를 재사용 가능
- 흐름을 시각화하기 쉬움

### 3. 메시지 누적 (`message_graph_example`)

**특별한 기능: `add_messages`**

```python
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]
```

**일반적인 상태 업데이트 (덮어쓰기):**
```python
# 노드가 {"count": 5}를 반환하면
# state["count"]는 5로 덮어쓰여집니다
```

**add_messages를 사용한 누적:**
```python
# 노드가 {"messages": [new_msg]}를 반환하면
# new_msg가 기존 messages 리스트에 추가됩니다 (덮어쓰기 X)
```

**왜 유용한가?**
- 대화 이력을 자동으로 관리
- LLM에게 전체 대화를 전달 가능
- 수동으로 메시지를 합칠 필요 없음

**Annotated 타입:**
```python
Annotated[list, add_messages]
```
- `list`: 기본 타입
- `add_messages`: 값을 병합하는 방법 (덮어쓰기가 아닌 추가)

### 4. 병렬 처리 (`parallel_processing_example`)

**그래프 구조:**
```
              ┌─→ summarize ─┐
START ─┼─→ count      ┼─→ output → END
              └─→ sentiment ─┘
```

**병렬 실행:**
- START에서 3개 노드로 동시에 엣지 추가
- 3개 노드가 독립적으로 실행됨
- 모두 완료되면 output 노드로 진행

**장점:**
- 실행 시간 단축 (병렬 처리)
- 각 작업이 독립적
- 자동으로 병렬 실행됨

**LangGraph의 자동 병렬화:**
- 의존성이 없는 노드들을 자동으로 감지
- 가능한 경우 병렬로 실행
- 개발자가 병렬 처리 로직을 작성할 필요 없음

## State 업데이트 메커니즘

### 기본 동작 (덮어쓰기)

```python
# 초기 상태
state = {"message": "hello", "count": 0}

# 노드가 반환
return {"message": "world"}

# 결과 상태
state = {"message": "world", "count": 0}
# message는 업데이트, count는 유지
```

### Reducer 사용 (병합)

**Reducer 함수:**
- 기존 값과 새 값을 어떻게 병합할지 정의
- `add_messages`가 대표적인 예

**커스텀 Reducer 예제:**
```python
def add_to_list(existing: list, new: list) -> list:
    return existing + new

class State(TypedDict):
    items: Annotated[list, add_to_list]
```

## LangChain Chain vs LangGraph

| 특징 | LangChain Chain | LangGraph |
|------|-----------------|-----------|
| **구조** | 선형 (A → B → C) | 그래프 (분기, 루프 가능) |
| **조건부 분기** | 복잡함 | 쉬움 |
| **루프/사이클** | 어려움 | 기본 지원 |
| **상태 관리** | 수동 | 자동 |
| **병렬 처리** | 가능하지만 복잡 | 자동 |
| **시각화** | 제한적 | 명확한 그래프 구조 |
| **사용 사례** | 단순한 파이프라인 | 복잡한 에이전트 |

## 그래프 시각화

그래프 구조를 시각화할 수 있습니다:

```python
from IPython.display import Image, display

# Mermaid 다이어그램 생성
display(Image(app.get_graph().draw_mermaid_png()))
```

## 핵심 개념 정리

### 1. State는 그래프의 메모리
- 노드 간 데이터 전달 수단
- 각 노드가 상태를 읽고 수정
- TypedDict로 타입 안정성 확보

### 2. 노드는 순수 함수
- State 입력 → State 반환
- 부분 업데이트 가능 (전체를 반환할 필요 없음)
- 재사용 가능하고 테스트 가능

### 3. 엣지는 실행 흐름
- 노드 연결 순서 정의
- 일반 엣지: 무조건 다음 노드로
- 조건부 엣지: 조건에 따라 다른 노드로 (Step 5에서 배움)

### 4. 컴파일은 실행 가능한 객체 생성
- `workflow.compile()` → 실행 가능한 앱
- 컴파일 시점에 그래프 검증
- 순환 참조, 고립된 노드 등 체크

## 다음 단계

LangGraph의 기본 구조를 이해했습니다!

다음 단계(Step 4)에서는 **State 관리**를 더 깊이 배웁니다.

**Step 4에서 배울 내용:**
- 복잡한 State 구조
- Reducer 함수 활용
- State 스키마 설계 패턴
- 체크포인트와 상태 영속성
