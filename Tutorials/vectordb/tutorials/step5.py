"""
Vector DB Step 5: RAG 통합

LangChain을 활용한 프로덕션급 RAG 시스템 구축

pip install chromadb langchain-community langchain-core
"""

import chromadb
import os
from dotenv import load_dotenv

load_dotenv()


def setup_knowledge_base():
    """지식 베이스 설정"""
    client = chromadb.PersistentClient(path="./final_rag_db")

    # 기존 컬렉션 삭제
    try:
        client.delete_collection("tech_docs")
    except:
        pass

    collection = client.create_collection("tech_docs")

    # 기술 문서 데이터
    documents = [
        "LangChain은 LLM 애플리케이션 개발 프레임워크입니다. Chain, Agent, Retriever 등의 구성요소를 제공합니다.",
        "LangGraph는 상태 기반 워크플로우 라이브러리로 복잡한 AI 에이전트를 만들 수 있습니다.",
        "Vector Database는 임베딩 벡터를 저장하고 유사도 검색을 수행합니다. ChromaDB, Pinecone 등이 있습니다.",
        "RAG(Retrieval-Augmented Generation)는 검색과 생성을 결합한 기법입니다. 외부 지식을 활용합니다.",
        "Ollama는 로컬에서 LLM을 실행하는 도구입니다. Llama 3, Mistral 등을 지원합니다.",
        "Langfuse는 오픈소스 LLM 모니터링 플랫폼입니다. Self-hosted 가능하며 무료입니다.",
    ]

    metadatas = [
        {"source": "langchain-docs", "category": "framework"},
        {"source": "langgraph-docs", "category": "framework"},
        {"source": "vectordb-guide", "category": "database"},
        {"source": "rag-tutorial", "category": "technique"},
        {"source": "ollama-docs", "category": "tools"},
        {"source": "langfuse-docs", "category": "monitoring"},
    ]

    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=[f"doc{i}" for i in range(len(documents))]
    )

    return collection


def basic_retrieval(collection, query):
    """기본 검색"""
    print(f"\n🔍 검색: {query}")
    print("-" * 60)

    results = collection.query(
        query_texts=[query],
        n_results=3
    )

    for i, (doc, meta) in enumerate(zip(
        results['documents'][0],
        results['metadatas'][0]
    ), 1):
        print(f"\n   {i}. [{meta['category']}] {meta['source']}")
        print(f"      {doc[:100]}...")


def filtered_retrieval(collection, query, category):
    """메타데이터 필터링 검색"""
    print(f"\n🔍 필터링 검색: {query} (category={category})")
    print("-" * 60)

    results = collection.query(
        query_texts=[query],
        n_results=3,
        where={"category": category}
    )

    if results['documents'][0]:
        for i, doc in enumerate(results['documents'][0], 1):
            print(f"   {i}. {doc[:80]}...")
    else:
        print("   검색 결과 없음")


def mmr_retrieval(collection, query):
    """MMR (다양성 고려) 검색 시뮬레이션"""
    print(f"\n🔍 MMR 검색 (다양성 고려): {query}")
    print("-" * 60)

    # 더 많은 후보 가져오기
    results = collection.query(
        query_texts=[query],
        n_results=10
    )

    # 카테고리 다양성 확보
    seen_categories = set()
    diverse_docs = []

    for doc, meta in zip(
        results['documents'][0],
        results['metadatas'][0]
    ):
        category = meta['category']
        if category not in seen_categories:
            diverse_docs.append((doc, category))
            seen_categories.add(category)

        if len(diverse_docs) >= 3:
            break

    print("   다양한 카테고리의 문서 선택:")
    for i, (doc, cat) in enumerate(diverse_docs, 1):
        print(f"   {i}. [{cat}] {doc[:80]}...")


def rag_with_context(collection, question):
    """컨텍스트 포함 RAG"""
    print(f"\n💬 RAG 질의응답: {question}")
    print("=" * 60)

    # 1. 검색
    results = collection.query(
        query_texts=[question],
        n_results=2
    )

    context_parts = []
    for doc, meta in zip(
        results['documents'][0],
        results['metadatas'][0]
    ):
        context_parts.append(f"[출처: {meta['source']}]\n{doc}")

    context = "\n\n".join(context_parts)

    print("\n📄 검색된 컨텍스트:")
    print("-" * 60)
    print(context)

    # 2. 프롬프트 생성
    prompt = f"""다음 컨텍스트를 바탕으로 질문에 답하세요.
컨텍스트에 없는 내용은 추측하지 마세요.

컨텍스트:
{context}

질문: {question}

답변:"""

    print("\n🤖 LLM 프롬프트:")
    print("-" * 60)
    print(prompt[:300] + "...\n")

    # 실제로는 LLM 호출
    print("   → LLM에 전송 (실제 구현 시)")


def production_rag_demo():
    """프로덕션 RAG 시스템 데모"""
    print("\n🏭 프로덕션 RAG 시스템 구조")
    print("=" * 60)

    code = '''
class ProductionRAG:
    def __init__(self):
        # Vector Store
        self.vectorstore = Chroma(
            persist_directory="./db",
            embedding_function=OpenAIEmbeddings()
        )

        # Retriever (MMR)
        self.retriever = self.vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 3, "fetch_k": 10}
        )

        # LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash"
        )

        # Memory
        self.memory = ConversationBufferMemory()

    def query(self, question):
        # 1. Retrieve
        docs = self.retriever.get_relevant_documents(question)

        # 2. Format context
        context = self.format_docs(docs)

        # 3. Generate answer
        answer = self.llm.invoke(
            f"Context: {context}\\nQuestion: {question}"
        )

        # 4. Save to memory
        self.memory.save_context(
            {"input": question},
            {"output": answer}
        )

        return {
            "answer": answer,
            "sources": [doc.metadata for doc in docs]
        }

# 사용
rag = ProductionRAG()
result = rag.query("질문")
print(result["answer"])
'''
    print(code)


def main():
    print("🚀 Vector DB Step 5: RAG 통합\n")
    print("=" * 60)

    # 지식 베이스 설정
    print("\n1. 지식 베이스 구축")
    print("-" * 60)
    collection = setup_knowledge_base()
    print(f"   ✅ {collection.count()}개 문서 저장 완료")

    # 기본 검색
    print("\n2. 기본 검색")
    basic_retrieval(collection, "로컬에서 LLM 실행하는 방법")

    # 필터링 검색
    print("\n3. 메타데이터 필터링")
    filtered_retrieval(collection, "프레임워크", "framework")

    # MMR 검색
    print("\n4. 다양성 고려 (MMR)")
    mmr_retrieval(collection, "LLM 애플리케이션 개발")

    # RAG 실행
    print("\n5. RAG 질의응답")
    rag_with_context(collection, "LLM을 모니터링하려면?")

    # 프로덕션 데모
    production_rag_demo()

    print("\n✅ Vector DB 튜토리얼 완료!")
    print("\n🎓 학습한 내용:")
    print("   1. Vector DB 기본 (ChromaDB)")
    print("   2. 문서 분할 및 임베딩")
    print("   3. RAG 시스템 구축")
    print("   4. 프로덕션 고려사항 (Pinecone)")
    print("   5. LangChain 통합")

    print("\n🚀 다음 단계:")
    print("   - Advanced RAG: Hybrid Search, Reranking")
    print("   - Multi-Modal: 이미지 + 텍스트")
    print("   - Langfuse/LangSmith: 모니터링")
    print("   - GraphRAG: 지식 그래프 검색\n")


if __name__ == "__main__":
    main()
