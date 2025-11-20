"""
Step 6: 실전 GraphRAG 시스템
완전한 GraphRAG 시스템을 구축하고 실제 문제를 해결합니다.
"""

import os
from dotenv import load_dotenv
import networkx as nx

# .env 파일에서 환경변수 로드
load_dotenv()
from typing import List, Tuple
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from networkx.algorithms import community


class GraphRAGSystem:
    """
    완전한 GraphRAG 시스템
    """

    def __init__(self, api_key: str):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key)
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)
        self.graph = nx.Graph()
        self.vectorstore = None
        self.community_summaries = {}

    def index_documents(self, documents: List[str]):
        """문서 인덱싱"""
        print("=== 문서 인덱싱 중 ===\n")

        # 1. 벡터 저장소 구축
        docs = [Document(page_content=text) for text in documents]
        self.vectorstore = FAISS.from_documents(docs, self.embeddings)
        print(f"✓ {len(documents)}개 문서를 벡터 저장소에 추가\n")

        # 2. 그래프 구축 (간소화: 실제로는 NER + 관계 추출)
        self._build_graph(documents)
        print(f"✓ 그래프 구축 완료: {self.graph.number_of_nodes()}개 노드, {self.graph.number_of_edges()}개 엣지\n")

        # 3. 커뮤니티 감지
        self._detect_communities()
        print(f"✓ {len(self.community_summaries)}개 커뮤니티 발견 및 요약\n")

    def _build_graph(self, documents: List[str]):
        """그래프 구축 (간소화)"""
        # 실제로는 NER과 관계 추출을 수행
        # 여기서는 간단히 시뮬레이션
        entities = [
            ("LangChain", "LIBRARY"),
            ("Python", "LANGUAGE"),
            ("OpenAI", "COMPANY"),
            ("GPT-4", "MODEL"),
            ("RAG", "CONCEPT"),
            ("GraphRAG", "CONCEPT")
        ]

        for entity, etype in entities:
            self.graph.add_node(entity, type=etype)

        relationships = [
            ("LangChain", "Python"),
            ("LangChain", "OpenAI"),
            ("OpenAI", "GPT-4"),
            ("LangChain", "RAG"),
            ("GraphRAG", "RAG"),
            ("GraphRAG", "LangChain")
        ]

        self.graph.add_edges_from(relationships)

    def _detect_communities(self):
        """커뮤니티 감지 및 요약"""
        communities = community.greedy_modularity_communities(self.graph)

        for i, comm in enumerate(communities):
            comm_name = f"Community_{i}"
            nodes = sorted(comm)

            # 커뮤니티 요약 생성
            summary = f"이 커뮤니티는 {', '.join(nodes[:3])} 등을 포함합니다."

            self.community_summaries[comm_name] = {
                "nodes": nodes,
                "summary": summary
            }

    def search(self, query: str, search_type: str = "hybrid") -> str:
        """검색 및 답변 생성"""

        if search_type == "vector":
            return self._vector_search(query)
        elif search_type == "graph":
            return self._graph_search(query)
        else:  # hybrid
            return self._hybrid_search(query)

    def _vector_search(self, query: str) -> str:
        """벡터 검색만 사용"""
        results = self.vectorstore.similarity_search(query, k=3)
        context = "\n".join([doc.page_content for doc in results])

        prompt = ChatPromptTemplate.from_messages([
            ("system", "다음 문서를 바탕으로 답변하세요:\n\n{context}"),
            ("user", "{question}")
        ])

        chain = prompt | self.llm
        response = chain.invoke({"context": context, "question": query})

        return response.content

    def _graph_search(self, query: str) -> str:
        """그래프 검색만 사용"""
        # 커뮤니티 요약 활용
        context = "\n".join([
            f"{name}: {data['summary']}"
            for name, data in self.community_summaries.items()
        ])

        prompt = ChatPromptTemplate.from_messages([
            ("system", "다음 커뮤니티 정보를 바탕으로 답변하세요:\n\n{context}"),
            ("user", "{question}")
        ])

        chain = prompt | self.llm
        response = chain.invoke({"context": context, "question": query})

        return response.content

    def _hybrid_search(self, query: str) -> str:
        """하이브리드 검색"""
        # 벡터 검색
        vector_results = self.vectorstore.similarity_search(query, k=2)
        vector_context = "\n".join([doc.page_content for doc in vector_results])

        # 그래프 컨텍스트
        graph_context = []
        for comm_name, comm_data in self.community_summaries.items():
            graph_context.append(f"- {comm_data['summary']}")

        # 통합 컨텍스트
        context = f"""
문서 내용:
{vector_context}

그래프 구조:
{chr(10).join(graph_context)}
"""

        prompt = ChatPromptTemplate.from_messages([
            ("system", "다음 정보를 모두 활용하여 답변하세요:\n\n{context}"),
            ("user", "{question}")
        ])

        chain = prompt | self.llm
        response = chain.invoke({"context": context, "question": query})

        return response.content


def complete_example():
    """
    완전한 GraphRAG 예제
    """
    print("=" * 60)
    print("실전 GraphRAG 시스템")
    print("=" * 60)
    print()

    # 샘플 문서
    documents = [
        "LangChain은 Python으로 작성된 LLM 애플리케이션 개발 프레임워크입니다.",
        "OpenAI는 GPT-4를 비롯한 강력한 언어 모델을 제공합니다.",
        "RAG는 검색 증강 생성으로, 외부 지식을 활용하여 답변을 개선합니다.",
        "GraphRAG는 그래프 구조를 활용하는 고급 RAG 기법입니다.",
        "LangChain은 OpenAI API를 포함한 다양한 LLM을 지원합니다.",
    ]

    # GraphRAG 시스템 초기화
    system = GraphRAGSystem(api_key=os.getenv("GOOGLE_API_KEY"))

    # 문서 인덱싱
    system.index_documents(documents)

    # 테스트 질문들
    questions = [
        ("LangChain이 뭔가요?", "vector"),
        ("전체 시스템의 구조는?", "graph"),
        ("GraphRAG와 LangChain의 관계는?", "hybrid")
    ]

    for question, search_type in questions:
        print("=" * 60)
        print(f"질문: {question}")
        print(f"검색 유형: {search_type}")
        print("-" * 60)

        answer = system.search(question, search_type)
        print(f"\n답변:\n{answer}\n")


def comparison_example():
    """
    RAG vs GraphRAG 비교
    """
    print("=" * 60)
    print("RAG vs GraphRAG 비교")
    print("=" * 60)
    print()

    documents = [
        "Alice는 CompanyA에서 일합니다.",
        "CompanyA는 ProductX를 개발합니다.",
        "ProductX는 Python을 사용합니다.",
    ]

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=os.getenv("GOOGLE_API_KEY"))
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))

    # 기본 RAG
    print("=== 기본 RAG ===\n")
    vectorstore = FAISS.from_documents(
        [Document(page_content=text) for text in documents],
        embeddings
    )

    query = "Alice가 사용하는 프로그래밍 언어는?"
    results = vectorstore.similarity_search(query, k=2)

    print(f"질문: {query}\n")
    print("검색 결과:")
    for doc in results:
        print(f"  - {doc.page_content}")

    context = "\n".join([doc.page_content for doc in results])
    prompt = ChatPromptTemplate.from_messages([
        ("system", "다음 정보로 답변하세요:\n{context}"),
        ("user", "{question}")
    ])

    chain = prompt | llm
    response = chain.invoke({"context": context, "question": query})
    print(f"\n기본 RAG 답변:\n{response.content}\n")

    print("=" * 60)
    print()

    # GraphRAG
    print("=== GraphRAG ===\n")

    G = nx.DiGraph()
    G.add_edge("Alice", "CompanyA", relationship="WORKS_AT")
    G.add_edge("CompanyA", "ProductX", relationship="DEVELOPS")
    G.add_edge("ProductX", "Python", relationship="USES")

    print(f"질문: {query}\n")

    # 경로 찾기
    path = nx.shortest_path(G, "Alice", "Python")
    print(f"추론 경로: {' → '.join(path)}\n")

    # 경로 설명
    path_description = []
    for i in range(len(path) - 1):
        source, target = path[i], path[i+1]
        rel = G[source][target]["relationship"]
        path_description.append(f"{source} --[{rel}]--> {target}")

    graph_context = "\n".join(path_description)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "다음 관계를 바탕으로 추론하세요:\n{context}"),
        ("user", "{question}")
    ])

    chain = prompt | llm
    response = chain.invoke({"context": graph_context, "question": query})
    print(f"GraphRAG 답변:\n{response.content}\n")

    print("=" * 60)
    print("\n→ GraphRAG는 다중 홉 추론이 가능합니다!")


if __name__ == "__main__":
    # 예제 1: 완전한 시스템
    complete_example()
    print("\n\n")

    # 예제 2: 비교
    comparison_example()
