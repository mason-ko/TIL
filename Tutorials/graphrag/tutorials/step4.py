"""
Step 4: GraphRAG 기본
그래프를 활용한 검색 증강 생성을 구현합니다.
"""

import os
from dotenv import load_dotenv
import networkx as nx

# .env 파일에서 환경변수 로드
load_dotenv()
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate


def hybrid_search_example():
    """
    하이브리드 검색: 벡터 + 그래프
    """
    print("=== 하이브리드 GraphRAG 검색 ===\n")

    # 1. 벡터 저장소 (기존 RAG)
    documents = [
        Document(page_content="LangChain은 Python으로 작성된 LLM 프레임워크입니다.", metadata={"entity": "LangChain"}),
        Document(page_content="OpenAI는 GPT-4를 개발했습니다.", metadata={"entity": "OpenAI"}),
        Document(page_content="LangGraph는 LangChain의 확장입니다.", metadata={"entity": "LangGraph"}),
    ]

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=os.getenv("GOOGLE_API_KEY"))
    vectorstore = FAISS.from_documents(documents, embeddings)

    # 2. 지식 그래프
    G = nx.DiGraph()
    G.add_edge("LangChain", "Python", relationship="WRITTEN_IN")
    G.add_edge("LangGraph", "LangChain", relationship="EXTENDS")
    G.add_edge("OpenAI", "GPT-4", relationship="DEVELOPS")

    # 질문
    query = "LangGraph와 Python의 관계는?"

    # Step 1: 벡터 검색으로 관련 엔티티 찾기
    results = vectorstore.similarity_search(query, k=2)
    print("벡터 검색 결과:")
    for doc in results:
        print(f"  - {doc.metadata['entity']}: {doc.page_content}")
    print()

    # Step 2: 그래프에서 관계 탐색
    print("그래프 탐색:")
    entity = "LangGraph"
    if entity in G:
        # 1홉 이웃
        neighbors = list(G.neighbors(entity))
        print(f"  {entity}의 직접 연결: {neighbors}")

        # 2홉 확장
        for neighbor in neighbors:
            if neighbor in G:
                second_hop = list(G.neighbors(neighbor))
                print(f"    {neighbor}의 연결: {second_hop}")

    # Step 3: 통합된 컨텍스트로 답변 생성
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))

    context = f"""
벡터 검색 결과:
{chr(10).join([doc.page_content for doc in results])}

그래프 관계:
- LangGraph → LangChain (EXTENDS)
- LangChain → Python (WRITTEN_IN)
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", "다음 정보를 바탕으로 질문에 답변하세요:\n\n{context}"),
        ("user", "{question}")
    ])

    chain = prompt | llm
    response = chain.invoke({"context": context, "question": query})

    print(f"\n최종 답변:\n{response.content}")

    return response


def multi_hop_reasoning_example():
    """
    다중 홉 추론
    """
    print("=== 다중 홉 추론 ===\n")

    # 복잡한 지식 그래프
    G = nx.DiGraph()

    # 엔티티와 관계
    edges = [
        ("Alice", "CompanyA", "WORKS_AT"),
        ("CompanyA", "ProductX", "DEVELOPS"),
        ("ProductX", "Python", "USES"),
        ("Bob", "CompanyA", "WORKS_AT"),
        ("CompanyA", "San Francisco", "LOCATED_IN"),
    ]

    for source, target, rel in edges:
        G.add_edge(source, target, relationship=rel)

    # 질문: "Alice가 사용하는 프로그래밍 언어는?"
    # 경로: Alice → CompanyA → ProductX → Python

    query = "Alice가 사용하는 프로그래밍 언어는?"
    print(f"질문: {query}\n")

    # 경로 찾기
    try:
        path = nx.shortest_path(G, "Alice", "Python")
        print(f"추론 경로: {' → '.join(path)}\n")

        # 경로 설명
        print("추론 과정:")
        for i in range(len(path) - 1):
            source, target = path[i], path[i+1]
            rel = G[source][target]["relationship"]
            print(f"  {i+1}. {source} --[{rel}]--> {target}")

    except nx.NetworkXNoPath:
        print("경로를 찾을 수 없습니다.")

    return G


def graph_rag_pipeline_example():
    """
    완전한 GraphRAG 파이프라인
    """
    print("=== GraphRAG 파이프라인 ===\n")

    # 샘플 문서
    docs_text = [
        "LangChain은 Harrison Chase가 개발한 LLM 프레임워크입니다.",
        "LangChain은 Python으로 작성되었습니다.",
        "OpenAI는 GPT-4 모델을 제공합니다.",
        "LangChain은 OpenAI API를 지원합니다.",
    ]

    # 1. 엔티티/관계 추출 (간소화)
    G = nx.DiGraph()
    G.add_edge("Harrison Chase", "LangChain", relationship="CREATED")
    G.add_edge("LangChain", "Python", relationship="WRITTEN_IN")
    G.add_edge("OpenAI", "GPT-4", relationship="PROVIDES")
    G.add_edge("LangChain", "OpenAI", relationship="SUPPORTS")

    # 2. 벡터 저장소
    documents = [Document(page_content=text) for text in docs_text]
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=os.getenv("GOOGLE_API_KEY"))
    vectorstore = FAISS.from_documents(documents, embeddings)

    # 3. 검색 함수
    def graphrag_search(query: str, k: int = 2, max_hops: int = 2):
        # 벡터 검색
        vector_results = vectorstore.similarity_search(query, k=k)

        # 그래프 확장
        graph_context = []
        for doc in vector_results:
            # 문서에서 엔티티 추출 (간소화)
            for node in G.nodes():
                if node in doc.page_content:
                    # 이웃 노드 가져오기
                    neighbors = list(G.neighbors(node))
                    for neighbor in neighbors:
                        rel = G[node][neighbor]["relationship"]
                        graph_context.append(f"{node} --[{rel}]--> {neighbor}")

        return vector_results, graph_context

    # 4. 질문
    query = "LangChain을 만든 사람은?"
    print(f"질문: {query}\n")

    vector_results, graph_context = graphrag_search(query)

    print("검색 결과:")
    print("\n벡터 검색:")
    for doc in vector_results:
        print(f"  - {doc.page_content}")

    print("\n그래프 컨텍스트:")
    for ctx in graph_context:
        print(f"  - {ctx}")

    # 5. LLM 답변 생성
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))

    context = f"""
문서:
{chr(10).join([doc.page_content for doc in vector_results])}

관계:
{chr(10).join(graph_context)}
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", "다음 정보를 바탕으로 정확하게 답변하세요:\n\n{context}"),
        ("user", "{question}")
    ])

    chain = prompt | llm
    response = chain.invoke({"context": context, "question": query})

    print(f"\n답변: {response.content}")

    return response


if __name__ == "__main__":
    print("=" * 60)
    print("Step 4: GraphRAG 기본")
    print("=" * 60)
    print()

    # 예제 1: 하이브리드 검색
    print("예제 1: 하이브리드 검색")
    print("-" * 60)
    hybrid_search_example()
    print("\n")

    # 예제 2: 다중 홉 추론
    print("예제 2: 다중 홉 추론")
    print("-" * 60)
    multi_hop_reasoning_example()
    print("\n")

    # 예제 3: 완전한 파이프라인
    print("예제 3: GraphRAG 파이프라인")
    print("-" * 60)
    graph_rag_pipeline_example()
