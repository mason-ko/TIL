"""
Step 1: 기본 LLM 호출
LangGraph를 배우기 전에 가장 기본적인 LLM API 호출을 이해합니다.
Google Gemini API를 직접 사용하는 방법을 배웁니다.
"""

import os
import sys
import google.generativeai as genai
from dotenv import load_dotenv

# Windows 콘솔 인코딩 설정 (이모지 등 유니코드 문자 지원)
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# .env 파일에서 환경변수 로드
load_dotenv()

def basic_llm_call():
    """
    가장 기본적인 LLM 호출 예제
    Gemini API를 사용하여 단순한 질문-응답을 수행합니다.
    """
    # Gemini API 설정
    # API 키는 환경변수 GOOGLE_API_KEY에서 자동으로 읽어옵니다
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    # 모델 초기화
    model = genai.GenerativeModel('gemini-2.5-flash')

    # 사용자 메시지
    user_message = "Python에서 리스트와 튜플의 차이점을 간단히 설명해주세요."

    print(f"사용자: {user_message}\n")

    # LLM에게 요청 보내기
    response = model.generate_content(
        user_message,
        generation_config=genai.types.GenerationConfig(
            temperature=0.7,  # 창의성 수준 (0.0 ~ 2.0)
            max_output_tokens=2000,  # 최대 응답 토큰 수
        )
    )

    # 응답 추출
    try:
        assistant_message = response.text
    except (ValueError, IndexError) as e:
        # 응답이 차단되었거나 비어있는 경우
        print(f"응답 생성 실패: {e}")
        print(f"응답 상태: {response}")
        if hasattr(response, 'prompt_feedback'):
            print(f"프롬프트 피드백: {response.prompt_feedback}")
        if hasattr(response, 'candidates') and response.candidates:
            print(f"후보 응답들: {response.candidates}")
        return None

    if not assistant_message:
        print("경고: 빈 응답을 받았습니다.")
        return None

    print(f"AI: {assistant_message}\n")

    # 토큰 사용량 출력 (사용 가능한 경우)
    if hasattr(response, 'usage_metadata') and response.usage_metadata:
        print(f"사용된 토큰: 입력={response.usage_metadata.prompt_token_count}, "
              f"출력={response.usage_metadata.candidates_token_count}, "
              f"총={response.usage_metadata.total_token_count}")
    else:
        print("토큰 사용량 정보를 사용할 수 없습니다.")

    return assistant_message


def conversation_example():
    """
    대화 이력을 유지하는 예제
    여러 메시지를 주고받으며 문맥을 유지합니다.
    """
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel('gemini-2.5-flash')

    # Gemini의 채팅 세션 시작
    chat = model.start_chat(history=[])

    print("=== 대화 시작 ===\n")

    # 첫 번째 메시지
    user_message_1 = "안녕하세요! Python을 배우고 싶어요."
    print(f"사용자: {user_message_1}\n")

    response_1 = chat.send_message(user_message_1)
    print(f"AI: {response_1.text}\n")

    # 두 번째 질문 (이전 대화를 기억함)
    user_message_2 = "그럼 먼저 변수에 대해 알려주세요."
    print(f"사용자: {user_message_2}\n")

    response_2 = chat.send_message(user_message_2)
    print(f"AI: {response_2.text}\n")

    return chat.history


def streaming_example():
    """
    스트리밍 응답 예제
    응답을 한 번에 받는 대신 실시간으로 받아옵니다.
    """
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel('gemini-2.5-flash')

    user_message = "Python의 장점 5가지를 설명해주세요."

    print(f"사용자: {user_message}\n")
    print("AI: ", end="", flush=True)

    # stream=True로 설정하면 실시간으로 응답을 받습니다
    response = model.generate_content(user_message, stream=True)

    # 스트림에서 청크를 하나씩 받아서 출력
    for chunk in response:
        if chunk.text:
            print(chunk.text, end="", flush=True)

    print("\n")


if __name__ == "__main__":
    print("=" * 60)
    print("Step 1: 기본 LLM 호출")
    print("=" * 60)
    print()


    # 예제 1: 기본 호출
    print("예제 1: 기본 LLM 호출")
    print("-" * 60)
    basic_llm_call()
    print()

    # 예제 2: 대화 이력 유지
    print("예제 2: 대화 이력 유지")
    print("-" * 60)
    conversation_example()
    print()

    # 예제 3: 스트리밍
    print("예제 3: 스트리밍 응답")
    print("-" * 60)
    streaming_example()
