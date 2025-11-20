"""
LangSmith Step 1: 기본 설정 및 트레이싱

실행 전 .env 파일 설정 필요:
- LANGCHAIN_TRACING_V2=true
- LANGCHAIN_API_KEY=your-key
- LANGCHAIN_PROJECT=langsmith-tutorial
- GOOGLE_API_KEY=your-key
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langsmith import traceable

load_dotenv()


def example1_basic_tracing():
    """
    예제 1: 기본 트레이싱

    LangSmith 환경 변수가 설정되어 있으면
    모든 LLM 호출이 자동으로 트레이싱됩니다.
    """
    print("=== 예제 1: 기본 트레이싱 ===\n")

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

    # 이 호출이 LangSmith에 자동 기록됨!
    response = llm.invoke("안녕하세요! LangSmith에 대해 한 문장으로 설명해주세요.")

    print(f"응답: {response.content}\n")
    print("✅ LangSmith UI에서 이 trace를 확인하세요!")
    print("   https://smith.langchain.com/\n")


def example2_chain_tracing():
    """
    예제 2: 체인 트레이싱

    프롬프트 + LLM 체인의 각 단계가
    트레이싱됩니다.
    """
    print("=== 예제 2: 체인 트레이싱 ===\n")

    # 프롬프트 템플릿
    prompt = ChatPromptTemplate.from_messages([
        ("system", "당신은 {role} 전문가입니다. 간단명료하게 답변하세요."),
        ("human", "{question}")
    ])

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

    # 체인 생성
    chain = prompt | llm

    # 체인 실행
    response = chain.invoke({
        "role": "Python",
        "question": "리스트 컴프리헨션이 뭔가요?"
    })

    print(f"응답: {response.content}\n")
    print("✅ LangSmith UI에서 체인의 각 단계를 확인하세요!")
    print("   - Prompt 렌더링")
    print("   - LLM 호출\n")


@traceable(
    name="번역기",
    metadata={"version": "1.0", "feature": "translation"}
)
def translate_text(text: str, target_lang: str) -> str:
    """
    커스텀 함수에 트레이싱 적용

    @traceable 데코레이터를 사용하면
    함수 이름, 메타데이터 등을 커스터마이징할 수 있습니다.
    """
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

    prompt = f"Translate the following text to {target_lang}: {text}"
    response = llm.invoke(prompt)

    return response.content


def example3_custom_tracing():
    """
    예제 3: 커스텀 트레이싱

    @traceable 데코레이터로 함수를 래핑하면
    커스텀 메타데이터를 추가할 수 있습니다.
    """
    print("=== 예제 3: 커스텀 트레이싱 ===\n")

    result = translate_text("Hello, world!", "Korean")
    print(f"번역 결과: {result}\n")

    print("✅ LangSmith UI에서 확인:")
    print("   - Run 이름: '번역기'")
    print("   - Metadata: version=1.0, feature=translation\n")


def example4_multiple_calls():
    """
    예제 4: 여러 호출 트레이싱

    여러 LLM 호출을 하면 각각 별도의 trace로 기록됩니다.
    """
    print("=== 예제 4: 여러 호출 트레이싱 ===\n")

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

    questions = [
        "Python이란?",
        "JavaScript란?",
        "Rust란?"
    ]

    for i, question in enumerate(questions, 1):
        print(f"{i}. {question}")
        response = llm.invoke(f"{question} 한 문장으로 설명해주세요.")
        print(f"   → {response.content}\n")

    print("✅ LangSmith UI에서 3개의 trace를 확인하세요!")
    print("   각 호출의 토큰 사용량과 지연시간을 비교해보세요.\n")


if __name__ == "__main__":
    # 환경 변수 확인
    if not os.getenv("LANGCHAIN_TRACING_V2"):
        print("❌ 환경 변수가 설정되지 않았습니다!")
        print("   .env 파일을 생성하고 다음 변수를 설정하세요:")
        print("   - LANGCHAIN_TRACING_V2=true")
        print("   - LANGCHAIN_API_KEY=your-key")
        print("   - LANGCHAIN_PROJECT=langsmith-tutorial")
        print("   - GOOGLE_API_KEY=your-key")
        exit(1)

    print("🚀 LangSmith Step 1: 기본 설정 및 트레이싱\n")
    print("=" * 50)
    print()

    # 모든 예제 실행
    example1_basic_tracing()
    print("-" * 50)
    print()

    example2_chain_tracing()
    print("-" * 50)
    print()

    example3_custom_tracing()
    print("-" * 50)
    print()

    example4_multiple_calls()
    print("=" * 50)
    print()

    print("✅ 모든 예제 완료!")
    print()
    print("📊 다음 단계:")
    print("   1. https://smith.langchain.com/ 접속")
    print("   2. 프로젝트 선택 (langsmith-tutorial)")
    print("   3. 방금 실행한 traces 확인")
    print("   4. 각 trace의 입력/출력/토큰/지연시간 확인")
    print()
    print("📚 다음 튜토리얼: step2.py - 프로덕션 모니터링")
