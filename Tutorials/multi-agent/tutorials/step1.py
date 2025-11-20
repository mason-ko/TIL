"""
Multi-Agent Step 1: 순차 실행

pip install langgraph langchain-community
"""

from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from langchain_community.llms import Ollama


class State(TypedDict):
    topic: str
    research: str
    summary: str


def researcher(state: State) -> State:
    """에이전트 1: 리서치"""
    llm = Ollama(model="llama3")
    research = llm.invoke(f"{state['topic']}에 대해 3줄로 설명해줘")
    return {"research": research}


def summarizer(state: State) -> State:
    """에이전트 2: 요약"""
    llm = Ollama(model="llama3")
    summary = llm.invoke(f"다음을 한 문장으로 요약: {state['research']}")
    return {"summary": summary}


def main():
    print("=== 멀티 에이전트: 순차 실행 ===\n")

    workflow = StateGraph(State)
    workflow.add_node("researcher", researcher)
    workflow.add_node("summarizer", summarizer)

    workflow.add_edge(START, "researcher")
    workflow.add_edge("researcher", "summarizer")
    workflow.add_edge("summarizer", END)

    app = workflow.compile()

    result = app.invoke({"topic": "Vector Database"})

    print(f"주제: {result['topic']}")
    print(f"\n리서치:\n{result['research']}")
    print(f"\n요약:\n{result['summary']}\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ 오류: {e}")
        print("Ollama 실행 확인: ollama pull llama3")
