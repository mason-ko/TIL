"""
Step 2: LangChain 기본 사용
LangChain을 사용하여 LLM 작업을 더 쉽고 구조적으로 수행하는 방법을 배웁니다.
"""

import sys
import io

# Windows 환경에서 UTF-8 출력을 위한 설정
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# .env 파일에서 환경변수 로드
load_dotenv()
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from pydantic import BaseModel, Field


def basic_langchain_call():
    """
    LangChain의 ChatGoogleGenerativeAI를 사용한 기본 호출
    Step 1의 Gemini 직접 호출과 비교해보세요.
    """
    # ChatGoogleGenerativeAI 모델 초기화
    # API 키는 환경변수에서 자동으로 읽어옵니다
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.7,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

    # 메시지 생성 - LangChain의 메시지 객체 사용
    messages = [
        SystemMessage(content="당신은 친절한 Python 튜터입니다."),
        HumanMessage(content="Python 리스트 컴프리헨션을 설명해주세요.")
    ]

    print("사용자: Python 리스트 컴프리헨션을 설명해주세요.\n")

    # LLM 호출 - invoke() 메서드 사용
    response = llm.invoke(messages)

    print(f"AI: {response.content}\n")

    # response는 AIMessage 객체입니다
    print(f"응답 타입: {type(response)}")
    print(f"메타데이터: {response.response_metadata}")

    return response


def prompt_template_example():
    """
    프롬프트 템플릿 사용하기
    재사용 가능한 프롬프트를 만들 수 있습니다.
    """
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))

    # 프롬프트 템플릿 정의
    prompt = ChatPromptTemplate.from_messages([
        ("system", "당신은 {subject} 전문가입니다. 초보자도 이해하기 쉽게 설명해주세요."),
        ("user", "{topic}에 대해 설명해주세요.")
    ])

    # 템플릿에 값을 채워서 실제 메시지 생성
    messages = prompt.invoke({
        "subject": "Python 프로그래밍",
        "topic": "데코레이터"
    }).to_messages()

    print("=== 생성된 프롬프트 ===")
    for msg in messages:
        print(f"{msg.__class__.__name__}: {msg.content}")
    print()

    # LLM 호출
    response = llm.invoke(messages)
    print(f"AI: {response.content}\n")

    return response


def chain_example():
    """
    체인(Chain) 사용하기
    여러 컴포넌트를 연결하여 파이프라인을 만듭니다.
    """
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))

    # 프롬프트 템플릿
    prompt = ChatPromptTemplate.from_messages([
        ("system", "당신은 {role}입니다."),
        ("user", "{input}")
    ])

    # 출력 파서 - 문자열로 변환
    output_parser = StrOutputParser()

    # 체인 구성: prompt -> llm -> output_parser
    # | 연산자로 컴포넌트들을 연결합니다 (LCEL: LangChain Expression Language)
    chain = prompt | llm | output_parser

    # 체인 실행
    print("=== 체인 실행 1 ===")
    result = chain.invoke({
        "role": "Python 전문가",
        "input": "람다 함수가 뭔가요?"
    })
    print(f"결과: {result}\n")

    # 같은 체인을 다른 입력으로 재사용
    print("=== 체인 실행 2 ===")
    result = chain.invoke({
        "role": "JavaScript 전문가",
        "input": "화살표 함수가 뭔가요?"
    })
    print(f"결과: {result}\n")

    return result


def json_output_example():
    """
    구조화된 출력 받기
    LLM의 응답을 JSON 형태로 파싱합니다.
    """

    # 출력 스키마 정의
    class ProgrammingConcept(BaseModel):
        name: str = Field(description="개념의 이름")
        difficulty: str = Field(description="난이도 (쉬움/보통/어려움)")
        description: str = Field(description="간단한 설명")
        example: str = Field(description="코드 예제")

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))

    # JSON 출력 파서
    parser = JsonOutputParser(pydantic_object=ProgrammingConcept)

    # 프롬프트에 파싱 지시사항 포함
    prompt = ChatPromptTemplate.from_messages([
        ("system", "당신은 프로그래밍 개념을 설명하는 전문가입니다."),
        ("user", "{concept}에 대해 설명해주세요.\n\n{format_instructions}")
    ])

    # 체인 구성
    chain = prompt | llm | parser

    # 실행
    result = chain.invoke({
        "concept": "Python 제너레이터",
        "format_instructions": parser.get_format_instructions()
    })

    print("=== 구조화된 출력 ===")
    print(f"이름: {result['name']}")
    print(f"난이도: {result['difficulty']}")
    print(f"설명: {result['description']}")
    print(f"예제:\n{result['example']}\n")

    return result


def streaming_chain_example():
    """
    체인에서 스트리밍 사용하기
    """
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))

    prompt = ChatPromptTemplate.from_messages([
        ("system", "당신은 코딩 튜터입니다."),
        ("user", "{question}")
    ])

    output_parser = StrOutputParser()

    chain = prompt | llm | output_parser

    print("질문: Python에서 비동기 프로그래밍의 장점을 설명해주세요.\n")
    print("AI: ", end="", flush=True)

    # stream() 메서드로 스트리밍 응답
    for chunk in chain.stream({"question": "Python에서 비동기 프로그래밍의 장점을 설명해주세요."}):
        print(chunk, end="", flush=True)

    print("\n")


def conversation_with_memory():
    """
    대화 이력을 템플릿에 포함하기
    """
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))

    # MessagesPlaceholder를 사용하여 대화 이력을 동적으로 삽입
    prompt = ChatPromptTemplate.from_messages([
        ("system", "당신은 친절한 AI 어시스턴트입니다."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}")
    ])

    chain = prompt | llm | StrOutputParser()

    # 대화 이력 관리
    chat_history = []

    # 첫 번째 대화
    print("사용자: 안녕하세요!\n")
    response = chain.invoke({
        "chat_history": chat_history,
        "input": "안녕하세요!"
    })
    print(f"AI: {response}\n")

    # 이력에 추가
    chat_history.append(HumanMessage(content="안녕하세요!"))
    chat_history.append(AIMessage(content=response))

    # 두 번째 대화 (이전 대화를 기억함)
    print("사용자: 방금 제가 뭐라고 인사했죠?\n")
    response = chain.invoke({
        "chat_history": chat_history,
        "input": "방금 제가 뭐라고 인사했죠?"
    })
    print(f"AI: {response}\n")


if __name__ == "__main__":
    print("=" * 60)
    print("Step 2: LangChain 기본 사용")
    print("=" * 60)
    print()

    # 예제 1: 기본 호출
    print("예제 1: LangChain 기본 호출")
    print("-" * 60)
    # basic_langchain_call()
    print()

    # 예제 2: 프롬프트 템플릿
    print("예제 2: 프롬프트 템플릿")
    print("-" * 60)
    # prompt_template_example()
    print()

    # 예제 3: 체인
    print("예제 3: 체인 사용")
    print("-" * 60)
    # chain_example()
    print()

    # 예제 4: JSON 출력
    print("예제 4: 구조화된 JSON 출력")
    print("-" * 60)
    # json_output_example()
    print()

    # 예제 5: 스트리밍 체인
    print("예제 5: 스트리밍 체인")
    print("-" * 60)
    # streaming_chain_example()
    print()

    # 예제 6: 대화 이력
    print("예제 6: 대화 이력 관리")
    print("-" * 60)
    conversation_with_memory()
