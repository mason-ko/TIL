"""
Step 4: State 관리
복잡한 State 구조와 Reducer 함수를 사용하는 방법을 배웁니다.
"""

import os
from dotenv import load_dotenv
import operator

# .env 파일에서 환경변수 로드
load_dotenv()
from typing import TypedDict, Annotated, List, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver


def custom_reducer_example():
    """
    커스텀 Reducer 함수 사용하기
    상태 업데이트 방식을 커스터마이징할 수 있습니다.
    """

    # Reducer 함수들
    def append_to_list(existing: List[str], new: List[str]) -> List[str]:
        """리스트에 항목 추가"""
        return existing + new

    def add_numbers(existing: int, new: int) -> int:
        """숫자 더하기"""
        return existing + new

    def merge_dicts(existing: Dict, new: Dict) -> Dict:
        """딕셔너리 병합"""
        return {**existing, **new}

    # State 정의 - Annotated로 Reducer 지정
    class State(TypedDict):
        # 기본 동작: 덮어쓰기
        current_step: str

        # 리스트 누적
        steps_taken: Annotated[List[str], append_to_list]

        # 숫자 누적
        total_count: Annotated[int, add_numbers]

        # 딕셔너리 병합
        metadata: Annotated[Dict, merge_dicts]

    # 노드 함수들
    def step_1(state: State) -> State:
        print("Step 1 실행")
        return {
            "current_step": "step_1",
            "steps_taken": ["step_1 완료"],
            "total_count": 1,
            "metadata": {"step_1_time": "10ms"}
        }

    def step_2(state: State) -> State:
        print("Step 2 실행")
        return {
            "current_step": "step_2",
            "steps_taken": ["step_2 완료"],
            "total_count": 1,
            "metadata": {"step_2_time": "15ms"}
        }

    def step_3(state: State) -> State:
        print("Step 3 실행")
        return {
            "current_step": "step_3",
            "steps_taken": ["step_3 완료"],
            "total_count": 1,
            "metadata": {"step_3_time": "20ms"}
        }

    # 그래프 구성
    workflow = StateGraph(State)

    workflow.add_node("s1", step_1)
    workflow.add_node("s2", step_2)
    workflow.add_node("s3", step_3)

    workflow.add_edge(START, "s1")

    workflow.add_edge("s1", "s2")
    workflow.add_edge("s2", "s3")
    workflow.add_edge("s3", END)

    app = workflow.compile()

    # 실행
    result = app.invoke({
        "current_step": "시작",
        "steps_taken": [],
        "total_count": 0,
        "metadata": {}
    })

    print("\n=== 최종 결과 ===")
    print(f"현재 단계: {result['current_step']}")  # 덮어쓰기 됨
    print(f"거쳐온 단계들: {result['steps_taken']}")  # 누적됨
    print(f"총 카운트: {result['total_count']}")  # 더해짐
    print(f"메타데이터: {result['metadata']}")  # 병합됨

    return result


def operator_reducer_example():
    """
    operator 모듈을 사용한 Reducer
    Python의 표준 operator를 Reducer로 사용할 수 있습니다.
    """

    class State(TypedDict):
        # operator.add는 + 연산자 (숫자 더하기, 리스트 합치기 등)
        score: Annotated[int, operator.add]
        items: Annotated[list, operator.add]

        # 일반 필드 (덮어쓰기)
        last_action: str

    def action_1(state: State) -> State:
        print("액션 1: 점수 +10, 아이템 획득")
        return {
            "score": 10,
            "items": ["sword"],
            "last_action": "액션1 완료"
        }

    def action_2(state: State) -> State:
        print("액션 2: 점수 +20, 아이템 획득")
        return {
            "score": 20,
            "items": ["shield"],
            "last_action": "액션2 완료"
        }

    workflow = StateGraph(State)
    workflow.add_node("a1", action_1)
    workflow.add_node("a2", action_2)
    workflow.add_edge(START, "a1")
    workflow.add_edge("a1", "a2")
    workflow.add_edge("a2", END)

    app = workflow.compile()

    result = app.invoke({
        "score": 0,
        "items": [],
        "last_action": "시작"
    })

    print("\n=== 게임 결과 ===")
    print(f"최종 점수: {result['score']}")  # 0 + 10 + 20 = 30
    print(f"획득 아이템: {result['items']}")  # [] + ["sword"] + ["shield"]
    print(f"마지막 액션: {result['last_action']}")

    return result


def message_state_deep_dive():
    """
    메시지 기반 State 심화
    add_messages Reducer의 동작 방식을 자세히 살펴봅니다.
    """

    class State(TypedDict):
        messages: Annotated[list, add_messages]
        summary: str

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))

    def chatbot(state: State) -> State:
        # 메시지 이력으로 LLM 호출
        response = llm.invoke(state["messages"])
        # AIMessage 하나만 반환해도 자동으로 리스트에 추가됨
        return {"messages": [response]}

    def summarizer(state: State) -> State:
        # 전체 대화를 요약
        all_messages = "\n".join([
            f"{msg.__class__.__name__}: {msg.content}"
            for msg in state["messages"]
        ])
        summary_response = llm.invoke([
            HumanMessage(content=f"다음 대화를 한 문장으로 요약해주세요:\n{all_messages}")
        ])
        return {"summary": summary_response.content}

    workflow = StateGraph(State)
    workflow.add_node("chat", chatbot)
    workflow.add_node("summarize", summarizer)

    workflow.add_edge(START, "chat")
    workflow.add_edge("chat", "summarize")
    workflow.add_edge("summarize", END)

    app = workflow.compile()

    # 첫 번째 대화
    print("=== 대화 1 ===")
    result = app.invoke({
        "messages": [HumanMessage(content="안녕하세요! 저는 서울에서 살아요.")],
        "summary": ""
    })

    print(f"사용자: 안녕하세요! 저는 서울에서 살아요.")
    print(f"AI: {result['messages'][-1].content[:100]}...")
    print(f"요약: {result['summary']}\n")

    # 이전 대화 이어서
    print("=== 대화 2 ===")
    result = app.invoke({
        "messages": result["messages"] + [
            HumanMessage(content="제가 사는곳의 날씨를 알려주세요.")
        ],
        "summary": ""
    })

    print(f"사용자: 사는곳의 날씨를 알려주세요.")
    print(f"AI: {result['messages'][-1].content[:100]}...")
    print(f"요약: {result['summary']}\n")

    print(f"총 메시지 수: {len(result['messages'])}")

    return result


def checkpoint_example():
    """
    체크포인트를 사용한 상태 영속성
    그래프 실행 중간 상태를 저장하고 복원할 수 있습니다.
    """

    class State(TypedDict):
        messages: Annotated[list, add_messages]

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))

    def chatbot(state: State) -> State:
        response = llm.invoke(state["messages"])
        return {"messages": [response]}

    # 메모리 기반 체크포인터 생성
    memory = MemorySaver()

    workflow = StateGraph(State)
    workflow.add_node("chat", chatbot)
    workflow.add_edge(START, "chat")
    workflow.add_edge("chat", END)

    # 체크포인터와 함께 컴파일
    app = workflow.compile(checkpointer=memory)

    # 설정: 대화 세션을 구분하기 위한 ID
    config = {"configurable": {"thread_id": "conversation_1"}}

    # 첫 번째 대화
    print("=== 대화 1 (thread_id: conversation_1) ===")
    result1 = app.invoke(
        {"messages": [HumanMessage(content="제 이름은 김철수입니다.")]},
        config
    )
    print(f"사용자: 제 이름은 김철수입니다.")
    print(f"AI: {result1['messages'][-1].content}\n")

    # 두 번째 대화 (같은 thread_id) - 자동으로 이전 대화 이어짐
    print("=== 대화 2 (같은 thread_id) ===")
    result2 = app.invoke(
        {"messages": [HumanMessage(content="제 이름이 뭐라고 했죠?")]},
        config
    )
    print(f"사용자: 제 이름이 뭐라고 했죠?")
    print(f"AI: {result2['messages'][-1].content}\n")

    # 다른 thread_id로 새로운 대화
    config2 = {"configurable": {"thread_id": "conversation_2"}}
    print("=== 대화 3 (다른 thread_id: conversation_2) ===")
    result3 = app.invoke(
        {"messages": [HumanMessage(content="제 이름이 뭐죠?")]},
        config2
    )
    print(f"사용자: 제 이름이 뭐죠?")
    print(f"AI: {result3['messages'][-1].content}\n")

    print("체크포인트 덕분에:")
    print("- conversation_1에서는 이름을 기억")
    print("- conversation_2에서는 이름을 모름 (새로운 세션)")

    return result2


def complex_state_example():
    """
    복잡한 State 구조 예제
    실제 애플리케이션에서 사용할 수 있는 State 설계 패턴
    """

    class UserInfo(TypedDict):
        name: str
        preferences: Dict[str, str]

    class State(TypedDict):
        # 사용자 정보 (덮어쓰기)
        user: UserInfo

        # 대화 메시지 (누적)
        messages: Annotated[List[BaseMessage], add_messages]

        # 실행 로그 (누적)
        logs: Annotated[List[str], operator.add]

        # 실행 횟수 (더하기)
        execution_count: Annotated[int, operator.add]

        # 에러 목록 (누적)
        errors: Annotated[List[str], operator.add]

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))

    def process_user_query(state: State) -> State:
        user_name = state["user"]["name"]
        preferences = state["user"]["preferences"]

        # 사용자 정보를 활용한 개인화된 프롬프트
        system_msg = f"사용자 {user_name}님은 {preferences}를 선호합니다. 이를 고려하여 답변하세요."

        messages = [HumanMessage(content=system_msg)] + state["messages"]

        try:
            response = llm.invoke(messages)
            return {
                "messages": [response],
                "logs": [f"LLM 호출 성공: {len(response.content)} 글자 응답"],
                "execution_count": 1,
                "errors": []
            }
        except Exception as e:
            return {
                "messages": [],
                "logs": [f"LLM 호출 실패"],
                "execution_count": 1,
                "errors": [str(e)]
            }

    workflow = StateGraph(State)
    workflow.add_node("process", process_user_query)
    workflow.add_edge(START, "process")
    workflow.add_edge("process", END)

    app = workflow.compile()

    # 실행
    result = app.invoke({
        "user": {
            "name": "김철수",
            "preferences": {"language": "Python", "style": "간결한 설명"}
        },
        "messages": [HumanMessage(content="리스트 컴프리헨션을 설명해주세요.")],
        "logs": [],
        "execution_count": 0,
        "errors": []
    })

    print("=== 실행 결과 ===")
    print(f"사용자: {result['user']['name']}")
    print(f"선호도: {result['user']['preferences']}")
    print(f"AI 응답: {result['messages'][-1].content[:100]}...")
    print(f"실행 로그: {result['logs']}")
    print(f"실행 횟수: {result['execution_count']}")
    print(f"에러: {result['errors'] if result['errors'] else '없음'}")

    return result


if __name__ == "__main__":
    print("=" * 60)
    print("Step 4: State 관리")
    print("=" * 60)
    print()

    # # 예제 1: 커스텀 Reducer
    # print("예제 1: 커스텀 Reducer 함수")
    # print("-" * 60)
    # custom_reducer_example()
    # print("\n")

    # # 예제 2: operator Reducer
    # print("예제 2: operator 모듈 사용")
    # print("-" * 60)
    # operator_reducer_example()
    # print("\n")
    #
    # # 예제 3: 메시지 State 심화
    # print("예제 3: 메시지 State 심화")
    # print("-" * 60)
    # message_state_deep_dive()
    # print("\n")
    #
    # # 예제 4: 체크포인트
    # print("예제 4: 체크포인트 (상태 영속성)")
    # print("-" * 60)
    # checkpoint_example()
    # print("\n")
    #
    # 예제 5: 복잡한 State
    print("예제 5: 복잡한 State 구조")
    print("-" * 60)
    complex_state_example()
