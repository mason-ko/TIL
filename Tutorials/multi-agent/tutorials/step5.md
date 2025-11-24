# Step 5: State Management (상태 관리)

## 목표

- 복잡한 상태 구조 설계
- 체크포인트와 영속성
- 대화 이력 관리
- 상태 디버깅

## 왜 상태 관리가 중요한가?

**Multi-Agent 시스템의 핵심**

```python
# 문제상황
Agent 1 → Agent 2 → Agent 3
         ↓
   정보 손실? 중복? 충돌?

# 해결: 체계적인 상태 관리
State: 모든 정보를 체계적으로 저장
```

## State 설계 전략

### 1. Flat State (단순)

```python
class SimpleState(TypedDict):
    task: str
    result: str
    status: str
```

**장점**: 간단
**단점**: 확장성 없음

### 2. Nested State (계층적)

```python
class ComplexState(TypedDict):
    task: TaskInfo
    agents: AgentStatus
    results: Results
    metadata: Metadata

class TaskInfo(TypedDict):
    id: str
    description: str
    priority: int

class AgentStatus(TypedDict):
    current: str
    completed: list[str]
    failed: list[str]

class Results(TypedDict):
    research: str
    code: str
    review: str
```

**장점**: 구조화, 확장 가능
**단점**: 복잡함

### 3. Message-based State

```python
from langgraph.graph.message import add_messages

class MessageState(TypedDict):
    messages: Annotated[list, add_messages]
    metadata: dict
```

**장점**: 대화 이력 자동 관리
**단점**: 큰 메모리 사용

## Reducer 함수

상태 업데이트 방식 정의

### 1. Overwrite (덮어쓰기)

```python
class State(TypedDict):
    counter: int  # 기본값: 덮어쓰기

# Agent 1
return {"counter": 5}

# Agent 2
return {"counter": 10}

# 최종: counter = 10 (덮어씀)
```

### 2. Add (추가)

```python
import operator

class State(TypedDict):
    scores: Annotated[list, operator.add]

# Agent 1
return {"scores": [80]}

# Agent 2
return {"scores": [90]}

# 최종: scores = [80, 90] (추가됨)
```

### 3. Custom Reducer

```python
def merge_dict(a: dict, b: dict) -> dict:
    """사전 병합"""
    return {**a, **b}

class State(TypedDict):
    config: Annotated[dict, merge_dict]

# Agent 1
return {"config": {"theme": "dark"}}

# Agent 2
return {"config": {"lang": "ko"}}

# 최종: config = {"theme": "dark", "lang": "ko"}
```

## Checkpointer (체크포인트)

**상태 영속성 - 중단된 곳부터 재개**

### Memory Checkpointer

```python
from langgraph.checkpoint.memory import MemorySaver

# 메모리 체크포인터
checkpointer = MemorySaver()

# 그래프 컴파일 시 추가
app = workflow.compile(checkpointer=checkpointer)

# 실행 (thread_id로 세션 관리)
config = {"configurable": {"thread_id": "user-123"}}

# 첫 실행
result1 = app.invoke({"task": "작업 1"}, config=config)

# 이어서 실행 (이전 상태 유지)
result2 = app.invoke({"task": "작업 2"}, config=config)
```

### SQLite Checkpointer

```python
from langgraph.checkpoint.sqlite import SqliteSaver

# DB에 저장
checkpointer = SqliteSaver.from_conn_string("checkpoints.db")

app = workflow.compile(checkpointer=checkpointer)

# 나중에 재시작해도 이어서 실행 가능
```

## 대화 이력 관리

```python
from langgraph.graph.message import add_messages, trim_messages

class ChatState(TypedDict):
    messages: Annotated[list, add_messages]

def chatbot(state: ChatState):
    """대화 이력 고려"""
    messages = state['messages']

    # 최근 10개만 사용 (토큰 절약)
    recent = messages[-10:]

    response = llm.invoke(recent)

    return {"messages": [response]}
```

## 상태 디버깅

### 1. State Snapshot

```python
# 각 단계별 상태 확인
for event in app.stream(initial_state):
    print(f"\n--- Event ---")
    print(event)
```

### 2. Logging

```python
def researcher(state):
    print(f"[DEBUG] State keys: {state.keys()}")
    print(f"[DEBUG] Task: {state.get('task')}")

    # 작업 수행
    result = do_research(state['task'])

    print(f"[DEBUG] Result length: {len(result)}")

    return {"research": result}
```

### 3. Validation

```python
def validate_state(state):
    """상태 검증"""
    required = ['task', 'messages']

    for key in required:
        if key not in state:
            raise ValueError(f"Missing required key: {key}")

    return state
```

## 실전 예제: 프로젝트 관리 시스템

```python
from typing import Annotated, Literal
import operator
from enum import Enum

class Priority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Task(TypedDict):
    id: str
    description: str
    priority: Priority
    assignee: str
    status: Literal["pending", "in_progress", "completed"]

class ProjectState(TypedDict):
    tasks: Annotated[list[Task], operator.add]
    current_task: str
    completed_count: int
    failed_count: int
    logs: Annotated[list, operator.add]

def task_manager(state: ProjectState):
    """작업 관리자"""
    # 다음 작업 선택 (우선순위 순)
    pending = [t for t in state['tasks'] if t['status'] == 'pending']
    pending.sort(key=lambda t: t['priority'].value)

    if pending:
        next_task = pending[0]
        return {
            "current_task": next_task['id'],
            "logs": [f"작업 선택: {next_task['description']}"]
        }

    return {"current_task": "none", "logs": ["모든 작업 완료"]}

def worker(state: ProjectState):
    """작업 수행"""
    task_id = state['current_task']

    # 작업 수행 (시뮬레이션)
    success = True

    if success:
        return {
            "completed_count": state['completed_count'] + 1,
            "logs": [f"작업 완료: {task_id}"]
        }
    else:
        return {
            "failed_count": state['failed_count'] + 1,
            "logs": [f"작업 실패: {task_id}"]
        }
```

## 메모리 최적화

### 1. Message Trimming

```python
from langgraph.graph.message import trim_messages

def trim_old_messages(state):
    """오래된 메시지 제거"""
    messages = state['messages']

    # 최근 20개만 유지
    if len(messages) > 20:
        trimmed = trim_messages(
            messages,
            max_tokens=4000,
            strategy="last"
        )
        return {"messages": trimmed}

    return {}
```

### 2. Summarization

```python
def summarize_history(state):
    """이력 요약"""
    messages = state['messages']

    if len(messages) > 50:
        # 오래된 메시지 요약
        old_messages = messages[:-20]
        summary = llm.invoke(f"다음 대화를 요약하세요:\n{old_messages}")

        # 요약 + 최근 메시지
        return {
            "messages": [
                {"role": "system", "content": f"이전 대화 요약: {summary}"}
            ] + messages[-20:]
        }

    return {}
```

## 다음 단계

**Step 6: 실전 프로젝트**
- 자동 리서치 봇 구축
- 모든 패턴 통합
- 프로덕션 고려사항

---

**핵심 요약:**
1. State = Multi-Agent 시스템의 메모리
2. Reducer = 상태 업데이트 방식
3. Checkpointer = 영속성 (중단 후 재개)
4. 디버깅과 검증 필수
