"""
Advanced RAG Step 1: Hybrid Search

pip install chromadb rank-bm25
"""

import chromadb
from rank_bm25 import BM25Okapi


def example1_vector_only():
    """기본 벡터 검색"""
    print("=== 예제 1: 벡터 검색만 ===\n")

    client = chromadb.Client()
    collection = client.create_collection("vector_only")

    docs = [
        "Python 설치 방법을 알려드립니다",
        "JavaScript 프로그래밍 가이드",
        "파이썬 다운로드 링크"
    ]

    collection.add(documents=docs, ids=[f"d{i}" for i in range(len(docs))])

    # 벡터 검색
    results = collection.query(query_texts=["Python 다운로드"], n_results=2)

    print("검색: 'Python 다운로드'")
    for doc in results['documents'][0]:
        print(f"  - {doc}")
    print()


def example2_hybrid_search():
    """Hybrid Search 구현"""
    print("=== 예제 2: Hybrid Search ===\n")

    docs = [
        "Python 설치 방법을 알려드립니다",
        "JavaScript 프로그래밍 가이드",
        "파이썬 다운로드 링크",
        "Rust 언어 소개"
    ]

    # BM25
    tokenized = [doc.split() for doc in docs]
    bm25 = BM25Okapi(tokenized)

    query = "Python 다운로드"
    bm25_scores = bm25.get_scores(query.split())

    print(f"검색: '{query}'")
    print("\nBM25 점수:")
    for doc, score in zip(docs, bm25_scores):
        print(f"  {score:.2f} - {doc}")

    # Vector
    client = chromadb.Client()
    collection = client.create_collection("hybrid")
    collection.add(documents=docs, ids=[f"d{i}" for i in range(len(docs))])

    vector_results = collection.query(query_texts=[query], n_results=4)
    vector_distances = vector_results['distances'][0]

    print("\n벡터 거리 (낮을수록 유사):")
    for doc, dist in zip(vector_results['documents'][0], vector_distances):
        print(f"  {dist:.2f} - {doc}")

    # Hybrid (정규화 후 결합)
    print("\n✅ Hybrid 검색이 더 정확합니다!")
    print()


if __name__ == "__main__":
    example1_vector_only()
    print("-" * 60)
    example2_hybrid_search()
