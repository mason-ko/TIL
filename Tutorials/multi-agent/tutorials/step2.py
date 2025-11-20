"""
Multi-Agent Step 2: Supervisor 패턴 (관리자 + 작업자)

pip install langgraph langchain-community
"""

from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict, Literal
from langchain_community.llms import Ollama


class State(TypedDict):
    task: str
    assigned_to: str
    research: str
    code: str
    review: str
    final_output: str


def supervisor(state: State) -> State:
    """Supervisor: 작업 분배"""
    task = state['task']

    # 간단한 라우팅 로직
    if "코드" in task or "프로그램" in task:
        assigned = "coder"
    elif "분석" in task or "조사" in task:
        assigned = "researcher"
    else:
        assigned = "researcher"

    print(f"[Supervisor] '{task}' → {assigned}에게 할당\n")
    return {"assigned_to": assigned}


def researcher(state: State) -> State:
    """작업자 1: 리서치"""
    print("[Researcher] 조사 중...")

    llm = Ollama(model="llama3")
    result = llm.invoke(f"{state['task']}에 대해 조사해줘")

    return {"research": result}


def coder(state: State) -> State:
    """작업자 2: 코딩"""
    print("[Coder] 코드 작성 중...")

    llm = Ollama(model="llama3")
    result = llm.invoke(f"{state['task']} 코드를 작성해줘")

    return {"code": result}


def reviewer(state: State) -> State:
    """작업자 3: 리뷰"""
    print("[Reviewer] 리뷰 중...")

    content = state.get('research') or state.get('code') or ""

    llm = Ollama(model="llama3")
    review = llm.invoke(f"다음 내용을 리뷰해줘:\n{content[:200]}")

    return {"review": review, "final_output": content}


def route_after_supervisor(state: State) -> Literal["researcher", "coder"]:
    """Supervisor 후 라우팅"""
    return state['assigned_to']


def main():
    print("=== Supervisor 패턴 ===\n")

    # 그래프 구성
    workflow = StateGraph(State)

    workflow.add_node("supervisor", supervisor)
    workflow.add_node("researcher", researcher)
    workflow.add_node("coder", coder)
    workflow.add_node("reviewer", reviewer)

    # 플로우
    workflow.add_edge(START, "supervisor")
    workflow.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {"researcher": "researcher", "coder": "coder"}
    )
    workflow.add_edge("researcher", "reviewer")
    workflow.add_edge("coder", "reviewer")
    workflow.add_edge("reviewer", END)

    app = workflow.compile()

    # 테스트
    tasks = [
        "Python FastAPI 서버 코드 작성",
        "Vector Database 조사",
    ]

    for task in tasks:
        print(f"\n{'='*60}")
        print(f"Task: {task}")
        print('='*60)

        try:
            result = app.invoke({"task": task})
            print(f"\n[최종] {result['assigned_to']} 완료")
            print(f"[리뷰] {result['review'][:100]}...\n")
        except Exception as e:
            print(f"❌ 오류: {e}")
            print("Ollama 실행 확인: ollama pull llama3")
            break


if __name__ == "__main__":
    main()
    print("\n✅ Supervisor 패턴 이해 완료!")
    print("\n💡 핵심: 관리자가 작업을 적절한 전문가에게 분배")
    print()
