"""
Step 3: LangGraph 기본 구조
LangGraph를 사용하여 상태 기반 워크플로우를 만드는 방법을 배웁니다.
"""

import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated

# .env 파일에서 환경변수 로드
load_dotenv()
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages


def simple_graph_example():
    """
    가장 단순한 LangGraph 예제
    노드 3개를 순차적으로 실행합니다.
    """

    # 1. State 정의
    # 그래프 내에서 전달되는 상태(데이터)의 구조를 정의합니다
    class State(TypedDict):
        message: str
        count: int

    # 2. 노드 함수들 정의
    # 각 노드는 현재 상태를 받아서 새로운 상태를 반환합니다
    def node_1(state: State) -> State:
        print(f"노드 1 실행 - 현재 메시지: {state['message']}")
        return {
            "message": state["message"] + " -> 노드1",
            "count": state["count"] + 1
        }

    def node_2(state: State) -> State:
        print(f"노드 2 실행 - 현재 메시지: {state['message']}")
        return {
            "message": state["message"] + " -> 노드2",
            "count": state["count"] + 1
        }

    def node_3(state: State) -> State:
        print(f"노드 3 실행 - 현재 메시지: {state['message']}")
        return {
            "message": state["message"] + " -> 노드3",
            "count": state["count"] + 1
        }

    # 3. 그래프 생성
    workflow = StateGraph(State)

    # 4. 노드 추가
    workflow.add_node("step1", node_1)
    workflow.add_node("step2", node_2)
    workflow.add_node("step3", node_3)

    # 5. 엣지(연결) 추가
    # START -> step1 -> step2 -> step3 -> END
    workflow.add_edge(START, "step1")
    workflow.add_edge("step1", "step2")
    workflow.add_edge("step2", "step3")
    workflow.add_edge("step3", END)

    # 6. 그래프 컴파일
    app = workflow.compile()

    # 7. 실행
    initial_state = {
        "message": "시작",
        "count": 0
    }

    print("=== 그래프 실행 ===")
    result = app.invoke(initial_state)

    print(f"\n최종 결과: {result}")
    print(f"최종 메시지: {result['message']}")
    print(f"노드 실행 횟수: {result['count']}")

    return result


def llm_graph_example():
    """
    LLM을 사용하는 간단한 그래프
    사용자 질문 -> LLM 응답 -> 결과 포맷팅
    """

    # State 정의
    class State(TypedDict):
        question: str
        answer: str
        formatted_output: str

    # LLM 초기화
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))

    # 노드 1: LLM에게 질문
    def ask_llm(state: State) -> State:
        print(f"질문: {state['question']}")
        response = llm.invoke([("user", state["question"])])
        print(f"LLM 응답 받음")
        return {"answer": response.content}

    # 노드 2: 결과 포맷팅
    def format_answer(state: State) -> State:
        formatted = f"""
===== 질문 =====
{state['question']}

===== 답변 =====
{state['answer']}
"""
        print("결과 포맷팅 완료")
        return {"formatted_output": formatted}

    # 그래프 구성
    workflow = StateGraph(State)

    workflow.add_node("ask", ask_llm)
    workflow.add_node("format", format_answer)

    workflow.add_edge(START, "ask")
    workflow.add_edge("ask", "format")
    workflow.add_edge("format", END)

    app = workflow.compile()

    # 실행
    result = app.invoke({
        "question": "Python에서 리스트와 딕셔너리의 차이는?"
    })

    print(result["formatted_output"])

    return result


def message_graph_example():
    """
    메시지 기반 상태 관리
    LangGraph의 특별한 기능: add_messages를 사용한 메시지 누적
    """
    from langchain_core.messages import HumanMessage, AIMessage

    # Annotated를 사용하여 메시지를 자동으로 누적
    class State(TypedDict):
        messages: Annotated[list, add_messages]

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))

    # LLM 호출 노드
    def call_llm(state: State) -> State:
        print(f"현재 메시지 수: {len(state['messages'])}")
        response = llm.invoke(state["messages"])
        # add_messages 덕분에 자동으로 기존 메시지에 추가됩니다
        return {"messages": [response]}

    # 그래프 구성
    workflow = StateGraph(State)
    workflow.add_node("llm", call_llm)
    workflow.add_edge(START, "llm")
    workflow.add_edge("llm", END)

    app = workflow.compile()

    # 실행
    print("=== 대화 1 ===")
    result = app.invoke({
        "messages": [HumanMessage(content="안녕하세요! 저는 Python을 배우고 있어요.")]
    })

    print(f"사용자: 안녕하세요! 저는 Python을 배우고 있어요.")
    print(f"AI: {result['messages'][-1].content}\n")

    # 이전 대화를 이어서 계속
    print("=== 대화 2 ===")
    result = app.invoke({
        "messages": result["messages"] + [
            HumanMessage(content="제가 방금 뭐라고 했죠?")
        ]
    })

    print(f"사용자: 제가 방금 뭐라고 했죠?")
    print(f"AI: {result['messages'][-1].content}\n")

    return result


def parallel_processing_example():
    """
    병렬 처리 예제
    여러 노드를 동시에 실행합니다.
    """
    import time

    class State(TypedDict):
        input_text: str
        summary: str
        word_count: int
        sentiment: str

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))

    # 요약 노드
    def summarize(state: State) -> State:
        start = time.time()
        response = llm.invoke([
            ("user", f"다음 텍스트를 한 문장으로 요약해주세요: {state['input_text']}")
        ])
        elapsed = time.time() - start
        print(f"요약 완료 ({elapsed:.2f}초)")
        return {"summary": response.content}

    # 단어 수 세기 노드
    def count_words(state: State) -> State:
        start = time.time()
        time.sleep(0.5)  # 시뮬레이션
        count = len(state["input_text"].split())
        elapsed = time.time() - start
        print(f"단어 수 계산 완료 ({elapsed:.2f}초)")
        return {"word_count": count}

    # 감정 분석 노드
    def analyze_sentiment(state: State) -> State:
        start = time.time()
        response = llm.invoke([
            ("user", f"다음 텍스트의 감정을 '긍정', '부정', '중립' 중 하나로 분류해주세요: {state['input_text']}")
        ])
        elapsed = time.time() - start
        print(f"감정 분석 완료 ({elapsed:.2f}초)")
        return {"sentiment": response.content}

    # 결과 출력 노드
    def print_results(state: State) -> State:
        print("\n=== 분석 결과 ===")
        print(f"원문: {state['input_text']}")
        print(f"요약: {state['summary']}")
        print(f"단어 수: {state['word_count']}")
        print(f"감정: {state['sentiment']}")
        return state

    # 그래프 구성
    workflow = StateGraph(State)

    workflow.add_node("summarize", summarize)
    workflow.add_node("count", count_words)
    workflow.add_node("sentiment", analyze_sentiment)
    workflow.add_node("output", print_results)

    # START에서 3개 노드로 병렬 실행
    workflow.add_edge(START, "summarize")
    workflow.add_edge(START, "count")
    workflow.add_edge(START, "sentiment")

    # 3개 노드가 모두 완료되면 output으로
    workflow.add_edge("summarize", "output")
    workflow.add_edge("count", "output")
    workflow.add_edge("sentiment", "output")

    workflow.add_edge("output", END)

    app = workflow.compile()

    # 실행
    start_time = time.time()
    result = app.invoke({
        "input_text": "Python은 배우기 쉽고 강력한 프로그래밍 언어입니다. "
                      "데이터 과학, 웹 개발, 자동화 등 다양한 분야에서 사용됩니다."
    })
    total_time = time.time() - start_time

    print(f"\n총 실행 시간: {total_time:.2f}초")
    print("(병렬 처리 덕분에 순차 처리보다 빠릅니다!)")

    return result


if __name__ == "__main__":
    print("=" * 60)
    print("Step 3: LangGraph 기본 구조")
    print("=" * 60)
    print()

    # 예제 1: 간단한 그래프
    # print("예제 1: 가장 단순한 그래프")
    # print("-" * 60)
    # simple_graph_example()
    # print("\n")

    # # 예제 2: LLM 사용
    # print("예제 2: LLM을 사용하는 그래프")
    # print("-" * 60)
    # llm_graph_example()
    # print("\n")
    # #
    # # 예제 3: 메시지 기반 상태
    # print("예제 3: 메시지 누적 (add_messages)")
    # print("-" * 60)
    # message_graph_example()
    # print("\n")
    #
    # # 예제 4: 병렬 처리
    print("예제 4: 병렬 처리")
    print("-" * 60)
    parallel_processing_example()
