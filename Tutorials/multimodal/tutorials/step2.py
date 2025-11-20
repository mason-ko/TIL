"""
Multimodal Step 2: Audio - Whisper로 음성 인식

pip install openai-whisper

주의: Whisper는 큰 모델이므로 다운로드 시간이 걸립니다
"""

import os


def whisper_basic_example():
    """Whisper 기본 사용법"""
    print("=== Whisper 음성 인식 ===\n")

    print("설치:")
    print("  pip install openai-whisper")
    print("  pip install ffmpeg-python")
    print()

    print("사용법:")
    code = '''import whisper

# 모델 로드 (최초 1회 다운로드)
model = whisper.load_model("base")  # tiny, base, small, medium, large

# 음성 파일 → 텍스트
result = model.transcribe("audio.mp3", language="ko")

print(result["text"])
'''
    print(code)
    print()


def whisper_models():
    """Whisper 모델 비교"""
    print("=== Whisper 모델 ===\n")

    models = [
        ("tiny", "39M", "빠름", "낮음", "1GB RAM"),
        ("base", "74M", "빠름", "중간", "1GB RAM"),
        ("small", "244M", "중간", "좋음", "2GB RAM"),
        ("medium", "769M", "느림", "우수", "5GB RAM"),
        ("large", "1550M", "매우 느림", "최고", "10GB RAM"),
    ]

    print("모델    | 크기  | 속도      | 품질 | 메모리")
    print("-" * 55)

    for name, size, speed, quality, memory in models:
        print(f"{name:7} | {size:5} | {speed:9} | {quality:4} | {memory}")

    print("\n💡 권장: base (한국어도 잘 인식)")
    print()


def use_cases():
    """실무 활용 사례"""
    print("=== 실무 활용 ===\n")

    cases = [
        "회의 녹음 → 텍스트 변환 → 요약",
        "유튜브 영상 → 자막 생성",
        "음성 명령 → 텍스트 → LLM 처리",
        "팟캐스트 → 텍스트 → 검색 가능",
    ]

    for i, case in enumerate(cases, 1):
        print(f"{i}. {case}")

    print()


def whisper_with_llm():
    """Whisper + LLM 조합"""
    print("=== Whisper + LLM ===\n")

    workflow = '''
1. 음성 녹음 (audio.mp3)
   ↓
2. Whisper로 텍스트 변환
   "오늘 회의에서 논의된 액션 아이템은..."
   ↓
3. LLM으로 요약
   "액션 아이템: 1) ... 2) ..."
'''

    print(workflow)

    code = '''# 예제 코드
import whisper
from langchain_community.llms import Ollama

# 1. 음성 → 텍스트
model = whisper.load_model("base")
result = model.transcribe("meeting.mp3", language="ko")
text = result["text"]

# 2. 텍스트 → 요약
llm = Ollama(model="llama3")
summary = llm.invoke(f"다음 회의록을 요약해줘:\\n{text}")

print(summary)
'''

    print("\n코드:")
    print(code)
    print()


if __name__ == "__main__":
    print("🎤 Whisper 음성 인식\n")
    print("=" * 60)

    whisper_basic_example()
    print("-" * 60)
    whisper_models()
    print("-" * 60)
    use_cases()
    print("-" * 60)
    whisper_with_llm()

    print("=" * 60)
    print("\n✅ Whisper 이해 완료!")
    print("\n💡 핵심:")
    print("  - Whisper = 음성 → 텍스트")
    print("  - LLM = 텍스트 처리")
    print("  - 조합 = 음성 기반 AI")
    print()
