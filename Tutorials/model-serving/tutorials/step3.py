"""
Model Serving Step 3: 모델 비교 및 선택

다양한 로컬 모델 비교
"""

from langchain_community.llms import Ollama
import time


def benchmark_model(model_name, question):
    """모델 벤치마크"""
    print(f"\n{model_name}:")

    try:
        llm = Ollama(model=model_name)

        start = time.time()
        response = llm.invoke(question)
        elapsed = time.time() - start

        print(f"  응답 시간: {elapsed:.2f}초")
        print(f"  응답: {response[:100]}...")

        return elapsed, len(response)

    except Exception as e:
        print(f"  ❌ 오류: {e}")
        print(f"     ollama pull {model_name}")
        return None, None


def compare_models():
    """여러 모델 비교"""
    print("=== 모델 성능 비교 ===\n")

    question = "Python과 JavaScript의 차이를 3줄로 설명해줘"
    print(f"질문: {question}\n")

    models = [
        "llama3:8b",      # 8B 파라미터
        "mistral:7b",     # 7B 파라미터
        "gemma:7b",       # Google 7B
    ]

    results = {}

    for model in models:
        elapsed, length = benchmark_model(model, question)
        if elapsed:
            results[model] = {"time": elapsed, "length": length}

    print("\n" + "=" * 60)
    print("\n결과 요약:")
    print("\n모델           | 시간   | 응답 길이")
    print("-" * 40)

    for model, data in results.items():
        print(f"{model:15} | {data['time']:.2f}초 | {data['length']:4}자")

    print()


def model_recommendations():
    """모델 추천"""
    print("=== 모델 선택 가이드 ===\n")

    recommendations = [
        ("llama3:8b", "범용", "가장 균형잡힌 성능", "⭐⭐⭐⭐⭐"),
        ("mistral:7b", "코딩", "코드 생성에 강함", "⭐⭐⭐⭐"),
        ("gemma:7b", "가벼움", "빠른 응답", "⭐⭐⭐"),
        ("phi3:mini", "초경량", "3.8B, CPU도 가능", "⭐⭐"),
    ]

    print("모델          | 용도   | 특징                | 추천도")
    print("-" * 65)

    for model, use, feature, rating in recommendations:
        print(f"{model:13} | {use:6} | {feature:18} | {rating}")

    print("\n💡 권장 조합:")
    print("  - 개발/테스트: llama3:8b")
    print("  - 프로덕션: llama3:70b (GPU 필요)")
    print("  - 경량화: phi3:mini (CPU 가능)")
    print()


def hardware_requirements():
    """하드웨어 요구사항"""
    print("=== 하드웨어 요구사항 ===\n")

    specs = [
        ("7B 모델", "16GB RAM", "CPU", "느림"),
        ("7B 모델", "8GB VRAM", "GPU", "빠름 ✅"),
        ("13B 모델", "16GB VRAM", "GPU", "빠름"),
        ("70B 모델", "40GB VRAM x2", "GPU", "매우 빠름"),
    ]

    print("모델 크기    | 메모리    | 장치 | 속도")
    print("-" * 50)

    for model, memory, device, speed in specs:
        print(f"{model:12} | {memory:9} | {device:4} | {speed}")

    print("\n✅ RTX 3090 (24GB) 권장")
    print()


if __name__ == "__main__":
    print("🚀 로컬 모델 비교 및 선택\n")
    print("=" * 60)

    compare_models()
    print("-" * 60)
    model_recommendations()
    print("-" * 60)
    hardware_requirements()

    print("=" * 60)
    print("\n✅ 모델 선택 가이드 완료!")
    print("\n📚 요약:")
    print("  - 범용: llama3:8b")
    print("  - 코딩: mistral:7b")
    print("  - 경량: phi3:mini")
    print()
