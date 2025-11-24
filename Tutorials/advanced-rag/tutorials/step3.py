"""
Advanced RAG Step 3: Query Rewriting

pip install chromadb langchain-community
"""

import chromadb
from typing import List


def expand_query(query: str) -> List[str]:
    """쿼리 확장 (시뮬레이션)"""
    expansions = {
        "LLM 비용": [
            "LLM API 비용 절감 방법",
            "로컬 LLM으로 비용 줄이기",
            "토큰 사용량 최적화"
        ],
        "Vector DB": [
            "벡터 데이터베이스란",
            "임베딩 검색 시스템",
            "유사도 검색 기술"
        ]
    }

    for key in expansions:
        if key in query:
            return expansions[key]

    return [query]


def multi_query_search(collection, query: str, k: int = 2):
    """Multi-Query 검색"""
    print(f"🔍 원본 쿼리: {query}\n")

    # 1. 쿼리 확장
    expanded = expand_query(query)
    print(f"📝 확장된 쿼리 ({len(expanded)}개):")
    for i, q in enumerate(expanded, 1):
        print(f"   {i}. {q}")

    # 2. 각 쿼리로 검색
    all_results = []
    seen_docs = set()

    print(f"\n🔎 검색 중...")
    for q in expanded:
        results = collection.query(query_texts=[q], n_results=k)

        for doc in results['documents'][0]:
            if doc not in seen_docs:
                all_results.append(doc)
                seen_docs.add(doc)

    return all_results


def main():
    print("=== Query Rewriting ===\n")

    # ChromaDB 설정
    client = chromadb.Client()

    try:
        client.delete_collection("tech_docs")
    except:
        pass

    collection = client.create_collection("tech_docs")

    # 데이터
    docs = [
        "Ollama는 로컬에서 LLM을 실행하여 API 비용을 절감할 수 있습니다.",
        "Vector Database는 임베딩 벡터를 저장하고 유사도 검색을 수행합니다.",
        "토큰 사용량을 줄이면 LLM API 비용을 크게 절감할 수 있습니다.",
        "ChromaDB는 로컬 벡터 데이터베이스로 무료로 사용 가능합니다.",
        "LangGraph를 사용하면 복잡한 AI 워크플로우를 구축할 수 있습니다."
    ]

    collection.add(
        documents=docs,
        ids=[f"doc{i}" for i in range(len(docs))]
    )

    print(f"✅ {len(docs)}개 문서 저장\n")
    print("="*60)

    # Multi-Query 검색
    query = "LLM 비용"
    results = multi_query_search(collection, query, k=2)

    print(f"\n✅ 검색 완료: {len(results)}개 문서\n")
    print("📄 결과:")
    for i, doc in enumerate(results, 1):
        print(f"   {i}. {doc[:60]}...")

    print("\n💡 핵심: 쿼리를 다양하게 표현하여 검색률 향상")
    print("📚 다음: step4.py - Contextual Compression\n")


if __name__ == "__main__":
    main()
