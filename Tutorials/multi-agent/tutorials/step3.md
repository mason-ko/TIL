# Step 3: Collaborative 패턴 (대화형 협업)

## 목표

- 에이전트 간 대화형 협업 구현
- 동적 의사결정
- 자율적 워크플로우
- 네트워크 구조 이해

## Collaborative 패턴이란?

**에이전트들이 서로 대화하며 협력**

```
      Agent 1
        ↕  ↘
      Agent 2 → Agent 3
        ↕
      Agent 4
```

### Supervisor vs Collaborative

| 항목 | Supervisor | Collaborative |
|------|-----------|---------------|
| **구조** | 중앙 집중형 | 분산형 |
| **의사결정** | Manager가 결정 | 각자 판단 |
| **통신** | Manager 경유 | 직접 통신 |
| **유연성** | 고정된 흐름 | 동적 흐름 |
| **복잡도** | 낮음 | 높음 |

## 실제 사례

### 소프트웨어 개발팀 시뮬레이션

```python
Architect: "API 설계했어. @Developer 구현해줘"
Developer: "구현 완료. @Reviewer 리뷰 부탁"
Reviewer: "몇 가지 수정 필요. @Developer 수정해줘"
Developer: "수정 완료. @Tester 테스트 부탁"
Tester: "모두 통과! @Deployer 배포 가능"
```

## 구현

### State 정의

```python
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph import add_messages

class CollaborativeState(TypedDict):
    messages: Annotated[list, add_messages]
    task: str
    current_agent: str
    iterations: int
    final_result: str
```

### 대화형 에이전트

```python
from langchain_community.llms import Ollama

class CollaborativeAgent:
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.llm = Ollama(model="llama3")

    def act(self, state):
        """에이전트 행동"""
        messages = state['messages']
        context = "\n".join([m['content'] for m in messages[-3:]])

        prompt = f"""당신은 {self.role}입니다.
현재 상황:
{context}

다음에 할 행동을 결정하세요:
1. 작업 수행 및 결과 공유
2. 다른 에이전트에게 작업 요청
3. 작업 완료 선언

답변:"""

        response = self.llm.invoke(prompt)

        return {
            "messages": [{
                "role": self.name,
                "content": response
            }],
            "current_agent": self.name
        }

# 에이전트 생성
architect = CollaborativeAgent("Architect", "시스템 설계자")
developer = CollaborativeAgent("Developer", "개발자")
reviewer = CollaborativeAgent("Reviewer", "코드 리뷰어")
```

### 다음 에이전트 결정

```python
def decide_next_agent(state) -> str:
    """다음 에이전트 자동 결정"""
    last_message = state['messages'][-1]['content'].lower()
    current = state['current_agent']

    # 키워드 기반 라우팅
    if "설계" in last_message and current != "architect":
        return "architect"
    elif ("구현" in last_message or "코드" in last_message) and current != "developer":
        return "developer"
    elif "리뷰" in last_message and current != "reviewer":
        return "reviewer"
    elif "완료" in last_message or "끝" in last_message:
        return "end"
    else:
        # 라운드 로빈
        agents = ["architect", "developer", "reviewer"]
        idx = agents.index(current) if current in agents else 0
        return agents[(idx + 1) % len(agents)]
```

### LangGraph 구성

```python
from langgraph.graph import StateGraph, START, END

def architect_node(state):
    print("[Architect] 설계 중...")
    agent = CollaborativeAgent("Architect", "시스템 설계자")
    return agent.act(state)

def developer_node(state):
    print("[Developer] 구현 중...")
    agent = CollaborativeAgent("Developer", "개발자")
    return agent.act(state)

def reviewer_node(state):
    print("[Reviewer] 리뷰 중...")
    agent = CollaborativeAgent("Reviewer", "코드 리뷰어")
    return agent.act(state)

# 그래프
workflow = StateGraph(CollaborativeState)

workflow.add_node("architect", architect_node)
workflow.add_node("developer", developer_node)
workflow.add_node("reviewer", reviewer_node)

# 순환 구조
workflow.add_edge(START, "architect")

workflow.add_conditional_edges(
    "architect",
    decide_next_agent,
    {
        "developer": "developer",
        "reviewer": "reviewer",
        "architect": "architect",
        "end": END
    }
)

workflow.add_conditional_edges(
    "developer",
    decide_next_agent,
    {
        "architect": "architect",
        "reviewer": "reviewer",
        "developer": "developer",
        "end": END
    }
)

workflow.add_conditional_edges(
    "reviewer",
    decide_next_agent,
    {
        "architect": "architect",
        "developer": "developer",
        "reviewer": "reviewer",
        "end": END
    }
)

app = workflow.compile()
```

### 실행

```python
initial_state = {
    "messages": [{
        "role": "user",
        "content": "사용자 인증 API를 만들어주세요"
    }],
    "task": "사용자 인증 API 개발",
    "current_agent": "architect",
    "iterations": 0
}

# 최대 반복 제한
config = {"recursion_limit": 10}

result = app.invoke(initial_state, config=config)

# 대화 이력 출력
for msg in result['messages']:
    print(f"\n[{msg['role']}]")
    print(msg['content'][:200])
```

## 고급 패턴

### 1. 투표 메커니즘

```python
def consensus_decision(state):
    """다수결로 결정"""
    votes = {}

    for agent in [architect, developer, reviewer]:
        vote = agent.vote(state)  # "approve" or "reject"
        votes[agent.name] = vote

    approve_count = sum(1 for v in votes.values() if v == "approve")

    if approve_count >= 2:
        return "approved"
    else:
        return "rejected"
```

### 2. 우선순위 큐

```python
import heapq

class TaskQueue:
    def __init__(self):
        self.queue = []

    def add_task(self, priority, agent, task):
        heapq.heappush(self.queue, (priority, agent, task))

    def get_next(self):
        if self.queue:
            return heapq.heappop(self.queue)
        return None

# 사용
queue = TaskQueue()
queue.add_task(1, "architect", "설계")
queue.add_task(2, "developer", "구현")
queue.add_task(1, "security", "보안 검토")  # 높은 우선순위
```

### 3. 병렬 협업

```python
from langgraph.pregel import Channel

# 여러 에이전트 동시 실행
workflow.add_conditional_edges(
    "architect",
    lambda s: ["developer", "tester"],  # 둘 다 병렬 실행
    {
        "developer": "developer",
        "tester": "tester"
    }
)

# 결과 병합
def merge_results(state):
    """여러 에이전트 결과 통합"""
    dev_result = state.get('code', '')
    test_result = state.get('tests', '')

    combined = f"Code:\n{dev_result}\n\nTests:\n{test_result}"

    return {"final_result": combined}
```

## 무한 루프 방지

### 1. 반복 횟수 제한

```python
def check_iterations(state):
    """최대 반복 체크"""
    iterations = state.get('iterations', 0) + 1

    if iterations > 10:
        print("⚠️ 최대 반복 도달")
        return "end"

    return {"iterations": iterations}

# 각 노드에 추가
workflow.add_node("check", check_iterations)
```

### 2. 진행률 모니터링

```python
def calculate_progress(state):
    """작업 진행률 계산"""
    required_steps = ["design", "implement", "review", "test"]
    completed = state.get('completed_steps', [])

    progress = len(completed) / len(required_steps) * 100

    if progress >= 100:
        return "end"

    return {"progress": progress}
```

### 3. 타임아웃

```python
import time

start_time = time.time()
TIMEOUT = 300  # 5분

def check_timeout(state):
    elapsed = time.time() - start_time

    if elapsed > TIMEOUT:
        print("⏰ 타임아웃")
        return "end"

    return {}
```

## 실전 활용

### 리서치 팀 시뮬레이션

```python
# 역할
Searcher: "웹 검색 및 정보 수집"
Analyst: "데이터 분석 및 패턴 발견"
Writer: "보고서 작성"
Critic: "내용 검토 및 피드백"

# 흐름
1. Searcher가 정보 수집
2. Analyst가 분석
3. Writer가 초안 작성
4. Critic이 검토
   → 수정 필요 시 Writer에게 회신
   → 완료 시 종료
```

## 장단점

### 장점
- ✅ 동적이고 유연함
- ✅ 실제 팀 작업 방식과 유사
- ✅ 복잡한 문제에 적합
- ✅ 에이전트 자율성

### 단점
- ❌ 디버깅 어려움
- ❌ 무한 루프 위험
- ❌ 예측 불가능
- ❌ 높은 복잡도

## 다음 단계

**Step 4: Tool Sharing**
- 여러 에이전트가 도구 공유
- 외부 API 연동
- 실제 작업 수행

---

**핵심 요약:**
1. Collaborative = 에이전트 간 대화형 협업
2. 동적 라우팅으로 다음 단계 결정
3. 무한 루프 방지 필수
4. 실제 팀 작업 패턴 시뮬레이션 가능
