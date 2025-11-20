"""
Langfuse Step 1: 기본 설정 및 Ollama 연동

실행 전 필요사항:
1. Langfuse 서버 실행:
   docker compose up -d

2. Ollama 설치 및 모델 다운로드:
   ollama pull llama3

3. .env 파일 설정:
   LANGFUSE_PUBLIC_KEY=pk-lf-...
   LANGFUSE_SECRET_KEY=sk-lf-...
   LANGFUSE_HOST=http://localhost:3000
"""

import os
from dotenv import load_dotenv
from langfuse import Langfuse
from langfuse.callback import CallbackHandler
from langfuse.decorators import observe, langfuse_context
from langchain_community.llms import Ollama
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

load_dotenv()


def example1_basic_tracing():
    """
    예제 1: 기본 트레이싱

    Ollama + Langfuse의 가장 간단한 예제입니다.
    """
    print("=== 예제 1: 기본 트레이싱 (Ollama) ===\n")

    # Langfuse 초기화
    langfuse = Langfuse(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        host=os.getenv("LANGFUSE_HOST", "http://localhost:3000")
    )

    # Ollama 모델
    llm = Ollama(model="llama3")

    # 트레이싱 시작
    trace = langfuse.trace(name="basic-ollama-call")

    # LLM 호출
    question = "Langfuse를 한 문장으로 설명해주세요."
    print(f"질문: {question}")

    generation = trace.generation(
        name="ollama-generation",
        model="llama3",
        input=question
    )

    response = llm.invoke(question)

    generation.end(output=response)

    print(f"응답: {response}\n")
    print(f"✅ Langfuse UI에서 확인: {trace.get_trace_url()}\n")


def example2_langchain_integration():
    """
    예제 2: LangChain 통합

    LangChain의 CallbackHandler를 사용하여
    자동으로 트레이싱합니다.
    """
    print("=== 예제 2: LangChain 통합 ===\n")

    # Langfuse Callback Handler
    langfuse_handler = CallbackHandler(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        host=os.getenv("LANGFUSE_HOST")
    )

    # 프롬프트 템플릿
    prompt = PromptTemplate(
        input_variables=["topic"],
        template="다음 주제에 대해 3줄 이내로 설명해주세요: {topic}"
    )

    llm = Ollama(model="llama3")
    chain = LLMChain(llm=llm, prompt=prompt)

    # 체인 실행 (자동 트레이싱)
    topic = "Vector Database"
    print(f"주제: {topic}")

    response = chain.invoke(
        {"topic": topic},
        config={"callbacks": [langfuse_handler]}
    )

    print(f"응답: {response['text']}\n")
    print("✅ Langfuse UI에서 체인의 각 단계를 확인하세요!\n")


@observe()
def translate_text(text: str, target_lang: str) -> str:
    """
    예제 3에서 사용할 번역 함수

    @observe 데코레이터로 자동 트레이싱
    """
    llm = Ollama(model="llama3")

    # 현재 trace에 메타데이터 추가
    langfuse_context.update_current_trace(
        metadata={
            "source_text": text,
            "target_language": target_lang,
            "model": "llama3",
            "environment": "development"
        },
        tags=["translation", "ollama", "step1"]
    )

    prompt = f"Translate the following text to {target_lang}. Only provide the translation, no explanations: {text}"
    response = llm.invoke(prompt)

    return response


def example3_metadata():
    """
    예제 3: 메타데이터 추가

    @observe 데코레이터와 메타데이터를 활용하여
    더 상세한 정보를 기록합니다.
    """
    print("=== 예제 3: 메타데이터 추가 ===\n")

    text = "Hello, world!"
    target = "Korean"

    print(f"원문: {text}")
    print(f"목표 언어: {target}")

    result = translate_text(text, target)

    print(f"번역 결과: {result}\n")
    print("✅ Langfuse UI에서 메타데이터와 태그를 확인하세요!\n")


def example4_error_tracking():
    """
    예제 4: 에러 추적

    에러가 발생해도 Langfuse에 기록됩니다.
    """
    print("=== 예제 4: 에러 추적 ===\n")

    langfuse = Langfuse(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        host=os.getenv("LANGFUSE_HOST", "http://localhost:3000")
    )

    trace = langfuse.trace(name="error-example")

    try:
        # 존재하지 않는 모델 호출 (에러 발생)
        llm = Ollama(model="nonexistent-model")

        generation = trace.generation(
            name="will-fail",
            model="nonexistent-model",
            input="This will fail"
        )

        response = llm.invoke("This will fail")
        generation.end(output=response)

    except Exception as e:
        # 에러 정보 기록
        generation.end(
            output=None,
            metadata={"error": str(e), "error_type": type(e).__name__},
            level="ERROR"
        )

        print(f"❌ 의도적 에러 발생: {e}")
        print(f"✅ Langfuse에서 에러 추적 확인: {trace.get_trace_url()}\n")


def example5_multiple_generations():
    """
    예제 5: 여러 번의 LLM 호출

    하나의 trace 안에서 여러 번 LLM을 호출할 수 있습니다.
    """
    print("=== 예제 5: 여러 LLM 호출 ===\n")

    langfuse = Langfuse(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        host=os.getenv("LANGFUSE_HOST", "http://localhost:3000")
    )

    llm = Ollama(model="llama3")

    # 하나의 trace
    trace = langfuse.trace(name="multi-step-conversation")

    # 1단계: 주제 선정
    gen1 = trace.generation(name="step1-topic", model="llama3", input="AI 기술 하나만 말해줘")
    topic = llm.invoke("AI 기술 하나만 말해줘")
    gen1.end(output=topic)
    print(f"1단계 - 주제: {topic}")

    # 2단계: 설명 요청
    gen2 = trace.generation(name="step2-explain", model="llama3", input=f"{topic}에 대해 설명해줘")
    explanation = llm.invoke(f"{topic}에 대해 2줄로 설명해줘")
    gen2.end(output=explanation)
    print(f"2단계 - 설명: {explanation}")

    # 3단계: 활용 사례
    gen3 = trace.generation(name="step3-usecase", model="llama3", input=f"{topic}의 활용 사례는?")
    usecase = llm.invoke(f"{topic}의 활용 사례 하나만 알려줘")
    gen3.end(output=usecase)
    print(f"3단계 - 활용: {usecase}\n")

    print(f"✅ 3단계 대화가 하나의 trace로 기록됨: {trace.get_trace_url()}\n")


if __name__ == "__main__":
    # 환경 변수 확인
    required_env = ["LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_HOST"]
    missing = [env for env in required_env if not os.getenv(env)]

    if missing:
        print("❌ 환경 변수가 설정되지 않았습니다!")
        print(f"   누락: {', '.join(missing)}")
        print("\n.env 파일을 생성하고 다음 변수를 설정하세요:")
        print("   LANGFUSE_PUBLIC_KEY=pk-lf-...")
        print("   LANGFUSE_SECRET_KEY=sk-lf-...")
        print("   LANGFUSE_HOST=http://localhost:3000")
        print("\n그리고 Langfuse 서버를 실행하세요:")
        print("   docker compose up -d")
        exit(1)

    print("🚀 Langfuse Step 1: Ollama 연동 및 기본 트레이싱\n")
    print("=" * 60)
    print()

    # 예제 1: 기본 트레이싱
    try:
        example1_basic_tracing()
    except Exception as e:
        print(f"⚠️  예제 1 실패 (Ollama 실행 중인지 확인): {e}\n")

    print("-" * 60)
    print()

    # 예제 2: LangChain 통합
    try:
        example2_langchain_integration()
    except Exception as e:
        print(f"⚠️  예제 2 실패: {e}\n")

    print("-" * 60)
    print()

    # 예제 3: 메타데이터
    try:
        example3_metadata()
    except Exception as e:
        print(f"⚠️  예제 3 실패: {e}\n")

    print("-" * 60)
    print()

    # 예제 4: 에러 추적
    example4_error_tracking()

    print("-" * 60)
    print()

    # 예제 5: 여러 LLM 호출
    try:
        example5_multiple_generations()
    except Exception as e:
        print(f"⚠️  예제 5 실패: {e}\n")

    print("=" * 60)
    print()

    print("✅ 모든 예제 완료!")
    print()
    print("📊 다음 단계:")
    print("   1. http://localhost:3000 접속")
    print("   2. Traces 탭에서 모든 실행 기록 확인")
    print("   3. 각 trace를 클릭하여 상세 정보 확인")
    print("   4. 지연시간, 입력/출력, 메타데이터 분석")
    print()
    print("📚 다음 튜토리얼: step2.py - RAG 파이프라인 트레이싱")
