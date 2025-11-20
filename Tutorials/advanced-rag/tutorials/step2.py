"""
Advanced RAG Step 2: Reranking으로 검색 품질 향상

pip install chromadb rank-bm25
"""

import chromadb
from rank_bm25 import BM25Okapi


def basic_vector_search():
    """기본 벡터 검색"""
    print("=== 기본 벡터 검색 ===\n")

    docs = [
        "Python은 프로그래밍 언어입니다",
        "Python으로 웹 개발을 할 수 있습니다",
        "Java는 객체지향 언어입니다",
        "JavaScript는 웹 브라우저에서 실행됩니다",
        "C++은 시스템 프로그래밍에 사용됩니다"
    ]

    client = chromadb.Client()
    collection = client.create_collection("basic")
    collection.add(documents=docs, ids=[f"d{i}" for i in range(len(docs))])

    query = "파이썬 웹 개발"
    results = collection.query(query_texts=[query], n_results=3)

    print(f"질문: {query}\n")
    print("검색 결과:")
    for i, doc in enumerate(results['documents'][0], 1):
        print(f"{i}. {doc}")

    print("\n⚠️  관련 없는 문서도 포함될 수 있음\n")


def reranking_example():
    """Reranking으로 정확도 향상"""
    print("=== Reranking 적용 ===\n")

    docs = [
        "Python은 프로그래밍 언어입니다",
        "Python으로 웹 개발을 할 수 있습니다",  # 가장 관련
        "Python은 데이터 분석에 많이 사용됩니다",
        "Java는 객체지향 언어입니다",
        "JavaScript는 웹 브라우저에서 실행됩니다"
    ]

    # 1차: 벡터 검색 (많이 가져옴)
    client = chromadb.Client()
    collection = client.create_collection("rerank")
    collection.add(documents=docs, ids=[f"d{i}" for i in range(len(docs))])

    query = "파이썬으로 웹사이트 만들기"

    # 상위 5개 가져오기
    results = collection.query(query_texts=[query], n_results=5)
    candidates = results['documents'][0]

    print(f"질문: {query}\n")
    print("1차 검색 (벡터):")
    for i, doc in enumerate(candidates, 1):
        print(f"{i}. {doc}")

    # 2차: Reranking (BM25로 재정렬)
    tokenized_docs = [doc.split() for doc in candidates]
    bm25 = BM25Okapi(tokenized_docs)

    query_tokens = query.split()
    scores = bm25.get_scores(query_tokens)

    # 점수 높은 순으로 정렬
    ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)

    print("\n2차 Reranking (BM25):")
    for i, (doc, score) in enumerate(ranked[:3], 1):
        print(f"{i}. [{score:.2f}] {doc}")

    print("\n✅ '웹 개발' 관련 문서가 상위로!")
    print()


def hybrid_search_final():
    """Hybrid Search 최종 구현"""
    print("=== Hybrid Search (벡터 + BM25) ===\n")

    docs = [
        "LangGraph는 상태 기반 워크플로우 라이브러리입니다",
        "Langfuse는 LLM 모니터링 도구입니다",
        "ChromaDB는 벡터 데이터베이스입니다",
        "Ollama로 로컬 LLM을 실행할 수 있습니다",
        "FastAPI는 Python 웹 프레임워크입니다"
    ]

    query = "로컬 LLM 모니터링"

    # 벡터 검색
    client = chromadb.Client()
    collection = client.create_collection("hybrid")
    collection.add(documents=docs, ids=[f"d{i}" for i in range(len(docs))])

    vector_results = collection.query(query_texts=[query], n_results=5)
    vector_docs = vector_results['documents'][0]
    vector_distances = vector_results['distances'][0]

    # 벡터 점수 (거리를 유사도로 변환, 0-1)
    vector_scores = [1 / (1 + d) for d in vector_distances]

    # BM25 점수
    tokenized = [doc.split() for doc in docs]
    bm25 = BM25Okapi(tokenized)
    bm25_scores = bm25.get_scores(query.split())

    # 정규화 (0-1 범위로)
    max_bm25 = max(bm25_scores) if max(bm25_scores) > 0 else 1
    bm25_scores_norm = [s / max_bm25 for s in bm25_scores]

    # Hybrid 점수 = Vector * 0.5 + BM25 * 0.5
    hybrid_scores = []
    for i, doc in enumerate(docs):
        if doc in vector_docs:
            idx = vector_docs.index(doc)
            v_score = vector_scores[idx]
        else:
            v_score = 0

        b_score = bm25_scores_norm[i]
        hybrid_score = v_score * 0.5 + b_score * 0.5
        hybrid_scores.append((doc, hybrid_score, v_score, b_score))

    # 정렬
    hybrid_scores.sort(key=lambda x: x[1], reverse=True)

    print(f"질문: {query}\n")
    print("Hybrid 검색 결과:")
    print("\n문서                                    | Hybrid | Vector | BM25")
    print("-" * 75)

    for doc, h_score, v_score, b_score in hybrid_scores[:3]:
        doc_short = doc[:40]
        print(f"{doc_short:40} | {h_score:.2f}   | {v_score:.2f}   | {b_score:.2f}")

    print("\n✅ Hybrid가 가장 관련 있는 문서를 찾음!")
    print()


if __name__ == "__main__":
    basic_vector_search()
    print("-" * 60)
    reranking_example()
    print("-" * 60)
    hybrid_search_final()

    print("=" * 60)
    print("\n✅ Reranking & Hybrid Search 완료!")
    print("\n💡 핵심:")
    print("  1. 벡터 검색: 의미 유사도")
    print("  2. BM25: 키워드 매칭")
    print("  3. Hybrid: 둘 다 고려 → 정확도 향상")
    print()
