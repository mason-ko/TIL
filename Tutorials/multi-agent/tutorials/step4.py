"""
Multi-Agent Step 4: Tool Sharing (도구 공유)

pip install langgraph langchain-community
"""

from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from typing import Annotated
import operator
import json


# Tool 정의 (간단한 시뮬레이션)
def web_search_tool(query: str) -> str:
    """웹 검색 도구 (시뮬레이션)"""
    # 실제로는 Google API 등 사용
    results = {
        "LangGraph": "상태 기반 워크플로우 라이브러리",
        "Vector DB": "임베딩 벡터 저장 및 검색",
        "RAG": "검색 기반 생성 기법"
    }

    for key in results:
        if key.lower() in query.lower():
            return results[key]

    return f"'{query}'에 대한 정보를 찾지 못했습니다"


def calculator_tool(expression: str) -> str:
    """계산 도구"""
    try:
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"계산 오류: {e}"


def file_save_tool(filename: str, content: str) -> str:
    """파일 저장 도구"""
    # 실제로는 파일 저장
    return f"✅ 파일 저장 완료: {filename} ({len(content)} 글자)"


class State(TypedDict):
    task: str
    messages: Annotated[list, operator.add]
    search_result: str
    calculation: str
    final_report: str


def researcher(state: State) -> State:
    """Researcher: 정보 검색"""
    print("\n[Researcher] 정보 검색 중...")

    task = state['task']

    # 웹 검색 도구 사용
    result = web_search_tool(task)

    print(f"   검색 결과: {result}")

    return {
        "messages": [f"[Researcher] {result}"],
        "search_result": result
    }


def analyst(state: State) -> State:
    """Analyst: 데이터 분석"""
    print("\n[Analyst] 데이터 분석 중...")

    # 계산 도구 사용 (예시)
    calculation = calculator_tool("1000 * 0.15")

    print(f"   분석 결과: {calculation}")

    return {
        "messages": [f"[Analyst] {calculation}"],
        "calculation": calculation
    }


def writer(state: State) -> State:
    """Writer: 보고서 작성"""
    print("\n[Writer] 보고서 작성 중...")

    search = state.get('search_result', '')
    calc = state.get('calculation', '')

    # 보고서 생성
    report = f"""
### 분석 보고서

**주제**: {state['task']}

**조사 결과**:
{search}

**분석**:
{calc}

**결론**:
위 데이터를 기반으로 분석을 완료했습니다.
"""

    # 파일 저장 도구 사용
    save_msg = file_save_tool("report.md", report)

    print(f"   {save_msg}")

    return {
        "messages": [f"[Writer] 보고서 작성 완료"],
        "final_report": report
    }


def main():
    print("=== Tool Sharing 패턴 ===\n")
    print("여러 에이전트가 동일한 도구를 공유합니다\n")

    # 그래프 구성
    workflow = StateGraph(State)

    workflow.add_node("researcher", researcher)
    workflow.add_node("analyst", analyst)
    workflow.add_node("writer", writer)

    # 순차 실행
    workflow.add_edge(START, "researcher")
    workflow.add_edge("researcher", "analyst")
    workflow.add_edge("analyst", "writer")
    workflow.add_edge("writer", END)

    app = workflow.compile()

    # 실행
    print("="*60)
    print("Task: LangGraph에 대해 조사")
    print("="*60)

    result = app.invoke({
        "task": "LangGraph에 대해 조사",
        "messages": [],
        "search_result": "",
        "calculation": "",
        "final_report": ""
    })

    print("\n" + "="*60)
    print("✅ 작업 완료!")
    print("="*60)

    print("\n📊 최종 보고서:")
    print(result['final_report'])

    print("\n💡 사용된 도구:")
    print("   1. web_search_tool - Researcher")
    print("   2. calculator_tool - Analyst")
    print("   3. file_save_tool - Writer")


if __name__ == "__main__":
    main()
    print("\n📚 다음: step5.py - State Management\n")
