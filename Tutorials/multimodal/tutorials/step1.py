"""
Multimodal Step 1: Vision (이미지 이해)

pip install langchain-google-genai pillow

.env 파일:
GOOGLE_API_KEY=your-key
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import base64

load_dotenv()


def example1_describe_image():
    """예제 1: 이미지 설명"""
    print("=== 예제 1: 이미지 설명 ===\n")

    # 이 예제는 실제 이미지 파일이 필요합니다
    # 테스트용으로 간단한 구조만 보여줍니다

    llm = ChatGoogleGenerativeAI(
        model="gemini-pro-vision",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

    print("이미지를 분석하려면:")
    print("1. 이미지 파일 준비")
    print("2. base64로 인코딩")
    print("3. VLM에 전달\n")

    # 실제 사용 예:
    # with open("image.jpg", "rb") as f:
    #     image_data = base64.b64encode(f.read()).decode()
    #
    # response = llm.invoke([
    #     {"type": "text", "text": "이 이미지를 설명해줘"},
    #     {"type": "image_url", "image_url": f"data:image/jpeg;base64,{image_data}"}
    # ])

    print("✅ Vision 모델로 이미지 분석 가능\n")


def example2_ocr():
    """예제 2: OCR (텍스트 추출)"""
    print("=== 예제 2: OCR ===\n")

    print("VLM을 사용한 OCR:")
    print("- 이미지에서 텍스트 추출")
    print("- 손글씨도 인식 가능")
    print("- 테이블 구조 파악\n")

    # 실제 사용:
    # response = llm.invoke([
    #     {"type": "text", "text": "이 이미지의 텍스트를 추출해줘"},
    #     {"type": "image_url", "image_url": "..."}
    # ])

    print("✅ OCR 기능 이해 완료\n")


if __name__ == "__main__":
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY 환경 변수를 설정하세요")
        print("   .env 파일에 추가: GOOGLE_API_KEY=your-key")
        exit(1)

    example1_describe_image()
    print("-" * 60)
    example2_ocr()

    print("=" * 60)
    print("\n✅ Vision 기초 이해 완료!")
    print("\n📚 다음: step2.py - Audio (Whisper)\n")
