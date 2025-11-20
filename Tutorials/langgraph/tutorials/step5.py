"""
Step 5: 조건부 엣지와 라우팅
조건에 따라 다른 경로로 분기하는 방법을 배웁니다.
"""

import os
from dotenv import load_dotenv
import random

# .env 파일에서 환경변수 로드
load_dotenv()
from typing import TypedDict, Annotated, Literal
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages


def simple_conditional_example():
    """
    가장 단순한 조건부 분기
    숫자가 짝수인지 홀수인지에 따라 다른 노드로 이동
    """

    class State(TypedDict):
        number: int
        result: str

    # 노드들
    def check_number(state: State) -> State:
        print(f"숫자 확인: {state['number']}")
        return state

    def even_handler(state: State) -> State:
        print(f"{state['number']}는 짝수입니다!")
        return {"result": "짝수"}

    def odd_handler(state: State) -> State:
        print(f"{state['number']}는 홀수입니다!")
        return {"result": "홀수"}

    # 라우팅 함수 - 다음에 갈 노드를 결정
    def route_based_on_number(state: State) -> Literal["even", "odd"]:
        """
        조건에 따라 다음 노드를 선택합니다.
        반환값: 노드 이름 (문자열)
        """
        if state["number"] % 2 == 0:
            return "even"
        else:
            return "odd"

    # 그래프 구성
    workflow = StateGraph(State)

    workflow.add_node("check", check_number)
    workflow.add_node("even", even_handler)
    workflow.add_node("odd", odd_handler)

    # 일반 엣지
    workflow.add_edge(START, "check")

    # 조건부 엣지: check 노드 이후 조건에 따라 분기
    workflow.add_conditional_edges(
        "check",  # 시작 노드
        route_based_on_number,  # 라우팅 함수
        {
            "even": "even",  # 라우팅 함수가 "even"을 반환하면 "even" 노드로
            "odd": "odd"     # 라우팅 함수가 "odd"를 반환하면 "odd" 노드로
        }
    )

    # 두 경로 모두 END로
    workflow.add_edge("even", END)
    workflow.add_edge("odd", END)

    app = workflow.compile()

    # 테스트
    print("=== 테스트 1: 짝수 ===")
    result1 = app.invoke({"number": 10})
    print(f"결과: {result1['result']}\n")

    print("=== 테스트 2: 홀수 ===")
    result2 = app.invoke({"number": 7})
    print(f"결과: {result2['result']}\n")

    return result1, result2


def loop_example():
    """
    루프 (사이클) 예제
    조건이 만족될 때까지 반복 실행
    """

    class State(TypedDict):
        count: int
        max_count: int
        history: Annotated[list, lambda x, y: x + y]

    def increment(state: State) -> State:
        new_count = state["count"] + 1
        print(f"카운트: {state['count']} -> {new_count}")
        return {
            "count": new_count,
            "history": [f"Step {new_count}"]
        }

    def should_continue(state: State) -> Literal["continue", "end"]:
        """계속할지 종료할지 결정"""
        if state["count"] < state["max_count"]:
            return "continue"
        else:
            return "end"

    workflow = StateGraph(State)

    workflow.add_node("increment", increment)

    workflow.add_edge(START, "increment")

    # 조건부 엣지: 루프 생성
    workflow.add_conditional_edges(
        "increment",
        should_continue,
        {
            "continue": "increment",  # 자기 자신으로 다시 (루프!)
            "end": END
        }
    )

    app = workflow.compile()

    # 실행
    result = app.invoke({
        "count": 0,
        "max_count": 5,
        "history": []
    })

    print(f"\n최종 카운트: {result['count']}")
    print(f"실행 이력: {result['history']}")

    return result


def llm_decision_example():
    """
    LLM이 의사결정을 하는 예제
    사용자 질문의 유형에 따라 다른 처리
    """

    class State(TypedDict):
        messages: Annotated[list, add_messages]
        question_type: str
        answer: str

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))

    # 질문 분류
    def classify_question(state: State) -> State:
        user_question = state["messages"][-1].content

        classification_prompt = f"""
다음 질문을 분류해주세요. 정확히 하나의 카테고리만 선택하세요:
- "code": 코드 작성 또는 코드 예제 요청
- "explanation": 개념 설명 요청
- "debug": 디버깅 또는 에러 해결

질문: {user_question}

답변은 반드시 "code", "explanation", "debug" 중 하나만 반환하세요.
"""

        response = llm.invoke([HumanMessage(content=classification_prompt)])
        question_type = response.content.strip().lower()

        # 안전장치: 유효한 값이 아니면 기본값
        if question_type not in ["code", "explanation", "debug"]:
            question_type = "explanation"

        print(f"질문 분류: {question_type}")
        return {"question_type": question_type}

    # 각 유형별 처리
    def handle_code_request(state: State) -> State:
        print("코드 생성 전문가 모드")
        response = llm.invoke([
            HumanMessage(content=f"코드 예제와 함께 설명해주세요: {state['messages'][-1].content}")
        ])
        return {"messages": [response], "answer": response.content}

    def handle_explanation_request(state: State) -> State:
        print("개념 설명 전문가 모드")
        response = llm.invoke([
            HumanMessage(content=f"초보자도 이해할 수 있게 쉽게 설명해주세요: {state['messages'][-1].content}")
        ])
        return {"messages": [response], "answer": response.content}

    def handle_debug_request(state: State) -> State:
        print("디버깅 전문가 모드")
        response = llm.invoke([
            HumanMessage(content=f"문제를 진단하고 해결 방법을 알려주세요: {state['messages'][-1].content}")
        ])
        return {"messages": [response], "answer": response.content}

    # 라우팅 함수
    def route_by_question_type(state: State) -> Literal["code", "explanation", "debug"]:
        return state["question_type"]

    # 그래프 구성
    workflow = StateGraph(State)

    workflow.add_node("classify", classify_question)
    workflow.add_node("code", handle_code_request)
    workflow.add_node("explanation", handle_explanation_request)
    workflow.add_node("debug", handle_debug_request)

    workflow.add_edge(START, "classify")

    workflow.add_conditional_edges(
        "classify",
        route_by_question_type,
        {
            "code": "code",
            "explanation": "explanation",
            "debug": "debug"
        }
    )

    workflow.add_edge("code", END)
    workflow.add_edge("explanation", END)
    workflow.add_edge("debug", END)

    app = workflow.compile()

    # 테스트
    test_questions = [
        "Python에서 리스트를 역순으로 만드는 코드를 보여주세요",
        "데코레이터가 뭔가요?",
        "제 코드에서 'list index out of range' 에러가 나요"
    ]

    results = []
    for question in test_questions:
        print(f"\n{'='*60}")
        print(f"질문: {question}")
        print(f"{'='*60}")

        result = app.invoke({
            "messages": [HumanMessage(content=question)],
            "question_type": "",
            "answer": ""
        })

        print(f"\n답변 (요약): {result['answer'][:150]}...\n")
        results.append(result)

    return results


def multi_path_example():
    """
    여러 경로가 있는 복잡한 워크플로우
    """

    class State(TypedDict):
        task: str
        priority: str
        assigned_to: str
        status: str
        logs: Annotated[list, lambda x, y: x + y]

    def analyze_task(state: State) -> State:
        # 간단한 우선순위 분석 (실제로는 LLM 사용 가능)
        task_lower = state["task"].lower()

        if "긴급" in task_lower or "urgent" in task_lower:
            priority = "high"
        elif "나중에" in task_lower or "later" in task_lower:
            priority = "low"
        else:
            priority = "medium"

        print(f"작업 분석 완료: {state['task']} -> 우선순위: {priority}")
        return {
            "priority": priority,
            "logs": [f"우선순위 분석: {priority}"]
        }

    def high_priority_handler(state: State) -> State:
        print("고우선순위 작업 - 즉시 처리")
        return {
            "assigned_to": "시니어 개발자",
            "status": "진행중",
            "logs": ["시니어 개발자에게 할당됨"]
        }

    def medium_priority_handler(state: State) -> State:
        print("중간우선순위 작업 - 대기열에 추가")
        return {
            "assigned_to": "팀",
            "status": "대기중",
            "logs": ["팀 대기열에 추가됨"]
        }

    def low_priority_handler(state: State) -> State:
        print("낮은우선순위 작업 - 백로그에 추가")
        return {
            "assigned_to": "백로그",
            "status": "백로그",
            "logs": ["백로그에 추가됨"]
        }

    def route_by_priority(state: State) -> Literal["high", "medium", "low"]:
        return state["priority"]

    workflow = StateGraph(State)

    workflow.add_node("analyze", analyze_task)
    workflow.add_node("high", high_priority_handler)
    workflow.add_node("medium", medium_priority_handler)
    workflow.add_node("low", low_priority_handler)

    workflow.add_edge(START, "analyze")

    workflow.add_conditional_edges(
        "analyze",
        route_by_priority,
        {
            "high": "high",
            "medium": "medium",
            "low": "low"
        }
    )

    workflow.add_edge("high", END)
    workflow.add_edge("medium", END)
    workflow.add_edge("low", END)

    app = workflow.compile()

    # 테스트
    tasks = [
        "긴급: 프로덕션 서버 다운",
        "신규 기능 개발",
        "나중에 처리: 문서 업데이트"
    ]

    for task in tasks:
        print(f"\n{'='*60}")
        result = app.invoke({
            "task": task,
            "priority": "",
            "assigned_to": "",
            "status": "",
            "logs": []
        })
        print(f"작업: {task}")
        print(f"할당: {result['assigned_to']}")
        print(f"상태: {result['status']}")
        print(f"로그: {result['logs']}")

    return result


def max_iterations_example():
    """
    최대 반복 횟수 제한이 있는 루프
    무한 루프 방지
    """

    class State(TypedDict):
        goal: str
        attempts: int
        max_attempts: int
        success: bool
        history: Annotated[list, lambda x, y: x + y]

    def attempt_task(state: State) -> State:
        attempts = state["attempts"] + 1
        # 랜덤하게 성공/실패 시뮬레이션
        success = random.random() > 0.6  # 40% 성공 확률

        print(f"시도 {attempts}/{state['max_attempts']}: {'성공' if success else '실패'}")

        return {
            "attempts": attempts,
            "success": success,
            "history": [f"시도 {attempts}: {'성공' if success else '실패'}"]
        }

    def should_retry(state: State) -> Literal["retry", "success", "failed"]:
        """재시도 여부 결정"""
        if state["success"]:
            return "success"
        elif state["attempts"] >= state["max_attempts"]:
            return "failed"
        else:
            return "retry"

    def handle_success(state: State) -> State:
        print("✓ 작업 성공!")
        return state

    def handle_failure(state: State) -> State:
        print("✗ 최대 시도 횟수 초과")
        return state

    workflow = StateGraph(State)

    workflow.add_node("attempt", attempt_task)
    workflow.add_node("success_handler", handle_success)
    workflow.add_node("failure_handler", handle_failure)

    workflow.add_edge(START, "attempt")

    workflow.add_conditional_edges(
        "attempt",
        should_retry,
        {
            "retry": "attempt",  # 재시도 (루프)
            "success": "success_handler",
            "failed": "failure_handler"
        }
    )

    workflow.add_edge("success_handler", END)
    workflow.add_edge("failure_handler", END)

    app = workflow.compile()

    # 실행
    result = app.invoke({
        "goal": "API 호출 성공",
        "attempts": 0,
        "max_attempts": 5,
        "success": False,
        "history": []
    })

    print(f"\n최종 결과:")
    print(f"성공 여부: {result['success']}")
    print(f"시도 횟수: {result['attempts']}")
    print(f"이력: {result['history']}")

    return result


if __name__ == "__main__":
    print("=" * 60)
    print("Step 5: 조건부 엣지와 라우팅")
    print("=" * 60)
    print()

    # 예제 1: 단순 조건 분기
    # print("예제 1: 단순 조건부 분기")
    # print("-" * 60)
    # simple_conditional_example()
    # print()

    # 예제 2: 루프
    # print("예제 2: 루프 (반복)")
    # print("-" * 60)
    # loop_example()
    # print("\n")

    # # 예제 3: LLM 의사결정
    # print("예제 3: LLM 기반 의사결정")
    # print("-" * 60)
    # llm_decision_example()
    # print()

    # # 예제 4: 다중 경로
    # print("예제 4: 다중 경로 워크플로우")
    # print("-" * 60)
    # multi_path_example()
    # print("\n")

    # # 예제 5: 최대 반복 제한
    print("예제 5: 최대 반복 횟수 제한")
    print("-" * 60)
    max_iterations_example()
