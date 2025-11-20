"""
Fine-tuning Step 1: LoRA 개념

이 파일은 개념 설명용입니다.
실제 fine-tuning은 GPU가 필요하며 step2에서 다룹니다.
"""


def explain_lora():
    """LoRA 개념 설명"""
    print("=== LoRA (Low-Rank Adaptation) ===\n")

    print("Full Fine-tuning:")
    print("  모델 크기: 7B 파라미터")
    print("  학습: 7B 전부")
    print("  메모리: ~28GB")
    print("  시간: 며칠\n")

    print("LoRA:")
    print("  모델 크기: 7B 파라미터")
    print("  학습: ~140M (2%)")
    print("  메모리: ~14GB")
    print("  시간: 몇 시간")
    print("  품질: 90% 유지\n")


def data_requirements():
    """데이터 요구사항"""
    print("=== 데이터 준비 ===\n")

    example = {
        "instruction": "다음 코드를 FastAPI로 변환해줘",
        "input": "def hello(): return 'hi'",
        "output": "@app.get('/') def hello(): return {'message': 'hi'}"
    }

    print("데이터 형식:")
    print(f"  {example}\n")

    print("필요한 양:")
    print("  최소: 1,000개")
    print("  권장: 10,000개")
    print("  고품질 > 양\n")


if __name__ == "__main__":
    explain_lora()
    print("-" * 60)
    data_requirements()

    print("=" * 60)
    print("\n✅ Fine-tuning 개념 이해 완료!")
    print("\n📚 다음: step2.py에서 실제 LoRA 학습")
    print("   (GPU 필요: RTX 3090 이상)\n")
