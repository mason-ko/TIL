# Step 3: Query Rewriting (쿼리 재작성)

## 목표

- Multi-query로 검색 정확도 향상
- HyDE (가상 답변 생성) 기법
- Query Expansion

## 왜 Query Rewriting?

```python
# 문제
사용자: "강아지 밥"
→ Vector 검색 실패 ("사료"라는 단어가 문서에 있지만 매칭 안됨)

# 해결: 쿼리 재작성
"강아지 밥" → ["강아지 사료", "반려견 먹이", "개 영양식"]
→ 검색 성공률 3배 증가
```

## 1. Multi-Query

```python
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_community.llms import Ollama

llm = Ollama(model="llama3")

retriever = MultiQueryRetriever.from_llm(
    retriever=vectorstore.as_retriever(),
    llm=llm
)

# 자동으로 여러 버전 생성 및 검색
docs = retriever.get_relevant_documents("Python 성능")

# 내부적으로:
# → "Python은 빠른가?"
# → "Python 속도 특징"
# → "Python 성능 최적화"
```

## 2. HyDE (Hypothetical Document Embeddings)

가상 답변을 먼저 생성하고, 그것으로 검색

```python
def hyde_retrieval(query, llm, vectorstore):
    # 1. 가상 답변 생성
    hypothetical_doc = llm.invoke(f"{query}에 대한 답변을 작성하세요")

    # 2. 가상 답변으로 검색
    docs = vectorstore.similarity_search(hypothetical_doc)

    return docs
```

## 3. Query Expansion

```python
def expand_query(query, llm):
    prompt = f"""다음 질문을 3가지 다른 방식으로 표현하세요:

질문: {query}

버전 1:
버전 2:
버전 3:"""

    expanded = llm.invoke(prompt)
    queries = parse_queries(expanded)

    return queries
```

## 실전 예제

```python
# 원본 쿼리
original = "LLM 비용 절감"

# Multi-query
queries = [
    "LLM API 비용을 줄이는 방법",
    "로컬 LLM 사용으로 비용 절감",
    "토큰 사용량 최적화 전략"
]

# 각 쿼리로 검색 → 결과 병합
all_results = []
for q in queries:
    results = vectorstore.similarity_search(q, k=2)
    all_results.extend(results)

# 중복 제거
unique_results = deduplicate(all_results)
```

---

**핵심**: 쿼리를 다양하게 재작성하여 검색 정확도 향상
