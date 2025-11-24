# Step 4: Tool Sharing (도구 공유)

## 목표

- 여러 에이전트가 동일한 도구 공유
- 외부 API 연동
- 실제 작업 수행 (파일, 웹 검색 등)

## Tool이란?

**에이전트가 사용할 수 있는 함수**

```python
# 도구 예시
def search_web(query: str) -> str:
    """웹 검색"""
    return f"'{query}'에 대한 검색 결과"

def save_file(filename: str, content: str) -> str:
    """파일 저장"""
    with open(filename, 'w') as f:
        f.write(content)
    return f"파일 저장: {filename}"

def send_email(to: str, subject: str) -> str:
    """이메일 발송"""
    return f"이메일 발송: {to}"
```

## LangChain Tool 정의

```python
from langchain.tools import tool

@tool
def calculator(expression: str) -> str:
    """간단한 계산 수행"""
    try:
        result = eval(expression)
        return f"결과: {result}"
    except Exception as e:
        return f"오류: {e}"

@tool
def web_search(query: str) -> str:
    """웹 검색 (시뮬레이션)"""
    # 실제로는 API 호출
    return f"'{query}'에 대한 검색 결과: ..."
```

## 에이전트에 Tool 바인딩

```python
from langgraph.prebuilt import ToolNode
from langchain_community.llms import Ollama

# Tool 정의
tools = [calculator, web_search]

# LLM에 도구 바인딩
llm = Ollama(model="llama3")
llm_with_tools = llm.bind_tools(tools)

# Tool 노드
tool_node = ToolNode(tools)
```

## Multi-Agent with Tools

### State 정의

```python
from typing_extensions import TypedDict, Annotated
from langgraph.graph.message import add_messages

class StateWithTools(TypedDict):
    messages: Annotated[list, add_messages]
    task: str
```

### 에이전트 구현

```python
def researcher_agent(state):
    """리서처 - 웹 검색 도구 사용"""
    messages = state['messages']

    # LLM에게 도구 사용 허용
    response = llm_with_tools.invoke(messages)

    # Tool call이 있으면 실행
    if hasattr(response, 'tool_calls') and response.tool_calls:
        return {"messages": [response]}

    return {"messages": [response]}

def analyst_agent(state):
    """분석가 - 계산 도구 사용"""
    messages = state['messages']
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}
```

### 그래프 구성

```python
from langgraph.graph import StateGraph, START, END

workflow = StateGraph(StateWithTools)

# 에이전트 노드
workflow.add_node("researcher", researcher_agent)
workflow.add_node("analyst", analyst_agent)

# Tool 노드 (공유)
workflow.add_node("tools", tool_node)

# 흐름
workflow.add_edge(START, "researcher")
workflow.add_conditional_edges(
    "researcher",
    lambda s: "tools" if needs_tool(s) else "analyst"
)
workflow.add_edge("tools", "analyst")
workflow.add_edge("analyst", END)

app = workflow.compile()
```

## 실전 예제: 데이터 분석 팀

```python
from langchain.tools import tool
import json

@tool
def fetch_data(source: str) -> str:
    """데이터 수집"""
    # 시뮬레이션
    data = {"users": 1000, "revenue": 50000}
    return json.dumps(data)

@tool
def analyze_data(data: str) -> str:
    """데이터 분석"""
    parsed = json.loads(data)
    avg_revenue = parsed["revenue"] / parsed["users"]
    return f"사용자당 평균 매출: ${avg_revenue}"

@tool
def create_report(analysis: str) -> str:
    """보고서 생성"""
    return f"### 분석 보고서\n\n{analysis}"

# 에이전트
def data_collector(state):
    """데이터 수집 에이전트"""
    return fetch_data.invoke({"source": "database"})

def data_analyst(state):
    """분석 에이전트"""
    data = state['data']
    return analyze_data.invoke({"data": data})

def report_writer(state):
    """보고서 작성 에이전트"""
    analysis = state['analysis']
    return create_report.invoke({"analysis": analysis})
```

## Tool Sharing의 장점

### 1. 재사용성

```python
# 동일한 도구를 여러 에이전트가 공유
Researcher → web_search
Analyst → web_search
Writer → web_search
```

### 2. 일관성

```python
# 모든 에이전트가 동일한 방식으로 파일 저장
save_file(filename, content)
```

### 3. 유지보수

```python
# 도구 하나만 수정하면 모든 에이전트에 반영
@tool
def web_search_v2(query: str) -> str:
    # 개선된 검색 로직
    pass
```

## 실무 도구 예시

### 파일 시스템

```python
@tool
def read_file(filepath: str) -> str:
    """파일 읽기"""
    with open(filepath, 'r') as f:
        return f.read()

@tool
def write_file(filepath: str, content: str) -> str:
    """파일 쓰기"""
    with open(filepath, 'w') as f:
        f.write(content)
    return f"저장 완료: {filepath}"
```

### API 호출

```python
@tool
def call_api(endpoint: str, params: dict) -> str:
    """외부 API 호출"""
    import requests
    response = requests.get(endpoint, params=params)
    return response.text
```

### 데이터베이스

```python
@tool
def query_database(sql: str) -> str:
    """데이터베이스 쿼리"""
    # 실제 DB 연결
    results = execute_query(sql)
    return str(results)
```

## 다음 단계

**Step 5: State Management**
- 복잡한 상태 관리
- 체크포인트
- 대화 이력 유지

---

**핵심 요약:**
1. Tool = 에이전트가 사용하는 함수
2. @tool 데코레이터로 정의
3. 여러 에이전트가 공유 가능
4. 실제 작업 수행 (파일, API, DB)
