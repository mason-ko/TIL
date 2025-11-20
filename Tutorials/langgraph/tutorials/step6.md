# Step 6: 실용적인 에이전트

## 개요
지금까지 배운 모든 것을 종합하여 실제로 사용할 수 있는 에이전트를 만듭니다!
Tool을 사용하고, ReAct 패턴으로 사고하며, 에러를 처리하는 견고한 에이전트를 구축합니다.

## 사전 준비

### 필요한 패키지 설치
```bash
pip install langgraph langchain-google-genai
```

### 실행
```bash
python tutorials/step6.py
```

## Tool이란?

**정의:**
- LLM이 외부 기능을 호출할 수 있게 하는 함수
- 계산, 검색, API 호출 등 LLM이 직접 할 수 없는 작업 수행

**왜 필요한가?**
- LLM은 텍스트 생성만 가능
- 실시간 데이터나 정확한 계산은 불가능
- Tool을 통해 실제 작업 수행 능력 획득

## Tool 정의 방법

### 1. @tool 데코레이터 사용

```python
from langchain_core.tools import tool

@tool
def calculate(expression: str) -> str:
    """
    수학 계산을 수행합니다.
    expression: 계산할 수식 (예: "2 + 3")
    """
    result = eval(expression)
    return f"계산 결과: {result}"
```

**중요:**
- 독스트링(docstring)은 LLM에게 tool 사용법을 알려줌
- 반드시 명확하게 작성!
- 파라미터와 반환값 설명 포함

### 2. Tool의 구조

```python
@tool
def tool_name(param1: type, param2: type) -> return_type:
    """
    Tool 설명 - LLM이 읽음
    param1: 파라미터 설명
    param2: 파라미터 설명
    """
    # 실제 작업 수행
    return result
```

## LLM에 Tool 바인딩

```python
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
tools = [calculate, get_weather, search_web]

# Tool을 LLM에 연결
llm_with_tools = llm.bind_tools(tools)
```

**bind_tools의 역할:**
- LLM에게 사용 가능한 tool 목록을 알려줌
- LLM이 필요 시 tool 호출을 생성하도록 함

## Tool 호출 흐름

```
1. 사용자: "25 곱하기 4는?"

2. LLM: "calculate tool을 호출해야겠다"
   → tool_calls 생성

3. Tool 실행: calculate("25 * 4")
   → "계산 결과: 100"

4. LLM: Tool 결과를 보고 답변 생성
   → "25 곱하기 4는 100입니다."
```

## 코드 설명

### 1. 간단한 Tool Agent (`simple_tool_agent_example`)

**그래프 구조:**
```
          ┌──────────┐
          ↓          │
START → agent → tools ┘
          │
          ↓
         END
```

**핵심 컴포넌트:**

**ToolNode:**
```python
from langgraph.prebuilt import ToolNode

tool_node = ToolNode(tools)
```

- LangGraph 내장 노드
- 자동으로 tool 실행
- tool_calls를 읽고 해당 tool 호출
- 결과를 ToolMessage로 반환

**조건부 분기:**
```python
def should_continue(state: State) -> Literal["tools", "end"]:
    last_message = state["messages"][-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"  # Tool 호출 필요
    else:
        return "end"    # 최종 답변 완성
```

**실행 흐름:**
1. Agent: LLM이 메시지 보고 판단
2. Tool 필요? → tools 노드로
3. Tools: Tool 실행, 결과 반환
4. 다시 Agent로 (결과를 보고 다음 판단)
5. Tool 불필요? → END

### 2. ReAct 패턴 (`react_agent_example`)

**ReAct = Reasoning + Acting**

```
Thought: 서울 날씨를 확인해야겠다
Action: get_weather("서울")
Observation: 서울의 날씨: 맑음, 15도

Thought: 15도를 화씨로 변환해야겠다
Action: calculate("15 * 9/5 + 32")
Observation: 계산 결과: 59

Thought: 이제 답변할 수 있다
Answer: 서울은 맑음 15도(59°F)입니다.
```

**구현:**

**System 메시지로 사고 패턴 강제:**
```python
system_msg = SystemMessage(content="""
당신은 단계별로 사고하는 에이전트입니다.
각 단계마다:
1. 현재 상황을 분석하고
2. 필요한 도구를 사용하거나
3. 최종 답변을 제공하세요.
""")
```

**반복 제한:**
```python
if state["iterations"] >= 10:
    return "max_iterations"
```

무한 루프 방지!

**복잡한 질문 처리:**
- 여러 tool을 순차적으로 사용
- 중간 결과를 바탕으로 다음 행동 결정
- 모든 정보가 모이면 최종 답변 생성

### 3. 스트리밍 Agent (`streaming_agent_example`)

**stream() 메서드:**
```python
for step in app.stream(input, stream_mode="updates"):
    for node_name, node_output in step.items():
        print(f"[{node_name}]")
        # 각 노드의 출력 확인
```

**stream_mode 옵션:**
- `"values"`: 전체 state (기본값)
- `"updates"`: 노드별 업데이트만
- `"messages"`: 메시지 증분만

**장점:**
- 실시간으로 agent 사고 과정 관찰
- 디버깅에 매우 유용
- 사용자에게 진행 상황 표시 가능

### 4. 에러 처리 (`error_handling_agent_example`)

**견고한 Agent 만들기:**

**Tool 실행 시 에러 처리:**
```python
try:
    result = tool.invoke(args)
    tool_results.append(ToolMessage(content=str(result)))
except Exception as e:
    # 에러를 LLM에게 알림
    tool_results.append(
        ToolMessage(content=f"오류 발생: {str(e)}")
    )
```

**에러 카운트 추적:**
```python
class State(TypedDict):
    messages: Annotated[list, add_messages]
    error_count: int

# 에러 발생 시 카운트 증가
return {"error_count": state["error_count"] + 1}
```

**너무 많은 에러 시 중단:**
```python
if state["error_count"] >= 3:
    return "too_many_errors"
```

**LLM에게 에러 알리는 이유:**
- LLM이 다른 방법 시도 가능
- 사용자에게 명확한 에러 메시지 전달
- Agent가 스스로 문제 해결 시도

## ToolNode 내부 동작

```python
# LangGraph의 ToolNode가 하는 일

def tool_node(state: State) -> State:
    last_message = state["messages"][-1]
    tool_results = []

    # 각 tool call 실행
    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        # Tool 찾기 및 실행
        result = tools[tool_name].invoke(tool_args)

        # ToolMessage 생성
        tool_results.append(
            ToolMessage(
                content=result,
                tool_call_id=tool_call["id"]
            )
        )

    return {"messages": tool_results}
```

## 메시지 타입 정리

### HumanMessage
- 사용자 입력
- `HumanMessage(content="질문")`

### AIMessage
- LLM 응답
- `tool_calls` 속성: tool 호출 정보
- `content`: 텍스트 응답

### ToolMessage
- Tool 실행 결과
- `tool_call_id`: 어떤 tool call의 결과인지
- `content`: tool 반환값

### SystemMessage
- LLM 행동 지시
- Agent 페르소나 정의

## Agent 설계 패턴

### 패턴 1: 단순 Tool Agent
```
사용자 → Agent → Tool? → 답변
```

- 간단한 작업
- 1-2개 tool 사용

### 패턴 2: ReAct Agent
```
사용자 → Agent ⇄ Tools (반복) → 답변
```

- 복잡한 작업
- 여러 tool 조합
- 중간 결과 기반 판단

### 패턴 3: 전문화된 Agent
```
분류 → 전문 Agent 1 → ...
      → 전문 Agent 2 → ...
      → 전문 Agent 3 → ...
```

- 도메인별 전문 agent
- 각자 다른 tool 사용

## 디버깅 팁

### 1. 메시지 이력 출력
```python
for msg in state["messages"]:
    print(f"{type(msg).__name__}: {msg.content}")
    if hasattr(msg, "tool_calls"):
        print(f"  Tool calls: {msg.tool_calls}")
```

### 2. 스트리밍으로 관찰
```python
for step in app.stream(input):
    print(step)
```

### 3. 반복 횟수 추적
```python
class State(TypedDict):
    iterations: int  # 디버깅용

# 각 반복마다 로그
print(f"반복 {state['iterations']}: ...")
```

### 4. Tool 호출 로그
```python
print(f"Tool 호출: {tool_call['name']}({tool_call['args']})")
print(f"Tool 결과: {result}")
```

## Tool 작성 베스트 프랙티스

### 1. 명확한 독스트링
```python
@tool
def search(query: str, limit: int = 5) -> str:
    """
    웹에서 정보를 검색합니다.

    Args:
        query: 검색 쿼리 (예: "Python 튜토리얼")
        limit: 최대 결과 수 (기본값: 5)

    Returns:
        검색 결과 문자열
    """
```

### 2. 에러 처리
```python
@tool
def api_call(endpoint: str) -> str:
    """API 호출"""
    try:
        response = requests.get(endpoint)
        return response.text
    except Exception as e:
        return f"API 호출 실패: {str(e)}"
```

### 3. 입력 검증
```python
@tool
def divide(a: float, b: float) -> str:
    """나눗셈"""
    if b == 0:
        return "오류: 0으로 나눌 수 없습니다"
    return str(a / b)
```

### 4. 타입 힌트
```python
@tool
def process_data(data: dict) -> dict:
    """데이터 처리"""
    # 타입이 명확하면 LLM이 올바른 인자 생성
```

## 실전 활용 예시

### 1. 고객 지원 Agent
```python
tools = [
    search_knowledge_base,
    create_ticket,
    check_order_status,
    send_email
]
# 고객 질문 → 지식베이스 검색 → 티켓 생성 또는 답변
```

### 2. 데이터 분석 Agent
```python
tools = [
    query_database,
    calculate_statistics,
    generate_chart,
    send_report
]
# 요청 → 데이터 조회 → 분석 → 시각화 → 보고서
```

### 3. 코딩 Assistant Agent
```python
tools = [
    search_documentation,
    run_code,
    analyze_error,
    suggest_fix
]
# 코드 문제 → 에러 분석 → 문서 검색 → 해결책 제시
```

## 핵심 개념 정리

### 1. Tool은 Agent의 손과 발
- LLM(뇌) + Tool(손발) = 실제 작업 수행 가능한 Agent

### 2. ReAct 패턴
- Reasoning: 상황 분석, 계획 수립
- Acting: Tool 사용, 행동 실행
- 반복하며 목표 달성

### 3. ToolNode의 편리함
- 자동으로 tool 실행
- 결과를 ToolMessage로 변환
- 에러 처리 커스터마이징 가능

### 4. 견고성이 중요
- 에러 처리
- 최대 반복 제한
- 입력 검증

## 다음 단계

축하합니다! LangGraph의 핵심을 모두 배웠습니다!

**여기서 더 나아가려면:**

1. **공식 문서 탐색**
   - https://langchain-ai.github.io/langgraph/

2. **고급 기능**
   - Subgraphs: 그래프 안에 그래프
   - Human-in-the-loop: 사람의 승인 필요
   - 영속적 체크포인터: DB에 상태 저장

3. **실전 프로젝트**
   - 자신만의 도메인에 Agent 적용
   - 커스텀 Tool 개발
   - 복잡한 워크플로우 설계

4. **성능 최적화**
   - 프롬프트 엔지니어링
   - Tool 응답 최적화
   - 비용 및 latency 개선

**Happy Building! 🚀**
