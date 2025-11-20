# Step 4: State 관리

## 개요
LangGraph에서 State는 매우 중요합니다. 이번 단계에서는 복잡한 State 구조를 다루고,
Reducer 함수를 사용하여 상태 업데이트 방식을 커스터마이징하는 방법을 배웁니다.

## 사전 준비

### 필요한 패키지 설치
```bash
pip install langgraph langchain-google-genai
```

### 실행
```bash
python tutorials/step4.py
```

## State 업데이트의 두 가지 방식

### 1. 덮어쓰기 (기본 동작)

```python
class State(TypedDict):
    counter: int  # Annotated 없음 = 덮어쓰기

# 노드가 {"counter": 5}를 반환하면
# state["counter"]는 5가 됩니다 (이전 값 무시)
```

### 2. 병합 (Reducer 사용)

```python
class State(TypedDict):
    counter: Annotated[int, operator.add]  # Reducer 지정

# 노드가 {"counter": 5}를 반환하면
# state["counter"] = 기존값 + 5 (누적)
```

## Reducer 함수란?

**정의:**
- 기존 값과 새 값을 받아 병합하는 함수
- `reducer(existing_value, new_value) -> merged_value`

**목적:**
- 상태를 덮어쓰는 대신 누적, 병합, 추가 등을 수행

## 코드 설명

### 1. 커스텀 Reducer (`custom_reducer_example`)

**Reducer 함수 정의:**

```python
def append_to_list(existing: List[str], new: List[str]) -> List[str]:
    """리스트에 항목 추가"""
    return existing + new

def add_numbers(existing: int, new: int) -> int:
    """숫자 더하기"""
    return existing + new

def merge_dicts(existing: Dict, new: Dict) -> Dict:
    """딕셔너리 병합"""
    return {**existing, **new}
```

**State에 적용:**

```python
class State(TypedDict):
    # 덮어쓰기
    current_step: str

    # 커스텀 Reducer 사용
    steps_taken: Annotated[List[str], append_to_list]
    total_count: Annotated[int, add_numbers]
    metadata: Annotated[Dict, merge_dicts]
```

**실행 흐름:**

```
초기 상태:
{
    "current_step": "시작",
    "steps_taken": [],
    "total_count": 0,
    "metadata": {}
}

노드 1이 반환:
{
    "current_step": "step_1",
    "steps_taken": ["step_1 완료"],
    "total_count": 1,
    "metadata": {"step_1_time": "10ms"}
}

상태 업데이트:
{
    "current_step": "step_1",  # 덮어쓰기
    "steps_taken": [] + ["step_1 완료"] = ["step_1 완료"],  # append
    "total_count": 0 + 1 = 1,  # add
    "metadata": {} | {"step_1_time": "10ms"} = {"step_1_time": "10ms"}  # merge
}
```

### 2. operator 모듈 사용 (`operator_reducer_example`)

Python의 `operator` 모듈은 표준 연산자를 함수로 제공합니다.

**operator.add의 동작:**

```python
import operator

# 숫자
operator.add(10, 20)  # 30

# 리스트
operator.add([1, 2], [3, 4])  # [1, 2, 3, 4]

# 문자열
operator.add("Hello ", "World")  # "Hello World"
```

**State에서 사용:**

```python
class State(TypedDict):
    score: Annotated[int, operator.add]  # 숫자 더하기
    items: Annotated[list, operator.add]  # 리스트 합치기
```

**장점:**
- 간결함: 커스텀 함수 작성 불필요
- 표준 라이브러리: 안정적이고 검증됨
- 다양한 연산자 지원: add, mul, sub 등

### 3. add_messages 심화 (`message_state_deep_dive`)

**add_messages의 특별한 기능:**

1. **자동 타입 처리:**
   ```python
   # 단일 메시지도 OK
   return {"messages": response}

   # 리스트도 OK
   return {"messages": [response]}
   ```

2. **메시지 ID 기반 업데이트:**
   - 같은 ID를 가진 메시지는 대체됩니다
   - 새로운 ID는 추가됩니다

3. **대화 이력 자동 관리:**
   - 수동으로 이력을 합칠 필요 없음
   - 전체 대화가 자동으로 유지됨

### 4. 체크포인트 (`checkpoint_example`)

**체크포인트란?**
- 그래프 실행 중간 상태를 저장하는 메커니즘
- 대화 세션을 여러 번에 걸쳐 유지 가능
- 각 실행 단계마다 상태 스냅샷 저장

**MemorySaver:**
```python
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)
```

- 메모리에 체크포인트 저장 (휘발성)
- 프로세스 종료 시 사라짐
- 개발/테스트용

**thread_id로 세션 구분:**
```python
config1 = {"configurable": {"thread_id": "conversation_1"}}
config2 = {"configurable": {"thread_id": "conversation_2"}}

# 같은 thread_id = 같은 대화 세션
app.invoke(input, config1)  # 세션 1
app.invoke(input, config1)  # 세션 1 이어서

# 다른 thread_id = 다른 대화 세션
app.invoke(input, config2)  # 세션 2 (독립적)
```

**실제 사용 예:**
- 채팅봇의 사용자별 대화 관리
- 멀티턴 대화 유지
- 중단된 작업 재개

**영속적 저장소:**
```python
# SQLite 체크포인터 (영구 저장)
from langgraph.checkpoint.sqlite import SqliteSaver

memory = SqliteSaver.from_conn_string("checkpoints.db")
app = workflow.compile(checkpointer=memory)
```

### 5. 복잡한 State 구조 (`complex_state_example`)

**실제 애플리케이션 State 패턴:**

```python
class State(TypedDict):
    # 사용자 정보 (덮어쓰기)
    user: UserInfo

    # 대화 (누적)
    messages: Annotated[List[BaseMessage], add_messages]

    # 로그 (누적)
    logs: Annotated[List[str], operator.add]

    # 카운터 (더하기)
    execution_count: Annotated[int, operator.add]

    # 에러 목록 (누적)
    errors: Annotated[List[str], operator.add]
```

**설계 원칙:**

1. **단일 값 데이터 → 덮어쓰기**
   - 현재 상태, 설정, 플래그 등
   - `current_step: str`

2. **누적 데이터 → Reducer**
   - 이력, 로그, 메시지 등
   - `logs: Annotated[List, operator.add]`

3. **집계 데이터 → Reducer**
   - 카운터, 점수, 통계 등
   - `count: Annotated[int, operator.add]`

4. **중첩 구조 → 별도 TypedDict**
   - 복잡한 객체는 별도 타입으로 정의
   - `user: UserInfo`

## Reducer 선택 가이드

| 데이터 타입 | Reducer | 용도 | 예시 |
|------------|---------|------|------|
| **숫자** | `operator.add` | 누적 합계 | 점수, 카운터 |
| **리스트** | `operator.add` | 항목 추가 | 로그, 이력 |
| **메시지** | `add_messages` | 대화 관리 | 채팅 메시지 |
| **딕셔너리** | 커스텀 함수 | 병합 | 메타데이터, 설정 |
| **단일 값** | 없음 (덮어쓰기) | 현재 상태 | 플래그, 현재 단계 |

## 체크포인트 사용 사례

### 1. 채팅봇
```python
# 사용자별 대화 세션 유지
config = {"configurable": {"thread_id": f"user_{user_id}"}}
app.invoke(user_input, config)
```

### 2. 장기 실행 워크플로우
```python
# 중간에 중단해도 재개 가능
# 각 단계마다 체크포인트 저장
app = workflow.compile(checkpointer=SqliteSaver(...))
```

### 3. 디버깅
```python
# 각 단계의 상태를 확인
for state in app.stream(input, config):
    print(f"현재 상태: {state}")
```

## State 스키마 설계 베스트 프랙티스

### 1. 명확한 타입 정의
```python
# Good
class State(TypedDict):
    user_id: str
    messages: Annotated[list, add_messages]
    score: Annotated[int, operator.add]

# Bad - 타입 불명확
class State(TypedDict):
    data: dict
    stuff: list
```

### 2. 적절한 Reducer 선택
```python
# Good - 의도가 명확
logs: Annotated[List[str], operator.add]

# Bad - 수동 관리
logs: List[str]
# 노드에서: state["logs"] = state["logs"] + new_logs
```

### 3. 중첩 구조 분리
```python
# Good
class UserInfo(TypedDict):
    name: str
    email: str

class State(TypedDict):
    user: UserInfo

# Bad
class State(TypedDict):
    user_name: str
    user_email: str
```

### 4. 기본값 제공
```python
# 초기 상태를 명확히
initial_state = {
    "messages": [],
    "logs": [],
    "count": 0,
    "user": None
}
```

## 핵심 개념 정리

### 1. Annotated 타입
```python
from typing import Annotated

# 형식: Annotated[타입, Reducer함수]
field: Annotated[int, operator.add]
```

### 2. Reducer 함수 시그니처
```python
def my_reducer(existing: T, new: T) -> T:
    # existing: 현재 상태의 값
    # new: 노드가 반환한 새 값
    # return: 병합된 값
    pass
```

### 3. 체크포인터
- 상태 영속성 제공
- thread_id로 세션 구분
- 각 노드 실행 후 자동 저장

## 다음 단계

복잡한 State 관리를 마스터했습니다!

다음 단계(Step 5)에서는 **조건부 엣지와 라우팅**을 배웁니다.

**Step 5에서 배울 내용:**
- 조건부 엣지 (Conditional Edge)
- 동적 라우팅
- 루프와 사이클
- 에이전트 의사결정 로직
