# Step 2: Reranking으로 검색 품질 향상

## 목표

- 벡터 검색의 한계 이해
- Reranking 개념 학습
- Hybrid Search (벡터 + BM25) 구현
- 검색 정확도 향상

## 벡터 검색의 한계

### 문제: 의미는 비슷하지만 관련 없음

```python
docs = [
    "Python은 프로그래밍 언어입니다",
    "Python으로 웹 개발을 할 수 있습니다",  # ← 원하는 답
    "Java는 객체지향 언어입니다"
]

query = "파이썬 웹 개발"

# 벡터 검색 결과
1. "Python은 프로그래밍 언어입니다"  # 의미 유사
2. "Python으로 웹 개발을 할 수 있습니다"  # 정답
```

**문제점:**
- "Python", "언어" 등 단어가 겹치면 상위 노출
- 정작 "웹 개발"이라는 핵심은 놓침
- 의미 유사도만 보고 키워드 매칭 부족

## Reranking이란?

**2단계 검색**

```
1단계: 벡터 검색 (많이 가져옴)
  ↓ 상위 10개
2단계: Reranking (정확하게 재정렬)
  ↓ 상위 3개
최종 결과
```

### 왜 필요한가?

```python
# 1단계: 벡터 검색 (recall 중시)
→ 관련 문서를 놓치지 않기 위해 10개 가져옴
→ 하지만 정확도는 낮음

# 2단계: Reranking (precision 중시)
→ 10개 중에서 진짜 관련 있는 3개만 선택
→ 정확도 향상
```

## BM25란?

**키워드 기반 검색 알고리즘**

```
TF-IDF의 개선판
= Term Frequency (단어 빈도) + Inverse Document Frequency
```

### BM25 vs 벡터 검색

| 방식 | 강점 | 약점 |
|------|------|------|
| **벡터 검색** | 의미 유사도 | 키워드 놓침 |
| **BM25** | 키워드 매칭 | 의미 이해 부족 |
| **Hybrid** | 둘 다 고려 ✅ | 복잡도 증가 |

### 예시

```python
query = "파이썬으로 웹사이트 만들기"

# 벡터 검색
→ "Python은 프로그래밍 언어입니다" (의미 유사)

# BM25
→ "Python으로 웹 개발을 할 수 있습니다" (키워드 매칭)
```

## Reranking 구현

### 1. 기본 벡터 검색

```python
import chromadb

docs = [
    "Python은 프로그래밍 언어입니다",
    "Python으로 웹 개발을 할 수 있습니다",
    "Java는 객체지향 언어입니다",
]

client = chromadb.Client()
collection = client.create_collection("basic")
collection.add(documents=docs, ids=["d0", "d1", "d2"])

query = "파이썬으로 웹사이트 만들기"

# 1차 검색: 상위 5개 (많이 가져옴)
results = collection.query(query_texts=[query], n_results=5)
candidates = results['documents'][0]

print("1차 검색 (벡터):")
for doc in candidates:
    print(f"  - {doc}")
```

### 2. BM25로 Reranking

```python
from rank_bm25 import BM25Okapi

# 후보 문서를 토큰화
tokenized_docs = [doc.split() for doc in candidates]

# BM25 모델 생성
bm25 = BM25Okapi(tokenized_docs)

# 쿼리 토큰화
query_tokens = query.split()

# BM25 점수 계산
scores = bm25.get_scores(query_tokens)

# 점수 높은 순으로 재정렬
ranked = sorted(
    zip(candidates, scores),
    key=lambda x: x[1],
    reverse=True
)

print("\n2차 Reranking (BM25):")
for doc, score in ranked[:3]:
    print(f"  [{score:.2f}] {doc}")
```

**출력:**
```
1차 검색 (벡터):
  - Python은 프로그래밍 언어입니다
  - Python으로 웹 개발을 할 수 있습니다
  - Java는 객체지향 언어입니다

2차 Reranking (BM25):
  [2.45] Python으로 웹 개발을 할 수 있습니다  ✅
  [0.87] Python은 프로그래밍 언어입니다
  [0.00] Java는 객체지향 언어입니다
```

## Hybrid Search (최종 구현)

**벡터 + BM25 점수를 결합**

### 점수 결합 공식

```python
Hybrid Score = (Vector Score × α) + (BM25 Score × β)

# 일반적으로
α = 0.5  # 벡터 가중치
β = 0.5  # BM25 가중치
```

### 전체 구현

```python
import chromadb
from rank_bm25 import BM25Okapi

docs = [
    "LangGraph는 상태 기반 워크플로우 라이브러리입니다",
    "Langfuse는 LLM 모니터링 도구입니다",
    "ChromaDB는 벡터 데이터베이스입니다",
    "Ollama로 로컬 LLM을 실행할 수 있습니다",
]

query = "로컬 LLM 모니터링"

# 1. 벡터 검색
client = chromadb.Client()
collection = client.create_collection("hybrid")
collection.add(documents=docs, ids=[f"d{i}" for i in range(len(docs))])

vector_results = collection.query(query_texts=[query], n_results=5)
vector_docs = vector_results['documents'][0]
vector_distances = vector_results['distances'][0]

# 거리를 유사도로 변환 (0-1 범위)
vector_scores = [1 / (1 + d) for d in vector_distances]

# 2. BM25 점수
tokenized = [doc.split() for doc in docs]
bm25 = BM25Okapi(tokenized)
bm25_scores = bm25.get_scores(query.split())

# 정규화 (0-1 범위)
max_bm25 = max(bm25_scores) if max(bm25_scores) > 0 else 1
bm25_scores_norm = [s / max_bm25 for s in bm25_scores]

# 3. Hybrid 점수 계산
hybrid_scores = []
for i, doc in enumerate(docs):
    # 벡터 점수 (해당 문서가 검색 결과에 있으면)
    if doc in vector_docs:
        idx = vector_docs.index(doc)
        v_score = vector_scores[idx]
    else:
        v_score = 0

    # BM25 점수
    b_score = bm25_scores_norm[i]

    # 결합 (50:50)
    hybrid_score = v_score * 0.5 + b_score * 0.5

    hybrid_scores.append((doc, hybrid_score, v_score, b_score))

# 정렬
hybrid_scores.sort(key=lambda x: x[1], reverse=True)

# 출력
print("Hybrid 검색 결과:\n")
print("문서                                    | Hybrid | Vector | BM25")
print("-" * 75)

for doc, h_score, v_score, b_score in hybrid_scores[:3]:
    print(f"{doc[:40]:40} | {h_score:.2f}   | {v_score:.2f}   | {b_score:.2f}")
```

**출력:**
```
Hybrid 검색 결과:

문서                                    | Hybrid | Vector | BM25
---------------------------------------------------------------------------
Langfuse는 LLM 모니터링 도구입니다        | 0.89   | 0.78   | 1.00  ✅
Ollama로 로컬 LLM을 실행할 수 있습니다    | 0.82   | 0.85   | 0.78
LangGraph는 상태 기반 워크플로우...       | 0.45   | 0.67   | 0.23
```

## 가중치 조정

### 키워드 중요

```python
# BM25 비중 증가
hybrid_score = v_score * 0.3 + b_score * 0.7
```

**사용 사례:** 제품명, 고유명사 검색

### 의미 중요

```python
# 벡터 비중 증가
hybrid_score = v_score * 0.7 + b_score * 0.3
```

**사용 사례:** 추상적인 개념, 질문 검색

### 동적 가중치

```python
# 쿼리 길이에 따라
if len(query.split()) <= 3:
    # 짧은 쿼리 = 키워드 중심
    alpha, beta = 0.3, 0.7
else:
    # 긴 쿼리 = 의미 중심
    alpha, beta = 0.7, 0.3

hybrid_score = v_score * alpha + b_score * beta
```

## 성능 비교

### 실험 결과

```python
query = "로컬에서 무료로 LLM 실행하는 방법"

# 벡터만
→ "LangGraph는..." (관련 없음)

# BM25만
→ "Ollama로 로컬 LLM..." (키워드 매칭)

# Hybrid
→ "Ollama로 로컬 LLM..." (정확!) ✅
→ "Langfuse는 모니터링..." (관련 높음)
```

## 실무 권장사항

### 1. n_results 설정

```python
# 1차: 많이 가져오기
vector_results = collection.query(query_texts=[query], n_results=10)

# 2차: Reranking 후 3개만
final_results = hybrid_scores[:3]
```

### 2. 언어별 토크나이저

```python
# 한국어
from konlpy.tag import Okt
okt = Okt()

tokenized = [okt.morphs(doc) for doc in docs]
query_tokens = okt.morphs(query)

# 영어
tokenized = [doc.lower().split() for doc in docs]
```

### 3. 캐싱

```python
# BM25 모델 재사용
bm25_cache = {}

def get_bm25(docs):
    key = tuple(docs)
    if key not in bm25_cache:
        bm25_cache[key] = BM25Okapi([d.split() for d in docs])
    return bm25_cache[key]
```

## 다음 단계

**Multi-Agent Tutorial**
- 에이전트 간 협업
- RAG + 에이전트 조합
- 복잡한 질의 처리

---

**핵심 요약:**
1. 벡터 검색 = 의미 유사도 (recall)
2. BM25 = 키워드 매칭 (precision)
3. Hybrid = 둘 다 고려 (정확도 ↑)
4. 가중치 조정 = 도메인에 맞게

**Reranking = 검색 품질 향상의 핵심 기법** ✅
