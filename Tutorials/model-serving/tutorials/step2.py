"""
Model Serving Step 2: Ollama API 서버 활용

실행 중: ollama serve
"""

import requests
from langchain_community.llms import Ollama


def example1_rest_api():
    """예제 1: REST API로 직접 호출"""
    print("=== Ollama REST API ===\n")

    url = "http://localhost:11434/api/generate"

    data = {
        "model": "llama3",
        "prompt": "LangGraph를 한 문장으로 설명해줘",
        "stream": False
    }

    print("요청 중...")
    response = requests.post(url, json=data)

    if response.status_code == 200:
        result = response.json()
        print(f"응답: {result['response']}\n")
    else:
        print(f"❌ 오류: {response.status_code}")
        print("   ollama serve 실행 확인\n")


def example2_chat_api():
    """예제 2: Chat API (대화형)"""
    print("=== Chat API ===\n")

    url = "http://localhost:11434/api/chat"

    messages = [
        {"role": "user", "content": "안녕! 너는 누구야?"},
    ]

    data = {
        "model": "llama3",
        "messages": messages,
        "stream": False
    }

    response = requests.post(url, json=data)

    if response.status_code == 200:
        result = response.json()
        print(f"응답: {result['message']['content']}\n")


def example3_streaming():
    """예제 3: 스트리밍 응답"""
    print("=== 스트리밍 (실시간 출력) ===\n")

    llm = Ollama(model="llama3")

    question = "Ollama의 장점 3가지를 알려줘"
    print(f"질문: {question}\n")
    print("응답: ", end="", flush=True)

    for chunk in llm.stream(question):
        print(chunk, end="", flush=True)

    print("\n")


def example4_model_management():
    """예제 4: 모델 관리"""
    print("=== 모델 관리 ===\n")

    # 설치된 모델 목록
    response = requests.get("http://localhost:11434/api/tags")

    if response.status_code == 200:
        models = response.json()
        print("설치된 모델:")
        for model in models.get('models', []):
            name = model['name']
            size = model['size'] / (1024**3)  # GB로 변환
            print(f"  - {name} ({size:.1f} GB)")

    print("\n새 모델 다운로드:")
    print("  ollama pull mistral")
    print("  ollama pull gemma:7b")
    print()


if __name__ == "__main__":
    print("🚀 Ollama API 서버 활용\n")
    print("=" * 60)

    try:
        example1_rest_api()
        print("-" * 60)
        example2_chat_api()
        print("-" * 60)
        example3_streaming()
        print("-" * 60)
        example4_model_management()

        print("=" * 60)
        print("\n✅ Ollama API 이해 완료!")
        print("\n💡 REST API로 어떤 언어에서든 사용 가능")
        print("📚 다음: step3.py - 여러 모델 비교\n")

    except Exception as e:
        print(f"❌ 오류: {e}")
        print("\nOllama 서버 실행 확인:")
        print("  ollama serve")
        print("  ollama pull llama3\n")
