"""
Step 2: 문서 처리와 청킹
다양한 형식의 문서를 로드하고 효과적으로 청크로 나누는 방법을 배웁니다.
"""

import os
from dotenv import load_dotenv
from langchain_core.documents import Document

# .env 파일에서 환경변수 로드
load_dotenv()
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    CharacterTextSplitter,
    TokenTextSplitter,
    MarkdownHeaderTextSplitter
)
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS


def basic_chunking_example():
    """
    기본 청킹 전략
    긴 텍스트를 작은 조각으로 나누기
    """
    # 긴 텍스트 샘플
    long_text = """
    인공지능(AI)은 기계가 인간의 지능을 모방하도록 하는 기술입니다.
    AI의 역사는 1950년대로 거슬러 올라가며, 앨런 튜링의 튜링 테스트로 시작되었습니다.

    머신러닝은 AI의 하위 분야로, 데이터로부터 학습하는 알고리즘을 다룹니다.
    지도 학습, 비지도 학습, 강화 학습 등 다양한 학습 방법이 있습니다.

    딥러닝은 인공신경망을 사용하는 머신러닝의 한 분야입니다.
    여러 층의 뉴런으로 구성되어 복잡한 패턴을 학습할 수 있습니다.
    이미지 인식, 자연어 처리, 음성 인식 등에서 뛰어난 성능을 보입니다.

    자연어처리(NLP)는 컴퓨터가 인간의 언어를 이해하고 생성하는 기술입니다.
    최근에는 트랜스포머 아키텍처와 대규모 언어 모델이 주목받고 있습니다.
    ChatGPT, GPT-4 등이 대표적인 예시입니다.
    """

    print("=== 원본 텍스트 ===")
    print(f"길이: {len(long_text)} 문자\n")
    print(long_text[:200] + "...\n")

    # 1. Character-based 분할
    print("=== 1. Character-based 분할 ===")
    text_splitter = CharacterTextSplitter(
        separator="\n\n",  # 단락 단위로 분할
        chunk_size=200,     # 최대 200자
        chunk_overlap=20,   # 20자 중복
        length_function=len
    )

    chunks = text_splitter.split_text(long_text)
    print(f"생성된 청크 수: {len(chunks)}\n")

    for i, chunk in enumerate(chunks):
        print(f"청크 {i+1} (길이: {len(chunk)}):")
        print(f"  {chunk[:100]}...\n")

    return chunks


def recursive_splitter_example():
    """
    Recursive Character Text Splitter
    가장 많이 사용되는 청킹 방법
    """
    text = """
    # LangChain 소개

    LangChain은 LLM 애플리케이션 개발을 위한 프레임워크입니다.

    ## 주요 기능

    1. 체인: 여러 컴포넌트를 연결
    2. 에이전트: 동적 의사결정
    3. 메모리: 대화 이력 관리

    ## 사용 예시

    ```python
    from langchain import LLMChain
    chain = LLMChain(llm=llm, prompt=prompt)
    result = chain.run("질문")
    ```

    이처럼 간단하게 LLM 파이프라인을 구성할 수 있습니다.
    """

    print("=== Recursive Character Text Splitter ===\n")

    # Recursive Splitter는 여러 구분자를 순서대로 시도
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=20,
        separators=[
            "\n\n",  # 먼저 단락으로 나누기 시도
            "\n",    # 그 다음 줄바꿈
            " ",     # 그 다음 공백
            ""       # 마지막으로 문자 단위
        ]
    )

    chunks = splitter.split_text(text)

    print(f"총 청크 수: {len(chunks)}\n")

    for i, chunk in enumerate(chunks):
        print(f"=== 청크 {i+1} ===")
        print(chunk)
        print(f"(길이: {len(chunk)})\n")

    return chunks


def token_based_splitter_example():
    """
    토큰 기반 청킹
    LLM의 토큰 제한을 고려한 분할
    """
    text = """
    LangGraph는 LangChain의 확장으로, 복잡한 에이전트 워크플로우를
    그래프로 표현할 수 있게 해줍니다. 노드는 작업 단위를, 엣지는
    노드 간 연결을 나타냅니다. 조건부 엣지를 사용하면 동적 라우팅이
    가능하고, 루프를 만들어 반복 작업을 수행할 수 있습니다.

    State는 그래프 내에서 데이터를 전달하는 핵심 요소입니다.
    TypedDict로 정의하며, Reducer를 사용하여 상태 업데이트 방식을
    커스터마이징할 수 있습니다. 체크포인터를 활용하면 상태를
    영속적으로 저장하여 대화 세션을 유지할 수 있습니다.
    """

    print("=== Token-based Splitter ===\n")

    # 토큰 기반 분할 (OpenAI의 토큰 계산 방식 사용)
    splitter = TokenTextSplitter(
        chunk_size=50,  # 50 토큰
        chunk_overlap=10
    )

    chunks = splitter.split_text(text)

    print(f"총 청크 수: {len(chunks)}\n")

    for i, chunk in enumerate(chunks):
        # 대략적인 토큰 수 (정확하지 않음)
        approx_tokens = len(chunk.split())
        print(f"청크 {i+1} (약 {approx_tokens} 단어):")
        print(f"  {chunk}\n")

    return chunks


def markdown_splitter_example():
    """
    Markdown 구조 기반 청킹
    헤더를 기준으로 분할
    """
    markdown_text = """
# 프로젝트 문서

## 1. 개요
이 프로젝트는 AI 기반 챗봇을 개발합니다.
주요 목표는 고객 지원 자동화입니다.

## 2. 기술 스택

### 2.1 백엔드
- Python 3.11
- FastAPI
- PostgreSQL

### 2.2 AI/ML
- LangChain
- OpenAI GPT-4
- FAISS

## 3. 아키텍처

### 3.1 시스템 구조
마이크로서비스 아키텍처를 채택합니다.
각 서비스는 독립적으로 배포 가능합니다.

### 3.2 데이터 흐름
사용자 → API Gateway → 챗봇 서비스 → LLM
"""

    print("=== Markdown Header Splitter ===\n")

    # 헤더 레벨별로 분할
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]

    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on
    )

    chunks = markdown_splitter.split_text(markdown_text)

    print(f"총 청크 수: {len(chunks)}\n")

    for i, chunk in enumerate(chunks):
        print(f"=== 청크 {i+1} ===")
        print(f"메타데이터: {chunk.metadata}")
        print(f"내용: {chunk.page_content[:100]}...")
        print()

    return chunks


def semantic_chunking_example():
    """
    의미 기반 청킹
    의미적으로 연관된 내용끼리 그룹화
    """
    paragraphs = [
        "인공지능은 기계가 인간의 지능을 모방하는 기술입니다.",
        "머신러닝은 데이터로부터 학습하는 AI의 한 분야입니다.",
        "오늘 날씨는 맑고 화창합니다.",
        "딥러닝은 인공신경망을 사용하는 머신러닝 기법입니다.",
        "저녁 메뉴로 피자를 주문했습니다.",
        "자연어처리는 컴퓨터가 인간의 언어를 이해하는 기술입니다."
    ]

    print("=== 의미 기반 청킹 ===\n")

    # 임베딩으로 의미적 유사도 계산
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=os.getenv("GOOGLE_API_KEY"))

    # 각 문단을 임베딩
    print("문단별 의미 분석...")
    embedded_paras = embeddings.embed_documents(paragraphs)

    # 간단한 휴리스틱: 연속된 문단의 유사도 확인
    import numpy as np

    def cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    print("\n연속 문단 간 유사도:")
    for i in range(len(paragraphs) - 1):
        similarity = cosine_similarity(embedded_paras[i], embedded_paras[i+1])
        print(f"{i} → {i+1}: {similarity:.4f}")
        print(f"  [{i}] {paragraphs[i]}")
        print(f"  [{i+1}] {paragraphs[i+1]}")
        print()

    # 유사도가 높은 것끼리 그룹화 (임계값 0.85)
    threshold = 0.85
    chunks = []
    current_chunk = [paragraphs[0]]

    for i in range(len(paragraphs) - 1):
        similarity = cosine_similarity(embedded_paras[i], embedded_paras[i+1])

        if similarity > threshold:
            current_chunk.append(paragraphs[i+1])
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = [paragraphs[i+1]]

    chunks.append(" ".join(current_chunk))

    print(f"\n의미 기반 청크 수: {len(chunks)}\n")
    for i, chunk in enumerate(chunks):
        print(f"청크 {i+1}:")
        print(f"  {chunk}\n")

    return chunks


def chunking_with_metadata():
    """
    메타데이터와 함께 청킹
    """
    # 여러 문서를 시뮬레이션
    documents_raw = [
        {
            "content": """
            제품명: Alpha Pro
            출시일: 2024-03-15
            가격: $999

            Alpha Pro는 프리미엄 시장을 타겟으로 한 신제품입니다.
            고성능 프로세서와 대용량 배터리가 특징입니다.
            """,
            "metadata": {
                "source": "products.txt",
                "product": "Alpha Pro",
                "category": "premium"
            }
        },
        {
            "content": """
            제품명: Beta Lite
            출시일: 2024-06-01
            가격: $599

            Beta Lite는 가성비를 중시하는 고객을 위한 제품입니다.
            합리적인 가격에 필수 기능을 모두 갖추었습니다.
            """,
            "metadata": {
                "source": "products.txt",
                "product": "Beta Lite",
                "category": "mid-range"
            }
        }
    ]

    print("=== 메타데이터와 함께 청킹 ===\n")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=20
    )

    all_chunks = []

    for doc_raw in documents_raw:
        # 텍스트 청킹
        chunks = splitter.split_text(doc_raw["content"])

        # 각 청크에 메타데이터 추가
        for i, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk,
                metadata={
                    **doc_raw["metadata"],
                    "chunk_id": i
                }
            )
            all_chunks.append(doc)

    print(f"총 문서 청크 수: {len(all_chunks)}\n")

    for i, doc in enumerate(all_chunks):
        print(f"청크 {i+1}:")
        print(f"  내용: {doc.page_content[:80]}...")
        print(f"  메타데이터: {doc.metadata}")
        print()

    # 벡터 저장소에 저장
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=os.getenv("GOOGLE_API_KEY"))
    vectorstore = FAISS.from_documents(all_chunks, embeddings)

    # 메타데이터 필터링 검색
    print("\n=== 메타데이터 필터링 검색 ===")
    query = "가격이 얼마인가요?"

    # 특정 카테고리만 검색
    results = vectorstore.similarity_search(
        query,
        k=2,
        filter={"category": "premium"}
    )

    print(f"질문: {query}")
    print(f"필터: category = premium\n")

    for doc in results:
        print(f"제품: {doc.metadata['product']}")
        print(f"내용: {doc.page_content}")
        print()

    return all_chunks


def optimal_chunk_size_experiment():
    """
    최적 청크 크기 실험
    """
    sample_text = """
    LangChain은 LLM 애플리케이션 개발을 위한 강력한 프레임워크입니다.
    다양한 컴포넌트를 제공하여 복잡한 AI 시스템을 쉽게 구축할 수 있습니다.
    체인을 사용하면 여러 단계의 처리를 연결할 수 있습니다.
    에이전트는 동적으로 의사결정을 내릴 수 있습니다.
    메모리 기능으로 대화 이력을 관리할 수 있습니다.
    다양한 데이터 소스와 통합이 가능합니다.
    벡터 저장소를 사용하여 RAG 시스템을 구축할 수 있습니다.
    프롬프트 템플릿으로 재사용 가능한 프롬프트를 만들 수 있습니다.
    """ * 3  # 텍스트 반복

    chunk_sizes = [100, 200, 500, 1000]

    print("=== 청크 크기별 비교 ===\n")

    for size in chunk_sizes:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=size,
            chunk_overlap=size // 10  # 10% 중복
        )

        chunks = splitter.split_text(sample_text)

        print(f"청크 크기: {size}")
        print(f"  생성된 청크 수: {len(chunks)}")
        print(f"  평균 청크 길이: {sum(len(c) for c in chunks) / len(chunks):.1f}")
        print(f"  최소/최대 길이: {min(len(c) for c in chunks)}/{max(len(c) for c in chunks)}")
        print()

    print("권장 사항:")
    print("  - 짧은 답변(FAQ): 200-500자")
    print("  - 일반 문서: 500-1000자")
    print("  - 기술 문서: 1000-1500자")
    print("  - chunk_overlap: chunk_size의 10-20%")


if __name__ == "__main__":
    print("=" * 60)
    print("Step 2: 문서 처리와 청킹")
    print("=" * 60)
    print()

    # 예제 1: 기본 청킹
    print("예제 1: 기본 청킹")
    print("-" * 60)
    basic_chunking_example()
    print("\n")

    # 예제 2: Recursive Splitter
    print("예제 2: Recursive Character Text Splitter")
    print("-" * 60)
    recursive_splitter_example()
    print("\n")

    # 예제 3: Token-based Splitter
    print("예제 3: 토큰 기반 청킹")
    print("-" * 60)
    token_based_splitter_example()
    print("\n")

    # 예제 4: Markdown Splitter
    print("예제 4: Markdown 구조 기반 청킹")
    print("-" * 60)
    markdown_splitter_example()
    print("\n")

    # 예제 5: 의미 기반 청킹
    print("예제 5: 의미 기반 청킹")
    print("-" * 60)
    semantic_chunking_example()
    print("\n")

    # 예제 6: 메타데이터와 함께
    print("예제 6: 메타데이터와 함께 청킹")
    print("-" * 60)
    chunking_with_metadata()
    print("\n")

    # 예제 7: 최적 크기 실험
    print("예제 7: 최적 청크 크기 실험")
    print("-" * 60)
    optimal_chunk_size_experiment()
