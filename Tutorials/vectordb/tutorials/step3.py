"""
Vector DB Step 3: RAG 실전 구현

pip install chromadb langchain-community
"""

import chromadb
import os
from dotenv import load_dotenv

load_dotenv()
from langchain_community.llms import Ollama
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI

def create_knowledge_base():
    """지식 베이스 구축"""
    documents = [
        """LangGraph는 LangChain 팀이 개발한 상태 기반 워크플로우 라이브러리입니다.
        복잡한 AI 에이전트를 만들 때 사용하며, StateGraph를 통해 노드와 엣지를 정의합니다.""",

        """Langfuse는 오픈소스 LLM Observability 플랫폼입니다.
        Self-hosted로 무료 사용 가능하며, Ollama 같은 로컬 LLM과 완벽하게 호환됩니다.
        모든 LLM 호출을 추적하고 모니터링할 수 있습니다.""",

        """ChromaDB는 로컬에서 실행 가능한 벡터 데이터베이스입니다.
        Python으로 쉽게 사용할 수 있으며, 자동으로 임베딩을 생성합니다.
        RAG 시스템의 핵심 컴포넌트입니다.""",

        """Ollama는 로컬에서 LLM을 실행하는 도구입니다.
        Llama 3, Mistral 등 다양한 모델을 지원하며, 완전 무료입니다.
        API 비용 없이 LLM을 사용할 수 있습니다."""
    ]

    # 문서 분할 (긴 문서는 작게 나눔)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=20
    )

    chunks = []
    for doc in documents:
        chunks.extend(splitter.split_text(doc))

    # ChromaDB에 저장
    client = chromadb.PersistentClient(path="./rag_db")
    collection = client.get_or_create_collection("knowledge")

    # 기존 데이터 클리어 (테스트용)
    if collection.count() > 0:
        collection.delete(ids=[collection.get()['ids'][i] for i in range(collection.count())])

    collection.add(
        documents=chunks,
        ids=[f"chunk_{i}" for i in range(len(chunks))]
    )

    return collection


def rag_query(collection, question):
    """RAG 질의응답"""
    print(f"\n질문: {question}\n")

    # 1. 관련 문서 검색
    results = collection.query(
        query_texts=[question],
        n_results=3
    )

    context = "\n".join(results['documents'][0])
    print(f"검색된 컨텍스트:\n{context}\n")

    # 2. LLM에 질문
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.7,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

    prompt = f"""다음 정보를 바탕으로 질문에 답하세요. 정보에 없으면 모른다고 하세요.

정보:
{context}

질문: {question}

답변:"""

    answer = llm.invoke(prompt)
    print(f"답변: {answer}\n")

    return answer


def main():
    print("🚀 RAG 시스템 구축\n")
    print("=" * 60)

    # 지식 베이스 구축
    print("\n1. 지식 베이스 구축 중...")
    collection = create_knowledge_base()
    print(f"   ✅ {collection.count()}개 청크 저장 완료")

    # 질의응답
    print("\n2. 질의응답 테스트")
    print("-" * 60)

    questions = [
        "로컬 LLM을 모니터링하는 도구는?",
        "벡터 데이터베이스는 뭐야?",
        "비용 없이 LLM 사용하는 방법은?"
    ]

    try:
        for q in questions:
            rag_query(collection, q)
            print("-" * 60)
    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        print("   GOOGLE_API_KEY 환경변수 설정이 필요할 수 있습니다.")

    print("\n✅ RAG 시스템 구축 완료!")
    print("\n💡 핵심: 검색 → 컨텍스트 → LLM")
    print("📚 다음: step4.py - 검색 품질 향상\n")


if __name__ == "__main__":
    main()
