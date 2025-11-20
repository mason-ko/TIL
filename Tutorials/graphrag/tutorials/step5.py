"""
Step 5: 커뮤니티 감지와 요약
그래프를 클러스터로 나누고 각 커뮤니티를 요약합니다.
"""

import os
from dotenv import load_dotenv
import networkx as nx

# .env 파일에서 환경변수 로드
load_dotenv()
from networkx.algorithms import community
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate


def community_detection_example():
    """
    커뮤니티 감지로 그래프 클러스터링
    """
    print("=== 커뮤니티 감지 ===\n")

    # 지식 그래프 생성
    G = nx.Graph()

    # AI/ML 관련 노드
    ai_ml_nodes = ["AI", "ML", "DL", "NLP", "CV", "RL"]
    # 프로그래밍 언어 노드
    lang_nodes = ["Python", "Java", "C++", "JavaScript"]
    # 프레임워크 노드
    framework_nodes = ["TensorFlow", "PyTorch", "Scikit-learn"]

    G.add_nodes_from(ai_ml_nodes + lang_nodes + framework_nodes)

    # AI/ML 내부 연결
    G.add_edges_from([
        ("AI", "ML"), ("AI", "DL"), ("ML", "DL"),
        ("ML", "NLP"), ("DL", "NLP"), ("DL", "CV"),
        ("ML", "RL")
    ])

    # 언어 내부 연결
    G.add_edges_from([
        ("Python", "Java"), ("Java", "C++")
    ])

    # 프레임워크 내부 연결
    G.add_edges_from([
        ("TensorFlow", "PyTorch"), ("PyTorch", "Scikit-learn")
    ])

    # 크로스 연결
    G.add_edges_from([
        ("ML", "Python"), ("DL", "Python"),
        ("TensorFlow", "Python"), ("PyTorch", "Python"),
        ("Scikit-learn", "Python")
    ])

    # 커뮤니티 감지
    communities = community.greedy_modularity_communities(G)

    print(f"발견된 커뮤니티 수: {len(communities)}\n")

    for i, comm in enumerate(communities):
        print(f"커뮤니티 {i+1}:")
        print(f"  노드: {sorted(comm)}")
        print(f"  크기: {len(comm)}")
        print()

    return communities, G


def hierarchical_summarization_example():
    """
    계층적 요약: 커뮤니티별 요약 생성
    """
    print("=== 계층적 요약 ===\n")

    # 커뮤니티와 관련 문서
    communities_data = {
        "AI/ML 커뮤니티": [
            "인공지능은 기계가 인간의 지능을 모방하는 기술입니다.",
            "머신러닝은 데이터로부터 패턴을 학습합니다.",
            "딥러닝은 다층 신경망을 사용합니다.",
        ],
        "프로그래밍 언어 커뮤니티": [
            "Python은 간결하고 읽기 쉬운 언어입니다.",
            "Java는 플랫폼 독립적입니다.",
            "C++는 고성능 애플리케이션에 사용됩니다.",
        ]
    }

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))

    prompt = ChatPromptTemplate.from_messages([
        ("system", "다음 문서들을 2-3 문장으로 요약하세요."),
        ("user", "{documents}")
    ])

    community_summaries = {}

    for comm_name, docs in communities_data.items():
        print(f"커뮤니티: {comm_name}")
        print(f"문서 수: {len(docs)}\n")

        # 요약 생성
        chain = prompt | llm
        response = chain.invoke({
            "documents": "\n\n".join([f"{i+1}. {doc}" for i, doc in enumerate(docs)])
        })

        summary = response.content
        community_summaries[comm_name] = summary

        print(f"요약:\n{summary}\n")
        print("-" * 60)
        print()

    return community_summaries


def global_vs_local_search_example():
    """
    전역 검색 vs 지역 검색
    """
    print("=== 전역 검색 vs 지역 검색 ===\n")

    # 커뮤니티 요약 (전역 지식)
    community_summaries = {
        "AI 커뮤니티": "AI, ML, DL 등 인공지능 관련 개념들. 데이터 기반 학습과 패턴 인식이 핵심.",
        "언어 커뮤니티": "Python, Java, C++ 등 프로그래밍 언어들. 각각 다른 용도와 특성.",
        "프레임워크 커뮤니티": "TensorFlow, PyTorch 등 ML 프레임워크. Python 기반으로 ML 모델 구축."
    }

    # 상세 문서 (지역 지식)
    detailed_docs = {
        "딥러닝": "딥러닝은 다층 인공신경망을 사용하는 머신러닝 기법입니다. "
                 "이미지 인식, 자연어 처리 등에서 뛰어난 성능을 보입니다.",
        "Python": "Python은 1991년 Guido van Rossum이 만든 고급 프로그래밍 언어입니다. "
                 "간결한 문법과 풍부한 라이브러리가 특징입니다."
    }

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))

    # 1. 전역 질문 (커뮤니티 요약 사용)
    global_query = "AI와 프로그래밍 언어의 관계는?"
    print(f"전역 질문: {global_query}\n")

    global_context = "\n".join([f"- {name}: {summary}" for name, summary in community_summaries.items()])

    prompt = ChatPromptTemplate.from_messages([
        ("system", "다음 커뮤니티 요약을 바탕으로 답변하세요:\n\n{context}"),
        ("user", "{question}")
    ])

    chain = prompt | llm
    response = chain.invoke({"context": global_context, "question": global_query})

    print(f"전역 답변:\n{response.content}\n")
    print("-" * 60)
    print()

    # 2. 지역 질문 (상세 문서 사용)
    local_query = "딥러닝의 응용 분야는?"
    print(f"지역 질문: {local_query}\n")

    local_context = detailed_docs["딥러닝"]

    response = chain.invoke({"context": local_context, "question": local_query})

    print(f"지역 답변:\n{response.content}\n")

    return community_summaries


def map_reduce_over_communities_example():
    """
    커뮤니티별 Map-Reduce
    """
    print("=== 커뮤니티별 Map-Reduce ===\n")

    # 여러 커뮤니티의 문서들
    communities = {
        "커뮤니티 A": [
            "Python은 데이터 과학에 널리 사용됩니다.",
            "Python은 배우기 쉽습니다.",
        ],
        "커뮤니티 B": [
            "머신러닝은 예측 모델을 만듭니다.",
            "머신러닝은 데이터가 많을수록 좋습니다.",
        ]
    }

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))

    # Map: 각 커뮤니티 요약
    print("=== Map 단계 ===\n")
    summaries = []

    for comm_name, docs in communities.items():
        prompt = ChatPromptTemplate.from_messages([
            ("system", "다음 문서들을 한 문장으로 요약하세요."),
            ("user", "{documents}")
        ])

        chain = prompt | llm
        response = chain.invoke({"documents": "\n".join(docs)})

        summary = response.content
        summaries.append(summary)

        print(f"{comm_name} 요약: {summary}")

    # Reduce: 전체 요약
    print("\n=== Reduce 단계 ===\n")

    reduce_prompt = ChatPromptTemplate.from_messages([
        ("system", "다음 커뮤니티 요약들을 하나로 통합하세요."),
        ("user", "{summaries}")
    ])

    chain = reduce_prompt | llm
    final_summary = chain.invoke({
        "summaries": "\n".join([f"{i+1}. {s}" for i, s in enumerate(summaries)])
    })

    print(f"최종 요약:\n{final_summary.content}")

    return final_summary


if __name__ == "__main__":
    print("=" * 60)
    print("Step 5: 커뮤니티 감지와 요약")
    print("=" * 60)
    print()

    # 예제 1: 커뮤니티 감지
    print("예제 1: 커뮤니티 감지")
    print("-" * 60)
    community_detection_example()
    print("\n")

    # 예제 2: 계층적 요약
    print("예제 2: 계층적 요약")
    print("-" * 60)
    hierarchical_summarization_example()
    print("\n")

    # 예제 3: 전역 vs 지역 검색
    print("예제 3: 전역 vs 지역 검색")
    print("-" * 60)
    global_vs_local_search_example()
    print("\n")

    # 예제 4: Map-Reduce
    print("예제 4: 커뮤니티별 Map-Reduce")
    print("-" * 60)
    map_reduce_over_communities_example()
