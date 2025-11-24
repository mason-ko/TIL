"""
Advanced RAG Step 4: Contextual Compression

pip install chromadb
"""

import chromadb


def compress_context(docs, query):
    """컨텍스트 압축 시뮬레이션"""
    compressed = []

    for doc in docs:
        # 간단한 압축: 쿼리 키워드를 포함한 문장만 추출
        sentences = doc.split('.')
        relevant = [s.strip() for s in sentences if query.lower() in s.lower()]

        if relevant:
            compressed.append('. '.join(relevant) + '.')

    return compressed


def main():
    print("=== Contextual Compression ===\n")

    # 데이터 (긴 문서 시뮬레이션)
    docs = [
        """LangChain은 LLM 애플리케이션 개발 프레임워크입니다.
        다양한 컴포넌트를 제공합니다. Chain, Agent, Memory 등이 있습니다.
        LangGraph는 LangChain 기반 워크플로우 라이브러리입니다.
        상태 기반 그래프를 사용합니다.""",

        """Vector Database는 임베딩 저장소입니다.
        유사도 검색을 지원합니다. ChromaDB, Pinecone 등이 있습니다.
        RAG 시스템의 핵심입니다.""",

        """Ollama는 로컬 LLM 실행 도구입니다.
        Llama 3, Mistral 등을 지원합니다.
        API 비용을 절감할 수 있습니다.
        완전 무료입니다."""
    ]

    # ChromaDB
    client = chromadb.Client()
    try:
        client.delete_collection("docs")
    except:
        pass

    collection = client.create_collection("docs")
    collection.add(documents=docs, ids=[f"doc{i}" for i in range(len(docs))])

    print(f"✅ {len(docs)}개 문서 저장\n")
    print("="*60)

    # 검색
    query = "LangGraph"
    print(f"🔍 질문: {query}\n")

    results = collection.query(query_texts=[query], n_results=2)

    # 압축 전
    print("📄 압축 전 (전체 문서):")
    for i, doc in enumerate(results['documents'][0], 1):
        print(f"\n   문서 {i} ({len(doc)}자):")
        print(f"   {doc}")

    # 압축 후
    compressed = compress_context(results['documents'][0], query)

    print("\n" + "="*60)
    print("✂️ 압축 후 (관련 부분만):")
    for i, doc in enumerate(compressed, 1):
        print(f"\n   문서 {i} ({len(doc)}자):")
        print(f"   {doc}")

    # 통계
    original_length = sum(len(d) for d in results['documents'][0])
    compressed_length = sum(len(d) for d in compressed)
    reduction = (1 - compressed_length / original_length) * 100

    print(f"\n📊 압축 통계:")
    print(f"   원본: {original_length}자")
    print(f"   압축: {compressed_length}자")
    print(f"   절감: {reduction:.1f}%")

    print("\n💡 핵심: 토큰 절감 → 비용 감소, 속도 향상")
    print("📚 다음: step5.py - Parent Document Retrieval\n")


if __name__ == "__main__":
    main()
