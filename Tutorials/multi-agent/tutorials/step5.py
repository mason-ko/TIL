"""
Multi-Agent Step 5: State Management (상태 관리)

pip install langgraph
"""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import TypedDict
from typing import Annotated
import operator


class ProjectState(TypedDict):
    """프로젝트 상태"""
    project_name: str
    tasks: Annotated[list, operator.add]  # 추가 방식
    completed_tasks: Annotated[list, operator.add]
    current_agent: str  # 덮어쓰기 방식
    logs: Annotated[list, operator.add]
    iteration: int


def planner(state: ProjectState) -> ProjectState:
    """Planner: 작업 계획"""
    print("\n[Planner] 작업 계획 수립 중...")

    project = state['project_name']

    # 작업 생성
    tasks = [
        f"{project} - 요구사항 분석",
        f"{project} - 설계",
        f"{project} - 구현"
    ]

    print(f"   생성된 작업: {len(tasks)}개")

    return {
        "tasks": tasks,
        "current_agent": "planner",
        "logs": ["[Planner] 작업 계획 완료"],
        "iteration": state.get('iteration', 0) + 1
    }


def executor(state: ProjectState) -> ProjectState:
    """Executor: 작업 실행"""
    print("\n[Executor] 작업 실행 중...")

    tasks = state.get('tasks', [])
    completed = state.get('completed_tasks', [])

    # 미완료 작업 찾기
    remaining = [t for t in tasks if t not in completed]

    if remaining:
        # 첫 번째 작업 실행
        task = remaining[0]
        print(f"   실행: {task}")

        return {
            "completed_tasks": [task],
            "current_agent": "executor",
            "logs": [f"[Executor] 완료: {task}"],
            "iteration": state.get('iteration', 0)
        }

    return {
        "current_agent": "executor",
        "logs": ["[Executor] 모든 작업 완료"],
        "iteration": state.get('iteration', 0)
    }


def reporter(state: ProjectState) -> ProjectState:
    """Reporter: 보고서 작성"""
    print("\n[Reporter] 보고서 작성 중...")

    completed = state.get('completed_tasks', [])
    tasks = state.get('tasks', [])

    progress = len(completed) / len(tasks) * 100 if tasks else 0

    report = f"""
    프로젝트: {state['project_name']}
    전체 작업: {len(tasks)}
    완료 작업: {len(completed)}
    진행률: {progress:.1f}%
    """

    print(report)

    return {
        "current_agent": "reporter",
        "logs": ["[Reporter] 보고서 작성 완료"],
        "iteration": state.get('iteration', 0)
    }


def check_completion(state: ProjectState) -> str:
    """작업 완료 여부 확인"""
    tasks = state.get('tasks', [])
    completed = state.get('completed_tasks', [])

    if len(completed) >= len(tasks):
        return "reporter"

    return "executor"


def main():
    print("=== State Management ===\n")
    print("복잡한 상태를 체계적으로 관리합니다\n")

    # 체크포인터 (상태 저장)
    checkpointer = MemorySaver()

    # 그래프 구성
    workflow = StateGraph(ProjectState)

    workflow.add_node("planner", planner)
    workflow.add_node("executor", executor)
    workflow.add_node("reporter", reporter)

    # 흐름
    workflow.add_edge(START, "planner")
    workflow.add_edge("planner", "executor")

    # 조건부: 완료 여부에 따라
    workflow.add_conditional_edges(
        "executor",
        check_completion,
        {
            "executor": "executor",  # 루프
            "reporter": "reporter"   # 완료
        }
    )

    workflow.add_edge("reporter", END)

    # 컴파일 (체크포인터 포함)
    app = workflow.compile(checkpointer=checkpointer)

    # 실행
    print("="*60)
    print("Project: 웹 애플리케이션 개발")
    print("="*60)

    # 세션 ID
    config = {"configurable": {"thread_id": "project-001"}}

    result = app.invoke({
        "project_name": "웹 애플리케이션 개발",
        "tasks": [],
        "completed_tasks": [],
        "current_agent": "",
        "logs": [],
        "iteration": 0
    }, config=config)

    print("\n" + "="*60)
    print("✅ 프로젝트 완료!")
    print("="*60)

    print(f"\n📊 최종 상태:")
    print(f"   전체 작업: {len(result['tasks'])}")
    print(f"   완료 작업: {len(result['completed_tasks'])}")
    print(f"   반복 횟수: {result['iteration']}")

    print(f"\n📝 로그:")
    for log in result['logs']:
        print(f"   {log}")

    print("\n💡 State Management 핵심:")
    print("   1. Annotated[list, operator.add] - 리스트 추가")
    print("   2. 일반 필드 - 덮어쓰기")
    print("   3. Checkpointer - 상태 영속성")


if __name__ == "__main__":
    main()
    print("\n📚 다음: step6.py - 실전 프로젝트\n")
