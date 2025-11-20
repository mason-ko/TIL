"""
Step 1: 기본 RAG (Retrieval-Augmented Generation) 개념
GraphRAG를 배우기 전에 먼저 기본 RAG를 이해합니다.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# .env 파일에서 환경변수 로드
load_dotenv()
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate


def without_rag_example():
    """
    RAG 없이 LLM만 사용하는 경우
    LLM의 지식에만 의존합니다.
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    question = "우리 회사의 2024년 신제품 출시 일정은?"

    print("=== RAG 없이 LLM에게 질문 ===")
    print(f"질문: {question}\n")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": question}
        ]
    )

    print(f"답변: {response.choices[0].message.content}\n")
    print("문제: LLM은 회사 내부 정보를 모릅니다!")

    return response


def simple_rag_example():
    """
    간단한 RAG 구현
    1. 문서를 벡터로 변환 (임베딩)
    2. 벡터 저장소에 저장
    3. 질문과 유사한 문서 검색
    4. 검색된 문서와 함께 LLM에게 질문
    """

    # 샘플 문서들 (회사 내부 정보)
    documents = [
        Document(
            page_content="2024년 신제품 Alpha는 3월 15일에 출시 예정입니다. "
                        "프리미엄 시장을 타겟으로 하며 가격은 $999입니다.",
            metadata={"source": "product_roadmap.pdf", "category": "product"}
        ),
        Document(
            page_content="Beta 제품은 6월 1일 출시 예정입니다. "
                        "중간 가격대 시장을 목표로 하며 $599에 판매됩니다.",
            metadata={"source": "product_roadmap.pdf", "category": "product"}
        ),
        Document(
            page_content="우리 회사는 2024년 1분기에 30% 성장을 목표로 합니다. "
                        "주요 전략은 신제품 출시와 해외 시장 확대입니다.",
            metadata={"source": "business_plan.pdf", "category": "strategy"}
        ),
        Document(
            page_content="고객 지원팀은 평일 9시부터 6시까지 운영됩니다. "
                        "이메일과 전화로 문의 가능합니다.",
            metadata={"source": "support_info.pdf", "category": "support"}
        )
    ]

    print("=== RAG 시스템 구축 ===\n")

    # 1. 임베딩 모델 초기화
    print("1. 임베딩 모델 초기화...")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=os.getenv("GOOGLE_API_KEY"))

    # 2. 벡터 저장소 생성 (FAISS)
    print("2. 문서를 벡터로 변환하여 저장...")
    vectorstore = FAISS.from_documents(documents, embeddings)
    print(f"   총 {len(documents)}개 문서 저장 완료\n")

    # 3. 질문
    question = "2024년 신제품 출시 일정은?"
    print(f"질문: {question}\n")

    # 4. 관련 문서 검색
    print("3. 관련 문서 검색 중...")
    retrieved_docs = vectorstore.similarity_search(question, k=2)

    print(f"   검색된 문서 수: {len(retrieved_docs)}\n")
    print("검색된 문서:")
    for i, doc in enumerate(retrieved_docs):
        print(f"  [{i+1}] {doc.page_content[:100]}...")
        print(f"      출처: {doc.metadata['source']}\n")

    # 5. LLM에게 검색된 문서와 함께 질문
    print("4. LLM에게 문서와 함께 질문...\n")

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))

    # RAG 프롬프트 템플릿
    prompt = ChatPromptTemplate.from_messages([
        ("system", "당신은 도움이 되는 어시스턴트입니다. "
                   "아래 제공된 문서를 바탕으로 질문에 답변해주세요.\n\n"
                   "문서:\n{context}"),
        ("user", "{question}")
    ])

    # 검색된 문서를 텍스트로 결합
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])

    # LLM 호출
    chain = prompt | llm
    response = chain.invoke({
        "context": context,
        "question": question
    })

    print(f"답변: {response.content}\n")

    return response


def embedding_similarity_example():
    """
    임베딩과 유사도 검색 이해하기
    """
    print("=== 임베딩과 유사도 ===\n")

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=os.getenv("GOOGLE_API_KEY"))

    # 샘플 텍스트들
    texts = [
        "고양이는 귀여운 동물입니다.",
        "강아지는 충성스러운 반려동물입니다.",
        "Python은 프로그래밍 언어입니다.",
        "자바스크립트는 웹 개발에 사용됩니다."
    ]

    print("텍스트 목록:")
    for i, text in enumerate(texts):
        print(f"  {i}: {text}")

    # 질문
    query = "애완동물에 대해 알려주세요"
    print(f"\n질문: {query}\n")

    # 벡터 저장소 생성
    docs = [Document(page_content=text) for text in texts]
    vectorstore = FAISS.from_documents(docs, embeddings)

    # 유사도 검색 (점수 포함)
    results = vectorstore.similarity_search_with_score(query, k=4)

    print("유사도 순위:")
    for i, (doc, score) in enumerate(results):
        print(f"  {i+1}. (유사도: {score:.4f}) {doc.page_content}")

    print("\n→ 점수가 낮을수록 더 유사합니다 (거리 기반)")

    return results


def retrieval_methods_example():
    """
    다양한 검색 방법
    """
    documents = [
        Document(page_content="인공지능은 기계가 인간의 지능을 모방하는 기술입니다.",
                metadata={"topic": "AI"}),
        Document(page_content="머신러닝은 데이터로부터 학습하는 AI의 한 분야입니다.",
                metadata={"topic": "ML"}),
        Document(page_content="딥러닝은 인공신경망을 사용하는 머신러닝 기법입니다.",
                metadata={"topic": "DL"}),
        Document(page_content="자연어처리는 컴퓨터가 인간의 언어를 이해하는 기술입니다.",
                metadata={"topic": "NLP"}),
        Document(page_content="컴퓨터 비전은 이미지와 비디오를 분석하는 AI 분야입니다.",
                metadata={"topic": "CV"})
    ]

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=os.getenv("GOOGLE_API_KEY"))
    vectorstore = FAISS.from_documents(documents, embeddings)

    query = "딥러닝과 관련된 내용"

    print("=== 검색 방법 비교 ===\n")

    # 1. Similarity Search (기본)
    print("1. Similarity Search (상위 k개)")
    results = vectorstore.similarity_search(query, k=2)
    for doc in results:
        print(f"   - {doc.page_content[:50]}...")
    print()

    # 2. MMR (Maximum Marginal Relevance) - 다양성 고려
    print("2. MMR Search (유사하면서도 다양한 결과)")
    results = vectorstore.max_marginal_relevance_search(query, k=2)
    for doc in results:
        print(f"   - {doc.page_content[:50]}...")
    print()

    # 3. Similarity with threshold
    print("3. Similarity with Score Threshold")
    retriever = vectorstore.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"score_threshold": 0.5, "k": 5}
    )
    results = retriever.invoke(query)
    print(f"   임계값 이상 문서 수: {len(results)}")
    for doc in results:
        print(f"   - {doc.page_content[:50]}...")

    return results


def rag_chain_example():
    """
    완전한 RAG 체인
    LangChain을 사용한 end-to-end RAG
    """
    from langchain.chains import RetrievalQA

    # 문서 준비
    documents = [
        Document(
            page_content="LangChain은 LLM 애플리케이션 개발 프레임워크입니다. "
                        "체인, 에이전트, 메모리 등의 기능을 제공합니다.",
            metadata={"source": "langchain_docs"}
        ),
        Document(
            page_content="LangGraph는 LangChain의 그래프 기반 워크플로우 라이브러리입니다. "
                        "복잡한 에이전트를 그래프로 표현할 수 있습니다.",
            metadata={"source": "langgraph_docs"}
        ),
        Document(
            page_content="RAG는 검색과 생성을 결합한 기법입니다. "
                        "외부 지식을 활용하여 더 정확한 답변을 생성합니다.",
            metadata={"source": "rag_guide"}
        )
    ]

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=os.getenv("GOOGLE_API_KEY"))
    vectorstore = FAISS.from_documents(documents, embeddings)

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))

    # RetrievalQA 체인 생성
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",  # 모든 문서를 한 번에 전달
        retriever=vectorstore.as_retriever(search_kwargs={"k": 2}),
        return_source_documents=True  # 출처 문서도 반환
    )

    # 질문
    question = "LangGraph가 뭔가요?"

    print("=== RAG 체인 실행 ===\n")
    print(f"질문: {question}\n")

    result = qa_chain.invoke({"query": question})

    print(f"답변: {result['result']}\n")

    print("출처 문서:")
    for i, doc in enumerate(result['source_documents']):
        print(f"  [{i+1}] {doc.metadata['source']}: {doc.page_content[:80]}...")

    return result


if __name__ == "__main__":
    print("=" * 60)
    print("Step 1: 기본 RAG 개념")
    print("=" * 60)
    print()

    # 예제 1: RAG 없이
    print("예제 1: RAG 없이 LLM만 사용")
    print("-" * 60)
    without_rag_example()
    print("\n")

    # 예제 2: 간단한 RAG
    print("예제 2: 간단한 RAG 구현")
    print("-" * 60)
    simple_rag_example()
    print("\n")

    # 예제 3: 임베딩 유사도
    print("예제 3: 임베딩과 유사도 검색")
    print("-" * 60)
    embedding_similarity_example()
    print("\n")

    # 예제 4: 다양한 검색 방법
    print("예제 4: 다양한 검색 방법")
    print("-" * 60)
    retrieval_methods_example()
    print("\n")

    # 예제 5: 완전한 RAG 체인
    print("예제 5: 완전한 RAG 체인")
    print("-" * 60)
    rag_chain_example()
