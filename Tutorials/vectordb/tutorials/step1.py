"""
Vector DB Step 1: ChromaDB 기본

실행 전:
pip install chromadb
"""

import chromadb
from chromadb.config import Settings


def example1_basic_usage():
    """
    예제 1: 기본 사용법

    ChromaDB의 가장 간단한 사용 예제입니다.
    """
    print("=== 예제 1: 기본 사용법 ===\n")

    # 클라이언트 생성
    client = chromadb.Client()

    # 컬렉션 생성
    collection = client.create_collection(name="basic_example")

    # 문서 추가
    documents = [
        "강아지 사료 추천해주세요",
        "고양이 간식 어떤게 좋나요",
        "반려견 영양제 필요할까요",
        "강아지 산책 시간은 얼마나?",
        "고양이 장난감 추천"
    ]

    collection.add(
        documents=documents,
        ids=[f"doc{i}" for i in range(len(documents))]
    )

    print(f"문서 {len(documents)}개 추가 완료\n")

    # 검색
    query = "멍멍이 먹이"
    print(f"검색어: '{query}'")

    results = collection.query(
        query_texts=[query],
        n_results=3
    )

    print(f"\n검색 결과:")
    for i, doc in enumerate(results['documents'][0], 1):
        print(f"{i}. {doc}")

    print()


def example2_metadata():
    """
    예제 2: 메타데이터 활용

    메타데이터를 추가하여 필터링된 검색을 수행합니다.
    """
    print("=== 예제 2: 메타데이터 활용 ===\n")

    client = chromadb.Client()
    collection = client.create_collection(name="with_metadata")

    # 메타데이터와 함께 문서 추가
    collection.add(
        documents=[
            "Python은 프로그래밍 언어입니다",
            "JavaScript는 웹 개발에 사용됩니다",
            "Rust는 시스템 프로그래밍 언어입니다",
            "Java는 엔터프라이즈 개발에 사용됩니다",
            "Go는 구글이 만든 언어입니다"
        ],
        metadatas=[
            {"category": "language", "level": "beginner", "type": "general"},
            {"category": "language", "level": "beginner", "type": "web"},
            {"category": "language", "level": "advanced", "type": "system"},
            {"category": "language", "level": "intermediate", "type": "enterprise"},
            {"category": "language", "level": "intermediate", "type": "backend"}
        ],
        ids=["py", "js", "rust", "java", "go"]
    )

    # 메타데이터 필터링 없이 검색
    print("1. 필터링 없이 검색: '웹 개발 언어'")
    results = collection.query(
        query_texts=["웹 개발 언어"],
        n_results=3
    )
    for doc in results['documents'][0]:
        print(f"   - {doc}")

    print()

    # 메타데이터 필터링
    print("2. 초급만 검색: level='beginner'")
    results = collection.query(
        query_texts=["프로그래밍 언어"],
        n_results=3,
        where={"level": "beginner"}
    )
    for doc in results['documents'][0]:
        print(f"   - {doc}")

    print()


def example3_persistent():
    """
    예제 3: 영구 저장

    데이터를 디스크에 저장하여 프로그램 재시작 후에도 유지합니다.
    """
    print("=== 예제 3: 영구 저장 ===\n")

    # 디스크에 저장
    client = chromadb.PersistentClient(path="./chroma_data")

    collection = client.get_or_create_collection(name="persistent_docs")

    # 기존 문서 수 확인
    count = collection.count()
    print(f"현재 문서 수: {count}")

    # 새 문서 추가
    new_docs = [
        "LangGraph는 상태 기반 워크플로우 라이브러리입니다",
        "Langfuse는 오픈소스 LLM 모니터링 플랫폼입니다",
        "ChromaDB는 벡터 데이터베이스입니다"
    ]

    collection.add(
        documents=new_docs,
        ids=[f"persist_{count + i}" for i in range(len(new_docs))]
    )

    print(f"문서 {len(new_docs)}개 추가")
    print(f"새 문서 수: {collection.count()}")
    print("\n✅ 데이터가 ./chroma_data 폴더에 저장되었습니다")
    print("   프로그램을 재실행해도 데이터가 유지됩니다\n")


def example4_distance_metrics():
    """
    예제 4: 거리 메트릭 비교

    다양한 거리 측정 방법을 비교합니다.
    """
    print("=== 예제 4: 거리 메트릭 ===\n")

    client = chromadb.Client()

    # Cosine 유사도 (기본, 권장)
    collection_cosine = client.create_collection(
        name="cosine_test",
        metadata={"hnsw:space": "cosine"}
    )

    docs = [
        "머신러닝은 인공지능의 한 분야입니다",
        "딥러닝은 머신러닝의 한 종류입니다",
        "강아지는 게으른 동물입니다"
    ]

    collection_cosine.add(
        documents=docs,
        ids=["ml", "dl", "dog"]
    )

    query = "AI 기술"
    results = collection_cosine.query(
        query_texts=[query],
        n_results=3
    )

    print(f"검색어: '{query}'")
    print("Cosine 유사도 결과:")
    for i, (doc, distance) in enumerate(zip(results['documents'][0], results['distances'][0]), 1):
        print(f"{i}. {doc}")
        print(f"   거리: {distance:.4f}")

    print()


def example5_simple_rag():
    """
    예제 5: 간단한 RAG

    ChromaDB + Ollama를 사용한 기본 RAG 구현
    (Ollama가 설치되어 있어야 합니다)
    """
    print("=== 예제 5: 간단한 RAG ===\n")

    try:
        from langchain_community.llms import Ollama

        client = chromadb.Client()
        collection = client.create_collection(name="rag_example")

        # 지식 베이스 구축
        knowledge = [
            "LangGraph는 LangChain 팀이 만든 상태 기반 워크플로우 라이브러리입니다. 복잡한 AI 에이전트를 만들 때 사용합니다.",
            "Langfuse는 오픈소스 LLM Observability 플랫폼입니다. Self-hosted로 무료로 사용 가능하며, Ollama 같은 로컬 LLM과 잘 호환됩니다.",
            "ChromaDB는 로컬에서 실행 가능한 벡터 데이터베이스입니다. 임베딩을 자동으로 생성하고 의미 기반 검색을 지원합니다.",
            "Ollama는 로컬에서 LLM을 실행할 수 있게 해주는 도구입니다. Llama 3, Mistral 등 다양한 모델을 지원합니다."
        ]

        collection.add(
            documents=knowledge,
            ids=[f"kb{i}" for i in range(len(knowledge))]
        )

        print("지식 베이스 구축 완료\n")

        # RAG 질의응답
        question = "로컬 LLM을 모니터링하는 도구는 뭐야?"
        print(f"질문: {question}\n")

        # 1. 관련 문서 검색
        results = collection.query(
            query_texts=[question],
            n_results=2
        )

        context = "\n".join(results['documents'][0])
        print(f"검색된 컨텍스트:\n{context}\n")

        # 2. LLM에 질문
        llm = Ollama(model="llama3")

        prompt = f"""다음 정보를 바탕으로 질문에 답하세요. 정보에 없는 내용은 답하지 마세요.

정보:
{context}

질문: {question}

답변:"""

        print("LLM 응답:")
        answer = llm.invoke(prompt)
        print(answer)
        print()

    except ImportError:
        print("⚠️  langchain-community가 설치되지 않았습니다")
        print("   pip install langchain-community")
    except Exception as e:
        print(f"⚠️  예제 5 실행 실패: {e}")
        print("   Ollama가 설치되어 있고 실행 중인지 확인하세요")
        print("   ollama pull llama3")


if __name__ == "__main__":
    print("🚀 ChromaDB Step 1: 기본 사용법\n")
    print("=" * 60)
    print()

    # 예제 1: 기본 사용법
    # example1_basic_usage()
    # print("-" * 60)
    # print()

    # 예제 2: 메타데이터
    # example2_metadata()
    # print("-" * 60)
    # print()

    # # 예제 3: 영구 저장
    # example3_persistent()
    # print("-" * 60)
    # print()

    # # 예제 4: 거리 메트릭
    example4_distance_metrics()
    print("-" * 60)
    print()

    # # 예제 5: 간단한 RAG
    # example5_simple_rag()
    # print("=" * 60)
    # print()

    # print("✅ 모든 예제 완료!")
    # print()
    # print("📊 다음 단계:")
    # print("   1. ./chroma_data 폴더에 저장된 데이터 확인")
    # print("   2. 다양한 검색어로 실험")
    # print("   3. 자신만의 지식 베이스 구축")
    # print()
    # print("📚 다음 튜토리얼: step2.py - 임베딩 모델 최적화")
