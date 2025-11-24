"""
Vector DB Step 4: Pinecone 프로덕션

주의: Pinecone은 유료 서비스입니다 (무료 티어 제한적)
이 예제는 설명 목적이며, 실제 실행시 API 키가 필요합니다.

pip install pinecone-client langchain-pinecone langchain-openai
"""

import os
from dotenv import load_dotenv

load_dotenv()

def demo_pinecone_setup():
    """Pinecone 설정 데모 (주석 처리)"""
    print("🚀 Pinecone 프로덕션 설정\n")
    print("=" * 60)

    print("\n1. Pinecone 초기화 (데모)")
    print("-" * 60)

    # 실제 코드 (API 키 필요):
    code = '''
import pinecone
import os

# 초기화
pinecone.init(
    api_key=os.getenv("PINECONE_API_KEY"),
    environment=os.getenv("PINECONE_ENVIRONMENT")
)

# 인덱스 생성
index_name = "knowledge-base"

if index_name not in pinecone.list_indexes():
    pinecone.create_index(
        name=index_name,
        dimension=1536,  # OpenAI 임베딩 차원
        metric="cosine"
    )

index = pinecone.Index(index_name)
'''
    print(code)

    print("\n2. LangChain 통합 (데모)")
    print("-" * 60)

    code2 = '''
from langchain_pinecone import PineconeVectorStore
from langchain.embeddings import OpenAIEmbeddings

# 임베딩
embeddings = OpenAIEmbeddings()

# 문서 저장
vectorstore = PineconeVectorStore.from_documents(
    documents,
    embeddings,
    index_name="knowledge-base"
)

# 검색
results = vectorstore.similarity_search("질문", k=3)
'''
    print(code2)


def demo_chroma_advanced():
    """ChromaDB 고급 기능 (실제 동작)"""
    import chromadb
    from chromadb.utils import embedding_functions

    print("\n3. ChromaDB 고급 기능 (실제 동작)")
    print("-" * 60)

    # 클라이언트 생성
    client = chromadb.PersistentClient(path="./advanced_db")

    # 컬렉션 생성 (기존 삭제)
    try:
        client.delete_collection("advanced")
    except:
        pass

    collection = client.create_collection(
        name="advanced",
        metadata={"description": "고급 기능 데모"}
    )

    # 메타데이터와 함께 문서 추가
    documents = [
        "Python은 1991년에 Guido van Rossum이 만들었습니다.",
        "JavaScript는 웹 프론트엔드 개발에 사용됩니다.",
        "Rust는 시스템 프로그래밍 언어입니다.",
        "Go는 Google이 개발한 언어입니다.",
        "TypeScript는 JavaScript의 슈퍼셋입니다."
    ]

    metadatas = [
        {"language": "python", "category": "general", "year": 1991},
        {"language": "javascript", "category": "web", "year": 1995},
        {"language": "rust", "category": "system", "year": 2010},
        {"language": "go", "category": "system", "year": 2009},
        {"language": "typescript", "category": "web", "year": 2012}
    ]

    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=[f"doc{i}" for i in range(len(documents))]
    )

    print(f"   ✅ {collection.count()}개 문서 저장 완료\n")

    # 메타데이터 필터링 검색
    print("4. 메타데이터 필터링")
    print("-" * 60)

    # 웹 관련 언어만 검색
    results = collection.query(
        query_texts=["웹 개발 언어"],
        n_results=3,
        where={"category": "web"}
    )

    print("   🔍 category='web'인 문서:")
    for doc in results['documents'][0]:
        print(f"      - {doc}")

    # 2000년 이후 언어
    results2 = collection.query(
        query_texts=["최신 언어"],
        n_results=3,
        where={"year": {"$gt": 2000}}
    )

    print(f"\n   🔍 year > 2000인 문서:")
    for doc in results2['documents'][0]:
        print(f"      - {doc}")

    print("\n5. 거리(distance) 기반 필터링")
    print("-" * 60)

    results3 = collection.query(
        query_texts=["프로그래밍 언어"],
        n_results=10,
        where={"category": {"$in": ["web", "system"]}}
    )

    print("   🔍 web 또는 system 카테고리:")
    for i, (doc, distance) in enumerate(zip(
        results3['documents'][0],
        results3['distances'][0]
    )):
        print(f"      {i+1}. [거리: {distance:.3f}] {doc}")


def demo_performance_tips():
    """성능 최적화 팁"""
    print("\n6. 성능 최적화 팁")
    print("-" * 60)

    tips = """
    ✅ 배치 처리:
       - 한 번에 여러 문서 추가 (add 메서드)
       - 100-1000개 단위로 배치

    ✅ 임베딩 캐싱:
       - 동일한 텍스트는 캐시에서 가져오기
       - Redis 등 외부 캐시 활용

    ✅ 적절한 n_results:
       - 너무 많으면 느림
       - 보통 3-5개가 적당

    ✅ 메타데이터 필터 먼저:
       - where 조건으로 후보 줄이기
       - 그 다음 벡터 검색

    ✅ 정기적인 최적화:
       - 사용하지 않는 문서 삭제
       - 인덱스 재구성
    """
    print(tips)


def demo_production_checklist():
    """프로덕션 체크리스트"""
    print("\n7. 프로덕션 체크리스트")
    print("-" * 60)

    checklist = """
    [ ] Vector DB 선택 (ChromaDB/Pinecone/Qdrant)
    [ ] 임베딩 모델 선택 (OpenAI/HuggingFace)
    [ ] 청크 크기 결정 (200-500자)
    [ ] 메타데이터 스키마 설계
    [ ] 배치 처리 구현
    [ ] 에러 핸들링
    [ ] 모니터링 (검색 지연시간, 정확도)
    [ ] 백업 전략
    [ ] 비용 모니터링 (API 호출 수)
    [ ] 확장성 계획
    """
    print(checklist)


def main():
    # Pinecone 설정 데모
    demo_pinecone_setup()

    # ChromaDB 고급 기능 (실제 동작)
    demo_chroma_advanced()

    # 성능 팁
    demo_performance_tips()

    # 체크리스트
    demo_production_checklist()

    print("\n✅ Step 4 완료!")
    print("\n💡 핵심:")
    print("   - ChromaDB: 개발/소규모")
    print("   - Pinecone: 프로덕션/대규모")
    print("   - 메타데이터 필터링으로 정확도 향상")
    print("   - 배치 처리로 성능 최적화")
    print("\n📚 다음: step5.py - RAG 통합\n")


if __name__ == "__main__":
    main()
