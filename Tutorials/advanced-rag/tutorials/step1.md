# Step 1: Hybrid Search - 키워드 + 벡터 검색

## 목표

- 기본 RAG의 한계 이해
- Hybrid Search 구현
- BM25 + 벡터 검색 결합
- 검색 정확도 향상

## 기본 RAG의 문제

```python
# 벡터 검색만 사용
query = "Python 설치 방법"
→ "Python installation guide" ✅
→ "파이썬 설치하기" ❌ (다른 단어)

# 키워드가 정확히 일치하지 않으면 놓침
```

## Hybrid Search란?

**키워드 검색(BM25) + 벡터 검색을 결합**하여 둘의 장점을 취합니다.

```python
BM25 (키워드):
- "Python" 단어 있음 → 점수 높음
- 정확한 매칭

Vector (의미):
- "파이썬", "설치" 의미 유사 → 점수 높음
- 유연한 매칭

Hybrid = BM25 점수 + Vector 점수
```

## BM25란?

**Best Matching 25** - 키워드 빈도 기반 검색 알고리즘

```python
from rank_bm25 import BM25Okapi

documents = ["Python 설치", "JavaScript 튜토리얼"]
tokenized = [doc.split() for doc in documents]

bm25 = BM25Okapi(tokenized)
scores = bm25.get_scores("Python".split())
# → [높음, 낮음]
```

## 실습 예제

### 기본 RAG vs Hybrid Search 비교

```python
# 1. 벡터만 (놓침)
query = "파이썬 다운로드"
vector_results = vectordb.search(query)
# "Python install" (다른 단어라 낮은 점수)

# 2. Hybrid (찾음)
hybrid_results = hybrid_search(query)
# BM25: "파이썬" 키워드 매칭 ✅
# Vector: "다운로드" ≈ "install" ✅
```

## 핵심 요약

- **Hybrid = BM25 + Vector**
- **정확도 30% 향상**
- **키워드 + 의미 모두 활용**

---

**다음**: step2 - Reranking으로 정확도 추가 향상
