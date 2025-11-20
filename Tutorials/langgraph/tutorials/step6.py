"""
Step 6: 실용적인 에이전트
Tool을 사용하는 ReAct 패턴 에이전트를 구축합니다.
"""

import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated, Literal

# .env 파일에서 환경변수 로드
load_dotenv()
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode


# ===== Tool 정의 =====

@tool
def calculate(expression: str) -> str:
    """
    수학 계산을 수행합니다.
    expression: 계산할 수식 (예: "2 + 3", "10 * 5")
    """
    try:
        # 안전한 계산을 위해 eval 대신 제한적 평가 사용
        result = eval(expression, {"__builtins__": {}}, {})
        return f"계산 결과: {result}"
    except Exception as e:
        return f"계산 오류: {str(e)}"


@tool
def get_weather(city: str) -> str:
    """
    특정 도시의 날씨 정보를 조회합니다.
    city: 도시 이름
    """
    # 실제로는 API 호출하지만, 여기서는 시뮬레이션
    weather_data = {
        "서울": "맑음, 15도",
        "부산": "흐림, 18도",
        "제주": "비, 20도",
        "seoul": "맑음, 15도",
        "busan": "흐림, 18도"
    }

    weather = weather_data.get(city.lower(), "정보 없음")
    return f"{city}의 날씨: {weather}"


@tool
def search_web(query: str) -> str:
    """
    웹에서 정보를 검색합니다.
    query: 검색 쿼리
    """
    # 실제로는 검색 API를 사용하지만, 여기서는 시뮬레이션
    mock_results = {
        "python": "Python은 1991년 Guido van Rossum이 만든 고급 프로그래밍 언어입니다.",
        "langgraph": "LangGraph는 LangChain의 그래프 기반 워크플로우 라이브러리입니다.",
        "ai": "인공지능(AI)은 기계가 인간의 지능을 모방하도록 하는 기술입니다."
    }

    for keyword, result in mock_results.items():
        if keyword in query.lower():
            return f"검색 결과: {result}"

    return f"'{query}'에 대한 검색 결과를 찾을 수 없습니다."


def simple_tool_agent_example():
    """
    간단한 Tool 사용 에이전트
    """

    class State(TypedDict):
        messages: Annotated[list, add_messages]

    # Tool 목록
    tools = [calculate, get_weather, search_web]

    # Tool을 사용할 수 있는 LLM 생성
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))
    llm_with_tools = llm.bind_tools(tools)

    # Tool 실행 노드 (LangGraph 내장)
    tool_node = ToolNode(tools)

    # LLM 호출 노드
    def call_llm(state: State) -> State:
        response = llm_with_tools.invoke(state["messages"])
        return {"messages": [response]}

    # 다음 단계 결정
    def should_continue(state: State) -> Literal["tools", "end"]:
        last_message = state["messages"][-1]

        print("OK?", last_message)
        # LLM이 tool을 호출하려고 하면
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        else:            
            return "end"

    # 그래프 구성
    workflow = StateGraph(State)

    workflow.add_node("agent", call_llm)
    workflow.add_node("tools", tool_node)

    workflow.add_edge(START, "agent")

    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END
        }
    )

    # Tool 실행 후 다시 agent로
    workflow.add_edge("tools", "agent")

    app = workflow.compile()

    # 테스트
    questions = [
        "25 곱하기 4는 얼마인가요?",
        "서울 날씨 알려줘",
        "langfuse는 뭐지 "
    ]

    for question in questions:
        print(f"\n{'='*60}")
        print(f"질문: {question}")
        print(f"{'='*60}\n")

        result = app.invoke({
            "messages": [HumanMessage(content=question)]
        })

        # 최종 답변 출력
        for msg in result["messages"]:
            if isinstance(msg, AIMessage) and not msg.tool_calls:
                print(f"답변: {msg.content}\n")

    return result


def react_agent_example():
    """
    ReAct 패턴 에이전트
    Reasoning (추론) + Acting (행동)을 반복
    """

    class State(TypedDict):
        messages: Annotated[list, add_messages]
        iterations: int

    tools = [calculate, get_weather, search_web]

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))
    llm_with_tools = llm.bind_tools(tools)

    tool_node = ToolNode(tools)

    # Agent 노드 - ReAct 패턴
    def agent(state: State) -> State:
        print(f"\n[반복 {state['iterations'] + 1}] Agent 사고 중...")

        # System 메시지로 ReAct 패턴 강제
        system_msg = SystemMessage(content="""
당신은 단계별로 사고하는 에이전트입니다.
각 단계마다:
1. 현재 상황을 분석하고
2. 필요한 도구를 사용하거나
3. 최종 답변을 제공하세요.

사용 가능한 도구:
- calculate: 수학 계산
- get_weather: 날씨 조회
- search_web: 웹 검색
""")

        messages = [system_msg] + state["messages"]
        response = llm_with_tools.invoke(messages)

        return {
            "messages": [response],
            "iterations": state["iterations"] + 1
        }

    # 계속할지 결정
    def should_continue(state: State) -> Literal["tools", "end", "max_iterations"]:
        # 최대 반복 제한
        if state["iterations"] >= 10:
            print("[경고] 최대 반복 횟수 도달")
            return "max_iterations"

        last_message = state["messages"][-1]

        # Tool 호출이 있으면
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            print(f"→ Tool 실행: {[tc['name'] for tc in last_message.tool_calls]}")
            return "tools"
        else:
            print("→ 최종 답변 생성")
            return "end"

    # 그래프 구성
    workflow = StateGraph(State)

    workflow.add_node("agent", agent)
    workflow.add_node("tools", tool_node)

    workflow.add_edge(START, "agent")

    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END,
            "max_iterations": END
        }
    )

    workflow.add_edge("tools", "agent")  # Tool 실행 후 다시 사고

    app = workflow.compile()

    # 복잡한 질문 테스트
    complex_question = """
서울의 날씨를 확인하고, 온도가 15도라면 섭씨를 화씨로 변환해주세요.
그리고 Python에 대해 간단히 설명해주세요.
"""

    print("="*60)
    print("복잡한 질문:")
    print(complex_question)
    print("="*60)

    result = app.invoke({
        "messages": [HumanMessage(content=complex_question)],
        "iterations": 0
    })

    print("\n" + "="*60)
    print("최종 답변:")
    print("="*60)

    # 최종 답변 찾기
    for msg in reversed(result["messages"]):
        if isinstance(msg, AIMessage) and not msg.tool_calls:
            print(msg.content)
            break

    print(f"\n총 반복 횟수: {result['iterations']}")

    return result


def streaming_agent_example():
    """
    스트리밍으로 Agent 실행 과정 보기
    """

    class State(TypedDict):
        messages: Annotated[list, add_messages]

    tools = [calculate]

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))
    llm_with_tools = llm.bind_tools(tools)
    tool_node = ToolNode(tools)

    def agent(state: State) -> State:
        response = llm_with_tools.invoke(state["messages"])
        return {"messages": [response]}

    def should_continue(state: State) -> Literal["tools", "end"]:
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return "end"

    workflow = StateGraph(State)
    workflow.add_node("agent", agent)
    workflow.add_node("tools", tool_node)
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", "end": END})
    workflow.add_edge("tools", "agent")

    app = workflow.compile()

    # 스트리밍 실행
    print("="*60)
    print("스트리밍으로 Agent 실행 과정 관찰")
    print("="*60 + "\n")

    question = "123 곱하기 456을 계산하고, 그 결과에 100을 더해주세요."

    print(f"질문: {question}\n")

    for step in app.stream(
        {"messages": [HumanMessage(content=question)]},
        stream_mode="updates"
    ):
        for node_name, node_output in step.items():
            print(f"[{node_name}]")

            if "messages" in node_output:
                for msg in node_output["messages"]:
                    if isinstance(msg, AIMessage):
                        if msg.tool_calls:
                            print(f"  Tool 호출: {msg.tool_calls}")
                        elif msg.content:
                            print(f"  응답: {msg.content}")
                    elif isinstance(msg, ToolMessage):
                        print(f"  Tool 결과: {msg.content}")

            print()

    return None


def error_handling_agent_example():
    """
    에러 처리가 있는 견고한 에이전트
    """

    class State(TypedDict):
        messages: Annotated[list, add_messages]
        error_count: int

    @tool
    def unreliable_tool(input: str) -> str:
        """가끔 실패하는 도구 (테스트용)"""
        import random
        if random.random() < 0.3:  # 30% 확률로 실패
            raise Exception("도구 실행 실패!")
        return f"처리 완료: {input}"

    tools = [calculate, unreliable_tool]

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))
    llm_with_tools = llm.bind_tools(tools)

    def agent(state: State) -> State:
        response = llm_with_tools.invoke(state["messages"])
        return {"messages": [response]}

    def call_tools(state: State) -> State:
        """에러 처리가 있는 Tool 실행"""
        last_message = state["messages"][-1]
        tool_results = []

        for tool_call in last_message.tool_calls:
            try:
                # Tool 찾기
                tool_map = {t.name: t for t in tools}
                selected_tool = tool_map[tool_call["name"]]

                # Tool 실행
                result = selected_tool.invoke(tool_call["args"])

                tool_results.append(
                    ToolMessage(
                        content=str(result),
                        tool_call_id=tool_call["id"]
                    )
                )
            except Exception as e:
                print(f"⚠ Tool 실행 오류: {e}")
                # 에러를 LLM에게 알림
                tool_results.append(
                    ToolMessage(
                        content=f"오류 발생: {str(e)}",
                        tool_call_id=tool_call["id"]
                    )
                )
                return {
                    "messages": tool_results,
                    "error_count": state["error_count"] + 1
                }

        return {"messages": tool_results}

    def should_continue(state: State) -> Literal["tools", "end", "too_many_errors"]:
        # 에러가 너무 많으면 중단
        if state["error_count"] >= 3:
            return "too_many_errors"

        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return "end"

    workflow = StateGraph(State)
    workflow.add_node("agent", agent)
    workflow.add_node("tools", call_tools)

    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END,
            "too_many_errors": END
        }
    )
    workflow.add_edge("tools", "agent")

    app = workflow.compile()

    print("="*60)
    print("에러 처리 Agent")
    print("="*60 + "\n")

    result = app.invoke({
        "messages": [HumanMessage(content="10 + 20을 계산해주세요")],
        "error_count": 0
    })

    print(f"\n에러 횟수: {result['error_count']}")

    return result


if __name__ == "__main__":
    print("=" * 60)
    print("Step 6: 실용적인 에이전트")
    print("=" * 60)
    print()

    # 예제 1: 간단한 Tool Agent
    print("예제 1: 간단한 Tool 사용 에이전트")
    print("-" * 60)
    simple_tool_agent_example()
    print()

    # # 예제 2: ReAct Agent
    # print("\n예제 2: ReAct 패턴 에이전트")
    # print("-" * 60)
    # react_agent_example()
    # print()

    # # 예제 3: 스트리밍 Agent
    # print("\n예제 3: 스트리밍 Agent")
    # print("-" * 60)
    # streaming_agent_example()
    # print()

    # # 예제 4: 에러 처리
    # print("\n예제 4: 에러 처리 Agent")
    # print("-" * 60)
    # error_handling_agent_example()
