"""
Step 3: 그래프 구조 구축
문서에서 엔티티와 관계를 추출하여 지식 그래프를 만듭니다.
"""

import os
from dotenv import load_dotenv
from typing import List, Dict

# .env 파일에서 환경변수 로드
load_dotenv()
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
import networkx as nx
import matplotlib.pyplot as plt


class Entity(BaseModel):
    """엔티티 정의"""
    name: str = Field(description="엔티티 이름")
    type: str = Field(description="엔티티 타입 (PERSON, ORGANIZATION, CONCEPT 등)")
    description: str = Field(description="엔티티 설명")


class Relationship(BaseModel):
    """관계 정의"""
    source: str = Field(description="출발 엔티티")
    target: str = Field(description="도착 엔티티")
    relationship: str = Field(description="관계 유형")
    description: str = Field(description="관계 설명")


class KnowledgeGraph(BaseModel):
    """지식 그래프"""
    entities: List[Entity] = Field(description="엔티티 목록")
    relationships: List[Relationship] = Field(description="관계 목록")


def extract_entities_example():
    """
    텍스트에서 엔티티 추출
    """
    text = """
    LangChain은 Harrison Chase가 만든 LLM 애플리케이션 개발 프레임워크입니다.
    이 프레임워크는 OpenAI, Anthropic 등 다양한 LLM 제공자를 지원합니다.
    LangGraph는 LangChain의 확장으로, 복잡한 에이전트 워크플로우를 구축할 수 있습니다.
    """

    print("=== 엔티티 추출 ===\n")
    print(f"원본 텍스트:\n{text}\n")

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))

    prompt = ChatPromptTemplate.from_messages([
        ("system", "당신은 텍스트에서 엔티티를 추출하는 전문가입니다. "
                   "PERSON(사람), ORGANIZATION(조직), PRODUCT(제품), CONCEPT(개념) 타입으로 분류하세요."),
        ("user", "다음 텍스트에서 중요한 엔티티를 추출하세요:\n\n{text}")
    ])

    # 구조화된 출력
    structured_llm = llm.with_structured_output(Entity)

    # 간단히 하기 위해 수동으로 처리
    entities_text = """
엔티티:
1. LangChain - PRODUCT - LLM 애플리케이션 개발 프레임워크
2. Harrison Chase - PERSON - LangChain 창시자
3. OpenAI - ORGANIZATION - LLM 제공 회사
4. Anthropic - ORGANIZATION - LLM 제공 회사
5. LangGraph - PRODUCT - 에이전트 워크플로우 구축 도구
"""

    print("추출된 엔티티:")
    print(entities_text)

    entities = [
        Entity(name="LangChain", type="PRODUCT", description="LLM 애플리케이션 개발 프레임워크"),
        Entity(name="Harrison Chase", type="PERSON", description="LangChain 창시자"),
        Entity(name="OpenAI", type="ORGANIZATION", description="LLM 제공 회사"),
        Entity(name="Anthropic", type="ORGANIZATION", description="LLM 제공 회사"),
        Entity(name="LangGraph", type="PRODUCT", description="에이전트 워크플로우 구축 도구"),
    ]

    for entity in entities:
        print(f"  - {entity.name} ({entity.type}): {entity.description}")

    return entities


def extract_relationships_example():
    """
    텍스트에서 관계 추출
    """
    text = """
    LangChain은 Harrison Chase가 만들었습니다.
    LangChain은 OpenAI를 지원합니다.
    LangGraph는 LangChain의 확장입니다.
    """

    print("=== 관계 추출 ===\n")
    print(f"원본 텍스트:\n{text}\n")

    relationships = [
        Relationship(
            source="Harrison Chase",
            target="LangChain",
            relationship="CREATED",
            description="창시함"
        ),
        Relationship(
            source="LangChain",
            target="OpenAI",
            relationship="SUPPORTS",
            description="통합 지원"
        ),
        Relationship(
            source="LangGraph",
            target="LangChain",
            relationship="EXTENDS",
            description="확장"
        ),
    ]

    print("추출된 관계:")
    for rel in relationships:
        print(f"  - {rel.source} --[{rel.relationship}]--> {rel.target}")
        print(f"    설명: {rel.description}")

    return relationships


def build_knowledge_graph_example():
    """
    지식 그래프 구축
    """
    print("=== 지식 그래프 구축 ===\n")

    # 여러 문서에서 추출한 엔티티와 관계
    entities = [
        Entity(name="Python", type="LANGUAGE", description="프로그래밍 언어"),
        Entity(name="LangChain", type="LIBRARY", description="LLM 프레임워크"),
        Entity(name="OpenAI", type="COMPANY", description="AI 회사"),
        Entity(name="GPT-4", type="MODEL", description="LLM 모델"),
        Entity(name="RAG", type="CONCEPT", description="검색 증강 생성"),
    ]

    relationships = [
        Relationship(source="LangChain", target="Python", relationship="WRITTEN_IN", description="Python으로 작성"),
        Relationship(source="LangChain", target="OpenAI", relationship="INTEGRATES", description="통합"),
        Relationship(source="OpenAI", target="GPT-4", relationship="DEVELOPS", description="개발"),
        Relationship(source="LangChain", target="RAG", relationship="IMPLEMENTS", description="구현"),
        Relationship(source="RAG", target="GPT-4", relationship="USES", description="사용"),
    ]

    # NetworkX 그래프 생성
    G = nx.DiGraph()

    # 노드 추가 (엔티티)
    for entity in entities:
        G.add_node(
            entity.name,
            type=entity.type,
            description=entity.description
        )

    # 엣지 추가 (관계)
    for rel in relationships:
        G.add_edge(
            rel.source,
            rel.target,
            relationship=rel.relationship,
            description=rel.description
        )

    print(f"노드 수: {G.number_of_nodes()}")
    print(f"엣지 수: {G.number_of_edges()}\n")

    print("그래프 구조:")
    for edge in G.edges(data=True):
        source, target, data = edge
        print(f"  {source} --[{data['relationship']}]--> {target}")

    # 시각화
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, k=2, iterations=50)

    # 노드 그리기
    nx.draw_networkx_nodes(G, pos, node_size=3000, node_color='lightblue', alpha=0.9)

    # 엣지 그리기
    nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, arrowsize=20)

    # 레이블 그리기
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')

    # 엣지 레이블
    edge_labels = nx.get_edge_attributes(G, 'relationship')
    nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=8)

    plt.title("Knowledge Graph", fontsize=16)
    plt.axis('off')
    plt.tight_layout()

    # 저장
    output_path = "knowledge_graph.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\n그래프 이미지 저장: {output_path}")

    return G


def graph_queries_example():
    """
    그래프 쿼리 예제
    """
    # 그래프 구축 (위 예제와 동일)
    G = nx.DiGraph()

    entities = [
        ("Python", {"type": "LANGUAGE"}),
        ("LangChain", {"type": "LIBRARY"}),
        ("OpenAI", {"type": "COMPANY"}),
        ("GPT-4", {"type": "MODEL"}),
    ]

    for name, attrs in entities:
        G.add_node(name, **attrs)

    G.add_edge("LangChain", "Python", relationship="WRITTEN_IN")
    G.add_edge("LangChain", "OpenAI", relationship="INTEGRATES")
    G.add_edge("OpenAI", "GPT-4", relationship="DEVELOPS")

    print("=== 그래프 쿼리 ===\n")

    # 1. 특정 노드의 이웃 찾기
    print("1. LangChain의 연결된 노드:")
    neighbors = list(G.neighbors("LangChain"))
    for neighbor in neighbors:
        rel = G.edges["LangChain", neighbor]["relationship"]
        print(f"   - {neighbor} ({rel})")
    print()

    # 2. 경로 찾기
    print("2. LangChain에서 GPT-4로 가는 경로:")
    try:
        path = nx.shortest_path(G, "LangChain", "GPT-4")
        print(f"   경로: {' -> '.join(path)}")
    except nx.NetworkXNoPath:
        print("   경로 없음")
    print()

    # 3. 중요 노드 찾기 (PageRank)
    print("3. 중요한 노드 (PageRank):")
    pagerank = nx.pagerank(G)
    sorted_nodes = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)
    for node, score in sorted_nodes:
        print(f"   - {node}: {score:.4f}")

    return G


def community_detection_example():
    """
    커뮤니티 감지 (그룹화)
    """
    # 더 큰 그래프
    G = nx.Graph()  # 무향 그래프

    nodes = ["AI", "ML", "DL", "NLP", "CV", "Python", "Java", "C++"]
    G.add_nodes_from(nodes)

    edges = [
        ("AI", "ML"), ("AI", "DL"), ("AI", "NLP"), ("AI", "CV"),
        ("ML", "DL"), ("ML", "NLP"),
        ("DL", "NLP"), ("DL", "CV"),
        ("Python", "Java"), ("Python", "C++"),
        ("ML", "Python"), ("DL", "Python")
    ]
    G.add_edges_from(edges)

    print("=== 커뮤니티 감지 ===\n")

    # Greedy modularity communities
    from networkx.algorithms import community
    communities = community.greedy_modularity_communities(G)

    print(f"발견된 커뮤니티 수: {len(communities)}\n")

    for i, comm in enumerate(communities):
        print(f"커뮤니티 {i+1}: {sorted(comm)}")

    return communities


if __name__ == "__main__":
    print("=" * 60)
    print("Step 3: 그래프 구조 구축")
    print("=" * 60)
    print()

    # 예제 1: 엔티티 추출
    print("예제 1: 엔티티 추출")
    print("-" * 60)
    extract_entities_example()
    print("\n")

    # 예제 2: 관계 추출
    print("예제 2: 관계 추출")
    print("-" * 60)
    extract_relationships_example()
    print("\n")

    # 예제 3: 지식 그래프 구축
    print("예제 3: 지식 그래프 구축")
    print("-" * 60)
    build_knowledge_graph_example()
    print("\n")

    # 예제 4: 그래프 쿼리
    print("예제 4: 그래프 쿼리")
    print("-" * 60)
    graph_queries_example()
    print("\n")

    # 예제 5: 커뮤니티 감지
    print("예제 5: 커뮤니티 감지")
    print("-" * 60)
    community_detection_example()
