# Step 6: Self-Query (메타데이터 필터링)

## 목표

- 자연어 쿼리에서 메타데이터 필터 자동 추출
- 구조화된 검색
- 정확도 향상

## 개념

```python
# 사용자 질문
"2023년 이후에 작성된 Python 관련 문서를 찾아줘"

# Self-Query가 분석
→ 검색어: "Python"
→ 필터: {"year": {"$gte": 2023}, "topic": "Python"}
```

## 구현

```python
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo

# 메타데이터 스키마 정의
metadata_field_info = [
    AttributeInfo(
        name="year",
        description="문서 작성 연도",
        type="integer"
    ),
    AttributeInfo(
        name="category",
        description="문서 카테고리 (tech, business, etc)",
        type="string"
    ),
    AttributeInfo(
        name="author",
        description="작성자",
        type="string"
    )
]

# Self-Query Retriever
retriever = SelfQueryRetriever.from_llm(
    llm=llm,
    vectorstore=vectorstore,
    document_contents="기술 문서",
    metadata_field_info=metadata_field_info
)

# 자연어 검색
docs = retriever.get_relevant_documents(
    "2023년 이후 김철수가 쓴 AI 관련 글"
)
# → 자동으로 필터 생성 및 적용
```

## 예제

```python
# 문서 with 메타데이터
docs = [
    {
        "content": "LangGraph 튜토리얼",
        "metadata": {
            "year": 2024,
            "category": "tech",
            "author": "김개발"
        }
    },
    {
        "content": "비즈니스 전략",
        "metadata": {
            "year": 2022,
            "category": "business",
            "author": "이경영"
        }
    }
]

# Self-Query
query = "2023년 이후 tech 카테고리 문서"

# 자동 변환:
# → search_query: "문서"
# → filter: {"year": {"$gte": 2023}, "category": "tech"}
```

## 장점

1. **자연어 인터페이스**: 사용자가 복잡한 필터 작성 불필요
2. **정확한 검색**: 메타데이터로 범위 제한
3. **유연성**: 다양한 필터 조합

## 실무 활용

```python
# 고객 지원 시스템
"최근 6개월 이내 결제 관련 FAQ"
→ filter: {
    "date": {"$gte": "2024-06-01"},
    "category": "payment",
    "type": "faq"
}

# 법률 문서 검색
"2020년 이후 개정된 노동법 관련 판례"
→ filter: {
    "year": {"$gte": 2020},
    "category": "labor_law",
    "type": "precedent"
}
```

---

**핵심**: 자연어 → 구조화된 필터 자동 변환
**Advanced RAG 튜토리얼 완료!** 🎉
