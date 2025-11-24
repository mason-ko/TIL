"""
Multi-Agent Step 3: Collaborative 패턴 (대화형 협업)

pip install langgraph langchain-community
"""

from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from typing import Annotated, Literal
import operator


class State(TypedDict):
    task: str
    messages: Annotated[list, operator.add]
    current_agent: str
    iterations: int
    completed: bool


def architect(state: State) -> State:
    """Architect: 시스템 설계"""
    print(f"\n[Architect] 반복 {state.get('iterations', 0) + 1}")

    task = state['task']

    # 설계 작업 (시뮬레이션)
    design = f"'{task}'에 대한 시스템 설계를 완료했습니다. @Developer에게 구현 요청합니다."

    print(f"   → {design}")

    return {
        "messages": [f"[Architect] {design}"],
        "current_agent": "architect",
        "iterations": state.get('iterations', 0) + 1
    }


def developer(state: State) -> State:
    """Developer: 구현"""
    print(f"\n[Developer] 반복 {state.get('iterations', 0)}")

    # 구현 작업
    code = "코드 구현을 완료했습니다. @Reviewer에게 리뷰 요청합니다."

    print(f"   → {code}")

    return {
        "messages": [f"[Developer] {code}"],
        "current_agent": "developer"
    }


def reviewer(state: State) -> State:
    """Reviewer: 코드 리뷰"""
    print(f"\n[Reviewer] 반복 {state.get('iterations', 0)}")

    iterations = state.get('iterations', 0)

    # 리뷰 결과 (2번째 반복에서 승인)
    if iterations >= 2:
        review = "리뷰 완료. 모든 것이 좋습니다. 작업을 승인합니다."
        completed = True
    else:
        review = "몇 가지 수정이 필요합니다. @Developer에게 수정 요청합니다."
        completed = False

    print(f"   → {review}")

    return {
        "messages": [f"[Reviewer] {review}"],
        "current_agent": "reviewer",
        "completed": completed
    }


def route_next(state: State) -> Literal["developer", "reviewer", "end"]:
    """다음 에이전트 결정"""
    current = state['current_agent']
    completed = state.get('completed', False)
    iterations = state.get('iterations', 0)

    # 최대 반복 체크
    if iterations > 5:
        print("\n⚠️ 최대 반복 횟수 도달")
        return "end"

    # 완료 체크
    if completed:
        return "end"

    # 순환
    if current == "architect":
        return "developer"
    elif current == "developer":
        return "reviewer"
    else:  # reviewer
        return "developer"  # 수정 요청


def main():
    print("=== Collaborative 패턴 ===\n")
    print("에이전트들이 대화하며 협업합니다\n")

    # 그래프 구성
    workflow = StateGraph(State)

    workflow.add_node("architect", architect)
    workflow.add_node("developer", developer)
    workflow.add_node("reviewer", reviewer)

    # 순환 구조
    workflow.add_edge(START, "architect")

    workflow.add_conditional_edges(
        "architect",
        route_next,
        {
            "developer": "developer",
            "reviewer": "reviewer",
            "end": END
        }
    )

    workflow.add_conditional_edges(
        "developer",
        route_next,
        {
            "developer": "developer",
            "reviewer": "reviewer",
            "end": END
        }
    )

    workflow.add_conditional_edges(
        "reviewer",
        route_next,
        {
            "developer": "developer",
            "reviewer": "reviewer",
            "end": END
        }
    )

    app = workflow.compile()

    # 실행
    print("="*60)
    print("Task: REST API 서버 개발")
    print("="*60)

    try:
        result = app.invoke({
            "task": "REST API 서버 개발",
            "messages": [],
            "current_agent": "",
            "iterations": 0,
            "completed": False
        })

        print("\n" + "="*60)
        print("✅ 협업 완료!")
        print(f"   총 {len(result['messages'])}번의 대화")
        print(f"   반복 횟수: {result['iterations']}")

    except Exception as e:
        print(f"\n❌ 오류: {e}")


if __name__ == "__main__":
    main()
    print("\n💡 핵심: 에이전트들이 서로 대화하며 작업을 완성")
    print("📚 다음: step4.py - Tool Sharing\n")
