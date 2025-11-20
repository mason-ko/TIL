"""
Fine-tuning Step 2: 데이터셋 준비

실제 fine-tuning은 GPU 필요
"""

import json


def create_sample_dataset():
    """샘플 데이터셋 생성"""
    print("=== 데이터셋 형식 ===\n")

    samples = [
        {
            "instruction": "FastAPI로 Hello World 엔드포인트 만들어줘",
            "input": "",
            "output": "@app.get('/')\\ndef hello():\\n    return {'message': 'Hello World'}"
        },
        {
            "instruction": "Python 리스트 컴프리헨션 설명해줘",
            "input": "",
            "output": "리스트 컴프리헨션은 간결하게 리스트를 생성하는 방법입니다. [x for x in range(10)]"
        },
        {
            "instruction": "다음 코드를 FastAPI로 변환해줘",
            "input": "def get_user(id): return users[id]",
            "output": "@app.get('/users/{id}')\\ndef get_user(id: int):\\n    return users[id]"
        },
    ]

    # JSON 파일로 저장
    with open("dataset.json", "w", encoding="utf-8") as f:
        json.dump(samples, f, ensure_ascii=False, indent=2)

    print("샘플 데이터:")
    for i, sample in enumerate(samples, 1):
        print(f"\n{i}. Instruction: {sample['instruction']}")
        if sample['input']:
            print(f"   Input: {sample['input']}")
        print(f"   Output: {sample['output'][:50]}...")

    print(f"\n✅ dataset.json 생성 ({len(samples)}개 샘플)")
    print()


def dataset_guidelines():
    """데이터셋 작성 가이드"""
    print("=== 데이터셋 작성 가이드 ===\n")

    guidelines = [
        ("양", "최소 1,000개, 권장 10,000개"),
        ("품질", "고품질 > 대량. 정확한 답변만"),
        ("다양성", "다양한 케이스 포함"),
        ("일관성", "스타일 통일 (코드, 톤앤매너)"),
        ("포맷", "JSON Lines (.jsonl) 권장"),
    ]

    for aspect, guide in guidelines:
        print(f"{aspect:10} | {guide}")

    print()


def quality_checklist():
    """품질 체크리스트"""
    print("=== 품질 체크리스트 ===\n")

    checklist = [
        "[ ] 모든 답변이 정확한가?",
        "[ ] 일관된 스타일인가?",
        "[ ] 너무 짧거나 길지 않은가?",
        "[ ] 다양한 케이스를 커버하는가?",
        "[ ] 중복된 샘플은 없는가?",
        "[ ] 편향(bias)은 없는가?",
    ]

    for item in checklist:
        print(f"  {item}")

    print()


def preparation_steps():
    """준비 단계"""
    print("=== Fine-tuning 준비 ===\n")

    steps = [
        "1. 목표 정의 (무엇을 잘하게 만들 것인가?)",
        "2. 데이터 수집 (최소 1,000개)",
        "3. 데이터 정제 (품질 검증)",
        "4. 포맷 변환 (.jsonl)",
        "5. Train/Val 분할 (90% / 10%)",
        "6. GPU 환경 준비 (RTX 3090 이상)",
    ]

    for step in steps:
        print(f"  {step}")

    print("\n다음 단계에서 실제 학습 진행")
    print()


if __name__ == "__main__":
    print("📝 Fine-tuning 데이터셋 준비\n")
    print("=" * 60)

    create_sample_dataset()
    print("-" * 60)
    dataset_guidelines()
    print("-" * 60)
    quality_checklist()
    print("-" * 60)
    preparation_steps()

    print("=" * 60)
    print("\n✅ 데이터셋 준비 완료!")
    print("\n📦 생성된 파일:")
    print("  - dataset.json (샘플)")
    print("\n💡 다음 단계:")
    print("  1. 데이터 1,000개 이상 수집")
    print("  2. GPU 환경 준비")
    print("  3. 실제 fine-tuning (step3)")
    print()
