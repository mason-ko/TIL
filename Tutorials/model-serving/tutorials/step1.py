"""
Model Serving Step 1: Ollama 기본

실행 전:
1. Ollama 설치: https://ollama.com/
2. 모델 다운로드: ollama pull llama3
3. pip install langchain-community
"""

from langchain_community.llms import Ollama


def example1_basic():
    """기본 사용"""
    print("=== Ollama 기본 사용 ===\n")

    llm = Ollama(model="llama3")
    response = llm.invoke("LangGraph를 한 문장으로 설명해줘")

    print(f"응답: {response}\n")


def example2_streaming():
    """스트리밍 (ChatGPT처럼)"""
    print("=== 스트리밍 ===\n")

    llm = Ollama(model="llama3")

    print("응답: ", end="", flush=True)
    for chunk in llm.stream("Ollama의 장점 3가지만 알려줘"):
        print(chunk, end="", flush=True)

    print("\n")


if __name__ == "__main__":
    try:
        example1_basic()
        example2_streaming()
        print("✅ 로컬 LLM 실행 성공! 비용: $0")
    except Exception as e:
        print(f"❌ 오류: {e}")
        print("Ollama가 설치되어 있고 실행 중인지 확인하세요")
        print("  ollama pull llama3")
