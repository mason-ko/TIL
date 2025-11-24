"""
Advanced RAG Step 6: Self-Query (메타데이터 필터링)

pip install chromadb
"""

import chromadb
from typing import Dict
import re


def parse_self_query(query: str) -> Dict:
    """자연어 쿼리에서 필터 추출 (간단 버전)"""
    filters = {}
    search_query = query

    # 연도 추출
    year_match = re.search(r'(\d{4})년 이후', query)
    if year_match:
        filters['year'] = {"$gte": int(year_match.group(1))}
        search_query = search_query.replace(year_match.group(0), "")

    # 카테고리 추출
    categories = ['tech', 'business', 'science']
    for cat in categories:
        if cat in query.lower():
            filters['category'] = cat
            search_query = search_query.replace(cat, "")

    return {
        "search_query": search_query.strip(),
        "filters": filters
    }


def main():
    print("=== Self-Query Retrieval ===\n")

    # ChromaDB
    client = chromadb.Client()
    try:
        client.delete_collection("docs")
    except:
        pass

    collection = client.create_collection("docs")

    # 메타데이터가 있는 문서
    docs = [
        "LangGraph는 AI 워크플로우 라이브러리입니다",
        "Vector Database는 임베딩을 저장합니다",
        "비즈니스 전략 수립 가이드",
        "Python 프로그래밍 기초",
        "머신러닝 알고리즘 소개"
    ]

    metadatas = [
        {"year": 2024, "category": "tech", "author": "김개발"},
        {"year": 2024, "category": "tech", "author": "이데이터"},
        {"year": 2022, "category": "business", "author": "박경영"},
        {"year": 2023, "category": "tech", "author": "최코딩"},
        {"year": 2023, "category": "science", "author": "정연구"}
    ]

    collection.add(
        documents=docs,
        metadatas=metadatas,
        ids=[f"doc{i}" for i in range(len(docs))]
    )

    print(f"✅ {len(docs)}개 문서 저장\n")
    print("="*60)

    # Self-Query
    natural_query = "2023년 이후 tech 카테고리 문서"
    print(f"🗣️ 자연어 질문: {natural_query}\n")

    # 파싱
    parsed = parse_self_query(natural_query)

    print("🔧 자동 변환:")
    print(f"   검색어: {parsed['search_query']}")
    print(f"   필터: {parsed['filters']}\n")

    # 검색 (필터 적용)
    filters = parsed['filters']

    # ChromaDB where 조건
    where_clause = {}
    if 'year' in filters and '$gte' in filters['year']:
        where_clause['year'] = {"$gte": filters['year']['$gte']}
    if 'category' in filters:
        where_clause['category'] = filters['category']

    results = collection.query(
        query_texts=[parsed['search_query'] or natural_query],
        n_results=5,
        where=where_clause if where_clause else None
    )

    print("="*60)
    print("📄 검색 결과:\n")

    for i, (doc, meta) in enumerate(zip(
        results['documents'][0],
        results['metadatas'][0]
    ), 1):
        print(f"   {i}. [{meta['year']}] [{meta['category']}] {doc}")
        print(f"      작성자: {meta['author']}\n")

    print("💡 핵심: 자연어 → 구조화된 필터 자동 변환")
    print("\n🎉 Advanced RAG 튜토리얼 완료!")
    print("\n📚 다음 학습:")
    print("   - Multi-Agent: 복잡한 작업 자동화")
    print("   - Fine-tuning: 모델 성능 향상")
    print("   - MLOps: 프로덕션 배포\n")


if __name__ == "__main__":
    main()
