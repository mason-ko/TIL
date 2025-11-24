# Step 6: 실전 프로젝트 (자동 리서치 봇)

## 목표

- 모든 패턴 통합
- 실용적인 Multi-Agent 시스템 구축
- 자동 리서치 및 보고서 생성
- 프로덕션 고려사항

## 프로젝트: 자동 리서치 봇

**주어진 주제에 대해 자동으로 조사하고 보고서 작성**

### 시스템 구조

```
User Input → Planner
              ↓
          [Supervisor]
        /      |      \
   Searcher Analyzer Writer
        \      |      /
          Reviewer
              ↓
         Final Report
```

### 에이전트 역할

| 에이전트 | 역할 |
|---------|------|
| **Planner** | 리서치 계획 수립, 하위 질문 생성 |
| **Supervisor** | 작업 분배 및 조율 |
| **Searcher** | 정보 검색 (웹, DB) |
| **Analyzer** | 데이터 분석 및 인사이트 도출 |
| **Writer** | 보고서 작성 |
| **Reviewer** | 품질 검토 및 피드백 |

## 전체 구현

### State 정의

```python
from typing_extensions import TypedDict, Annotated
from typing import Literal
import operator

class ResearchState(TypedDict):
    # 입력
    topic: str
    user_requirements: str

    # 계획
    sub_questions: Annotated[list, operator.add]
    assigned_tasks: dict

    # 결과
    search_results: Annotated[list, operator.add]
    analysis: str
    draft_report: str
    final_report: str

    # 메타데이터
    current_agent: str
    iteration: int
    feedback: Annotated[list, operator.add]
    status: Literal["planning", "researching", "analyzing", "writing", "reviewing", "completed"]
```

### 1. Planner

```python
def planner_agent(state: ResearchState):
    """리서치 계획 수립"""
    print(f"\n[Planner] '{state['topic']}' 리서치 계획 수립 중...")

    topic = state['topic']

    # 하위 질문 생성 (실제로는 LLM 사용)
    sub_questions = [
        f"{topic}이란 무엇인가?",
        f"{topic}의 장단점은?",
        f"{topic}의 실무 활용 사례는?",
        f"{topic}의 미래 전망은?"
    ]

    # 작업 할당
    tasks = {
        "searcher": sub_questions[:2],
        "analyzer": ["데이터 분석", "트렌드 파악"]
    }

    print(f"   생성된 하위 질문: {len(sub_questions)}개")

    return {
        "sub_questions": sub_questions,
        "assigned_tasks": tasks,
        "current_agent": "planner",
        "status": "researching",
        "iteration": state.get('iteration', 0) + 1
    }
```

### 2. Searcher

```python
def searcher_agent(state: ResearchState):
    """정보 검색"""
    print(f"\n[Searcher] 정보 검색 중...")

    questions = state.get('assigned_tasks', {}).get('searcher', [])

    results = []
    for q in questions:
        # 실제로는 웹 검색 API 사용
        result = {
            "question": q,
            "answer": f"{q}에 대한 검색 결과...",
            "sources": ["source1.com", "source2.com"]
        }
        results.append(result)
        print(f"   검색 완료: {q}")

    return {
        "search_results": results,
        "current_agent": "searcher",
        "status": "analyzing"
    }
```

### 3. Analyzer

```python
def analyzer_agent(state: ResearchState):
    """데이터 분석"""
    print(f"\n[Analyzer] 데이터 분석 중...")

    search_results = state.get('search_results', [])

    # 분석 (실제로는 LLM 사용)
    analysis = f"""
## 주요 발견사항

1. {state['topic']}은(는) 최근 주목받는 기술입니다
2. 장점: 효율성, 확장성
3. 단점: 학습 곡선
4. 활용 사례: {len(search_results)}개 발견

## 데이터 기반 인사이트

- 검색 결과 분석: {len(search_results)}개 소스
- 신뢰도: 높음
- 트렌드: 상승세
"""

    print("   분석 완료")

    return {
        "analysis": analysis,
        "current_agent": "analyzer",
        "status": "writing"
    }
```

### 4. Writer

```python
def writer_agent(state: ResearchState):
    """보고서 작성"""
    print(f"\n[Writer] 보고서 작성 중...")

    topic = state['topic']
    sub_questions = state.get('sub_questions', [])
    analysis = state.get('analysis', '')
    search_results = state.get('search_results', [])

    draft = f"""# {topic} 리서치 보고서

## 개요
본 보고서는 '{topic}'에 대한 종합적인 리서치 결과입니다.

## 조사 질문
{chr(10).join([f"- {q}" for q in sub_questions])}

## 분석 결과
{analysis}

## 검색 결과 요약
총 {len(search_results)}개의 소스를 조사했습니다.

## 결론
{topic}은(는) 실무에서 활용 가능한 기술입니다.

---
생성 일시: 2024-01-01
작성자: AI Research Bot
"""

    print("   초안 작성 완료")

    return {
        "draft_report": draft,
        "current_agent": "writer",
        "status": "reviewing"
    }
```

### 5. Reviewer

```python
def reviewer_agent(state: ResearchState):
    """품질 검토"""
    print(f"\n[Reviewer] 보고서 검토 중...")

    draft = state.get('draft_report', '')
    iteration = state.get('iteration', 0)

    # 검토 기준
    has_structure = "##" in draft
    has_conclusion = "결론" in draft
    min_length = len(draft) > 500

    # 피드백
    if has_structure and has_conclusion and min_length:
        feedback = "✅ 보고서 품질 우수. 승인합니다."
        status = "completed"
        final = draft
    else:
        feedback = "⚠️ 개선 필요: 구조, 결론, 분량을 보완하세요."
        status = "writing"  # 재작성 요청
        final = ""

    print(f"   {feedback}")

    return {
        "feedback": [feedback],
        "current_agent": "reviewer",
        "status": status,
        "final_report": final
    }
```

### 6. Supervisor

```python
def supervisor_agent(state: ResearchState):
    """작업 조율"""
    status = state['status']

    # 다음 에이전트 결정
    if status == "planning":
        return "planner"
    elif status == "researching":
        return "searcher"
    elif status == "analyzing":
        return "analyzer"
    elif status == "writing":
        return "writer"
    elif status == "reviewing":
        return "reviewer"
    else:
        return "end"
```

### LangGraph 통합

```python
from langgraph.graph import StateGraph, START, END

# 그래프 구성
workflow = StateGraph(ResearchState)

# 노드 추가
workflow.add_node("planner", planner_agent)
workflow.add_node("searcher", searcher_agent)
workflow.add_node("analyzer", analyzer_agent)
workflow.add_node("writer", writer_agent)
workflow.add_node("reviewer", reviewer_agent)

# 흐름
workflow.add_edge(START, "planner")
workflow.add_edge("planner", "searcher")
workflow.add_edge("searcher", "analyzer")
workflow.add_edge("analyzer", "writer")

# 리뷰 후 분기
def route_after_review(state):
    status = state['status']
    if status == "completed":
        return "end"
    else:
        return "writer"  # 재작성

workflow.add_conditional_edges(
    "reviewer",
    route_after_review,
    {
        "writer": "writer",
        "end": END
    }
)

workflow.add_edge("writer", "reviewer")

# 컴파일
app = workflow.compile()
```

### 실행

```python
# 입력
initial_state = {
    "topic": "LangGraph",
    "user_requirements": "실무 활용 가능성 조사",
    "sub_questions": [],
    "assigned_tasks": {},
    "search_results": [],
    "analysis": "",
    "draft_report": "",
    "final_report": "",
    "current_agent": "",
    "iteration": 0,
    "feedback": [],
    "status": "planning"
}

# 실행
result = app.invoke(initial_state)

# 결과
print("\n" + "="*60)
print("📄 최종 보고서")
print("="*60)
print(result['final_report'])
```

## 프로덕션 고려사항

### 1. 에러 핸들링

```python
def safe_agent(agent_func):
    """에이전트 래퍼 - 에러 처리"""
    def wrapper(state):
        try:
            return agent_func(state)
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            return {
                "feedback": [f"오류: {e}"],
                "status": "error"
            }
    return wrapper

# 사용
workflow.add_node("searcher", safe_agent(searcher_agent))
```

### 2. 타임아웃

```python
import signal

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("에이전트 실행 시간 초과")

# 5분 타임아웃
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(300)

try:
    result = app.invoke(initial_state)
finally:
    signal.alarm(0)
```

### 3. 로깅 및 모니터링

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def planner_agent(state):
    logger.info(f"Planner started: {state['topic']}")
    # 작업 수행
    logger.info("Planner completed")
    return {...}
```

### 4. 비용 추적

```python
class CostTracker:
    def __init__(self):
        self.total_tokens = 0
        self.total_cost = 0

    def track(self, agent_name, tokens):
        cost = tokens * 0.0001  # 예시 비용
        self.total_tokens += tokens
        self.total_cost += cost
        print(f"[Cost] {agent_name}: {tokens} tokens, ${cost:.4f}")

tracker = CostTracker()
```

## 확장 아이디어

### 1. 실시간 웹 검색

```python
from langchain.tools import DuckDuckGoSearchRun

search = DuckDuckGoSearchRun()

def searcher_agent(state):
    questions = state['assigned_tasks']['searcher']
    results = []

    for q in questions:
        result = search.run(q)
        results.append({"question": q, "answer": result})

    return {"search_results": results}
```

### 2. 이미지/차트 생성

```python
import matplotlib.pyplot as plt

def visualizer_agent(state):
    # 데이터 시각화
    data = state['analysis_data']

    plt.figure()
    plt.plot(data)
    plt.savefig('chart.png')

    return {"chart": "chart.png"}
```

### 3. 다국어 지원

```python
def translator_agent(state):
    """보고서 번역"""
    report = state['final_report']
    target_lang = state.get('target_lang', 'en')

    # 번역 API 사용
    translated = translate(report, target_lang)

    return {"final_report": translated}
```

## 다음 단계

**추가 학습 자료:**
1. **LangSmith/Langfuse**: Multi-Agent 디버깅
2. **Advanced RAG**: 정보 검색 품질 향상
3. **Fine-tuning**: 특화된 에이전트 모델

---

**핵심 요약:**
1. Multi-Agent = 협업하는 AI 시스템
2. 각 에이전트는 전문화된 역할
3. State로 정보 공유
4. 프로덕션에서는 에러 처리, 로깅, 비용 추적 필수

**축하합니다! Multi-Agent 튜토리얼 완료!** 🎉
